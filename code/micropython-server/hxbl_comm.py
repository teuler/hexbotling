# ----------------------------------------------------------------------------
# hbxl_comm.py
#
# Communication
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2021-08-27, v1.0
# ----------------------------------------------------------------------------
import array
try:
  from micropython import const
  from time import ticks_ms, ticks_diff
  import robotling_lib.misc.ansi_color as ansi
  import hxbl_global as glb
  MICROPYTHON = True
except ModuleNotFoundError:
  const = lambda x: x
  from time import monotonic
  ticks_ms = lambda : int(monotonic()*1_000)
  ticks_diff = lambda x,y: int(x -y)
  import hexbotling.robotling_lib.misc.ansi_color as ansi
  import hexbotling.hxbl_global as glb
  MICROPYTHON = False

# pylint: disable=bad-whitespace
# ----------------------------------------------------------------------------
# Messages
MSG_NONE       = const(0)
# Nothing to do, no parameters
#
MSG_STOP       = const(1)
# Stop the robot immediately, no parameters
#
MSG_MOVE       = const(2)
# Move robot; direction and velocity depends on the parameters:
# `dir`:   with `dir` < 0 a left and `dir` > 0 a right turn, and `dir` size
#          giving the turning strength (0 <= |`dir`| <= 100)
#          e.g. 100=turn in place, 20=walk in a shallow curve).
# `vel`:   with 1 <= `vel` <= 125 and `vel` == 50 normal velocity
# `rev`:   1=reverse movement, 0=normal
# `lift`:  leg lift in [°]
#
MSG_GAIT       = const(3)
# Change gait
# `gait`   a gait index
#
MSG_STA        = const(20)
# Acknowledge command and return status:
# `cmdID`: ID of last received command
# `sLoad`: Current servo load in [A*10]
# 'sVolt': Voltage of servo battery in [V*10]
#
MSG_POWER_DOWN = const(99)
# Bring legs in resting position and power down
#
MSG_PING       = const(101)
# Used to check if server/client connection is up and running
# pylint: enable=bad-whitespace

N_PARAMS_MSG = {
    MSG_NONE: 0,
    MSG_STOP: 0, MSG_MOVE: 4, MSG_GAIT: 1,
    MSG_STA: 3, MSG_POWER_DOWN: 0,
    MSG_PING: 0
  }

# ----------------------------------------------------------------------------
class Communicator(object):
  """Class with convinience routines for client-server communication"""

  def __init__(self, msgr):
    """ Initialize communication
    """
    self._Msgr = msgr

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def wait_for_client(self, f_wait_ms=None, tOut_s=15, verbose=False):
    """ Wait for client to handshake. If it does, the connection is established
        and True is returned, else (or if timeout occurs) return False.
    """
    self._Msgr._isConnected = False
    if self._Msgr._isReady:
      t = ticks_ms()
      while True:
        res = self._Msgr.read()
        if res:
          if verbose:
            print("-> ", res)
          if len(res) == 2 and res[1] == MSG_PING:
            # Success
            self._Msgr.write(array.array(self._Msgr._arrType, [MSG_PING]))
            self._Msgr._log("Client responded.")
            self._Msgr._isConnected = True
            break
        if ticks_diff(ticks_ms(), t) > tOut_s*1_000:
          # Timeout
          break
        if f_wait_ms:
          f_wait_ms(500)
    return self._Msgr._isConnected

  def ping_server(self, f_wait_ms=None, tOut_s=5, verbose=False):
    """ Ping server, if it responds, the connection is established and True is
        returned, else (or if timeout occurs) return False.
    """
    self._Msgr._isConnected = False
    if self._Msgr._isReady:
      t = ticks_ms()
      while True:
        self._Msgr.write(array.array(self._Msgr._arrType, [MSG_PING]))
        res = self._Msgr.read()
        if res:
          if verbose:
            print("-> ", res)
          if len(res) == 2 and res[1] == MSG_PING:
            self._Msgr._log("Server responded.")
            self._Msgr._isConnected = True
            return True
        if ticks_diff(ticks_ms(), t) > tOut_s*1_000:
          # Timeout
          break
        if f_wait_ms:
          f_wait_ms(500)
    return self._Msgr._isConnected

  def send(self, msg):
    """ Send a message using the Messenger instance
    """
    self._Msgr.write(msg)

  def receive(self):
    """ Receive a message using the Messenger instance; returns message data
        array or `None`
    """
    return self._Msgr.read()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def check(self, msg):
    """ Checks if valid message, and returns an error code
    """
    if len(msg) < 2:
      return glb.ERR_INVALID_MSG
    if len(msg)-2 != N_PARAMS_MSG[msg[1]]:
      return glb.ERR_TOO_FEW_PARAMS, MSG_NONE
    return glb.ERR_OK

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def msgtoStr(self, msg, isReply=True):
    """ Returns the command/reply as a string
    """
    if len(msg) > 1:
      if msg[1] == MSG_MOVE:
        return (
            "MSG_MOVE: dir={0}, vel={1}, reverse={2}, leg lift={3}°"
            .format(
            msg[2],    # direction
            msg[3],    # velocity
            msg[4],    # 1=reverse
            msg[5])    # leg lift angle
        )
      if msg[1] == MSG_STOP:
        return ("MSG_STOP: -")
      if msg[1] == MSG_STA:
        return (
            "MSG_STA : last cmdID={0}, servo load={1:.1f} A at {2:.1f} V"
            .format(
            msg[2],    # last command idea
            msg[3]/10, # mean servo load in [A*10]
            msg[4]/10) # servo battery voltage in [V*10]
          )
    return "n/a"

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def is_connected(self):
    return self._Msgr._isConnected

  @property
  def available(self):
    return self._Msgr._available()

# ----------------------------------------------------------------------------
