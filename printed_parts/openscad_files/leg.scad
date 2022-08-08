// --------------------------------------------------------------------------------
// leg.scad (Hexabotling project)
// All modules that define a leg
// (not stand-alone; requires constants defined in the main program)
//
// The MIT License (MIT)
// Copyright (c) 2022 Thomas Euler
//
// --------------------------------------------------------------------------------
module _arm1(px, py, pz, select) {
  // Creates one side ("arm") of a clamp for the legs
  //
  module _front1() {
    translate([srv_axis_x +px -4, -srv_base_dy/2 +0.25, 5])  
    hull() {
      cylinder(h=4, r=5, $fn=_fn);
      translate([15+4, 0,0])  
        cylinder(h=4, r=5, $fn=_fn);
    }  
    translate([srv_axis_x +px +15, -srv_base_dy/2 +0.25, -3])  
      cylinder(h=8, r1=7, r2=5, $fn=_fn);
    translate([px +28, -14, -8.75])  
      cube([6,14.5,5.75]);  
  }
  module _back1() {
    translate([srv_axis_x +px -4, -srv_base_dy/2, 4])  
      cylinder(h=3, r=6.2/2, $fn=_fn);
    translate([srv_axis_x +px +0.75, -14, -21])  
      cube([10, 20, 26]);          
    translate([srv_axis_x +px +10, 0.5, -24])  
      cube([11, 10, 30]);     
    translate([34 +px, -15, -16.5 -0.25])  
      cube([6, 16.5, 13.5 +1 -0.5]);          
    _link_hole(px);  
  }
  if((select == 0) || (select == 1)) {
    difference() {
      union() {
        difference() {
          _front1();
          _back1();
        }
        if(arm_latches) 
          if((select == 0) || (select == 1))
            _arm_latch(px, pz);
      }      
      _link_pin_hole(px);
    }  
  }
}


module _arm2(px, py, pz, select) {
 // Creates the other side ("arm") of a clamp for the legs
 //
  module _front1() {
    translate([srv_axis_x +px -4, -srv_base_dy/2, -25])  
    hull() {
      cylinder(h=4, r=5, $fn=_fn);
      translate([15+4, 0,0])  
        cylinder(h=4, r=4, $fn=_fn);
    }  
    translate([srv_axis_x +px +15, -srv_base_dy/2, -21])  
      cylinder(h=4.5, r1=4, r2=7, $fn=_fn);
    translate([px +28, -14, -16.5])  
      cube([6,14.5,5.75]);          
  }
  module _back1() {
    hull() {
      translate([srv_axis_x +px-4, -srv_base_dy/2, -24])  
        cylinder(h=5, r=7/2, $fn=_fn);
      translate([srv_axis_x +px+15, -srv_base_dy/2, -24])  
        cylinder(h=5, r=3/2, $fn=_fn);
      translate([srv_axis_x +px-5 -6, -srv_base_dy/2, -24])  
        cylinder(h=5, r=3/2, $fn=_fn);
    }  
    translate([srv_axis_x +px -4, -srv_base_dy/2, -27])  
      cylinder(h=10, r=1.0, $fn=_fn);
    translate([srv_axis_x +px -4, -srv_base_dy/2, -27.75])  
      cylinder(h=3, r=6.5/2, $fn=_fn);

    translate([srv_axis_x +px +0.75, -14, -21])  
      cube([10, 20, 26]);          
    translate([srv_axis_x +px +10, 0.5, -24])  
      cube([11, 10, 30]);     
    translate([34 +px, -15, -16.5 -0.25])  
      cube([6, 16.5, 13.5 +1 -0.5]);          
    _link_hole(px);  
  }
  if((select == 0) || (select == 2)) {
    difference() {
      union() {
        difference() {
          _front1();
          _back1();
        }
        if(arm_latches) 
          if((select == 0) || (select == 2))
            _arm_latch(px, pz -5);
      }      
      _link_pin_hole(px);
    }
  }
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
module _link_hole(px) {
  // Creates the hole for a leg link
  //
  translate([31+px, -4.8 +yoffs_link, -29]) {
    cylinder(h=42, r=r_hole2, $fn=_fn);        
    cylinder(h=10+5, r=r_hole3, $fn=_fn);        
  }
  translate([31+px, -4.8 +yoffs_link, 3-7]) 
    cylinder(h=10+5, r=r_hole3, $fn=_fn);        
}

module _link_pin_hole(px) {
  // Creates the pin for a leg link
  //
  translate([31+px, -9.8 -yoffs_link, -13.25]) 
    cylinder(h=7, r=r_hole2, $fn=_fn);        
}

module _arm_latch(px,pz,dz=3) {
  // Creates the latch that allows combining to leg elements via a clamp
  //
  color("Orange", _alpha1)  
  difference() {
    hull() {
      translate([px +28+3, -4, -8.75 +pz])  
        cylinder(h=dz, r=3, $fn=_fn);      
      translate([px +28+3, 3, -8.75 +pz])    
        cylinder(h=dz, r=3, $fn=_fn);      
    }   
    union() {
      translate([px +28+3, 3, -8.75 +pz+-3])    
        cylinder(h=10, r=1.5, $fn=_fn);      
    }
  }
}

// --------------------------------------------------------------------------------
module Coxa(pxyz=[0,0,0], wServo=false, wSlit=false, noConnect=false) { 
  // Creates the coxa 
  //
  module _body() {
    w = 2;
    translate([-w*2, -w, -w])
      cube([srv_base_dx +w*2, srv_base_dy +w*2, srv_base_dz+ w], center=false);  
    _r = 8;  
    translate([srv_axis_x+2, srv_base_dy/2, -w])  
    cylinder(h=srv_base_dz +2, r1=_r-1.6, r2=_r, $fn=_fn);
    translate([srv_axis_x+srv_axis_x_corr, srv_base_dy/2, -w-4])  
    cylinder(h=3, r=1.35, $fn=_fn);
    translate([srv_axis_x+srv_axis_x_corr, srv_base_dy/2, +2])  
    sphere(r=_r-2, $fn=_fn);
    if(!noConnect)
      translate([-10, srv_base_dy/2 -1, -2])
      cube([6.5, 2, srv_base_dz +w], center=false);  
    if(wSlit) {  
      translate([-10 -1, srv_base_dy/2 -1 -0.5, -2 -1])
      cube([6.5 +1, 2 +1, srv_base_dz +w +2.5], center=false);  
    }
    /*
    translate([srv_axis_x, srv_base_dy/2, -w-4-5])  
      cylinder(h=40, r=1.35, $fn=_fn);
    */  
  }
  module _link_pin() {
    rotate([90,0,0]) 
    translate([-7, srv_base_dz/2 -4.1 -yoffs_link, -7.25]) {
      cylinder(h=5, r=r_hole2-0.25, $fn=_fn);        
      if(wSlit) {
        _dy = (r_hole2-0.25)*2.5;
        translate([-3, -_dy/2, -0.5])
        cube([10, _dy, 6]);
      }  
    }    
  }
  module _link_hole() {
    // Link hole
    rotate([90,0,0]) 
    translate([-7, srv_base_dz/2 +0.9 +yoffs_link, -20]) {
      cylinder(h=30, r=r_hole2, $fn=_fn);          
      if(wSlit) {
        translate([0,0,-4.5])
        cylinder(h=10, r=r_hole2+2, $fn=_fn);        
        translate([0,0,25.2])
        cylinder(h=10, r=r_hole2+2, $fn=_fn);        
      }
    }  
  }  
  
  rotate([180,0,0])
  translate(pxyz) {
    color("DarkOrange",_alpha1)
    difference() {
      union() {
        _body();
        if(wSlit)
          _link_hole();
      }  
      union() {
        Servo([0,0,0.5], wHoles=!wSlit);
        translate([25.5,-4,-3])
          cube([10, 16, srv_base_dz+4]);
        translate([-1, 0, -1])
          cube([28, srv_base_dy, 5]);        
        if(!wSlit) {
          _l = !noConnect? 8: 16;  
          translate([-5, 0, -4])
            cube([_l, srv_base_dy/3, srv_base_dz +2]);      
        }  
        if(!wSlit)
          _link_hole();
      }
    }
    color("DarkOrange", _alpha1)
    _link_pin();    
    if(wServo)
      color("DimGray", _alpha2)
      Servo();
  }
}

// --------------------------------------------------------------------------------
module Femur(pxyz=[0,0,0], wServo=false, select=0) {
  // Creates the femur
  //
  px = pxyz[0] +4;
  py = pxyz[1];
  pz = pxyz[2];
  if((select == 0) || (select == 3)) {
    rotate([90,0,0]) 
      Coxa([px +38, py+5, pz-12], wServo);
  }
  color("OrangeRed", _alpha1)  
  union() {
    _arm1(px, py, pz, select);
    _arm2(px, py, pz, select);
  }  
}

// --------------------------------------------------------------------------------
module Tibia1(pxyz=[0,0,0], select=0) {
  // Creates the tibia
  //
  px = pxyz[0] +8;
  py = pxyz[1];
  pz = pxyz[2];
  _rot = [0, 0, 0];
  _tra = [0, 0, 0];
  
  rotate([90,0,0])
  translate([30 +px, -5+py, 12+pz]) {
    // Arms
    color("OrangeRed", _alpha1)      
    rotate(_rot) 
    translate(_tra)
    union() {
      _arm1(px, py, pz, select);
      _arm2(px, py, pz, select);
    }  

    // Leg
    color("Goldenrod", _alpha1)
    difference() {
      union() {
        translate([39, -4.8, -9.75]) {      
          translate([0,0,-1])
          linear_extrude(height=2, slices=25, scale=1.0, $fn=_fn)
          polygon([
            [15,-9.25], [10,-12], [3,-9.25], [-3,-9.25], [-3,5.25], [10,5.25], 
          ]);
          translate([-33, -20, 0])  
          difference() {
            union() {
              translate([0, 0, srv_base_dy/2-3.75]) 
                cylinder(h=3, r=60, $fn=_fn);        
              translate([36,10.8,-6.75]) 
                cube([6,14.5,6]);  
              translate([36,10.8,1]) 
                cube([6,14.5,6]);  
              translate([32.8,-51.5, 2.5]) 
                sphere(r=3, $fn=_fn);    
            }   
            union() {  
              translate([-70,-65,0]) 
                cube([100,130,5]);  
              translate([25, 20, srv_base_dy/2-4.5]) 
                cylinder(h=5, r=15, $fn=_fn);        
              hull() {
                translate([31, 45, srv_base_dy/2-4.5]) 
                  cylinder(h=5, r=8, $fn=_fn);        
                translate([55, 30, srv_base_dy/2-4.5]) 
                  cylinder(h=5, r=2, $fn=_fn);        
              }
              _x = [53,52,49,43];
              for(i=[0:3]) 
                hull() {
                  translate([25+12, -11*i, srv_base_dy/2-4.5]) 
                    cylinder(h=5, r=4, $fn=_fn);        
                  //translate([25+30-3.5*i, 3-10*i, srv_base_dy/2-4.5]) 
                  translate([_x[i], -11*i, srv_base_dy/2-4.5]) 
                    cylinder(h=5, r=2, $fn=_fn);        
                }
            }
          }  
        }  
        // Link pin
        rotate(_rot) 
        translate(_tra)
        translate([px+31, srv_base_dz/2 -4.1 -yoffs_link-12, -12.25])
        cylinder(h=5, r=r_hole2-0.25, $fn=_fn);   
          
        // Latch
        rotate(_rot) 
        translate(_tra)
        _arm_latch(px,pz-2,dz=2);
      }
      union() {
        rotate(_rot) 
        translate(_tra)
        _link_hole(px);
      }
    } 
  }   
}

// --------------------------------------------------------------------------------