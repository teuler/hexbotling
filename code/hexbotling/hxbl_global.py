# ----------------------------------------------------------------------------
# hbxl_global.py
#
# Global definitions
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2021-05-04, v1.0
# 2022-07-11, v1.1, now also compatible with standard Python 3
# ----------------------------------------------------------------------------
import gc
try:
  from micropython import const
  import robotling_lib.misc.ansi_color as ansi
  MICROPYTHON = True
except ModuleNotFoundError:
  const = lambda x: x
  import hexbotling.robotling_lib.misc.ansi_color as ansi
  MICROPYTHON = False

# pylint: disable=bad-whitespace
# ----------------------------------------------------------------------------
# Internal commands to control the walk engine
CMD_NONE            = const(0)
CMD_STOP            = const(1)
CMD_MOVE            = const(2)
CMD_POWER_DOWN      = const(99)

# States
STA_NONE            = const(0)
STA_IDLE            = const(1)
STA_STOPPING        = const(2)
STA_WALKING         = const(3)
STA_REVERSING       = const(4)
STA_TURNING         = const(5)
STA_POWERING_DOWN   = const(6)
STA_OFF             = const(7)
# ...

# Error codes
ERR_OK              = const(0)
ERR_LOW_BATTERY     = const(-1)
ERR_INVALID_MSG     = const(-2)
ERR_UNKNOWN_MSG     = const(-3)
ERR_TOO_FEW_PARAMS  = const(-4)
ERR_CANNOT_CONNECT  = const(-5)

# ...
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
'''
class RobotState(object):
  """Class subsummizing the robot's state"""
  # pylint: disable=bad-whitespace
  WE_state         = STA_NONE
  last_cmd         = CMD_NONE
  move_dir         = 0
  move_vel         = 1.0
  move_rev         = False
'''
# ----------------------------------------------------------------------------
def toLog(sMsg, sTopic="", errC=0, green=False, color=None, head=True):
  """ Print message to history
  """
  c = ""
  if errC == 0:
    s = "INFO" if len(sTopic) == 0 else sTopic
    if green:
      c = ansi.GREEN
    else:
      c = ansi.BLUE
  elif errC > 0:
    s = "WARNING"
    c = ansi.YELLOW
  else:
    s = "ERROR"
    c = ansi.RED
  if color:
    c = color
  if head:
    msg = "[{0:>12}] {1:35}".format(s, sMsg)
    msg = c +msg +ansi.BLACK if MICROPYTHON else msg
    print(msg)
  else:
    c = ansi.LIGHT_BLUE if not color else color
    msg = c +sMsg +ansi.BLACK if MICROPYTHON else sMsg
    print(msg)

# ----------------------------------------------------------------------------
