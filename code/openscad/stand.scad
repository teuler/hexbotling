// --------------------------------------------------------------------------------
// stand.scad (Hexabotling project)
// Modules that define the stand
// (not stand-alone; requires constants defined in the main program)
//
// The MIT License (MIT)
// Copyright (c) 2022 Thomas Euler
//
// --------------------------------------------------------------------------------
module stand() {
  _x1 = 25;
  _y1 = 25;
  _z = -12;
  _r1 = 7;
  _r2 = 5;
  _r3 = 7;
  _h1 = 65;
  _xy = [[ _x1, _y1,_z], [-_x1, _y1,_z], [ _x1,-_y1,_z], [-_x1,-_y1,_z]];
  
  module adapter() {
    for(xy=_xy) {
      translate([-xy[0]*0.11, 0, -1])
      scale([1.10, 1.05, 1])
      difference() {
        translate(xy)
        sphere(_r1);
        body(wBattery=false);
      }
    }  
  }
  module base() {  
    translate([0,0,-20]) 
    linear_extrude(2) {
      hull() {
        translate(_xy[0])
        circle(r=_r2);
        translate(_xy[3])
        circle(r=_r2);
      }
      hull() {
        translate(_xy[1])
        circle(r=_r2);
        translate(_xy[2])
        circle(r=_r2);
      }
    }  
  }
  
  adapter();
  base();
  
  translate([0,0,-_h1-18])
  linear_extrude(_h1)
  circle(r=_r3);
  
  rotate([0,0,45])
  scale([1.75, 1.75, 1])
  translate([0,0,-_h1+2])
  base();
}

// --------------------------------------------------------------------------------
