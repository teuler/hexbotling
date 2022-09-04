#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# hexbotling_remote_bluetooth.py
# Receive game controller commands via USB and sends these commands via
# Bluetooth as simple messages (`messenger.py`) to the hexbotling
#
# The MIT License (MIT)
# Copyright (c) 2018-2022 Thomas Euler
# 2020-08-20, v1
# 2022-07-17, v2 - adapted to Hexbotling
# ---------------------------------------------------------------------
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import asyncio
import array
import numpy as np
import pygame
import time
import modules.joystick as joy
from argparse import ArgumentParser
from hexbotling.robotling_lib.misc.messenger import MessengerCOM
import hexbotling.hxbl_global as glb
import hexbotling.hxbl_comm as com

# pylint: disable=bad-whitespace
__version__        = "0.2.0.0"
COM_PORT           = 7
MSG_ARRAY_TYPE     = "b"
JY_ZERO_LIMIT      = 0.2
MAX_GAIT_TYPE      = 1
CHECK_PING_TIME_S  = 10
# pylint: ensable=bad-whitespace

# ---------------------------------------------------------------------
def parseCmdLn():
  parser = ArgumentParser()
  parser.add_argument('-p', '--port', type=str, default=COM_PORT)
  return parser.parse_args()

def wait_ms(dt):
  time.sleep(dt/1_000)

def exit_on_not_connected():
  if not Com.is_connected:
    print("\rERROR: Could get a serial connection")
    exit()

# ---------------------------------------------------------------------
class Params(object):
  def __init__(self):
    self._dir = 0
    self._vel = 50
    self._rev = False
    self._is_changed = False
    self._is_turbo = False
    self._lift_deg = 25
    self._type = 0

  def reset(self):
    self._is_changed = False

  @property
  def is_changed(self):
    return self._is_changed

  @property
  def dir(self):
    return self._dir
  @dir.setter
  def dir(self, val):
    if val != self._dir:
      self._dir = val
      self._is_changed = True

  @property
  def vel(self):
    return self._vel
  @vel.setter
  def vel(self, val):
    if val != self._vel:
      self._vel = val
      self._is_changed = True

  @property
  def rev(self):
    return self._rev
  @rev.setter
  def rev(self, val):
    if val != self._rev:
      self._rev = val
      self._is_changed = True

  @property
  def lift_deg(self):
    return self._lift_deg
  @lift_deg.setter
  def lift_deg(self, val):
    if val != self._lift_deg:
      self._lift_deg = val
      self._is_changed = True

  @property
  def type(self):
    return self._type

  def inc_type(self, inc=1):
    if inc > 0:
      self._type = self._type +1 if self._type < MAX_GAIT_TYPE else 0
    elif inc < 0:
      self._type = self._type -1 if self._type > 0 else MAX_GAIT_TYPE
    else:
      return
    self._is_changed = True

  def __repr__(self):
    return (
        f"dir={self.dir} vel={self.vel} rev={self.rev} " +
        f"lift_deg={self._lift_deg} type={self._type}"
      )
    return

# ---------------------------------------------------------------------
def getCmdMsgFromJoystickInput():
  """ Generate a new command based on the joystick input, if any
  """
  # Initialize input parameters
  params_changed = False
  msg = None

  # Button `A` prints help
  bA = JS.BtnA.pressed
  if bA is not None and bA:
    print("`A`                - Prints this help screenTurbo on/off")
    print("`B`                - Turbo on/off")
    print("`Y`                - Feet high/low")
    print("`X`                - Shutdown robot")
    print("left hat up/down   - Change gait")
    print("left joystick      - Walk forwards/backwards/turn")
    print("`Back`             - Exit program")

  # Button `B` toggles "turbo"
  bB = JS.BtnB.pressed
  if bB is not None and bB:
    params._is_turbo = not params._is_turbo
    print("Turbo {0}".format("ON" if params._is_turbo else "OFF"))

  # Button `X` shuts robot down
  bX = JS.BtnX.pressed
  if bX is not None and bX:
    msg = array.array(MSG_ARRAY_TYPE, [0, com.MSG_POWER_DOWN])

  # Button `Y` toggles foot height
  bY = JS.BtnY.pressed
  if bY is not None and bY:
    params._lift_deg = 25 if params._lift_deg != 25 else 50
    print("Foot lift height is {0}°".format(params._lift_deg))

  # The left hat controls gait
  hatL = JS.HatL.value
  if hatL is not None:
    if hatL[1] != 0:
      params.inc_type(hatL[1])
      msg = array.array(MSG_ARRAY_TYPE, [0, com.MSG_GAIT, params.type])
      print("Gait type changed to {0}".format(params.type))

  # Control walking ...
  xyL = JS.StickL.xy
  xyR = JS.StickR.xy
  if xyL is not None or xyR is not None or params_changed:
    params.reset()
    # Joystick input has changed
    if xyL is not None:
      # Calculate the direction by the x-axis deflection
      if abs(xyL[0]) >= JY_ZERO_LIMIT:
        params.dir = int(-xyL[0] *100)
      else:
        params.dir = 0
      # Calculate velocity by x-y vector length
      v = np.sqrt(xyL[0]**2 +xyL[1]**2)
      if v < JY_ZERO_LIMIT:
        params.vel = 0
        msg = array.array(MSG_ARRAY_TYPE, [0, com.MSG_STOP])
      else:
        max_vel = 127 if params._is_turbo else 64
        vel = min(max(int(v *max_vel), -127), 127)
        vel = vel if vel > 10 else 0
        params.vel = vel
        params.rev = xyL[1] > 0 and vel > 0

    if not msg and params.is_changed:
      dta = [
          0, com.MSG_MOVE,
          params.dir, params.vel, int(params.rev),
          params._lift_deg
        ]
      msg = array.array(MSG_ARRAY_TYPE, dta)

  return msg

# ---------------------------------------------------------------------
async def run():
  """ Run the loop
  """
  global isReady, Msg
  tLastResponse = time.monotonic()

  # Loop
  while Com.is_connected and isReady:
    try:
      # Check for pygame events
      for ev in pygame.event.get():
        if ((ev.type == pygame.QUIT) or
            (ev.type == pygame.JOYBUTTONDOWN and ev.button == joy.BTN_BACK_ID)
          ):
          # Exit programm
          isReady = False

      if isReady:
        # Check for input from joystick
        msg = getCmdMsgFromJoystickInput()
        if msg:
          Com.send(msg[1:])
          print("Sent    : " +Com.msgtoStr(msg))
          res = Com.receive()
          if res and len(res) >= 2:
            tLastResponse = time.monotonic()
            if res[1] == com.MSG_STA:
              # Ack/status message received, parse and print ...
              print("Received: " +Com.msgtoStr(res))

        # Check periodically, if server is connected
        if (time.monotonic() -tLastResponse) > CHECK_PING_TIME_S:
          print("Pinging server ...")
          Com.ping_server(f_wait_ms=wait_ms, tOut_s=20)
          exit_on_not_connected()
          tLastResponse = time.monotonic()

        # Keep events running
        Clock.tick(5)
        await asyncio.sleep(0.010)

    except KeyboardInterrupt:
      isReady = False

  print("User requested exit program.")

# ---------------------------------------------------------------------
if __name__ == '__main__':

  # Initialize variables
  isConnected = False
  isReady = False
  params = Params()
  print("Remote control for Hexabotling via BT (v" +__version__ +")")

  # Check for command line parameter(s)
  args = parseCmdLn()

  # Create messenger object
  print("Opening COM port ... ", end="")
  Com = com.Communicator(MessengerCOM(chan=args.port, type=MSG_ARRAY_TYPE))
  print("Pinging server ...")
  Com.ping_server(f_wait_ms=wait_ms, tOut_s=20)
  exit_on_not_connected()

  # Access joystick ...
  try:
    print("Checking for joystick ... ", end="")
    JS = joy.Joystick(0)
    Clock = pygame.time.Clock()
    _ = JS.BtnA.pressed
    print("Joystick found.")
    isReady = True
  except AttributeError:
    print("\rERROR: No joystick found")
    exit()

  # Run loop
  print("Ready.")
  try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
  except TimeoutError:
    print("ERROR: Connection lost")

  # Disconnect
  print("... done.")

# ---------------------------------------------------------------------
