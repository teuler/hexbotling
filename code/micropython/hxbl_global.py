# ----------------------------------------------------------------------------
# hbxl_global.py
#
# Global definitions
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2021-05-04, v1.0
# ----------------------------------------------------------------------------
import gc
from micropython import const
import robotling_lib.misc.ansi_color as ansi

# pylint: disable=bad-whitespace
# Commands
CMD_NONE            = const(0)
CMD_STOP            = const(1)
CMD_MOVE            = const(2)
CMD_POWER_DOWN      = const(3)
# ...

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
# ...
# pylint: enable=bad-whitespace

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
    print(c +"[{0:>12}] {1:35}".format(s, sMsg) +ansi.BLACK)
  else:
    c = ansi.LIGHT_BLUE if not color else color
    print(c +sMsg +ansi.BLACK)

# ----------------------------------------------------------------------------
