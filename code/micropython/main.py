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

# ----------------------------------------------------------------------------
if __name__ == "__main__":
  # Create server instance
  RSrv = Server(core=cfg.HW_CORE, verbose=True)
  RSrv.velocity = 1.2

  try:
    is_running = True
    n_rounds = 0

    # Main loop
    glb.toLog("Entering loop ...", head=False)
    try:
      while not RSrv.state == glb.STA_OFF and is_running:
        # Get sensor input and/or commands from client
        # ...

        # Act ...
        if True:
          if RSrv.state is not glb.STA_WALKING:
            # Start walking if not already doing that
            RSrv.move_forward()
        else:
          # Stop walking and wait until idle
          RSrv.stop()
          while RSrv.state is not glb.STA_IDLE:
            RSrv.sleep_ms(25)

        # Sleep for a while and, if running only on one core, make sure that
        # the server's hardware is updated
        RSrv.sleep_ms(25)

        # Check if user button is pressed; when debugging, exit also if a
        # maximum number of rounds have been done, as a precaution
        is_running = not RSrv.exit_requested
        if cfg.DEBUG:
          is_running = is_running and n_rounds < 2_000
        n_rounds += 1

    except KeyboardInterrupt:
      is_running = False
      pass

  finally:
    # Power down and clean up
    glb.toLog("Loop stopped.", head=False)
    RSrv.deinit()

# ----------------------------------------------------------------------------
