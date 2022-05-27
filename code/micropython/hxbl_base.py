# ----------------------------------------------------------------------------
# hxbl_base.py
# Definition of a base class `HexbotlingBase`, currently contains some
# general memory- and reporting related functions
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-05-13, v1
# ----------------------------------------------------------------------------
import gc
import time
from micropython import const
from robotling_lib.misc.helpers import TimeTracker, timed_function
from robotling_lib.platform.platform import platform as pf
import robotling_lib.misc.ansi_color as ansi
import hxbl_global as glb

# pylint: disable=bad-whitespace
__version__     = "0.1.0.0"
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class HexbotlingBase(object):
  """Hexbotling base class."""
  def __init__(self):
    # Get the current time in seconds
    self._run_duration_s = 0
    self._start_s = time.time()

    # Initialize some variables
    self._ID = pf.GUID

    # Initialize spin function-related variables
    self._spin_period_ms = 0
    self._spin_t_last_ms = 0
    self._spin_callback = None
    self._spinTracker = TimeTracker()
    self._collect()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  def _collect(self):
    gc.collect()

  @property
  def memory(self):
    return (gc.mem_alloc(), gc.mem_free())

  @property
  def ID(self):
    return self._ID

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def uodatePowerDown(self):
    """ Record run time
    """
    self._run_duration_s = time.time() -self._start_s

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def updateStart(self):
    """ To be called at the beginning of the update function
    """
    self._spinTracker.reset()

  def updateEnd(self):
    """ To be called at the end of the update function
    """
    self._spinTracker.update()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def printReport(self):
    """ Prints a report on memory usage and performance
    """
    self.printMemory(report=True)
    avg_ms = self._spinTracker.meanDuration_ms
    dur_ms = self._spinTracker.period_ms
    glb.toLog(
        "Performance: spin: {0:6.3f}ms @ {1:.1f}Hz ~{2:.0f}%"
        .format(avg_ms, 1000/dur_ms, avg_ms /dur_ms *100),
        head=False
      )

  def printMemory(self, do_collect=False, report=False, as_str=False):
    """ Prints just the information about memory usage
    """
    used, free = self.memory
    total = free +used
    if do_collect:
      self._collect()
      used, free1 = self.memory
      freed = free1 -free
    usedp = used /total *100
    tot_kb = total /1024
    s1 = "Memory     : " if report else ""
    s2 = "" if not(do_collect) else " ({0} bytes freed)".format(freed)
    s3 = "{0}{1:.0f}% of {2:.0f}kB RAM used{3}.".format(s1, usedp, tot_kb, s2)
    if not(as_str):
      glb.toLog(s3, head=False)
    else:
      return s3

  def collectMemory(self):
    return self.printMemory(True, False, True)

# ----------------------------------------------------------------------------
