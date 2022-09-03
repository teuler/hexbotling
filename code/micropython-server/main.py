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
import hxbl_comm as com
from hxbl_server import Server
from robotling_lib.misc.helpers import timed_function
from robotling_lib.misc.messenger import MessengerUART
import hxbl_server

# ----------------------------------------------------------------------------
#@timed_function
def handleCmd(msgData):
  """ Handles command in `msgData`, returns ERR_OK or error code
  """
  res = Comm.check(msgData)
  if res is not glb.ERR_OK:
    # Invalid message
    return res, com.MSG_NONE

  # Extract elements
  RSrv.set_msg_LED(True)
  errC = glb.ERR_OK
  msgID = msgData[1]
  params = msgData[2:]
  nParams = len(params)

  # Handle command ...
  if msgID == com.MSG_STOP:
    # Stop robot and wait until in neutral position
    RSrv.stop(wait_for_neutral=True)

  elif msgID == com.MSG_GAIT:
    # Change gait
    RSrv.stop(wait_for_neutral=True)
    RSrv.set_gait_parameters(type=params[0])

  elif msgID == com.MSG_MOVE:
    # Move robot depending on parameters ...
    dir = min(max(params[0], -100), 100) /100
    vel = min(max(params[1]*2, 1), 250) / 100
    rev = params[2] > 0
    lft = params[3]
    RSrv.set_gait_parameters(velocity=vel, lift_deg=lft)
    hxbl_server.g_we._tLastMsg = time.ticks_ms()
    if abs(dir) < 0.1:
      # ... forward
      RSrv.move_forward(reverse=rev)
    else:
      # ... turn
      RSrv.turn(dir)

  elif msgID == com.MSG_POWER_DOWN:
    # Power down
    pass

  elif msgID == com.MSG_PING:
    # Client sent a ping, respond ...
    Comm.send([com.MSG_PING])

  else:
    # Command not recognized
    errC = glb.ERR_UNKNOWN_MSG
    msgID = com.MSG_NONE

  if errC is glb.ERR_OK and msgID is not com.MSG_PING:
    sendStatus(msgID)
  RSrv.set_msg_LED(False)
  return errC, msgID

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#@timed_function
def sendStatus(msgID):
  """ Confirm receipt/execution of command. Includes:
      - message ID (`msgID`)
      - the servo load (in [A]*10)
      - the servo battery voltage (in [V]*10)
  """
  Comm.send(
      [com.MSG_STA, msgID,
      int(RSrv.servo_load_A *10), int(RSrv.servo_battery_V *10)]
    )

# ----------------------------------------------------------------------------
if __name__ == "__main__":

  # Create server instance
  RSrv = Server(core=cfg.HW_CORE, verbose=True)

  # Create a communicator instance and wait for connection to client
  Comm = com.Communicator(MessengerUART(
      chan=cfg.UART_CH, fToLog=glb.toLog,
      tx=cfg.UART_PIN_TX, rx=cfg.UART_PIN_RX, baud=cfg.UART_BAUD
    ))
  RSrv.set_pulse_LED_hue(cfg.HUE_WAITING)
  glb.toLog("Wait for ping from server ...")
  if not Comm.wait_for_client(f_wait_ms=RSrv.sleep_ms):
    glb.toLog("No client connection", errC=glb.ERR_CANNOT_CONNECT)
    RSrv.deinit()
    sys.exit()
  else:
    RSrv.set_pulse_LED_hue(cfg.HUE_NORMAL_BT)
  glb.toLog("Ready.", head=False)

  try:
    is_running = True
    n_rounds = 0
    msgID = com.MSG_NONE

    # Main loop
    glb.toLog("Entering loop ...", head=False)
    try:
      while not RSrv.state == glb.STA_OFF and is_running:
        # Get sensor input and/or commands from client
        # ...

        # Check if message is available
        if Comm.available > 0:
          data = Comm.receive()
          if data is not None and len(data) > 0:
            # If message data ok, handle the message ...
            errC, msgID = handleCmd(data)
            if errC is not glb.ERR_OK:
              glb.toLog("Command not handled", errC=errC)

        # Sleep for a while and, if running only on one core, make sure that
        # the server's hardware is updated
        RSrv.sleep_ms(25)

        # Check if user button is pressed; when debugging, exit also if a
        # maximum number of rounds have been done, as a precaution
        is_running = (
            not RSrv.exit_requested
            and not msgID == com.MSG_POWER_DOWN
          )
        if cfg.DEBUG:
          is_running = is_running and n_rounds < 25_000
        n_rounds += 1

    except KeyboardInterrupt:
      is_running = False
      pass

  finally:
    # Power down and clean up
    glb.toLog("Loop stopped.", head=False)
    RSrv.deinit()

# ----------------------------------------------------------------------------
