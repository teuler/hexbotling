# ----------------------------------------------------------------------------
# messenger.py
#
# Simple hexlified messages via UART
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-07-10, v1.0
# 2022-08-19, v1.1 - `ping` method to check for connection added.
# 2022-08-19, v1.2 - removed `ping`; belongs to a higher level
#
# Tested with HC05 bluetooth module
# HC05     servo2040
# ----     ----
# VCC  ->  5V
# GND  ->  GND
# RDX  ->  SERVO13 (GP12, UART0 TX)
# TDX  ->  SERVO14 (GP13, UART0 RX)
#
# ----------------------------------------------------------------------------
import array
from binascii import hexlify, unhexlify
try:
  from micropython import const
  from machine import UART, Pin
  MICROPYTHON = True
except ModuleNotFoundError:
  import serial
  const = lambda x: x
  MICROPYTHON = False

# pylint: disable=bad-whitespace
__version__        = "0.1.2.0"

UART_CHAN          = const(0)
UART_PORT          = const(7)
UART_BAUD          = const(115_200)
UART_TIMEOUT_MS    = const(50)

MSG_START          = b">"
MSG_END            = b";"
MSG_LF             = b"\n"
MSG_ARR_TYPES      = {"b": 2, "h":4}
MSG_BASE_LEN       = const(5)
# pylint: endable=bad-whitespace

# ----------------------------------------------------------------------------
class Messenger(object):
  """Class to send/receive messages."""
  # pylint: disable=bad-whitespace
  ERR_OK           = const(0)
  ERR_INVALID_MSG  = const(-1)
  ERR_WRONG_TYPE   = const(-2)
  ERR_UART_ERROR   = const(-3)
  ERR_SERIAL_ERROR = const(-4)
  # pylint: enable=bad-whitespace

  def __init__(self, chan=UART_CHAN, baud=UART_BAUD, fToLog=None, type="b"):
    """ Initialize UART/serial connection on channel `chan` with baudrate
        `baud`, external log function `fToLog`) and the array data type `type`.
    """
    self._uart = None
    self._uart_chan = chan
    self._uart_baud = baud
    self._tout_ms = UART_TIMEOUT_MS
    self._toLog = fToLog
    self._arrItemLen = MSG_ARR_TYPES[type]
    self._minMsgLen = MSG_BASE_LEN +self._arrItemLen
    self._arrType = type
    self._isReady = False
    self._isConnected = False
    self._isVerbose = False

  def deinit(self):
    pass

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def timeout_ms(self):
    """ Get/set timeout """
    return self._tout_ms
  @timeout_ms.setter
  def timeout(self, t):
    self._tout_ms = max(t, 0)

  @property
  def verbose(self):
    """ Get/set verbose """
    return self._isVerbose
  @verbose.setter
  def verbose(self, val):
    self._isVerbose = val > 0

  @property
  def available(self):
    return self._available()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def write(self, data, only_log=False):
    """ Send a data array
    """
    if self._isReady:
      n = len(data)
      arr = array.array(self._arrType, [0] +list(data))
      arr[0] = self._minMsgLen +self._arrItemLen*(n)
      s = MSG_START +self._arrType.encode() +hexlify(arr) +MSG_END
      if not only_log:
        self._write(s +MSG_LF)
      if self._isVerbose:
        self._log(f"<- msg={s} ({list(data)})", head=False)

  def read(self):
    """ Read message and return data array or None, if an error occurred
    """
    if self._isReady and self._available() > 0:
      s = self._readline()
      if s is not None and len(s) >= self._minMsgLen:
        # Some message received
        n = len(s)
        if s[0] == ord(MSG_START) and s[n-2] == ord(MSG_END):
          # Correct start and end characters, extract data array
          try:
            dta = array.array(self._arrType, unhexlify(s[2:n-2]))
            if self._isVerbose:
              self._log(f"-> msg={s}", head=False)
            return dta
          except ValueError:
            self._log("Message parsing error", errC=self.ERR_INVALID_MSG)
        else:
          self._log("Message incomplete", errC=self.ERR_INVALID_MSG)
    return None

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _log(self, sMsg, sTopic="", errC=0, green=False, color=None, head=True):
    """ Call external log function, if defined, or just use print
    """
    if self._toLog:
      self._toLog(sMsg, sTopic, errC, green, color, head)
    else:
      print(sMsg)

# ----------------------------------------------------------------------------
# MicroPython version (UART)
# ----------------------------------------------------------------------------
class MessengerUART(Messenger):
  """Class to send/receive messages via UART."""
  # pylint: disable=bad-whitespace
  PIN_TX           = const(12)
  PIN_RX           = const(13)
  # pylint: enable=bad-whitespace

  def __init__(
      self, chan=UART_CHAN, baud=UART_BAUD, fToLog=None, type="b",
      tx=PIN_TX, rx=PIN_RX
    ):
    """ Initialize UART connection on channel `chan` and pins `tx`, `rx`
    """
    super().__init__(chan, baud, fToLog, type)

    # Open UART ...
    try:
      self._uart = UART(
          chan, baudrate=baud, tx=Pin(tx), rx=Pin(rx),
          timeout=self._tout_ms,
          )
      self._sPort = f"UART{chan}"
      self._isReady = self._uart is not None
    except ValueError:
      self._log(f"Invalid UART parameters.", errC=self.ERR_UART_ERROR)
      return
    self._log(f"{self._sPort} open w/ {baud} Bd.", green=True)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def deinit(self):
    if self._uart:
      self._uart.deinit()
      self._log(f"{self._sPort} closed.", green=True)

  def _write(self, bs):
    self._uart.write(bs)

  def _readline(self):
    return self._uart.readline()

  def _available(self):
    return self._uart.any() > 0 if self._uart else False

  @property
  def is_connected(self):
    return self._isConnected

# ----------------------------------------------------------------------------
# PC version (COM port)
# ----------------------------------------------------------------------------
class MessengerCOM(Messenger):
  """Class to send/receive messages via a COM port."""

  def __init__(self, chan=UART_PORT, baud=UART_BAUD, fToLog=None, type="b"):
    """ Initialize COM port `chan`
    """
    super().__init__(chan, baud, fToLog, type)

    # Open serial port ...
    self._sPort = f"COM{chan}"
    try:
      self._uart = serial.Serial(self._sPort, baud, timeout=self._tout_ms /1_000)
    except serial.serialutil.SerialException:
      self._log(f"Cannot open `{self._sPort}`.", errC=self.ERR_SERIAL_ERROR)
      return
    self._uart.flushInput()
    self._uart.flushOutput()
    self._isReady = self._uart.isOpen()
    self._log(f"{self._sPort} open w/ {baud} Bd.", green=True)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _write(self, bs):
    self._uart.write(bs)

  def _readline(self):
    return self._uart.readline()

  def _available(self):
    return self._uart.in_waiting > 0 if self._uart else False

  @property
  def is_connected(self):
    return self._isConnected

# ----------------------------------------------------------------------------
