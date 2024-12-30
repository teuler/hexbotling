' hexapod-server library v0.1.5
'
' Options:
'   OPTION WIFI "Elchland3", "xxx"
'   OPTION COLORCODE ON
'   OPTION DISPLAY 64,80

' For visual "simulation" on a PicoMiteVGA:
'   OPTION SYSTEM I2C GP14,GP15
'   OPTION KEYBOARD GR
'   OPTION PICO OFF
'   OPTION CPUSPEED 252000
'   OPTION SDCARD GP13,GP10,GP11,GP12
' Optional:
'   OPTION AUDIO GP22,GP22
'   OPTION MODBUFF 128
'
' Robot's coordinate system:
'  x-axis points left
'  y-axis points down
'  z-axis points backwards
'
' Hardware:
' - COM2 (tx=GP4, rx=GP5) as device #5 -> Meastro18 servo controller
' - Buzzer @ GP3
' - Yellow onboard LED @ GP2
' ---------------------------------------------------------------------------
Option Base 0
Option Explicit
Option Escape
Option Default Float
Const  RUN_TESTS = 1

GoTo Start
' ---------------------------------------------------------------------------
TestCode:
  ' Start of minimal test code for library
  ' (Only executed if `RUN_TESTS = 1`)
  DEBUG = 0 'DEB_INP Or DEB_SIM Or DEB_IK

  Dim integer i, j, t, ch, running = 1
  Dim string key$
  Dim bo_y = 15, lh = 30
  Dim tl_x = 0, tl_z = -30, tr_y = 0, ds = 50

  R.Init
  Sim.Init
  R.LED 1
  R.Buzz 440, 100

  R.resetGait
  R.resetInput
  R.resetGaitGen
  Sim.Update
  Pause 1000

  g.isInMot = 1 ' why not automatically?

  R.switchGaitGen 1
  R.inputBody bo_y,lh
  R.inputWalk tl_x, tl_z, tr_y, ds

  Do While running
    t = Timer
    R.spinGaitGen
    Print "dt="+Str$(Timer -t,2,1)+" ms"
    Sim.Update
    key = Inkey$
    If Len(key$) > 0 Then
      ch = Asc(LCase$(key$))
      Select Case ch
        Case 27 : running = 0 : Exit
        Case 49,50   ' 1,2 - body offset
          Inc bo_y, Choice(ch = 49, -5, 5)
          R.inputBody bo_y, lh
          bo_y = in.bodyYOffs_v
        Case 51,52   ' 3,4 - leg lift height
          Inc lh, Choice(ch = 51, -5, 5)
          R.inputBody bo_y, lh
          lh = in.legLiftH_v
        Case 128,129 ' up,down - z travel length
          Inc tl_z, Choice(ch = 128, -10, 10)
          R.inputWalk tl_x, tl_z, tr_y, ds
          tl_z = in.x_zTravL_v(2)
        Case 130,131 ' left,right - x travel length
          Inc tl_x, Choice(ch = 130, -5, 5)
          R.inputWalk tl_x, tl_z, tr_y, ds
          tl_x = in.x_zTravL_v(0)
        Case 127,137 ' del,pg-down - y travel rotation
          Inc tr_y, Choice(ch = 127, -5, 5)
          R.inputWalk tl_x, tl_z, tr_y, ds
          tr_y = in.travRotY_v
        Case 135     ' end - stop all motion
          tl_x = 0 : tl_z = 0 : tr_y = 0
          R.inputWalk tl_x, tl_z, tr_y, ds
        Case Else
          Print "ch=";ch
      End Select
    EndIf
    Pause 100
  Loop

  R.LED 0
  Sim.Exit
  R.Shutdown
  End

' ---------------------------------------------------------------------------
Sub Sim.Init
  ' Initialize graphical simulation
  ' (only with VGA firmware)
  Option LCDPanel NoConsole
  MODE 2
  FRAMEBUFFER Create
  Dim integer s.cx1=MM.HRes/4, s.cy1=MM.VRes/2, s.dx1=MM.HRes/2, s.dy1=s.dx1
  Dim integer s.cx2=MM.HRes*3/4, s.cy2=MM.VRes/4, s.dx2=s.dx1, s.dy2=MM.VRes/2
  Dim integer s.cx3=s.cx2, s.cy3=s.cy2+s.dy2, s.cyo = -20
  Dim s.sc1=0.45, s.sc2=0.3
End Sub

Sub Sim.Exit
  FRAMEBUFFER Close
End Sub

Sub Sim.Update
  ' Update graphical simulation
  ' (only with VGA firmware)
  Local integer iL
  Local x, y, bh = 50*s.sc2, coa
  Local rot(2), r1(2), nxyz(LEG_N-1,2), v1(2)
  Local string s$
  FRAMEBUFFER Write F
  CLS RGB(black)

  ' Draw subwindow frames
  x = s.cx1-s.dx1/2
  y = s.cy1-s.dy1/2
  Box x,y, s.dx1,s.dy1, 1, RGB(white)
  Text x+2,y+2, "x/-z"
  x = s.cx2-s.dx2/2
  y = s.cy2-s.dy2/2
  Box x,y,s.dx2,s.dy2, 1, RGB(red)
  Text x+2,y+2, "-z/y (side)"
  x = s.cx3-s.dx2/2
  y = s.cy3-s.dy2/2
  Box x,y,s.dx2,s.dy2, 1, RGB(green)
  Text x+2,y+2, "x/y (front)"

  ' Some text
  x = 1
  y = s.cy1-s.dy1/2 +s.dy1 +1
  s$ = "body>Off="+Str$(in.bodyYOffs_v,2,0)
  s$ = s$ +" legLiftH="+Str$(in.legLiftH_v,2,0)
  Text x,y, s$
  Inc y, 8
  s$ = "trav xl="+Str$(in.x_zTravL_v(0),2,0)
  s$ = s$ +" zl="+Str$(in.x_zTravL_v(2),2,0)
  s$ = s$ +" yr="+Str$(in.travRotY_v,2,0)
  Text x,y, s$

  ' Body
  Circle s.cx1,s.cy1, BODY_R*s.sc1, 1,,,RGB(blue)
  x = s.cx2-BODY_R*s.sc2
  y = s.cy2+s.cyo -bh*3/4
  Box x,y, BODY_R*2*s.sc2, bh, 1,,RGB(blue)
  x = s.cx3-BODY_R*s.sc2
  y = s.cy3+s.cyo -bh*3/4
  Box x,y, BODY_R*2*s.sc2, bh, 1,,RGB(blue)

  ' `nxyz()` will be updated to contain the current joint position
  Math Scale COX_OFF_XYZ(), 1, nxyz()

  ' Legs
  For iL=2 To 4 'LEG_N-1
    ' Get angles for this leg (`rot()`)
    Math Set 0, rot()
    Math Slice ggn.legAng(), iL,, rot()
    If DEBUG And DEB_SIM Then
      Print iL;" cx=";Str$(rot(0),3,0);" fm=";Str$(rot(1),3,0);
      Print " tb=";Str$(rot(2),3,0)
    EndIf

    ' Coxa
    Math Set 0, r1()
    Sim.drawNode iL, nxyz(), RGB(cyan)
    coa = -BODY_COX_ANG*iL +270
    r1(0) = coa ' coxa offset angle; rotation around y (yaw)
   'Sim.drawVect iL, nxyz(), COX_LEN, r1(), v1(), RGB(gray)
    Inc r1(0), rot(0)
    Sim.drawVect iL, nxyz(), COX_LEN, r1(), v1(), RGB(cerulean)

    ' Femur
    ' (add to `nxyz()` the last drawn vector's end point)
    Inc nxyz(iL,0), v1(0)
    Inc nxyz(iL,1), v1(1)
    Inc nxyz(iL,2), v1(2)
    Sim.drawNode iL, nxyz(), RGB(rust)
    Math Set 0, r1()
    r1(0) = coa +rot(0)
    r1(1) = -rot(1) +120
    Sim.drawVect iL, nxyz(), FEM_LEN, r1(), v1(), RGB(brown)

    ' Tibia
    Inc nxyz(iL,0), v1(0)
    Inc nxyz(iL,1), v1(1)
    Inc nxyz(iL,2), v1(2)
    Sim.drawNode iL, nxyz(), RGB(lilac)
    Math Set 0, r1()
    r1(0) = coa +rot(0)
    r1(1) = -60 -rot(2)
    Sim.drawVect iL, nxyz(), TIB_LEN, r1(), v1(), RGB(fuchsia)

    ' Foot
    Inc nxyz(iL,0), v1(0)
    Inc nxyz(iL,1), v1(1)
    Inc nxyz(iL,2), v1(2)
    Sim.drawNode iL, nxyz(), RGB(red)

    ' Starting positions of feet
    Sim.drawNode iL, FEET_INIT_XYZ(), RGB(yellow)

    ' Target positions of feet
   'Sim.drawNode iL, g.xyz(), RGB(red)         ' from gait only
   'Sim.drawNode iL, ggn.xyzLeg(), RGB(cyan)   ' = start positions
    Sim.drawNode iL, ggn.xyzFoot(), RGB(green) ' after bodyIK
  Next iL
  FRAMEBUFFER Copy F,N
End Sub

Sub Sim.drawVect iL, xyz(), l, a(), xyzOut(), c
  ' Draw line of length `l` from coordinate `xyz(iL,2)` with angle `ang(2)`
  ' in color `c`. Returns the coordinates of the vector target (`xyzOut()`)
  Local integer _c = Choice(c = 0, RGB(white), c)
  Local  x1, y1, x2, y2
  Local v(4), r(4), w(4)
  ' Create vector to coordinate, rotation quaternion, and rotate vector
  Math Q_Vector 0,0,l, v()
  Math Q_Euler Rad(a(0)),Rad(a(1)),Rad(a(2)), r()
  Math Q_Rotate r(), v(), w()
  ' Draw lines in each subwindow
  x1 = s.cx1 +xyz(iL,0)*s.sc1 ' -z/x
  y1 = s.cy1 +xyz(iL,2)*s.sc1
  x2 = x1 +w(1)*w(4)*s.sc1
  y2 = y1 +w(3)*w(4)*s.sc1
  Line x1, y1, x2, y2, 1,_c
  x1 = s.cx2 +xyz(iL,2)*s.sc2 '-z/y
  y1 = s.cy2+s.cyo +xyz(iL,1)*s.sc2
  x2 = x1 +w(3)*w(4)*s.sc2
  y2 = y1 +w(2)*w(4)*s.sc2
  Line x1, y1, x2, y2, 1,_c
  x1 = s.cx3 -xyz(iL,0)*s.sc2 ' x/y
  y1 = s.cy3+s.cyo +xyz(iL,1)*s.sc2
  x2 = x1 -w(1)*w(4)*s.sc2
  y2 = y1 +w(2)*w(4)*s.sc2
  Line x1, y1, x2, y2, 1,_c
  xyzOut(0) = w(1)*w(4)
  xyzOut(1) = w(2)*w(4)
  xyzOut(2) = w(3)*w(4)
End Sub

Sub Sim.drawNode iL, xyz(), c
  ' Draw dot at coordinate `xyz(iL,2)` in color `c`
  Local integer _c = Choice(c = 0, RGB(white), c)
  Local integer x, y
  ' Draw spots in all subwindows
  x = s.cx1 +xyz(iL,0) *s.sc1 ' -z/x
  y = s.cy1 +xyz(iL,2) *s.sc1
  Circle x,y, 2,1,1, _c
  x = s.cx2 +xyz(iL,2) *s.sc2 ' -z/y
  y = s.cy2+s.cyo +xyz(iL,1) *s.sc2
  Circle x,y, 2,1,1, _c
  x = s.cx3 -xyz(iL,0) *s.sc2 ' x/y
  y = s.cy3+s.cyo +xyz(iL,1) *s.sc2
  Circle x,y, 2,1,1, _c
End Sub

' ---------------------------------------------------------------------------
' Start of definitions
'
Start:
  ' Set data read pointer here
10 Restore 10

  Const R.VERSION$       = "0.1.5"
  Const R.NAME$          = "hexapod|server"

  Const DEB_SRV          = &H01
  Const DEB_VERB         = &H02
  Const DEB_GAIT         = &H04
  Const DEB_INP          = &H08
  Const DEB_IK           = &H10
  Const DEB_SIM          = &H20
  Dim integer DEBUG      = 0
  Const CHK_SRV_PARAMS   = 0
  Const NOT_AN_ANGLE     = -1

  ' Pico pins
  Const PIN_LED          = 4       ' GP2
  Const PIN_BUZZER       = 5       ' GP3
  Const PIN_SRV_TX       = 6       ' GP4
  Const PIN_SRV_RX       = 7       ' GP5

  ' Servo controller-related definitions
  Const SRV_PORT$        = "COM2:57600"
  Const SRV_MIN_US       = 600
  Const SRV_MAX_US       = 2400
  Const SRV_N            = 18
  Const SRV_RES          = 4       ' 0.25 us resolution
  Const SRV_SPEED        = 40
  Const SRV_ACCEL        = 3

  ' Gait generator (GGN) states
  Const GGN_IDLE         = 0
  Const GGN_COMPUTE      = 1
  Const GGN_STAND_BY     = 2
  Const GGN_MOVING       = 3
  Const GGN_DO_SERVOS    = 4
  ' ...
  Const GGN_STATE$       = "Idle,Compute,Standby,Moving,DoServos"

  ' Error codes
  Const ERR_OK           = 0
  Const ERR_MOVE_OVERDUE = -1
  ' ...

  ' Leg-related definitions
  Const LEG_N            = 6

  Const LEG_RM           = 0       ' Right middle
  Const LEG_RF           = 1       ' Right front
  Const LEG_LF           = 2       ' Left front
  Const LEG_LM           = 3       ' Left middle
  Const LEG_LR           = 4       ' Left rear
  Const LEG_RR           = 5       ' Right rear

 'Dim integer R_LEGS(2)  = (LEG_RM, LEG_RF, LEG_RR)
 'Dim integer L_LEGS(2)  = (LEG_LF, LEG_LM, LEG_LR)

  Const COX              = 0
  Const FEM              = 1
  Const TIB              = 2

  Const COX_LEN          = 48
  Const FEM_LEN          = 47
  Const TIB_LEN          = 84

  Const FEM2TIB2_DIF     = FEM_LEN^2 -TIB_LEN^2
  Const FEM_2LEN         = FEM_LEN *2
  Const FEMTIB_2LEN      = FEM_LEN *TIB_LEN *2

  ' Body-related definitions
  Const TIB_CORR_ANG     = 50
  Const BODY_R           = 60      ' Body radius [mm]
  Const BODY_COX_ANG     = 60      ' Fixed leg offset angle around body

  Dim integer COX_OFF_ANG(LEG_N-1) ' Leg angles (in degree)
 'Data  0, 60, 60,  0,-60,-60 'original
  Data  0, 60,120,180,240,300 'new?
  Read COX_OFF_ANG()

  Dim COX_OFF_XYZ(LEG_N-1, 2)      ' Leg positions relative to body
  R._calcLegPos BODY_COX_ANG, BODY_R, COX_OFF_XYZ()

  ' Movement-related definitions
  ' ----------------------------
  ' Limits within movements are considered finished
  Const TRAVEL_DEAD_Z    = 2
  Const TURN_DEAD_Z      = 5
  Const LEGS_DOWN_DEAD_Z = 10      ' TODO

  ' Limits of movement control parameters
  ' (Rotations are in [degree], travel in [mm],
  '  and  delays in [ms])
  Const BODY_Y_OFFS_MAX  = 70
  Const BODY_Y_SHFT_LIM  = 64

  Dim integer BODY_X_Z_POS_LIM(2)
  Data 15, BODY_Y_OFFS_MAX +BODY_Y_SHFT_LIM, 15
  Read BODY_X_Z_POS_LIM()

  Dim integer BODY_XYZ_ROT_LIM(2) = (5, 20, 5)
  Dim integer TRAVEL_X_Z_LIM(2) = (40, 0, 40)

  Const TRAV_ROT_Y_LIM   = 25
  Const LEG_LIFT_MIN     = 20 ' 40
  Const LEG_LIFT_MAX     = 60 ' 80
  Const DELAY_INPUT_MIN  = 0
  Const DELAY_INPUT_MAX  = 255
  Const DELAY_SPEED_MAX  = 2000

  ' Start position of feet
  ' (Measured from beginning of coxa; leg coordinate system (?))
  Const FEM_STRT_ANG     = -20
  Const TIB_STRT_ANG     = 10
  Const COX_OFFS_FACT    = 1.0 '1.5
  Dim FEET_INIT_XYZ(LEG_N-1, 2)
  R._calcFootPos FEM_STRT_ANG, TIB_STRT_ANG, BODY_COX_ANG, FEET_INIT_XYZ()

  ' Jump to library test code, if any
  If RUN_TESTS Then GoTo TestCode

' ===========================================================================
' Initialization and shutdown
' ---------------------------------------------------------------------------
Sub R.Init
  ' Prepare handware
  Local integer j
  Local float af, at, ac
  InitR: Restore InitR
  Print "\r\n"+R.NAME$+" v"+R.VERSION$
  Print "Initializing onboard hardware ..."

  ' LED
  SetPin PIN_LED, DOUT
  Pin(PIN_LED) = 0

  ' Buzzer
  SetPin PIN_BUZZER, PWM1B

  ' Open COM port to MiniMaestro 18 servo board
  Print "Connecting to Meastro servo controller ..."
  Print "-> RX="+Str$(PIN_SRV_RX)+" TX="+Str$(PIN_SRV_TX);
  Print " options=`";SRV_PORT;"`"
  SetPin PIN_SRV_RX, PIN_SRV_TX, COM2
  Open SRV_PORT$ As #5
  Pause 200

  ' Leg servos
  ' ----------
  ' e.g., leg.srv(COX,LEG_RM) -> servo #4
  Dim integer leg.srv(2, LEG_N-1)
  Data  4,10,16  ' Leg 0 (RM) right-middle
  Data  5,11,17  ' Leg 1 (RF) right-front
  Data  0, 6,12  ' Leg 2 (LF) left-front
  Data  1, 7,13  ' Leg 3 (LM) left-middle
  Data  2, 8,14  ' Leg 4 (LR) left-rear
  Data  3, 9,15  ' Leg 5 (RR) right-rear
  Read leg.srv()

  Dim integer srv.dir(SRV_N-1)
  Data -1,-1,-1,  1, 1, 1
  Data  1, 1, 1,  1, 1, 1
  Data  1, 1, 1,  1, 1, 1
  Read srv.dir()

  ' Servo angle factor (by leg and limb)
  Dim srv.ang_f(LEG_N-1, 2)
  Data  1, 1, 1, 1, 1, 1
  Data  1, 1, 1, 1, 1, 1
  Data -1,-1,-1,-1,-1,-1
  Read srv.ang_f()

  ' Servo ranges (by servo ID, 0..17, as angle [deg])
  Dim integer srv.r_deg(1, SRV_N-1)
  Dim integer srv.da_deg(SRV_N-1)
  Data -45, +45,  -45, +45,  -45, +45
  Data -45, +45,  -45, +45,  -45, +45
  Data -55, +55,  -55, +55,  -55, +55
  Data -55, +55,  -55, +55,  -55, +55
  Data -90, +35,  -90, +35,  -90, +35
  Data -90, +35,  -90, +35,  -90, +35
  Read srv.r_deg()
  For j=0 To SRV_N-1
    srv.da_deg(j) = srv.r_deg(1,j) -srv.r_deg(0,j)
  Next j

  ' Servo ranges (by servo ID, 0..17, as timing in us)
  ' e.g., srv.ranges(0,5) -> minimum for servo #5
  Print "Reading servo calibration data ..."
  Dim float srv.r_us(1, SRV_N-1)
  Dim integer srv.dt_us(SRV_N-1)
  ' Coxa (-45, +45)
  Data  965, 1812,  1001, 1857
  Data  900, 1803,  1167, 2000
  Data 1030, 1970,  1074, 1931
  ' Femur (-55, +55)
  Data 1640-500, 1640+500,  1600-500, 1600+500
  Data 1570-500, 1570+500,  1360-500, 1360+500
  Data 1460-500, 1460+500,  1493-500, 1493+500
  ' Tibia (-90, +35)
  Data  782, (1847  -782) /90 *(35 -2) +1847
  Data  634, (1764  -634) /90 *(35 -7) +1764
  Data  846, (1850  -846) /90 *(35 +3) +1850
  Data  943, (2020  -943) /90 *(35   ) +2020
  Data 1027, (1995 -1027) /90 *(35 +4) +1995
  Data  840, (1900  -840) /90 *(35 -2) +1900
  Read srv.r_us()
  For j=0 To SRV_N-1
    srv.dt_us(j) = srv.r_us(1,j) -srv.r_us(0,j)
  Next

  ' Set servo speed and acceleration at the Maestro level
  Print "-> Setting servo speed to "+Str$(SRV_SPEED)+" and ";
  Print "acceleration limit to "+Str$(SRV_ACCEL)
  For j=0 To SRV_N-1
    R.setServoSpeed j, SRV_SPEED
    R.setServoAccel j, SRV_ACCEL
  Next j

  If DEBUG And DEB_VERB Then
    ' List calibration values
    Print "Calibrated servo positions and ranges ..."
    Print "Servo min           max        dt[us] ds["+Chr$(186)+"]"
    Print "----- ----------    ---------- ------ -----"
    For j=0 To SRV_N-1
      Print " #"+Str$(j,2)+"  ";
      Print Str$(srv.r_us(0,j),4,0) +" ("+Str$(srv.r_deg(0,j),3,0)+")";
      Print " .. ";
      Print Str$(srv.r_us(1,j),4,0) +" ("+Str$(srv.r_deg(1,j),3,0)+")  ";
      Print Str$(srv.dt_us(j),4,0)+"  "+Str$(srv.da_deg(j),3,0)
    Next j
  EndIf
  Print "Ready."
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.Shutdown
  ' Shutdown hardware
  Print "Shutting down ..."
  Pin(PIN_LED) = 0
  SetPin PIN_LED, Off
  PWM 1, Off
  Close #5
  Print "Done."
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R._calcLegPos ac, br, xyz()
  ' Calculate leg positions relative to body
  Local integer i
  Math Set 0, xyz()
  For i=0 To LEG_N-1
   'xyz(i,0) = -Cos(i*Rad(ac)) *br
    xyz(i,0) = +Cos(i*Rad(ac)) *br ' new
    xyz(i,2) = -Sin(i*Rad(ac)) *br
   'Print i,xyz(i,0),xyz(i,1),xyz(i,2)
  Next
End Sub

Sub R._calcFootPos af, at, ac, xyz()
  ' Calculate starting positions for feet (from angles)
  Local float rf = Rad(af), rt = Rad(at), rc = Rad(ac), rx
  Local integer i
  Math Set 0, xyz()
  For i=0 To LEG_N-1
    rx = FEM_LEN *Cos(rf) -TIB_LEN *Sin(rt +rf) +COX_LEN*COX_OFFS_FACT
    xyz(i,0) = rx *Cos(rc *i)
    xyz(i,1) = FEM_LEN *Sin(rf) +TIB_LEN *Cos(rt -rf)
    xyz(i,2) = -rx *Sin(rc *i)
   'Print i,xyz(i,0),xyz(i,1),xyz(i,2)
  Next
End Sub

' ===========================================================================
' Walk engine
' ---------------------------------------------------------------------------
Sub R.resetGaitGen
  ' Reset gait generator (ggn)
  Static integer first = 1
  If first Then
    ' Allocate variables
    first = 0
    Dim integer ggn.isOnPrev, ggn.state, ggn.nextState, ggn.legsDown
    Dim integer ggn.lastErr, ggn.IKErr
    Dim integer ggn.dtMov, ggn.dtPrevMov, ggn.dtNextMov, ggn.dtLastCalc
    Dim integer ggn.tWaitUntil, ggn.dtLastSpin, ggn.dtMoveLate
    Dim integer ggn.tMoveStart
    Dim ggn.xyzLeg(LEG_N-1, 2), ggn.xyzFoot(LEG_N-1, 2)
    Dim ggn.legAng(LEG_N-1, 2), ggn.srvAng(LEG_N-1, 2)
    Dim ggn.srvPos(SRV_N-1)

    ' TEMPORARY, TO BE ACCESSIBLE BY SIM
    Dim tmp1xyz(LEG_N-1,2), tmp2xyz(LEG_N-1,2)
  EndIf
  ' Reset GGN control parameters
  ' (all times are in [ms])
  ggn.isOnPrev   = 0         ' Previous state of GGN on/off switch
  ggn.state      = GGN_IDLE  ' Current and next state of GGN
  ggn.nextState  = ggn.state
  ggn.dtMov      = 0         ' Durations [ms] ...
  ggn.dtPrevMov  = 0
  ggn.dtNextMov  = 0
  ggn.dtLastCalc = 0
  ggn.dtLastSpin = 0
  ggn.dtMoveLate = 0
  ggn.tWaitUntil = 0         ' Wait until this time
  ggn.tMoveStart = 0         ' Time when move last was started
  ggn.legsDown   = 1
  ggn.lastErr    = ERR_OK
  ggn.IKErr      = 0

  ' Reset input parameters
  R.resetInput

  ' Current leg (`ggn.xyzLeg`) and foot (`ggn.xyzFoot`) positions
  Math Scale FEET_INIT_XYZ(), 1, ggn.xyzLeg()
  Math Set 0, ggn.xyzFoot()

  ' Current leg angles (`ggn.legAng`, from IK), converted into servo
  ' angles (`ggn.srvAng`) and timing (`ggn.srvPos`)
  Math Set 0, ggn.legAng()
  Math Set 0, ggn.srvAng()
  Math Set 0, ggn.srvPos()
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.switchGaitGen state%
  ' Start (`state% = 1`) or stop gait generator
  in.doEmergStop = 0
  in.isOn = state% <> 0
  ggn.state = Choice(in.isOn, GGN_COMPUTE, GGN_STAND_BY)
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.spinGaitGen
  ' Keeps everything running; needs to be called frequencly
 'Print "R.spinGaitGen\r\n  ggn.state=";Field$(GGN_STATE$, ggn.state, ",")
  If ggn.state = GGN_MOVING Then
    ' Still executing move
    If ggn.tWaitUntil > 0 And Timer >= ggn.tWaitUntil Then
      ' Trigger execution of next move
      ggn.state = GGN_DO_SERVOS
      ggn.tWaitUntil = 0
    EndIf
  EndIf
  If ggn.state = GGN_DO_SERVOS Then
    ' Previous move is finished, now commit next move
    R._executeMove
  ElseIf ggn.state = GGN_COMPUTE Then
    ' Calculate next move and set timer for move execution
    R._computeMove
  EndIf
 'Print "->ggn.state=";Field$(GGN_STATE$, ggn.state, ",")
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R._computeMove
  ' Execute move ...
  Static xyz1(2), xyz2(2), xyz3(2)
  Static integer RL_LEG(LEG_N-1) = (-1,-1, 1, 1, 1,-1)
  Local integer legsDown, gaitInMotion, iL, s
  Local t1, t2, dt

  ' Initialize
 'Print "R._computeMove"
  t1 = Timer
  ggn.lastErr = ERR_OK
  ggn.IKErr = 0

  ' Update input parameters (e.g., blending)
  R.inputUpdate

  ' Check if all legs are down and if not so, set them to their initial
  ' positions
  legsDown = R._arelegsDown()
  If Not(legsDown) Then
    Math Scale FEET_INIT_XYZ(), 1, ggn.xyzLeg()
  EndIf

  ' Calculate update of gate sequence
  g.isInMot = R._isGaitInMotion(1)
  R.generateGaitSeq

  ' Do IK for all legs
  '  ggn.xyzLeg(LEG_N-1,2)  (lgxyz)
  '  in.xyzBody_v(2)        (boxyz)
  '  in.xyzBodyRot_v(2)     (brxyz)
  '  g.xyz(LEG_N-1,2)       (gaxyz)
  '  COX_OFF_XYZ(LEG_N-1,2) (coxyz)
  For iL=0 To LEG_N-1
    ' xyz1() - target foot positions
    ' xyz2() - rotation matrix (body)
    ' xyz3() -
    s = RL_LEG(iL) ' -1=for right, +1=for left leg
    xyz1(0) = s*ggn.xyzLeg(iL,0) -s*in.xyzBody_v(0) +g.xyz(iL,0)
    xyz1(1) =   ggn.xyzLeg(iL,1) +  in.xyzBody_v(1) +g.xyz(iL,1)
    xyz1(2) =   ggn.xyzLeg(iL,2) +  in.xyzBody_v(2) +g.xyz(iL,2)
    R._bodyIK iL, xyz1(), xyz2()
    xyz3(0) =   ggn.xyzLeg(iL,0) +s*in.xyzBody_v(0) -s*xyz2(0) +s*g.xyz(iL,0)
    xyz3(1) =   ggn.xyzLeg(iL,1) +  in.xyzBody_v(1) -  xyz2(1) +  g.xyz(iL,1)
    xyz3(2) =   ggn.xyzLeg(iL,2) +  in.xyzBody_v(2) -  xyz2(2) +  g.xyz(iL,2)
    Math Insert ggn.xyzFoot(), iL,, xyz3()
    R._legIK iL, xyz3()
  Next
  ' ###
 'Print "--tmp2xyz()"
 'Math M_print tmp2xyz()
 'Print "--ggn.legAng()"
 'Math M_print ggn.legAng()
  ' ###

  ' Check and report IK errors
  If ggn.IKErr > 0 Then
    If DEBUG And DEB_IK Then Print "ggn.IKErr=";ggn.IKErr
  EndIf

  ' Drive servos, if GGN is on
  If in.isOn Then
    ' Calculate time the next move will take
    If R._isGaitInMotion(2) Then
      ggn.dtNextMov = g.nomSpeed
      Inc ggn.dtNextMov, in.delayInput_v*2 +in.delaySpeed_v
    Else
      ' Movement speed if not walking
      ggn.dtNextMov = 200 +in.delaySpeed_v
    EndIf
    t2 = Timer
    ggn.dtLastCalc = t2 -t1

    ' Send new leg positions to the servo manager
    If (ggn.tMoveStart = 0) Or ((ggn.tMoveStart +ggn.dtMov) < t2) Then
      ' Is first move or next servo update is overdue, in any case execute
      ' the move immediately
      R._executeMove
      ggn.lastErr = ERR_MOVE_OVERDUE
    Else
      ' The last move is not yet finished, we need to wait ...
      ' (for this the timer is used, so that other sections of the main
      '  loop get processing time)
      ggn.state = GGN_MOVING
      ggn.nextState = GGN_DO_SERVOS
      ggn.tWaitUntil = Timer +Max(ggn.dtNextMov -ggn.dtLastCalc, 1)
    EndIf
  Else
    ' Turn GGN off
    If Not(legsDown) Then
      ggn.dtMov = 600
      R._executeMove()
    EndIf
  EndIf
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R._bodyIK iL%, xyzIn(), xyzOut()
  ' Calculates IK of the body for leg `iL%`, with foot position(`xyzIn(2)`).
  ' Uses `COX_OFF_XYZ(iL%,2)`, `g.rotY(iL%)`, and `in.xyzBodyRot_v(2)`
  ' -> `xyzOut(2)`
  Static d(2) = (0,0,0)
  Local rx, ry, rz, sx, sy, sz, cx, cy, cz, v
 'Print "R._bodyIK| iL=";iL%

  ' Calculate total x,z distance between center of body and foot
  d(0) = COX_OFF_XYZ(iL%,0) +xyzIn(0)
  d(2) = COX_OFF_XYZ(iL%,2) +xyzIn(2)

  ' Calculate sin and cos for each rotation
  rx = Rad(in.xyzBodyRot_v(0))
  ry = Rad(in.xyzBodyRot_v(1) +g.rotY(iL%))
  rz = Rad(in.xyzBodyRot_v(2))
  sx = Sin(rx)
  sy = Sin(ry)
  sz = Sin(rz)
  cx = Cos(rx)
  cy = Cos(ry)
  cz = Cos(rz)

  ' Calculate rotation matrix (`xyzOut(2)`)
  xyzOut(0) = d(0) -(d(0)*cy*cz -d(2)*cz*sy +xyzIn(1)*sz)
  v = d(0)*sy*sx -d(0)*cy*cx*sz +d(2)*cy*sx +d(2)*cx*sy*sz +xyzIn(1)*cz*cx
  xyzOut(1) = d(1) -v
  v = d(0)*cx*sy +d(0)*cy*sz*sx +d(2)*cy*cx -d(2)*sy*sz*sx -xyzIn(1)*cz*sx
  xyzOut(2) = d(2) -v
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R._legIK iL%, xyzIn()
  ' Calculates the angles of coxa, femur and tibia (`ggn.legAng(LEG_N-1,2)`)
  ' for the given foot position (`xyzIn(2)`) of leg (`iL%`).
  ' All intermediate angles are in radians.
  ' -> ggn.legAng(iL%, )
  Local dCF, aCx, IKSW, IKA1, IKA2, v, w, a
 'Print "R._legIK| iL=";iL%
  'legA = self._legAngles = ggn.legAng(LEG_N-1,2)
  'cLen = COX_LEN
  'fLen = FEM_LEN
  'tLen = TIB_LEN
  'tCor = TIB_CORR_ANGLE
  'cxoA = COX_OFF_ANG(6)
  'IKCoxaAngle -> aCx

  ' Calculate coxa angle
  ' (w/ `dCF` the length between coxa and foot; make sure that angle is
  '  between +/- 180)
  dCF = Sqr(xyzIn(0)^2 +xyzIn(0)^2)
  aCx = Atan2(xyzIn(2), xyzIn(0))
  a = Deg(aCx) +COX_OFF_ANG(iL%)
  ggn.legAng(iL%,COX) = Choice(Abs(a) > 180, a-Sgn(a)*360, a)

  ' Solving `IKA1`, `IKA2` and `IKSW`
  ' w/ `IKA1` the angle between SW line and the ground in radians
  '    `IKSW` the distance between femur axis and tars
  '    `IKA2` the angle between the line S>W with respect to femur
  IKA1 = Atan2(aCx -COX_LEN, xyzIn(1))
  IKSW = Sqr(xyzIn(1)^2 +(aCx -COX_LEN)^2)
  v = FEM2TIB2_DIF +IKSW^2
  w = v/(FEM_2LEN *IKSW)
  If w < -1 Or w > 1 Then
    Inc ggn.IKErr, 10
    w = Sgn(w)
  EndIf
  IKA2 = ACos(w)

  ' Calculate femur and tibia angles
  ggn.legAng(iL%,FEM) = -Deg(IKA1 +IKA2) +90
  w = v /FEMTIB_2LEN
  If w < -1 Or w > 1 Then
    Inc ggn.IKErr, 1
    w = Sgn(w)
  EndIf
  ggn.legAng(iL%,TIB) = TIB_CORR_ANG -Deg(ACos(w))
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R._executeMove
  ' Executes the move based on leg angles (`ggn.legAng(LEG_N-1, 2)`)
  ' and updates the GGN status and timing parameters
  Local t
 'Print "R._executeMove"

  ' Convert leg angles to servo angles
  Math C_MULT ggn.legAng(), srv.ang_f(), ggn.srvAng()
 'Math M_print ggn.legAng()
 'Math M_print ggn.srvAng()

  ' Convert servo angles to position (in [ms])
  R.Angles2Pos ggn.srvAng(), ggn.srvPos()

  ' Send positions to servos
  ' TODO: Add duration of move (`ggn.dtMov`)
  R._setAllServos ggn.srvPos()

  ' Keep track of timing
  t = Timer
  ggn.dtMoveLate = t -ggn.tMoveStart -ggn.dtPrevMov
  ggn.tMoveStart = t
  ggn.dtPrevMov = ggn.dtMov
  ggn.dtMov = ggn.dtNextMov
  ggn.state = GGN_COMPUTE
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Function R._arelegsDown()
  ' Check if all legs are down
  Static v(LEG_n-1, 2)
  Local sum = 0
  Math C_Sub ggn.xyzFoot(), FEET_INIT_XYZ(), v()
  sum = Abs(Math(SUM v()))
  R._arelegsDown = sum <= LEGS_DOWN_DEAD_Z
End Function


Function R._isGaitInMotion(zFactor)
  ' Returns True if one of the travel lengths are outside the range
  ' considered as the dead zone, that means basically in motion
  Local integer res
  res = Abs(in.x_zTravL_v(0)) > TRAVEL_DEAD_Z
  res = res Or (Abs(in.x_zTravL_v(2)) > TRAVEL_DEAD_Z)
  R._isGaitInMotion = res Or (Abs(in.travRotY_v *zFactor) > TRAVEL_DEAD_Z)
End Function

' ===========================================================================
' Input-related routines
' ---------------------------------------------------------------------------
Sub R.resetInput
  ' Define input control variables
  Static integer first = 1
  ResetIn: Restore ResetIn
  If first Then
    ' Allocate variables
    first = 0
    Dim integer in.isOn
    Dim integer in.doEmergStop

    ' Each parameter is described in addition by an array, with:
    ' (target_value, value_inc, n_steps_to_target, min, max)
    ' Note: The first 3 parameters are used for value "blending".
    Dim in.bodyYOffs_v, in.bodyYOffs(4)
    Dim in.bodyYShft_v, in.bodyYShft(4)
    Dim in.x_zTravL_v(2), in.x_zTravL(4,2)
    Dim in.travRotY_v, in.travRotY(4)
    Dim in.legLiftH_v, in.legLiftH(4)
    Dim in.xyzBody_v(2), in.xyzBody(4,2)
    Dim in.xyzBodyRot_v(2), in.xyzBodyRot(4,2)
    Dim in.delaySpeed_v, in.delaySpeed(4)
    Dim integer in.delayInput_v, in.delayInput(4)
  EndIf
  ' Status
  in.isOn = 0
  in.doEmergStop = 0

  ' Body offset (0=down, 35=default up) and y-shift
  in.bodyYOffs_v = 0
  Data 0, 0, 0, 0, BODY_Y_OFFS_MAX
  Read in.bodyYOffs()
  in.bodyYShft_v = g.bodyYOffs
  Data 0, 0, 0, -BODY_Y_SHFT_LIM, BODY_Y_SHFT_LIM
  Read in.bodyYShft()

  ' Current travel length (x,z), rotation (y), and height
  Math Set 0, in.x_zTravL_v()
  Data 0, 0, 0, -TRAVEL_X_Z_LIM(0), TRAVEL_X_Z_LIM(0)
  Data 0, 0, 0, -TRAVEL_X_Z_LIM(1), TRAVEL_X_Z_LIM(1)
  Data 0, 0, 0, -TRAVEL_X_Z_LIM(2), TRAVEL_X_Z_LIM(2)
  Read in.x_zTravL()
  in.travRotY_v = 0
  Data 0, 0, 0, -TRAV_ROT_Y_LIM, TRAV_ROT_Y_LIM
  Read in.travRotY()
  in.legLiftH_v = g.legLiftHDef
  Data 0, 0, 0, LEG_LIFT_MIN, LEG_LIFT_MAX
  Read in.legLiftH()

  ' Global input for body position (xyzBodyPos[1] is calculated),
  ' pitch (x), rotation (y), and roll (z)
  Math Set 0, in.xyzBody_v()
  Data 0, 0, 0, BODY_X_Z_POS_LIM(0), BODY_X_Z_POS_LIM(0)
  Data 0, 0, 0, BODY_X_Z_POS_LIM(1), BODY_X_Z_POS_LIM(1)
  Data 0, 0, 0, BODY_X_Z_POS_LIM(2), BODY_X_Z_POS_LIM(2)
  Read in.xyzBody()
  Math Set 0, in.xyzBodyRot_v()
  Data 0, 0, 0, -BODY_XYZ_ROT_LIM(0), BODY_XYZ_ROT_LIM(0)
  Data 0, 0, 0, -BODY_XYZ_ROT_LIM(1), BODY_XYZ_ROT_LIM(1)
  Data 0, 0, 0, -BODY_XYZ_ROT_LIM(2), BODY_XYZ_ROT_LIM(2)
  Read in.xyzBodyRot()

  ' Movement speed via adjustible delay [ms] and input-depdent delay
  in.delaySpeed_v = 80
  Data 0, 0, 0, 0, DELAY_SPEED_MAX
  Read in.delaySpeed()
  in.delayInput_v = 0
  Data 0, 0, 0, DELAY_INPUT_MIN, DELAY_INPUT_MAX
  Read in.delayInput()
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.inputUpdate
  ' Some input parameters are ramped slowly to their target values; this
  ' is done my frequently calling this routine
  ' TODO: Blending
  ' ...
  in.xyzBody_v(1) = Max(in.bodyYOffs_v +in.bodyYShft_v, 0)
  If Not(DEBUG And DEB_INP) Then Exit Sub
  Print "R.inputUpdate| xyzBody(1)=";in.xyzBody_v(1)
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.inputBody bo_y, lh
  ' Change body-related parameters
  '   bo_y := bodyYOffs; 0=down, 35=default up
  '   lh   := legLiftH; current travel height
  ' TODO: Blending
  in.bodyYOffs_v = Min(Max(bo_y, in.bodyYOffs(3)), in.bodyYOffs(4))
  in.legLiftH_v  = Min(Max(lh, in.legLiftH(3)), in.legLiftH(4))
  If Not(DEBUG And DEB_INP) Then Exit Sub
  Print "R.inputBody| ";
  Print "bo_y=";in.bodyYOffs_v;" lh=";in.legLiftH_v
End Sub

Sub R.inputWalk tl_x, tl_z, tr_y, ds
  ' Change walking-related parameters
  '   tl_x, tl_z := x_zTravL; current travel length X,Z
  '   tr_y       := travRotY; current travel rotation Y
  '   ds         : delaySpeed; adjustible delay [ms]
  ' TODO: Blending
  in.doEmergStop = 0
  in.x_zTravL_v(0) = Min(Max(tl_x, in.x_zTravL(3,0)), in.x_zTravL(4,0))
  in.x_zTravL_v(2) = Min(Max(tl_z, in.x_zTravL(3,2)), in.x_zTravL(4,2))
  in.travRotY_v    = Min(Max(tr_y, in.travRotY(3)), in.travRotY(4))
  in.delaySpeed_v  = Min(Max(ds, in.delaySpeed(3)), in.delaySpeed(4))
  If Not(DEBUG And DEB_INP) Then Exit Sub
  Print "R.inputWalk| ";
  Print "tl_x_z=";in.x_zTravL_v(0);",";in.x_zTravL_v(2);" ";
  Print "tr_y=";in.travRotY_v;" ds=";in.delaySpeed_v
End Sub

' ===========================================================================
' Gait-related routines
' ---------------------------------------------------------------------------
Sub R.resetGait
  ' Define gait
  Static integer first = 1
  resetG: Restore resetG
  If first Then
    first = 0
    Dim integer g.iSt, g.iLegIn, g.isInMot, g.isLastLeg
    Dim integer g.nSt, g.isHalfLiftH, g.TLDivFact, g.nPosLift
    Dim g.legLiftHDef, g.bodyYOffs, g.nomSpeed
    Dim g.xyz(LEG_N-1, 2)
    Dim g.legNr(LEG_N-1), g.rotY(LEG_N-1)
  EndIf
  ' Control variables
  g.iSt         = 1  ' Index of current gait step
  g.iLegIn      = 0  ' Input number of the leg
  g.isInMot     = 0  ' 1=gait is in motion
  g.isLastLeg   = 0  ' 1=current leg is last leg of sequence

  ' Relative x,y,z positions and y rotations
  Math Set 0, g.xyz()
  Math Set 0, g.rotY()

  ' Gait-specific
  g.nSt         = 8  ' Number of steps in gait
  g.legLiftHDef = 65 ' Default travel height (50)
  g.bodyYOffs   = 10
  g.isHalfLiftH = 1  ' Outer positions of lifted half height
  g.TLDivFact   = 4  ' n steps w/ leg on the floor (walking)
  g.nPosLift    = 3  ' n positions single leg is lifted
  g.nomSpeed    = 70 ' Nominal speed of the gait
  Data 5,1,5, 1,5,1  ' Initial leg positions
  Read g.legNr()
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.generateGaitSeq
  ' Generate the gait sequence for all legs
  ' Uses `g.xxx`  - gait-related variables
  '      `in.xxx` - input parameters (movement)
  Static integer iL, lNr, res1, res2, iS, nL, j
  Static float x, y, z, yr, lh
  iS  = g.iSt
  nL  = g.nPosLift

  ' If gait is not in motion, reset travel parameters
  If Not(g.isInMot) Then
    Math Set 0, in.x_zTravL_v()
    in.travRotY_v = 0
  EndIf
 'Print g.isInMot, in.x_zTravL_v(0), in.x_zTravL_v(2), in.legLiftH_v

  ' Proceed with gait ...
  For iL=0 To LEG_N-1
    x   = g.xyz(iL,0)
    y   = g.xyz(iL,1)
    z   = g.xyz(iL,2)
    yr  = g.rotY(iL)
    lNr = g.legNr(iL)

    ' Leg middle up position
    res1 = g.isInMot And (nL=1 Or nL=3) And iS=lNr
    res2 = Not(g.isInMot) And (iS=lNr)
    res2 = res2 And ((Abs(x)>2) Or (Abs(z)>2) Or (Abs(yr)>2))
    If res1 Or res2 Then
      ' Up ...
      g.xyz(iL,0) = 0
      g.xyz(iL,1) = -in.legLiftH_v
      g.xyz(iL,2) = 0
      g.rotY(iL)  = 0
    Else
      ' Optional half heigth rear
      res1 = (nL=2 And iS=lNr) Or (nL=3 And ((iS=lNr-1) Or (iS=lNr+g.nSt-1)))
      If g.isInMot And res1 Then
        lh = in.legLiftH_v
        g.xyz(iL,0) = -in.x_zTravL_v(0) /2
        g.xyz(iL,1) = Choice(g.isHalfLiftH, -lh /2, -lh)
        g.xyz(iL,2) = -in.x_zTravL_v(2) /2
        g.rotY(iL)  = -in.travRotY_v /2
      Else
        ' Optional half heigth front
        If g.isInMot And nL>=2 And ((iS=lNr+1) Or (iS=lNr-(g.nSt-1))) Then
          lh = in.legLiftH_v
          g.xyz(iL,0) = in.x_zTravL_v(0) /2
          g.xyz(iL,1) = Choice(g.isHalfLiftH, -lh /2, -lh)
          g.xyz(iL,2) = in.x_zTravL_v(2) /2
          g.rotY(iL)  = in.travRotY_v /2
        Else
          ' Leg front down position
          If (iS=(lNr+nL) Or iS=(lNr-(g.nSt-nL))) And y<0 Then
            g.xyz(iL,0) = in.x_zTravL_v(0) /2
            g.xyz(iL,1) = 0
            g.xyz(iL,2) = in.x_zTravL_v(2) /2
            g.rotY(iL)  = in.travRotY_v /2
          Else
            ' Move body forward
            g.xyz(iL,0) = x -in.x_zTravL_v(0) /g.TLDivFact
            g.xyz(iL,1) = 0
            g.xyz(iL,2) = z -in.x_zTravL_v(2) /g.TLDivFact
            Inc g.rotY(iL), -in.travRotY_v /g.TLDivFact
          EndIf
        EndIf
      EndIf
    EndIf
  Next
  ' Advance to the next step
  Inc g.iSt, 1
  If g.iSt > g.nSt Then g.iSt = 1

  ' Exit, if debug info is not requested
  If Not(DEBUG And DEB_GAIT) Then Exit Sub
  Print "g.iSt =";g.iSt
  For j=0 To LEG_N-1
    Print "  iLeg=";g.legNr(j);" xyz=";Str$(g.xyz(j,0),3,1);",";
    Print Str$(g.xyz(j,1),3,1);",";Str$(g.xyz(j,2),3,1);" ";
    Print "yrot=";Str$(g.rotY(j),3,1)
  Next j
End Sub

' ===========================================================================
' Maestro controller-related routines
' ---------------------------------------------------------------------------
' All-servo routines
' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.Angles2Pos a_deg(), p()
  ' Converts all servo positions from angle (in degree) to position (in us)
  ' Note that is `a_deg(iLeg, COX|FEM|TIB)`
  Local integer i, j, k,  a
  For i=0 To LEG_N-1
    For j=0 To 2
      k = leg.srv(j,i)
      a = Min(srv.r_deg(1,k), Max(srv.r_deg(0,k), a_deg(i,j)))
      p(k) = srv.r_us(0,k) +srv.dt_us(k) *(a -srv.r_deg(0,k)) /srv.da_deg(k)
    Next j
  Next i
 'For i=0 To SRV_N-1
 '  a = Min(srv.r_deg(1,i), Max(srv.r_deg(0,i), a_deg(i)))
 '  p(i) = srv.r_us(0,i) +srv.dt_us(i) *(a -srv.r_deg(0,i)) /srv.da_deg(i)
 'Next
End Sub

Sub R._setAllServos t_us(), wait%
  ' Set all `SRV_N` servos, starting with #0 to position `t_us%()`
  ' (NO PARAMETER CHECKING)
  Static String cmd$ length 64
  Static integer t(SRV_N-1)
  Local integer i, hb, lb
  cmd$ = "\&9F"+Chr$(SRV_N)+Chr$(0)
  Math Scale t_us(), SRV_RES, t()
  For i=0 To SRV_N-1
    hb = (t(i) And &H7F00) >> 7
    lb = t(i) And &H7F
    cmd$ = cmd$ +Chr$(lb)+Chr$(hb)
  Next
  Print #5, cmd$
  If wait% Then Do While Lof(#5) < 256 : Pause 1 : Loop
End Sub

' ---------------------------------------------------------------------------
' Single-servo methods
' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.setServo_deg i%, a_deg%, wait%
  ' Set servo `i%` position as angle `a_deg%` in degree
  If i% >= 0 And i% < SRV_N Then
    Local integer _t = R._a2t(i%, a_deg%)
    R._SetServo i%, _t, wait%
  EndIf
End Sub

Sub R.setServo i%, t_us%, wait%
  ' Set servo `i%` position as timing `t_us%` (in us)
  If i% >= 0 And i% < SRV_N Then
    Local integer _t = Min(Max(t_us%, SRV_MIN_US), SRV_MAX_US)
    R._SetServo i%, _t, wait%
  EndIf
End Sub

Sub R._setServo i%, t_us%, wait%
  ' Set servo `i%` position as timing `t_us%` (in us)
  ' If `wait` <> 0, it is waited until the out buffer is empty, NOT until
  ' the servo has reached its position
  ' (NO PARAMETER CHECKING)
  Static integer hb, lb
  Local integer _t = t_us% *SRV_RES
  hb = (_t And &H7F00) >> 7
  lb = _t And &H7F

  ' Send `set target` command
  If DEBUG And DEB_SERVOS Then
    Print "Servo #";i%;" to ";Str$(_t /SRV_RES, 0);" us"
  EndIf
  Print #5, "\&84"+Chr$(i%)+Chr$(lb)+Chr$(hb)
  If wait% Then Do While Lof(#5) < 256 : Pause 1 : Loop
End Sub

Function R._a2t(i%, a_deg%) As integer
  ' Convert for servo `%i` the angle `a_deg%` into the position (in us)
  ' Considers the servo's range in deg and its calibration values
  Local integer t, a = Min(srv.r_deg(1,i%), Max(srv.r_deg(0,i%), a_deg%))
  t = srv.r_us(0,i%) +srv.dt_us(i%) *(a -srv.r_deg(0,i%)) /srv.da_deg(i%)
  R._a2t = t
  If Not(DEBUG And DEB_SERVOS) Then Exit Function
  Print "Servo #"+Str$(i%)+" "+Str$(a,3,0) +Chr$(186)+" -> ";
  Print Str$(t,4,0)+" us"
End Function

' ---------------------------------------------------------------------------
' Routines to change servo parameters and retrieve information
' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub R.setServoSpeed i%, speed%
  ' Sets speed of servo `i%`
  Static integer hb, lb
  If i% < 0 Or i% > SRV_N-1 Then Exit Sub
  hb = (speed% >> 7) And &H7F
  lb = speed% And &H7F
  Print #5, "\&87"+Chr$(i%)+Chr$(lb)+Chr$(hb)
End Sub

Sub R.setServoAccel i%, accel%
  ' Sets acceleration of servo `i%`
  Static integer hb, lb
  If i% < 0 And i% > SRV_N-1 Then Exit Sub
  hb = (accel% >> 7) And &H7F
  lb = accel% And &H7F
  Print #5, "\&89"+Chr$(i%)+Chr$(lb)+Chr$(hb)
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Function R.getServoErr() As integer
  ' Returns (and clears) last servo controller error
  Static string res$
  Static integer i, pRes = Peek(VARADDR res$)

  ' Send `get errors` command and wait for reply
  If DEBUG And DEB_SERVOS Then Print "Get errors: ";
  Print #5, "\&A1"
  i = 20
  Do While Loc(#5) = 0 And i > 0
    Pause 2
    Inc i, -1
  Loop
  res$ = Input$(2, #5)

  ' Process reply
  If Peek(BYTE pRes) > 0 Then
    R.getServoErr = Peek(BYTE pRes+1) +(Peek(BYTE pRes+2) << 8)
    If DEBUG And DEB_SERVOS Then Print "0x"+Hex$(R.getServoErr, 2)
  Else
    R.getServoErr = -1
    If DEBUG And DEB_SERVOS Then Print "No reply"
  EndIf
End Function

' ===========================================================================
' Hexapod board-related routines
' ---------------------------------------------------------------------------
Sub R.LED state%
  ' Set/reset onboard (yellow) LED
  Pin(PIN_LED) = state% <> 0
End Sub

Sub R.Buzz freq%, dur_ms%
  ' Buzz at `freq%` Hz for `dur_ms%` milliseconds
  Local integer f = Max(Min(freq%, 10000), 0)
  PWM 1, f,,50
  If dur_ms% > 0 Then Pause dur_ms% : PWM 1, f,,0 : EndIf
End Sub

' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Sub _log.servos
  ' Print current angle (in degree) and position (in us) for each servo
  Local integer i
  For i=0 To SRV_N-1
    Print "Servo #"+Str$(i)+" "+Str$(srv.ang(i),3,0) +Chr$(186)+" -> ";
    Print Str$(srv.pos(i),4,0)+" us"
  Next
End Sub

' ---------------------------------------------------------------------------
                                                                                                                               