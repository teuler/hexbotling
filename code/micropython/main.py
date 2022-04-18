# ----------------------------------------------------------------------------
# main.py
#
# Main program
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

SRV_RANGE_US   = [(900, 1650), (700, 1600)]
SRV_RANGE_DEG  = [(-30, 45), (-45, 45)]
SRV_ID         = bytearray([0,1])
SRV_PIN        = bytearray([board.D2, board.D3])
SRV_MIN_US     = const(700)
SRV_MAX_US     = const(2300)

def wait():
  while _SM.is_moving:
    time.sleep_ms(100)

# ----------------------------------------------------------------------------
if __name__ == "__main__":
  _Servos = []
  _SM = ServoManager(2, verbose=True)
  for j in range(len(SRV_ID)):
    srv = Servo(SRV_PIN[j], freq=100,
        us_range=SRV_RANGE_US[j],
        ang_range=SRV_RANGE_DEG[j]
      )
    _SM.add_servo(SRV_ID[j], srv)

  _SM.move([0,1], [0,0])
  time.sleep_ms(2000)

  _SM.move([0,1], [20,0], 200)
  wait()

  for i in range(10):
    _SM.move([0,1], [20,-30], 500)
    wait()
    _SM.move([0,1], [0,-30], 200)
    wait()
    _SM.move([0,1], [0,30], 500)
    wait()
    _SM.move([0,1], [20,30], 200)
    wait()
  _SM.move([0,1], [0,0], 1000)
  wait()

  print("Done.")

# ----------------------------------------------------------------------------
