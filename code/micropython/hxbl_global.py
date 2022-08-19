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
# Commands
# (to control the server (running on the servo2040 board); a subset of these
#  commands is also used internally to control the walk engine)
CMD_NONE            = const(0)
# Nothing to do, no parameters
#
CMD_STOP            = const(1)
# Stop the robot immediately, no parameters
#
CMD_MOVE            = const(2)
# Move robot; direction and velocity depends on the parameters:
# `dir`:   with `dir` < 0 a left and `dir` > 0 a right turn, and `dir` size
#          giving the turning strength (0 <= |`dir`| <= 100)
#          e.g. 100=turn in place, 20=walk in a shallow curve).
# `vel`:   with 1 <= `vel` <= 125 and `vel` == 50 normal velocity
# `rev`:   1=reverse movement, 0=normal
# `lift`:  leg lift in [°]
#
'''
CMD_SIT_DOWN        = const(3)
# Bring legs in resting position, no parameters
#
CMD_STAND_UP        = const(4)
# Bring legs in standing position, no parameters
#
'''
CMD_STA             = const(20)
# Acknowledge command and return status:
# `cmdID`: ID of last received command
# `sLoad`: Current servo load in [A*10]
# 'sVolt': Voltage of servo battery in [V*10]
#
CMD_POWER_DOWN      = const(99)
# Bring legs in resting position and power down
#
# ----------------------------------------------------------------------------
# Message format(s)
CMD_N_PARAMS = {
    CMD_NONE: 0, CMD_STOP: 0, CMD_MOVE: 4,
    CMD_STA: 3, CMD_POWER_DOWN: 0
}

def msgtoStr(msg, isReply=True):
  """ Returns the command/reply as a string
  """
  if len(msg) > 1:
    if msg[1] == CMD_MOVE:
      return (
          "CMD_MOVE: dir={0}, vel={1}, reverse={2}, leg lift={3}°"
          .format(
          msg[2],    # direction
          msg[3],    # velocity
          msg[4],    # 1=reverse
          msg[5])    # leg lift angle
      )
    if msg[1] == CMD_STOP:
      return ("CMD_STOP: -")
    if msg[1] == CMD_STA:
      return (
          "CMD_STA : last cmdID={0}, servo load={1:.1f} A at {2:.1f} V"
          .format(
          msg[2],    # last command idea
          msg[3]/10, # mean servo load in [A*10]
          msg[4]/10) # servo battery voltage in [V*10]
        )
  return "n/a"

# ----------------------------------------------------------------------------
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
ERR_UNKNOWN_CMD     = const(-3)
ERR_TOO_FEW_PARAMS  = const(4)

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
