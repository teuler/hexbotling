# ----------------------------------------------------------------------------
# calibrate_servos.py
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-03-21, v1.0
# ----------------------------------------------------------------------------
import time
from micropython import const
from robotling_lib.platform.rp2 import board_rp2 as board
from robotling_lib.motors.servo import Servo
from robotling_lib.motors.servo_manager import ServoManager

# pylint: disable=bad-whitespace
SRV_MIN_US     = const(700)
SRV_MAX_US     = const(2300)

SRV_ID         = bytearray([0,1])
SRV_PIN        = bytearray([board.D2, board.D3])
SRV_RANGE_US   = [(900, 1650), (700, 1600)]
SRV_RANGE_DEG  = [(-30, 45), (-45, 45)]
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
def Calibrate():
  new_pos_us = []
  for i in range(len(SRV_ID)):
    temp = []
    for j in range(3):
      pos_deg = 0 if j == 0 else SRV_RANGE_DEG[i][j-1]
      _SM._Servos[SRV_ID[i]].angle = pos_deg
      pos_us = _SM._Servos[SRV_ID[i]].angle_in_us(pos_deg)
      print(f"Servo {SRV_ID[i]:2d}, target angle {pos_deg:4d} deg")
      print(f"-> {_SM._Servos[SRV_ID[i]].angle_in_us(pos_deg)} us")
      s = "-"
      while not s.lower() == "y":
        s = input("   `y` for done or increment/decrement in [us]: ").lower()
        dt_us = 0
        try:
          dt_us = int(s)
        except ValueError:
          if len(s) > 0:
            print("   Not a number")
          else:
            temp.append([SRV_ID[i], pos_deg, pos_us])
            continue
        if dt_us != 0:
          pos_us += dt_us
          pos_us = min(max(pos_us, SRV_MIN_US), SRV_MAX_US)
          print(f"   New position [us]: {pos_us}")
          _SM._Servos[SRV_ID[i]].write_us(pos_us)
    new_pos_us.append(temp)
  print("Done.")
  for row in new_pos_us:
    print(f"Servo {row[0][0]:2d}: {row[1][1]} = {row[1][2]}, " \
          "{row[2][1]} = {row[2][2]}")
  print(new_pos_us)

# ----------------------------------------------------------------------------
if __name__ == "__main__":
  _Servos = []
  n = len(SRV_ID)
  _SM = ServoManager(n, verbose=True)
  for j in range(n):
    srv = Servo(SRV_PIN[j], freq=50,
        us_range=SRV_RANGE_US[j],
        ang_range=SRV_RANGE_DEG[j]
      )
    _SM.add_servo(SRV_ID[j], srv)

  empty = False
  while not empty:
    s = input()
    empty = len(s) == 0

  Calibrate()
  print("Done.")

# ----------------------------------------------------------------------------
