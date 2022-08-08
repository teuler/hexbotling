// --------------------------------------------------------------------------------
// servo2040_wbattery.scad (Hexabotling project)
// Modules that define a servo2040 board and the servo battery pack
// (not stand-alone; requires constants defined in the main program)
//
// The MIT License (MIT)
// Copyright (c) 2022 Thomas Euler
//
// --------------------------------------------------------------------------------
module ServoBattery(n=2) {
  // Creates a servo battery pack
  // (BH-18650-PC_DS Battery holder)
  //
  color("Blue", _alpha2) {
    _zbat = -13+1 -3; 
    dx = [11, -11];
    _h = 8;
    for(i=[0:n-1]) {
      translate([n>1?dx[i]:0, 0, _zbat]) {
        cube([22.9, 77.7, 21.3], center=true); 
        
        translate([0, 55.6/2, 5])
        cylinder(h=_h, r=3/2, $fn=_fn);
        translate([0, 55.6/2, 12])
        cylinder(h=_h, r=6/2, $fn=_fn);

        translate([0, -55.6/2, 5])
        cylinder(h=_h, r=3/2, $fn=_fn);
        translate([0, -55.6/2, 12])
        cylinder(h=_h, r=6/2, $fn=_fn);
        
      }
    }
  }
}    

// --------------------------------------------------------------------------------
function PCB_servo2040_metrics() 
  = [srv2040_dx, srv2040_dy, 
     [[ srv2040_dx/2 -2.7,  srv2040_dy/2 -2.7], 
      [-srv2040_dx/2 +2.7,  srv2040_dy/2 -2.7],
      [ srv2040_dx/2 -2.7, -srv2040_dy/2 +2.7], 
      [-srv2040_dx/2 +2.7, -srv2040_dy/2 +2.7]
     ]];

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -      
module PCB_servo2040(holes_only=false, screw_only=false) {
  // Creates a Pimoroni servo2040 board
  //
  _temp = PCB_servo2040_metrics();
  _dx = _temp[0];
  _dy = _temp[1];
  _xy = _temp[2];
  
  module _pbc() {
    color("ForestGreen", _alpha2)
    cube([_dx, _dy, 1], center=true);
    color("gray", _alpha2)
    translate([0, -_dy/2 +9.5/2, -15/2])
    cube([_dx-2*5, 9.5, 15], center=true);
  }  
  module _holes(_h) {
    for(xy=_xy) {    
      translate([xy[0], xy[1], -2])
      cylinder(h=_h, r=2.7/2, $fn=_fn);
      if(!screw_only) 
        translate([xy[0], xy[1], 15])
        cylinder(h=15, r=2.3, $fn=_fn);
    }  
  }

  rotate([180,0,90]) 
  translate([srv2040_offx, 0, srv2040_offz]) 
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
