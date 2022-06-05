// --------------------------------------------------------------------------------
// servo.scad (Hexabotling project)
// Modules that define a micro servo
// (stand-alone)
//
// The MIT License (MIT)
// Copyright (c) 2022 Thomas Euler
//
// --------------------------------------------------------------------------------
srv_dspace       = 0.5;
srv_fn           = 60;

// Servo definitions
srv_base_dx      = 20 +srv_dspace*2;
srv_base_dy      = 8.6 +srv_dspace*2;
srv_base_dz      = 12 +srv_dspace;
srv_bar_dx       = 28;
srv_bar_dz       = 1;
srv_top_dz       = 17 -srv_bar_dz -srv_base_dz;
srv_top2_dz      = 20.2 -17;
srv_top3_dz      = 23.5 -20.2;
srv_hole_dist_dx = 17.5 +6;
srv_hole1_x      = (srv_bar_dx -srv_hole_dist_dx)/2;
srv_hole2_x      = srv_hole1_x +srv_base_dx;
srv_axis_x       = srv_hole2_x -6;
srv_axis_x_corr  = -1;

module Servo(pxyz=[0,0,0], axyz=[0,0,0], wHoles=false) {
  // Creates a servo 
  //
  module _Holes() {
    union() {
      translate([-srv_hole1_x+0.25+0.35, srv_base_dy/2, srv_base_dz-4]) 
        cylinder(h=srv_base_dz, r=r_hole4, center=true, $fn=srv_fn);
      translate([srv_hole2_x-0.5-0.35, srv_base_dy/2, srv_base_dz-4]) 
        cylinder(h=srv_base_dz, r=r_hole4, center=true, $fn=srv_fn);
    }
  }
  color("DimGray", _alpha2)
  translate(pxyz) 
  rotate(axyz)
  difference() {
    union() {
      cube([srv_base_dx, srv_base_dy, srv_base_dz], center=false);
      translate([-(srv_bar_dx -srv_base_dx)/2,0, srv_base_dz]) 
        cube([srv_bar_dx, srv_base_dy, srv_bar_dz], center=false);
      translate([0,0, srv_base_dz +srv_bar_dz]) 
        cube([srv_base_dx, srv_base_dy, srv_top_dz], center=false);
      z = srv_base_dz +srv_bar_dz +srv_top_dz;
      translate([srv_axis_x+srv_axis_x_corr, srv_base_dy/2, z]) {
        cylinder(h=srv_top2_dz, r=8/2, center=false, $fn=srv_fn);
        cylinder(h=srv_top3_dz +srv_top2_dz, r=4/2, center=false, $fn=srv_fn);
      }
    }
    _Holes();
  }
  if(wHoles)
    _Holes();
}

// --------------------------------------------------------------------------------
