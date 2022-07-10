// Hexbotling
//
// Global variables
dspace           = 0.5;
_fn              = 60;
_alpha1          = 0.9;
_alpha2          = 0.7;

// Leg positions and body size
leg_dx           = 33; //28 35
leg_dy           = 60;
leg_cdx          = 7; //5
leg_dy_off       = -4.75;
legs_xyz         = [
    [ leg_dx, leg_dy-leg_dy_off, 1], 
    [ leg_dx +leg_cdx, -leg_dy_off, 1], 
    [ leg_dx,-leg_dy-leg_dy_off, 1],
    [-leg_dx, leg_dy+leg_dy_off, 1], 
    [-leg_dx -leg_cdx, leg_dy_off, 1], 
    [-leg_dx,-leg_dy+leg_dy_off, 1]
  ];
legs_xy_corr     = [
    [ -5,0], [-5,0], [-3.4,0], 
    [3.4,0], [ 5,0],   [ 5,0]
  ];
legs_rot         = [10,0,-10,-10,0,10];  

// PCBs
srv2040_dx       = 62;
srv2040_dy       = 42;
srv2040_offx     = -29;
srv2040_offz     = -5.5;

logPCB_dx        = 50;
logPCB_dy        = 42;
logPCB_offx      = +30;
logPCB_offz      = -17.5;

// Other parameters
r_hole1          = 1.1;
r_hole2          = 1.5;
r_hole3          = r_hole2*1.6;
r_hole4          = 0.9;
yoffs_link       = -6;
arm_latches      = true;

include <servo.scad>
include <leg.scad>
include <stand.scad>
include <servo2040_wbattery.scad>

// --------------------------------------------------------------------------------
module LogicBattery() {
  // Creates battery for logics
  //
  color("Blue", 0.2) 
  translate([0,40,6])
  rotate([0,90,90])
  cube([6.5,40,66], center=true);
}  
  
// --------------------------------------------------------------------------------
function PCB_log_metrics() 
  = [logPCB_dx, logPCB_dy, 
     [[ logPCB_dx/2 -2.7,  logPCB_dy/2 -2.7], 
      [-logPCB_dx/2 +2.7,  logPCB_dy/2 -2.7],
      [ logPCB_dx/2 -2.7, -logPCB_dy/2 +2.7], 
      [-logPCB_dx/2 +2.7, -logPCB_dy/2 +2.7]
     ]];


module PCB_log(holes_only=false) {
  // Creates the main PCB
  //
  _temp = PCB_log_metrics();
  _dx = _temp[0];
  _dy = _temp[1];
  _xy = _temp[2];
  
  module _pbc() {
    color("ForestGreen", _alpha2)
    cube([_dx, _dy, 1], center=true);
  }  
  module _holes(_h) {
    for(xy=_xy) {
      translate([xy[0], xy[1], -2])
      cylinder(h=_h, r=2.7/2, $fn=_fn);
      translate([xy[0], xy[1], 17])
      cylinder(h=15, r=2.3, $fn=_fn);
    }
  }

  rotate([180,0,90]) 
  translate([logPCB_offx, 0, logPCB_offz]) 
  union() {
    if(holes_only) {
      translate([0,0,-10])
      _holes(_h=30);
    }
    else {
      difference() {
        _pbc();
        _holes(_h=10);
      }  
    } 
   } 
}    

// --------------------------------------------------------------------------------
module voltage_converter_holder() {
  color("brown")
  union() {
    scale([0.98,1,1])
    difference() {
      union() {
        translate([0,-58,-3])
        cube([50,8,3], center=true);
        translate([0,-58,-10])
        cube([25,8,12], center=true);
      }
      union() {
        body(wBattery=false);
        PCB_servo2040(holes_only=true, screw_only=true);
        translate([0,-58,-8])
        cube([20,21,14], center=true);
        
      }  
    }  
    translate([0,-58,-16.5])
    difference() {
      cube([44, 17, 3], center=true);
      union() {
        translate([36.3/2, 10.0/2, -5]) 
        cylinder(h=10, r=1.3, $fn=_fn);
        translate([36.3/2, 10.0/2, 0]) 
        cylinder(h=10, r=3, $fn=6);
        
        translate([-36.3/2, -10.0/2, -5]) 
        cylinder(h=10, r=1.3, $fn=_fn);
        translate([-36.3/2, -10.0/2, 0]) 
        cylinder(h=10, r=3, $fn=6);

        translate([-36.3/2 -4, -1.5, -3]) 
        cube([10,15,5]);
        translate([+36.3/2 -6, -13.5, -3]) 
        cube([10,15,5]);

        translate([-36.3/2 +4, +4, -3]) 
        cube([20,5,5]);
        translate([+36.3/2 -24, -9, -3]) 
        cube([20,5,5]);
        
      }
    }
  }
} 
   
// ================================================================================
module body(wBattery=false,wPCBHoles=false) {
  // Creates the body
  //
  _r = 11;
  _h = 15.5;
  _z = -14.2;
  _axyz = [5.5,16,15.5];
  _xy1 = [[-20,0],        [-20,  -5],   [-20,  -10], 
          [+20,10],       [+20,   5],   [+20,    0]];
  _xy2 = [[-9.9,-13.9],   [-12, -12.8], [-12.7,-11.3], 
          [  +4.5, -3.5], [  6.5,-3.3], [  7.3, -2.8]];
  _srvPCB = PCB_servo2040_metrics();   
  _logPCB = PCB_log_metrics();
  _xoff1 = [7,2,-11,-6];  
  _yoff1 = [-3,-7,-3,-7];
  _xoff2 = [3,7,-7,-11.5];  
  _yoff2 = [-3,-7,-3,-7];
  
  module _b1() {
    // Frame
    //
    color("Crimson", _alpha2)
    translate([0,0,_z]) {
      hull() 
      for(iL=[0:5]) {
        translate([
            legs_xyz[iL][0] +_xy1[iL][0], 
            legs_xyz[iL][1] +_xy1[iL][1], 
            legs_xyz[iL][2]
          ])
        linear_extrude(_h)
        circle(r=_r, $fn=_fn);
      }
    }
  }
  module _b2() {
    // Coxa connectors
    //
    color("Crimson", _alpha2)
    translate([0,0,_z]) {
      for(iL=[0:5]) {
        translate([
            legs_xyz[iL][0] +_xy2[iL][0], 
            legs_xyz[iL][1] +_xy2[iL][1], 
            legs_xyz[iL][2]
          ])
        rotate(legs_rot[iL])  
        cube(_axyz);
      }
    }
  }
  module _b3() {
    // servo2040 connectors
    //
    color("Crimson", _alpha2)
    rotate([0,0,90])
    translate([srv2040_offx, 0, _z +13])
    for(i=[0:3]) {
      hull() {
        translate([_srvPCB[2][i][0], _srvPCB[2][i][1], 0]) 
        linear_extrude(6)
        circle(r=4, $fn=_fn);
        translate([_srvPCB[2][i][0] +_yoff1[i], _srvPCB[2][i][1] +_xoff1[i], 0])
        cube([10,4,4]);
      }  
    }  
  }   
  module _b4() {
    // Logics PCB connectors
    //
    color("Crimson", _alpha2)
    rotate([0,0,90])
    translate([logPCB_offx, 0, _z +13])
    for(i=[0:3]) {
      hull() {
        translate([_logPCB[2][i][0], _logPCB[2][i][1], 0])
        linear_extrude(18)
        circle(r=4, $fn=_fn);
        translate([_logPCB[2][i][0] +_yoff2[i], _logPCB[2][i][1] +_xoff2[i], 0])
        cube([10,4,4]);
      }  
    }  
  }   
  
  module _holes1() {
    scale([0.85,0.97,1.2]) 
    translate([0,0,1])
    _b1();
    translate([-13.5/2,-80,-10])
    cube([13.5,20,8.4]);
  }
  module _holes2(_wSlit,_noConnect) {  
    for(iL=[0:5]) {
      translate(legs_xyz[iL] +legs_xy_corr[iL])
      translate([0,0,-0.2]) 
      rotate([0, -10, legs_xyz[iL][0] < 0? 180 +legs_rot[iL]:0 +legs_rot[iL]])  
      Coxa(wServo=false, wSlit=_wSlit, noConnect=_noConnect);
    }
  }
  module _holes3() {
    for(x=[-8,8]) {
      translate([x,80,-6])
      rotate([90,0,0])
      cylinder(15, r=r_hole2, $fn=_fn);
    }  
  }  
  
  if(wBattery)
    ServoBattery();
  color("Crimson", _alpha2)
  difference() {
    union() {
      translate([0,28,-3])
      cube([50,12,4], center=true);
      translate([0,-28,-3])
      cube([50,12,4], center=true);
    }
    ServoBattery();
  }  
  difference() {
    union() {
      _b2();
      _b1();
      _holes2(_wSlit=false,_noConnect=true);    
    }  
    union() {
      _holes1();
      _holes3();
      PCB_servo2040(holes_only=true);
    }
  }
  difference() {
    union() {
      _b3();
      _b4();
    }  
    PCB_servo2040(holes_only=true);
    PCB_log(holes_only=true);
    LogicBattery();
  }
  /*
  for ...
    if(wPCBHoles) {
      translate([_srvPCB[2][i][0], _srvPCB[2][i][1], -20]) 
      cylinder(30,r=r_hole2, $fn=_fn);
    }  
  }
  */
}

// ================================================================================
// MAIN PROGRAM
// ================================================================================
if(false) {
  // Draw a single leg
  Coxa(wServo=true);
  Femur(wServo=true, select=0);
  Tibia(select=0); 
}
else {
  // Draw the whole robot ...
  if(true) {
    // ... with legs
    for(iL=[0:5]) {
      translate(legs_xyz[iL] +legs_xy_corr[iL]) 
      rotate([0, -10, legs_xyz[iL][0] < 0? 180 +legs_rot[iL]:0 +legs_rot[iL]]) { 
        Coxa(wServo=true, noConnect=true);
        Femur(wServo=true, select=0);
        Tibia(select=0);
      }
    }
  };  
  *stand();
  
  
  PCB_servo2040();
  PCB_log();
  LogicBattery();
  
  body(wBattery=false);
  voltage_converter_holder();
  
  
  /*difference() {
    body(wBattery=false);
    union() {
      translate([-10,-50,-20])
      cube([100,150,40]);
      translate([-40,-120,-20])
      cube([100,100,40]);
    }
  }*/
  /*
  color("yellow", 0.1)
  translate([0,59.6,0])
  cube([41.4,15.9,4], center=true);
  color("yellow", 0.1)
  translate([0,-59.6,0])
  cube([41.4,15.9,4], center=true);
  */
}
// --------------------------------------------------------------------------------

