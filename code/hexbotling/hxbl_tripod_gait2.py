# ----------------------------------------------------------------------------
# hxbl_tripod_gait2.py
#
# Tripod gait class (more phases)
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-08-19, v1.2 - More phases
# ----------------------------------------------------------------------------
import array
import time
import hxbl_config as cfg
import hxbl_global as glb
from hxbl_gait_base import GaitBase
from robotling_lib.motors.servo_manager import ServoManager as sma

# pylint: disable=bad-whitespace
__version__  = "0.1.2.0"
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class TripodGait(GaitBase):
  """Tripod gait class"""

  def __init__(self):
    # Initializing ...
    super().__init__()
    self._gaitType = "Tripod2"
    self._subtypes = [0,1]
    self.reset()
    glb.toLog("Gait set to `tripod2`")

  def reset(self):
    """ Resets current gait
    """
    super().reset()
    self._aCoxaSwing_deg = 23
    self._aCoxaCenter_deg = 0
    self._aLgLift_deg = 30
    self._aLgPreLift_deg = 30
    self._aLgDown_deg = 5
    self._nPhase = [4, 6][self._subtype]
    self._tPhase_ms = 1000
    self._aMaxCoxa_deg = 40
    self._phaseRatio = 0.30
    self._legSets = [
        bytearray([cfg.LEG_FL, cfg.LEG_CR, cfg.LEG_BL]),
        bytearray([cfg.LEG_FR, cfg.LEG_CL, cfg.LEG_BR])
      ]

  def _set_subtype(self, val):
    """ Set gait subtype
    """
    val = val if val in self._subtypes else 0
    if self._subtype != val:
      self._subtype = val
      self.reset()

  def get_next_servo_pos(self, stop=False, turn_dir=0, rev=False):
    """ Returns a tuple consisting of the duration of the move (in ms) and an
        array of angles for all servos for the current gait and phase).
        -1 <= `turn_dir` <= 1 gives the turn strength and direction.
        `rev` == True inverses the sequence.
        If `stop` is True, `turn_dir` is ignored.
    """
    def _set_leg(legs, a_cox, a_fem, d_coxL=1, d_coxR=1):
      for iL in legs:
        if iL % 2 == 0:
          # Even leg index -> left side leg
          pol = d_coxL
        else:
          # Odd leg index -> right side leg
          pol = d_coxR
        out[cfg.SRV_COX[iL]] = int(a_cox) *cfg.SRV_COX_DIR[iL] *pol
        out[cfg.SRV_FEM[iL]] = int(a_fem)

    # Get parameters and go to next phase
    seq = self._seq
    asw = self._aCoxaSwing_deg if seq == super().NORMAL else -self._aCoxaSwing_deg
    ac0 = self._aCoxaCenter_deg
    alf = self._aLgLift_deg
    apl = self._aLgPreLift_deg
    adn = self._aLgDown_deg
    rat = self._phaseRatio
    dtp = self._tPhase_ms
    trj = sma.TRJ_SINE
    lift_from_neutral = False
    dt_ms = dtp

    out = array.array("h", [0]*cfg.SRV_COUNT)

    if stop:
      # Stopped, move to neutral position
      _set_leg(self._legSets[0], ac0, adn)
      _set_leg(self._legSets[1], ac0, adn)
      self._isInSeq = False
      self._phase = 0

    else:
      if not self._isInSeq:
        # Not yet running, move to neutral position
        self._isInSeq = True
        lift_from_neutral = True

      # Move ...
      tlc = 1
      trc = 1
      if abs(turn_dir) > 0.001:
        tlc = -1 if turn_dir > 0 else 1
        trc = -1 if turn_dir < 0 else 1

      # Leg servo angles according to phase
      phs = self._phase
      if self._subtype == 0:
        # Move leg sets up/down at the same time (4 phases)
        #
        if phs == 0:   # Lift 1st set of legs and set down other set
          asw = 0 if lift_from_neutral else asw
          _set_leg(self._legSets[0],  asw, alf, tlc, trc)  # legs 0,3,4
          _set_leg(self._legSets[1], -asw, adn, tlc, trc)  # legs 1,2,5
          dt_ms *= rat if not rev else (1-rat)

        elif phs == 1: # Move lifted set legs
          _set_leg(self._legSets[0], -asw, alf, tlc, trc)
          _set_leg(self._legSets[1],  asw, adn, tlc, trc)
          dt_ms *= (1 -rat) if not rev else rat

        elif phs == 2: # Set down 1st set of legs and lift other set up
          _set_leg(self._legSets[0], -asw, adn, tlc, trc)
          _set_leg(self._legSets[1],  asw, alf, tlc, trc)
          dt_ms *= rat if not rev else (1-rat)

        elif phs == 3: # Move lifted set legs
          _set_leg(self._legSets[0],  asw, adn, tlc, trc)
          _set_leg(self._legSets[1], -asw, alf, tlc, trc)
          dt_ms *= (1 -rat) if not rev else rat

      elif self._subtype == 1:
        # Move leg sets seperately up and down (6 phases)
        #
        if phs == 0:   # Just lift 1st set of legs
          asw = 0 if lift_from_neutral else asw
          _set_leg(self._legSets[0],  asw, apl, tlc, trc)  # legs 0,3,4
          _set_leg(self._legSets[1], -asw, adn, tlc, trc)  # legs 1,2,5
          dt_ms *= rat if not rev else (1-rat)
          #trj = sma.TRJ_RAMP_UP

        elif phs == 1: # Move lifted set legs
          _set_leg(self._legSets[0], -asw, alf, tlc, trc)
          _set_leg(self._legSets[1],  asw, adn, tlc, trc)
          dt_ms *= (1 -rat) if not rev else rat

        elif phs == 2: # Set down 1st set of legs
          _set_leg(self._legSets[0], -asw, adn, tlc, trc)
          _set_leg(self._legSets[1],  asw, adn, tlc, trc)
          dt_ms *= rat if not rev else (1-rat)
          #trj = sma.TRJ_RAMP_DOWN

        elif phs == 3: # Now just lift 2nd set of legs
          _set_leg(self._legSets[0], -asw, adn, tlc, trc)
          _set_leg(self._legSets[1],  asw, apl, tlc, trc)
          dt_ms *= rat if not rev else (1-rat)
          #trj = sma.TRJ_RAMP_UP

        elif phs == 4: # Move lifted set legs
          _set_leg(self._legSets[0],  asw, adn, tlc, trc)
          _set_leg(self._legSets[1], -asw, alf, tlc, trc)
          dt_ms *= (1 -rat) if not rev else rat

        elif phs == 5: # Set down 1st set of legs
          _set_leg(self._legSets[0],  asw, adn, tlc, trc)
          _set_leg(self._legSets[1], -asw, adn, tlc, trc)
          dt_ms *= rat if not rev else (1-rat)
          #trj = sma.TRJ_RAMP_DOWN

      if not rev:
        self._phase = phs +1 if phs < self._nPhase-1 else 0
      else:
        self._phase = phs -1 if phs > 0 else self._nPhase-1

    # Return time to move and angle array
    return int(dt_ms), out, trj

# ----------------------------------------------------------------------------
