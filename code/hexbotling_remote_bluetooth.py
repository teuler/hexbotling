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
#
# ---------------------------------------------------------------------
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import asyncio
import array
import numpy as np
import pygame
import modules.joystick as joy
from argparse import ArgumentParser
from hexbotling.robotling_lib.misc.messenger import MessengerCOM
import hexbotling.hxbl_global as glb

# pylint: disable=bad-whitespace
__version__        = "0.2.0.0"
COM_PORT           = 7
MSG_ARRAY_TYPE     = "b"
JY_ZERO_LIMIT      = 0.1
# pylint: ensable=bad-whitespace

# ---------------------------------------------------------------------
def parseCmdLn():
  parser = ArgumentParser()
  parser.add_argument('-p', '--port', type=str, default=COM_PORT)
  return parser.parse_args()

# ---------------------------------------------------------------------
class Params(object):
  def __init__(self):
    self._dir = 0
    self._vel = 50
    self._rev = False
    self._is_changed = False
    self._is_turbo = False
    self._lift_deg = 25

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

  def __repr__(self):
    return f"dir={self.dir} vel={self.vel} rev={self.rev}"

# ---------------------------------------------------------------------
def getCmdFromJoystickInput():
  """ Generate a new command based on the joystick input, if any
  """
  # Initialize input parameters
  params_changed = False
  cmd = None

  # Button `A` prints help
  bA = JS.BtnA.pressed
  if bA is not None and bA:
    print("`A`                - Prints this help screenTurbo on/off")
    print("`B`                - Turbo on/off")
    print("`Y`                - Feet high/low")
    print("`X`                - Shutdown")
    print("`Back`             - Exit program")

  # Button `B` toggles "turbo"
  bB = JS.BtnB.pressed
  if bB is not None and bB:
    params._is_turbo = not params._is_turbo
    print("Turbo {0}".format("ON" if params._is_turbo else "OFF"))

  # Button `X` shuts robot down
  bX = JS.BtnX.pressed
  if bX is not None and bX:
    cmd = array.array(MSG_ARRAY_TYPE, [glb.CMD_POWER_DOWN])

  # Button `Y` toggles foot height
  bY = JS.BtnY.pressed
  if bY is not None and bY:
    params._lift_deg = 30 if params._lift_deg != 30 else 50
    print("Foot lift height is {0}°".format(params._lift_deg))

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
        cmd = array.array(MSG_ARRAY_TYPE, [glb.CMD_STOP])
      else:
        max_vel = 127 if params._is_turbo else 64
        vel = min(max(int(v *max_vel), -127), 127)
        vel = vel if vel > 10 else 0
        params.vel = vel
        params.rev = xyL[1] > 0 and vel > 0

    if not cmd and params.is_changed:
      dta = [
          glb.CMD_MOVE,
          params.dir, params.vel, int(params.rev),
          params._lift_deg
        ]
      cmd = array.array(MSG_ARRAY_TYPE, dta)

  return cmd

# ---------------------------------------------------------------------
async def run():
  """ Run the loop
  """
  global isReady, Msg

  # Loop
  while Msg.is_connected and isReady:
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
        cmd = getCmdFromJoystickInput()
        if cmd:
          Msg.write(cmd)
          res = Msg.read()
          if res:
            if res[1] == glb.CMD_STA:
              # Ack/status message received, parse and print ...
              print(glb.CMD_STRS[glb.CMD_STA].format(
                  res[2],    # last command idea
                  res[3]/10, # mean servo load in [A*10]
                  res[4]/10) # servo battery voltage in [V*10]
                )

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
  Msg = MessengerCOM(chan=args.port, type=MSG_ARRAY_TYPE)
  if not Msg.is_connected:
    print("\rERROR: Could get a serial connection")
    exit()

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
