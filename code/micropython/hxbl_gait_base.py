# ----------------------------------------------------------------------------
# hxbl_gait_base.py
#
# Gait base class
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-05-04, v1.0
# 2022-07-17, v1.1 - Take turn direction into account
# ----------------------------------------------------------------------------
from micropython import const

# pylint: disable=bad-whitespace
__version__  = "0.1.1.0"
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class GaitBase(object):
  """Gait base class"""
  # pylint: disable=bad-whitespace
  NORMAL        = const(1)
  REVERSE       = const(-1)
  # pylint: enable=bad-whitespace

  def __init__(self):
    # Initializing ...
    self._gaitType = "n/a"
    self.reset()

  def reset(self):
    """ Resets current gait
    """
    self._isInSeq = False
    self._phase = 0
    self._seq = NORMAL
    self._aCoxaSwing_deg = 0
    self._aLgLift_deg = 0

  def get_next_servo_pos(self, stop=False, turn_dir=0):
    """ Returns a tuple consisting of the duration of the move (in ms) and an
        array of angles for all servos for the current gait and phase).
    """
    return None

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  """ Leg swing angle (in degrees) """
  @property
  def leg_swing_angle(self):
    return self._aCoxaSwing_deg
  @leg_swing_angle.setter
  def swing_angle(self, val):
    amax = self._aMaxCoxa_deg
    self._aCoxaSwing_deg = min(max(val, -amax), amax)

  """ Leg lift angle (in degrees) """
  @property
  def leg_lift_angle(self):
    return self._aLgLift_deg
  @leg_lift_angle.setter
  def leg_lift_angle(self, val):
    self._aLgLift_deg = val

  """ Gait sequence, `NORMAL` or `REVERSE` """
  @property
  def sequence(self):
    return self._seq
  @sequence.setter
  def sequence(self, val):
    if val in [NORMAL, REVERSE]:
      self._seq = val

  @property
  def phase(self):
    """ Current gait phase index """
    return self._phase

  @property
  def can_stop(self):
    """ Returns `True` if gait can stop from this phase """
    return True


# ----------------------------------------------------------------------------
