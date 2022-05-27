# ----------------------------------------------------------------------------
# hxbl_server.py
#
# Server that offers an interface to the walk engine
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-05-04, v1.0
# ----------------------------------------------------------------------------
import time
import hxbl_config as cfg
import hxbl_global as glb
from micropython import const
from hxbl_base import HexbotlingBase
from hxbl_walk_engine import WalkEngine as WE
from robotling_lib.platform.platform import platform as pf
from robotling_lib.misc.helpers import timed_function
import robotling_lib.misc.ansi_color as ansi

# pylint: disable=bad-whitespace
__version__  = "0.1.0.0"

# Global variables to communicate with task on core 1
# (Do not access other than via the `Server` instance!!)
g_state      = glb.STA_NONE
g_cmd        = glb.CMD_NONE
g_counter    = 0
g_we         = None
g_we_state   = glb.STA_NONE
g_move_dir   = 0.0
g_move_vel   = 1.0
g_move_rev   = False
g_do_exit    = False
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class Server(HexbotlingBase):
  """Server to access the walk engine"""

  def __init__(self, core=0, verbose=False):
    global g_state, g_we

    glb.toLog(
        "Hexbotling server (servo2040 board, software v{0}) "+
        "w/ MicroPython {1} ({2})"
        .format(__version__, pf.sysInfo[2], pf.sysInfo[0]), head=False,
        color=ansi.CYAN
      )
    glb.toLog("Initializing ...", head=False)
    super().__init__()
    glb.toLog(self.ID, sTopic="GUID")

    # Initializing ...
    g_state = glb.STA_NONE
    self._verbose = verbose
    self._core = core
    self._spin_period_ms = 0
    self._spin_t_last_ms = 0
    self._user_abort = False

    # Create walk engine object
    g_we = WE()

    # Depending on `core`, the thread that updates the hardware either runs
    # on the second core (`core` == 1) or on the same core as the main program
    # (`core` == 0). In the latter case, the classes `sleep_ms()` function
    # needs to be used and called frequencly to keep the hardware updated.
    if self._core == 1:
      # Starting hardware thread on core 1 and wait until it is ready
      import _thread
      self._Task = _thread.start_new_thread(self._task_core1, ())
      glb.toLog("Walk engine thread on core 1 starting ...")
      while not g_we_state == glb.STA_IDLE:
        time.sleep_ms(50)
      glb.toLog("Walk engine thread ready.", green=True)
    else:
      # Do not use core 1 for hardware thread; instead the main loop has to
      # call `sleep_ms()` frequently. Here, prime that sleep function ...
      self.sleep_ms(period_ms=cfg.MIN_UPDATE_MS, callback=self._task_core0)
      glb.toLog("Walk engine co-uses core 0.")

    # Force collect and increase CPU speed, if requested
    glb.toLog(self.collectMemory())
    '''
    if self.Cfg.SRV_CPU_SPEED is not 125_000_000:
      from machine import freq
      freq(self.Cfg.SRV_CPU_SPEED)
      toLog("CPU speed set to {0} MHz".format(self.Cfg.SRV_CPU_SPEED /10**6))
    '''
    g_state = glb.STA_IDLE
    glb.toLog("Ready.", head=False)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def deinit(self):
    global g_state, g_we

    if g_state is not glb.STA_OFF:
      glb.toLog("Powering down ...", head=False)
      self.power_down()
      while g_state is not glb.STA_OFF:
        self.sleep_ms(25)
    g_we.servos_off()
    self.uodatePowerDown()
    self.printReport()
    glb.toLog("... done.", head=False)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def state(self):
    """ Get `state` as a constant `STA_xxx` (`hxbl_global.py`)
    """
    global g_state
    return g_state

  @property
  def direction(self):
    """ Get current movement direction (see `turn()` for details)
    """
    global g_move_dir
    return g_move_dir

  @property
  def exit_requested(self):
    """ Get status of user button; True if pressed during `sleep_ms()`
    """
    return self._user_abort

  @property
  def velocity(self):
    """ Get/set velocity, with 1.0 normal speed, <1 faster and >1 slower
    """
    global g_move_vel
    return g_move_vel
  @velocity.setter
  def velocity(self, val):
    global g_move_vel
    g_move_vel = val

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def move_forward(self, wait_for_idle=False, reverse=False):
    """ Move straight forward using current gait and velocity.
        If `wait_for_idle` is True, then trigger action only when idle.
    """
    global g_cmd, g_move_dir, g_move_rev, g_we_state
    if not wait_for_idle or g_we_state == glb.STA_IDLE:
      g_move_dir = 0.
      g_move_rev = reverse
      g_cmd = glb.CMD_MOVE

  def move_backward(self, wait_for_idle=False):
    self.move_forward(wait_for_idle, True)

  def turn(self, dir, wait_for_idle=False):
    """ Turn using current gait and velocity; making with `dir` < 0 a left and
        `dir` > 0 a right turn. The size of `dir` (1 >= |`dir`| > 0) giving
        the turning strength (e.g. 1.=turn in place, 0.2=walk in a shallow
        curve). If `wait_for_idle` is True, then trigger action only when idle.
    """
    global g_cmd, g_move_dir, g_we_state
    if not wait_for_idle or g_we_state == glb.STA_IDLE:
      g_move_dir = max(min(dir, 1.0), -1.0)
      g_cmd = glb.CMD_MOVE

  def stop(self):
    """ Stop if walking
    """
    global g_cmd, g_we_state
    if g_we_state in [glb.STA_WALKING, glb.STA_TURNING]:
      g_cmd = glb.CMD_STOP

  def power_down(self):
    """ Power down and end task
    """
    global g_cmd, g_move_dir
    g_move_dir = 0.
    g_cmd = glb.CMD_POWER_DOWN

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def sleep_ms(self, dur_ms=0, period_ms=-1, callback=None):
    """ This function is an alternative to `time.sleep_ms()`; it sleeps but
        also keep the robot's hardware updated.
        e.g. "sleep_ms(period_ms=50, callback=myfunction)"" is setting it up;
        "sleep_ms(100)"" (~sleep for 100 ms) or "sleep_ms()" keeps it
        running.
    """
    global g_we

    if self._spin_period_ms > 0:
      p_ms = self._spin_period_ms
      p_us = p_ms *1000
      d_us = dur_ms *1000

      if dur_ms > 0 and dur_ms < (p_ms -cfg.APPROX_SPIN_MS):
        time.sleep_ms(int(dur_ms))

      elif dur_ms >= (p_ms -cfg.APPROX_SPIN_MS):
        # Sleep for given time while updating the board regularily; start by
        # sleeping for the remainder of the time to the next update ...
        t_us  = time.ticks_us()
        dt_ms = time.ticks_diff(time.ticks_ms(), self._spin_t_last_ms)
        if dt_ms > 0 and dt_ms < p_ms:
          time.sleep_ms(dt_ms)

        # Update
        self._spin_callback()
        if g_we.is_button_pressed:
          self._user_abort = True
          return
        self._spin_t_last_ms = time.ticks_ms()

        # Check if sleep time is left ...
        d_us = d_us -int(time.ticks_diff(time.ticks_us(), t_us))
        if d_us <= 0:
          return

        # ... and if so, pass the remaining time by updating at regular
        # intervals
        while time.ticks_diff(time.ticks_us(), t_us) < (d_us -p_us):
          time.sleep_us(p_us)
          self._spin_callback()
          if g_we.is_button_pressed:
            self._user_abort = True
            return

        # Remember time of last update
        self._spin_t_last_ms = time.ticks_ms()

      else:
        # No sleep duration given, thus just check if time is up and if so,
        # call update and remember time
        d_ms = time.ticks_diff(time.ticks_ms(), self._spin_t_last_ms)
        if d_ms > self._spin_period_ms:
          self._spin_callback()
          self._spin_t_last_ms = time.ticks_ms()

    elif period_ms > 0:
      # Set up spin parameters and return
      self._spin_period_ms = period_ms
      self._spin_callback = callback
      self._spinTracker.reset(period_ms)
      self._spin_t_last_ms = time.ticks_ms()
    else:
      # Spin parameters not setup, therefore just sleep
      time.sleep_ms(dur_ms)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _task_core0(self):
    """ This is the core 0-version of the routine that keeps the hardware
        updated and responds to commands (e.g. move, turn).
        - It is called by `sleep_ms()`.
        - It uses only global variables for external objects to stay
          compatible with the core-1 version below.
    """
    global g_we_state, g_state, g_counter
    global g_cmd, g_do_exit
    global g_move_dir, g_move_rev, g_move_vel
    global g_we

    try:
      self.updateStart()

      if g_state == glb.STA_OFF:
        # Nothing to do
        return

      if g_state == glb.STA_POWERING_DOWN:
        # Powering down, clean up ...
        g_we.deinit()
        g_state = glb.STA_OFF
        return

      if g_cmd is not glb.CMD_NONE:
        # Handle new command ...

        if g_cmd == glb.CMD_MOVE:
          # Walk ...
          g_we.set_params(g_move_dir, g_move_rev, g_move_vel)
          g_we.walk()
          if abs(g_move_dir) > 0.1:
            g_state = glb.STA_TURNING
          elif g_move_rev:
            g_state = glb.STA_REVERSING
          else:
            g_state = glb.STA_WALKING

        elif g_cmd in [glb.CMD_STOP, glb.CMD_POWER_DOWN]:
          # Stop or power down ...
          g_we.stop()
          g_do_exit = g_cmd == glb.CMD_POWER_DOWN
          g_state = glb.STA_STOPPING

        g_cmd = glb.CMD_NONE

      # Wait for transitions to update state accordingly ...
      if g_state == glb.STA_STOPPING and g_we_state == glb.STA_IDLE:
        g_state = glb.STA_IDLE
      if g_state == glb.STA_IDLE and g_do_exit:
        g_state = glb.STA_POWERING_DOWN

      # Spin everyone who needs spinning
      g_we.spin()
      g_we_state = g_we.state
      g_counter += 1

    finally:
      self.updateEnd()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  '''
  @staticmethod
  def _task_core1():
    """ This is the core 1-version of the routine that keeps the hardware
        updated and responds to commands (e.g. move, turn).
        - It runs independently on core 1; in parallel to the main program on
          core 0.
        - It communicates via global variables.
    """
    global g_we_state, g_state, g_counter
    global g_cmd, g_do_exit
    global g_move_dir, g_move_rev
    global g_we

    # Loop
    g_do_exit = False
    try:
      try:
        g_we_state = glb.STA_IDLE

        # Main loop ...
        while g_state is not glb.STA_POWERING_DOWN:
          if g_cmd is not glb.CMD_NONE:
            # Handle new command ...

            if g_cmd == glb.CMD_MOVE:
              g_we.direction = g_move_dir
              g_we.reverse = g_move_rev
              g_we.walk()
              if abs(g_move_dir) > 0.01:
                g_state = glb.STA_TURNING
              elif g_move_rev:
                g_state = glb.STA_REVERSING
              else:
                g_state = glb.STA_WALKING

            if g_cmd in [glb.CMD_STOP, glb.CMD_POWER_DOWN]:
              # Stop or power down ...
              g_we.stop()
              g_state = glb.STA_STOPPING
              g_do_exit = g_cmd == glb.CMD_POWER_DOWN

            g_cmd = glb.CMD_NONE

          # Wait for transitions to update state accordingly ...
          if g_state == glb.STA_STOPPING and g_we_state == glb.STA_IDLE:
            g_state = glb.STA_IDLE
          if g_state == glb.STA_IDLE and g_do_exit:
            g_state = glb.STA_POWERING_DOWN

          # Spin everyone who needs spinning
          g_we.spin()
          g_we_state = g_we.state
          g_counter += 1

          # Wait for a little while
          time.sleep_ms(25)
          print(g_counter)

      except KeyboardInterrupt:
        pass

    finally:
      g_we.deinit()
      glb.toLog("Hardware thread ended.")
      g_state = glb.STA_OFF
  '''
# ----------------------------------------------------------------------------
