# ----------------------------------------------------------------------------
# hxbl_tripod_gait.py
#
# Tripod gait class
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-05-04, v1.0
# ----------------------------------------------------------------------------
import array
import time
import hxbl_config as cfg
import hxbl_global as glb
from hxbl_gait_base import GaitBase

# pylint: disable=bad-whitespace
__version__  = "0.1.0.0"
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class TripodGait(GaitBase):
  """Tripod gait class"""

  def __init__(self):
    # Initializing ...
    super().__init__()
    self._gaitType = "Tripod"
    self.reset()
    glb.toLog("Gait set to `tripod`")

  def reset(self):
    """ Resets current gait
    """
    super().reset()
    self._aCoxaSwing_deg = 35
    self._aCoxaCenter_deg = 0
    self._aLgLift_deg = 15
    self._aLgDown_deg = -15
    self._nPhase = 4
    self._tPhase_ms = 1000
    self._aMaxCoxa_deg = 40
    self._legSets = [
        bytearray([cfg.LEG_FL, cfg.LEG_CR, cfg.LEG_BL]),
        bytearray([cfg.LEG_FR, cfg.LEG_CL, cfg.LEG_BR])
      ]

  def get_next_servo_pos(self, stop=False):
    """ Returns a tuple consisting of the duration of the move (in ms) and an
        array of angles for all servos for the current gait and phase).
    """
    def _set_leg(_out, legs, a_cox, a_fem):
      for iL in legs:
        out[cfg.SRV_COX[iL]] = int(a_cox) *cfg.SRV_COX_DIR[iL]
        out[cfg.SRV_FEM[iL]] = int(a_fem)

    # Get parameters and go to next phase
    seq = self._seq
    asw = self._aCoxaSwing_deg if seq == super().NORMAL else -self._aCoxaSwing_deg
    ac0 = self._aCoxaCenter_deg
    alf = self._aLgLift_deg
    adn = self._aLgDown_deg
    dtp = self._tPhase_ms
    rat = 0.80
    out = array.array("h", [0]*cfg.SRV_COUNT)

    if stop or not self._isInSeq:
      # Stopped or not yet running, move to neutral position
      _set_leg(out, self._legSets[0], ac0, adn)
      _set_leg(out, self._legSets[1], ac0, adn)
      self._isInSeq = not stop

    else:
      # Leg servo angles according to phase
      phs = self._phase
      if phs == 0:
        _set_leg(out, self._legSets[0], -asw*rat, alf) # legs 0,3,4
        _set_leg(out, self._legSets[1],  asw*rat, adn) # legs 1,2,5
        dtp *= rat
      elif phs == 1:
        _set_leg(out, self._legSets[0], -asw, adn)
        _set_leg(out, self._legSets[1],  asw, alf)
        dtp *= (1 -rat)
      elif phs == 2:
        _set_leg(out, self._legSets[0],  asw*rat, adn)
        _set_leg(out, self._legSets[1], -asw*rat, alf)
        dtp *= rat
      elif phs == 3:
        _set_leg(out, self._legSets[0],  asw, alf)
        _set_leg(out, self._legSets[1], -asw, adn)
        dtp *= (1 -rat)
      self._phase = phs +1 if phs < self._nPhase-1 else 0

    # Return time to move and angle array
    return dtp, out

# ----------------------------------------------------------------------------
