# ----------------------------------------------------------------------------
# hxbl_config.py
#
# Configuration
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-05-04, v1.0
# ----------------------------------------------------------------------------
import array
from micropython import const
from servo import servo2040 as srv

# pylint: disable=bad-whitespace
# Firmware info
HXBL_VERSION       = 1.0
HXBL_INFO          = "Hexbotling"
DEBUG              = const(1)
CALIBRATE          = []

# Control how hardware is kept updated
HW_CORE            = const(0)   # 1=hardware update runs on second core
APPROX_SPIN_MS     = const(5)   # core==0, approx. duration of hardware update
MIN_UPDATE_MS      = const(20)  # core==0, minimal time between hardware updates
PULSE_STEPS        = const(25)  # Number of steps for Pixel/RGB pulsing

# Global parameters
MAX_CURR_A         = 1.0         # maximum for normalizing sensed current
DT_CURR_UPDATE     = const(50)
MAX_VOLT_V         = 5.5         # maximum for normalizing voltage
BATT_SERVO_THRES_V = 4.6
DT_VOLT_UPDATE     = const(2000)

# LED-related
LEDS_BRIGHTNESS    = 0.5         # maximum LED brighness (0..1)
LEDS_FREQ          = const(20)   # Hz (frequency of LED driver)
ID_LED_CURR        = const(0)    # ID of LED for current load indicator
ID_LED_VOLT        = const(2)    # ID of LED for servo voltage indicator
ID_LED_PULSE       = const(5)    # ID of pulsing LED

# ----------------------------------------------------------------------------
# Leg- and servo-related definitions and calibration data
#
# Leg order:
# ---------
# front   0  __  1
#          \|  |/
# center 2--|  |--3
#          /|__|\
# back    4      5
#
LEG_FL            = const(0)
LEG_FR            = const(1)
LEG_CL            = const(2)
LEG_CR            = const(3)
LEG_BL            = const(4)
LEG_BR            = const(5)

# Servo order:
# -----------
#    --1--0  __  -2--3-
#          \|  |/
#   --5--4--|  |---6--7-
#          /|__|\
#    --9--8      10-11-
#
SRV_COUNT         = const(12)
SRV_ID            = bytearray([0,1, 2,3, 4,5, 6,7, 8,9, 10,11])
SRV_RANGE_US      = [
    (1000, 1950), (1100, 1900),  # 0,1
    (1050, 2050), (1110, 2070),  # 2.3
    ( 900, 1650), ( 700, 1600),  # 4,5
    ( 900, 1650), ( 700, 1600),  # 6,7
    (1570-450, 1570+450), (1535-450, 1535+450),  # 8,9
    (1505-450, 1505+450), (1630-450, 1630+450)   # 10,11
  ]
SRV_PIN           = bytearray([
    srv.SERVO_1,  srv.SERVO_2,  srv.SERVO_3,  srv.SERVO_4,
    srv.SERVO_5,  srv.SERVO_6,  srv.SERVO_7,  srv.SERVO_8,
    srv.SERVO_9,  srv.SERVO_10, srv.SERVO_11, srv.SERVO_12
  ])
SRV_COX           = bytearray([0,2,4,6,8,10])
SRV_COX_DIR       = array.array("h", [ 1,-1, 1,-1, 1,-1])
SRV_FEM           = bytearray([1,3,5,7,9,11])

# Servo ranges (for all legs)
SRV_RANGE_DEG     = [(-45, 45), (-45, 45)]
SRV_MIN_US        = const(700)
SRV_MAX_US        = const(2300)
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
