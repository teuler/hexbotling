# ----------------------------------------------------------------------------
# hxbl_walk_engine.py
#
# Walk engine
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-05-04, v1.0
# ----------------------------------------------------------------------------
import sys
import array
import time
import hxbl_config as cfg
import hxbl_global as glb
from time import sleep_ms, ticks_ms, ticks_diff
from hxbl_tripod_gait2 import TripodGait
from micropython import const
from pimoroni import Analog, AnalogMux, Button
from servo import servo2040
from plasma import WS2812
from machine import Pin
from robotling_lib.motors.servo_manager import ServoManager
from robotling_lib.motors.servo2040 import Servo
from robotling_lib.misc.helpers import timed_function, TemporalFilter
from robotling_lib.misc.pulse_pixel_led import PulsePixelLED_Hue

# pylint: disable=bad-whitespace
__version__  = "0.1.0.0"
MIN_DIR_VAL  = 0.15
MIN_VEL_VAL  = 0.10
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class WalkEngine(object):
  """Walk engine"""

  def __init__(self, verbose=True):
    # Initializing ...
    glb.toLog("Initializing walk engine ...", head=False)
    self._verbose = verbose
    self._state = glb.STA_NONE
    self._isUpdateStatusLEDs = True
    self._tLastVoltUpdate = 0
    self._tLastCurrUpdate = 0
    self._tLastCmd = 0

    # Define walk control variables
    self._vel = 1.
    self._dir = 0.
    self._rev = False

    # Configure LEDs
    self._LEDs = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)
    self._Pixel = PulsePixelLED_Hue(
        self._LEDs.set_hsv, n_steps=cfg.PULSE_STEPS, iLED=cfg.ID_LED_PULSE
      )
    self._pinMsgLED = Pin(cfg.MSG_LED_PIN, Pin.OUT)
    glb.toLog("LED array ready.", green=True)

    # Configure sensors
    self._adcU = Analog(servo2040.SHARED_ADC, servo2040.VOLTAGE_GAIN)
    self._adcI = Analog(
        servo2040.SHARED_ADC, servo2040.CURRENT_GAIN,
        servo2040.SHUNT_RESISTOR, servo2040.CURRENT_OFFSET
      )
    self._adcAIn = Analog(servo2040.SHARED_ADC)
    self._mux = AnalogMux(
        servo2040.ADC_ADDR_0, servo2040.ADC_ADDR_1, servo2040.ADC_ADDR_2
      )
    self._servoU_V = 0
    self._servoI_A = 0
    self._servoI_minmax = array.array("f", [0,0])
    self._servoAvI_A = TemporalFilter(10)
    self._sensData = array.array("f", [0]*servo2040.NUM_SENSORS)
    self._sensDataMask = 0b000000
    glb.toLog("Analog sensors ready.", green=True)
    v = self.get_servo_battery_V()
    errC = glb.ERR_OK if v > cfg.BATT_SERVO_THRES_V else glb.ERR_LOW_BATTERY
    glb.toLog("Servo battery = {0:.2f} V".format(v), errC=errC, green=True)

    # Configure button
    self._user_sw = Button(servo2040.USER_SW)

    # Configure servos and servo manager
    self._Servos = []
    self._SM = ServoManager(cfg.SRV_COUNT)
    for i, pin in enumerate(cfg.SRV_PIN):
      srv = Servo(
          pin, us_range=cfg.SRV_RANGE_US[i],
          ang_range=cfg.SRV_RANGE_DEG[i % 2]
        )
      self._Servos.append(srv)
      self._SM.add_servo(cfg.SRV_ID[i], srv)
    self._SM.trajectory = ServoManager.TRJ_SINE
    glb.toLog("Servo manager ready", green=True)
    if len(cfg.CALIBRATE) > 0:
      # If list of servo IDs is not empty, start interactive calibration ...
      self._SM.calibrate(cfg.CALIBRATE)
      sys.exit()

    # Create gait object
    self._Gait = TripodGait()

    # Getting ready ...
    self._LEDs.start(cfg.LEDS_FREQ)
    self._Pixel.dim(cfg.LEDS_BRIGHTNESS)
    self._Pixel.startPulse(0.1)
    self._SM.define_servo_pos(cfg.SRV_RESTING_DEG)
    self.to_resting()
    self.to_neutral(dt_ms=1000)
    self._state = glb.STA_IDLE
    glb.toLog("... done.", head=False)

  def deinit(self):
    """ Shutting down walk engine
    """
    self._state = glb.STA_POWERING_DOWN
    self.to_resting(dt_ms=1000)
    self._SM.deinit()
    self._LEDs.clear()
    self._state = glb.STA_OFF
    glb.toLog("Walk engine shut down.")
    glb.toLog(
        "Current    : {0:.3f} ... {1:.3f} A"
        .format(self._servoI_minmax[0], self._servoI_minmax[1]),
        head=False
      )

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def to_neutral(self, dt_ms=0):
    """ Assume neutral position
    """
    res = self._Gait.get_next_servo_pos(stop=True)
    self._SM.move(cfg.SRV_ID, res[1], dt_ms)
    sleep_ms(1000 if dt_ms <= 0 else dt_ms +200)

  def to_resting(self, dt_ms=2000):
    """ Assume resting position
    """
    self._SM.move(cfg.SRV_ID, cfg.SRV_RESTING_DEG, dt_ms)
    sleep_ms(1000 if dt_ms <= 0 else dt_ms +200)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def walk(self):
    """ Start walking, defined by the properties `direction` and `velocity`
    """
    if abs(self._dir) < 0.0001:
      self._state = glb.STA_WALKING if not self._rev else glb.STA_REVERSING
    else:
      self._state = glb.STA_TURNING
    self.spin()

  def stop(self):
    """ Stop movement gracefully
    """
    self._state = glb.STA_STOPPING
    self.spin()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  def spin(self):
    """ Keep walk engine running; needs to be called frequently
    """
    # Keep LEDs update, if requested
    if self._isUpdateStatusLEDs:
      t = ticks_ms()
      if ticks_diff(t, self._tLastVoltUpdate) > cfg.DT_VOLT_UPDATE:
        self.get_servo_battery_V()
        self._tLastVoltUpdate = t
      if ticks_diff(t, self._tLastCurrUpdate) > cfg.DT_CURR_UPDATE:
        self.get_servo_load_A()
        self._servoI_minmax[0] = min(self._servoI_minmax[0], self._servoI_A)
        self._servoI_minmax[1] = max(self._servoI_minmax[1], self._servoI_A)
        self._tLastCurrUpdate = t

    # Pulse pixel
    self._Pixel.spin()

    # Update analog-in sensors, if activated
    if self._sensDataMask > 0:
      self.update_analog_sensors()

    # Update walk engine
    st = self._state
    sm = self._SM
    if st == glb.STA_IDLE or sm.is_moving:
      # Walk engine is idle or still executing the next move
      return

    dr = self._dir
    rv = self._rev
    if st in [glb.STA_WALKING, glb.STA_REVERSING, glb.STA_TURNING]:
      # Execute next move after applying direction
      dt, ang, trj = self._Gait.get_next_servo_pos(turn_dir=dr, rev=rv)
      dt_ms = min(max(int(dt /self._vel), 100), 1500)
      #print(dt, dt_ms, ang, self._vel)
      #print("WE_MOVE", time.ticks_diff(time.ticks_ms(), self._tLastCmd), "ms")
      sm.trajectory = trj
      sm.move(cfg.SRV_ID, ang, dt_ms)

    elif st == glb.STA_STOPPING:
      # Execute stop
      dt, ang, trj = self._Gait.get_next_servo_pos(stop=True)
      sm.trajectory = trj
      sm.move(cfg.SRV_ID, ang, dt)
      self._state = glb.STA_IDLE

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def state(self):
    return self._state

  @property
  def is_button_pressed(self):
    return self._user_sw.read()

  def set_params(self, dir, rev, vel):
    """ Set movement parameters direction (with `dir` <0.1, left turn; >0.1,
        right turn; 0, straight ahead), normal or reverse (`rev` == True),
        and velocity (with `vel` <1, slower; >1 faster).
    """
    d = max(min(dir, 1.0), -1.0) if dir is not None else self._dir
    self._dir = d if abs(d) >= MIN_DIR_VAL else 0
    self._rev = bool(rev) if rev is not None else self._rev
    self._vel = max(vel, MIN_VEL_VAL) if vel is not None else self._vel

  def get_params(self):
    """ Returns direction, normal or reverse, and velocity as a tuple.
    """
    return self._dir, self._rev, self._vel

  def set_LED(self, state):
    self._pinMsgLED.value(state)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def get_servo_load_A(self, update=True):
    """ Returns the current load of the servos as a running average;
        if `update` == True, it re-reads the value first.
        If `self._isUpdateStatusLEDs` == True, the assigned LED is updated
        as well.
    """
    if update:
      self._mux.select(servo2040.CURRENT_SENSE_ADDR)
      I = self._adcI.read_current()
      if self._isUpdateStatusLEDs:
        hue = 0.3 *(1 -(min(max(I, 0) /cfg.MAX_CURR_A, 1)))
        self._LEDs.set_hsv(cfg.ID_LED_CURR, hue, 1.0, cfg.LEDS_BRIGHTNESS)
      self._servoI_A = self._servoAvI_A.mean(I)
    return self._servoI_A

  def get_servo_battery_V(self, update=True):
    """ Returns the last voltage; if `update` == True, it re-reads the value
        first. If `self._isUpdateStatusLEDs` == True, the assigned LED is
        updated as well.
    """
    if update:
      self._mux.select(servo2040.VOLTAGE_SENSE_ADDR)
      U = self._adcU.read_voltage()
      if self._isUpdateStatusLEDs:
        hue = 0.3 *(min(max(U, 0) /cfg.MAX_VOLT_V, 1))
        self._LEDs.set_hsv(cfg.ID_LED_VOLT, hue, 1.0, cfg.LEDS_BRIGHTNESS)
      self._servoU_V = U
    return self._servoU_V

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def update_analog_sensors(self):
    """ Updates the analog-in sensor readings for those indicated in the bit
        mask `_sensDataMask`. Is automatically called ny `spin()`.
    """
    for iS in range(servo2040.NUM_SENSORS):
      if self._sensDataMask & (1 << iS):
        self._mux.select(iS)
        self._sensData[iS] = self._adcAIn.read_voltage()

  @property
  def analog_sensors_V(self):
    """ Returns the last analog-in sensor readings
    """
    return self._sensData

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def servos_off(self):
    """ Turn all servos off
    """
    self._SM.turn_all_off()

# ----------------------------------------------------------------------------
