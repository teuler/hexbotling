# ----------------------------------------------------------------------------
# main.py
#
# Main program
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-03-21, v1.0
# ----------------------------------------------------------------------------
import sys
import time
import hxbl_global as glb
import hxbl_config as cfg
from hxbl_server import Server
from robotling_lib.misc.helpers import timed_function
from robotling_lib.misc.messenger import MessengerUART
import hxbl_server

# ----------------------------------------------------------------------------
#@timed_function
def handleCmd(msgData):
  """ Handles command in `msgData`, returns ERR_OK or error code
  """
  if len(msgData) < 2:
    # Data array too short
    return glb.ERR_INVALID_MSG, glb.CMD_NONE

  # Extract elements
  RSrv.set_msg_LED(True)
  errC = glb.ERR_OK
  cmdID = msgData[1]
  params = msgData[2:]
  nParams = len(params)

  # Check number of parameters
  if cmdID == glb.CMD_MOVE and nParams != glb.CMD_N_PARAMS[glb.CMD_MOVE]:
    return glb.ERR_TOO_FEW_PARAMS, glb.CMD_NONE

  # Handle command ...
  if cmdID == glb.CMD_STOP:
    print("Cmd STOP")
    RSrv.stop()
    while RSrv.state is not glb.STA_IDLE:
      RSrv.sleep_ms(25)

  elif cmdID == glb.CMD_MOVE:
    dir = min(max(params[0], -100), 100) /100
    vel = min(max(params[1]*2, 1), 250) / 100
    rev = params[2] > 0
    lft = params[3]
    RSrv.set_gait_parameters(velocity=vel, lift_deg=lft)

    hxbl_server.g_we._tLastCmd = time.ticks_ms()
    if abs(dir) < 0.1:
      print("Cmd `MOVE`", dir, vel, rev, lft)
      RSrv.move_forward(reverse=rev)
    else:
      print("Cmd `TURN`", dir, vel, rev, lft)
      RSrv.turn(dir)
    '''
  elif cmdID == glb.CMD_SIT_DOWN:
    pass
  elif cmdID == glb.CMD_STAND_UP:
    pass
    '''
  elif cmdID == glb.CMD_POWER_DOWN:
    pass

  else:
    # Command not recognized
    errC = glb.ERR_UNKNOWN_CMD
    cmdID = glb.CMD_NONE

  if errC is glb.ERR_OK:
    sendStatus(cmdID)
  RSrv.set_msg_LED(False)
  return errC, cmdID

#@timed_function
def sendStatus(cmdID):
  """ Confirm receipt/execution of command. Includes:
      - command ID (`cmID`)
      - the servo load (in [A]*10)
      - the servo battery voltage (in [V]*10)
  """
  Msgr.write(
      [glb.CMD_STA, cmdID,
      int(RSrv.servo_load_A *10), int(RSrv.servo_battery_V *10)]
    )

# ----------------------------------------------------------------------------
if __name__ == "__main__":

  # Create server instance
  RSrv = Server(core=cfg.HW_CORE, verbose=True)
  Msgr = MessengerUART(
      chan=cfg.UART_CH, type="b", fToLog=glb.toLog,
      tx=cfg.UART_PIN_TX, rx=cfg.UART_PIN_RX, baud=cfg.UART_BAUD
    )

  try:
    is_running = True
    n_rounds = 0
    cmdID = glb.CMD_NONE

    # Main loop
    glb.toLog("Entering loop ...", head=False)
    try:
      while not RSrv.state == glb.STA_OFF and is_running:
        # Get sensor input and/or commands from client
        # ...

        # Check if messge is available
        if Msgr.available > 0:
          data = Msgr.read()
          if data is not None and len(data) > 0:
            # If message data ok, handle the message ...
            errC, cmdID = handleCmd(data)
            if errC is not glb.ERR_OK:
              glb.toLog("Command not handled", errC=errC)

        # Sleep for a while and, if running only on one core, make sure that
        # the server's hardware is updated
        RSrv.sleep_ms(25)

        # Check if user button is pressed; when debugging, exit also if a
        # maximum number of rounds have been done, as a precaution
        is_running = (
            not RSrv.exit_requested
            and not cmdID == glb.CMD_POWER_DOWN
          )
        if cfg.DEBUG:
          is_running = is_running and n_rounds < 15_000
        n_rounds += 1

    except KeyboardInterrupt:
      is_running = False
      pass

  finally:
    # Power down and clean up
    glb.toLog("Loop stopped.", head=False)
    RSrv.deinit()

# ----------------------------------------------------------------------------
