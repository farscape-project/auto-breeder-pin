#!/usr/env/python3

import gmsh
import math
import os
import sys
import csv
import subprocess
import struct # for hexing

# to convert float to hex
def float2hex(f):
    return struct.pack('f', f).hex()

class RunMoose:
    def __init__(self, application, path, input, csv_name):
        self.application = application
        self.application_path = path
        self.input = input
        self.output_filename = csv_name
        self.output_data = []

    def run(self):
        full_app = self.application_path + '/' + self.application
        # note deletes the old data
        process = subprocess.Popen(['rm', '-f', 'breeder-pin_out.*'], \
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = subprocess.Popen([full_app, '-i',self.input], \
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        return

    # gets a csv file from mooose and returns the text
    def collect_output(self):
        with open('breeder-pin_out.csv', newline='') as csvfile:
            data = []
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csvreader:
                data.append(row)     

        # return only the first and last row of the list
        self.output_data = [data[0],data[-1]]

    # write a csv file
    def output_csv(self):
        with open(self.output_filename, 'w', newline='') as csvfile:
            output = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
            output.writerow(self.output_data[0])
            output.writerow(self.output_data[1])

class counter:
    def __init__(self):
        self.count = 1

    def nextid(self):
        id = self.count
        self.count = self.count + 1
        return id
    
    def currentid(self):
        return self.count

class BreederPin:
    def __init__(self):
        gmsh.initialize()
        self.vertex_counter = counter()
        self.curve_counter = counter()
        self.group_counter = counter()
        self.lc = 0.01
        gmsh.option.setNumber('General.Verbosity', 1)

    def __del__(self):
        gmsh.finalize()

    # set the pin parameters
    def build_pin(self, inner_bore, outer_bore, \
                      bore_turning_point_x, bore_turning_point_y, \
                      pin_radial_thickness, breeder_inner_length, \
                      breeder_outer_length, \
                      outer_turning_point_x, outer_turning_point_y, \
                      outer_length, \
                      view = False):

        # sanity check add more geometric requirements here 
        if inner_bore > outer_bore:
            return False
        if inner_bore + pin_radial_thickness > outer_bore:
            return False
        if breeder_inner_length > outer_length:
            return False
        if breeder_outer_length > outer_length:
            return False
        if bore_turning_point_x > inner_bore + pin_radial_thickness:
            return False
        if bore_turning_point_x < inner_bore:
            return False
        if bore_turning_point_y < 0:
            return False

        # build the perimeter vertices in a clockwise way
        gmsh.model.geo.addPoint(inner_bore, 0, 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(0, 0, 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(0, outer_length , 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(outer_turning_point_x, outer_turning_point_y , 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(outer_bore, outer_length , 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(outer_bore, 0 , 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(outer_bore - pin_radial_thickness, 0 , 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(outer_bore - pin_radial_thickness, breeder_outer_length , 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(bore_turning_point_x, bore_turning_point_y , 0, self.lc, self.vertex_counter.nextid())
        gmsh.model.geo.addPoint(inner_bore, breeder_inner_length , 0, self.lc, self.vertex_counter.nextid())

        # make the curves
        gmsh.model.geo.addLine(1, 2, self.curve_counter.nextid())
        gmsh.model.geo.addLine(2, 3, self.curve_counter.nextid())
        gmsh.model.geo.addSpline([3,4,5], self.curve_counter.nextid())
        gmsh.model.geo.addLine(5, 6, self.curve_counter.nextid())
        gmsh.model.geo.addLine(6, 7, self.curve_counter.nextid())
        gmsh.model.geo.addLine(7, 8, self.curve_counter.nextid())
        gmsh.model.geo.addSpline([8,9,10], self.curve_counter.nextid())
        gmsh.model.geo.addLine(10, 1, self.curve_counter.nextid())
        gmsh.model.geo.addLine(3, 10, self.curve_counter.nextid())
        gmsh.model.geo.addLine(5, 8, self.curve_counter.nextid())
        gmsh.model.geo.addLine(7, 1, self.curve_counter.nextid())

        # make the loops
        gmsh.model.geo.addCurveLoop([1,2,9,8], 1)
        gmsh.model.geo.addSurfaceFilling([1], 1)
        gmsh.model.geo.addCurveLoop([-9,3,10,7], 2)
        gmsh.model.geo.addSurfaceFilling([2], 2)    
        gmsh.model.geo.addCurveLoop([-10,4,5,6], 3)
        gmsh.model.geo.addSurfaceFilling([3], 3)  
        gmsh.model.geo.addCurveLoop([11,-8,-7,-6], 4)
        gmsh.model.geo.addSurfaceFilling([4], 4) 

        # add the groups
        gmsh.model.geo.addPhysicalGroup(1,[1],self.group_counter.nextid(),"outlet")
        gmsh.model.geo.addPhysicalGroup(1,[5],self.group_counter.nextid(),"inlet")
        gmsh.model.geo.addPhysicalGroup(1,[2,3,4,6,7,8],self.group_counter.nextid(),"noslip")
        gmsh.model.geo.addPhysicalGroup(2,[1,2,3],self.group_counter.nextid(),"fluid")
        gmsh.model.geo.addPhysicalGroup(2,[4],self.group_counter.nextid(),"breeder")

        gmsh.model.geo.synchronize()

        if view:
           gmsh.fltk.run()

        return True

    def build_mesh(self, view = False):
        gmsh.model.mesh.setCompound(2, [1,2,3])
        gmsh.model.mesh.generate(2)

        if view:
           gmsh.fltk.run()

    def export_mesh(self,filename = "breeder_pin.msh"):
        gmsh.write(filename) 

bp = BreederPin()
# for your first go you could maybe fix the outer_length and the outer bore
# and let the rest be free?
# 
inner_bore = 0.05
outer_bore = 0.5
bore_turning_point_x = 0.2
bore_turning_point_y = 0.8
pin_radial_thickness = 0.3
breeder_inner_length = 0.7
breeder_outer_length = 0.7
outer_turning_point_x = 0.25
outer_turning_point_y = 1.01
outer_length = 0.9

error_code = bp.build_pin(inner_bore = inner_bore, outer_bore = outer_bore,\
                      bore_turning_point_x = bore_turning_point_x, \
                      bore_turning_point_y = bore_turning_point_y, \
                      pin_radial_thickness = pin_radial_thickness, \
                      breeder_inner_length = breeder_inner_length, \
                      breeder_outer_length = breeder_outer_length, \
                      outer_turning_point_x = outer_turning_point_x, \
                      outer_turning_point_y = outer_turning_point_y, \
                      outer_length = outer_length) 
if not error_code:
    print('inconsistent parameter set')
    sys.exit(1)

bp.build_mesh()
bp.export_mesh()

# params that define the problem
parameters = [inner_bore, outer_bore, bore_turning_point_x, \
              bore_turning_point_y, pin_radial_thickness, \
              breeder_inner_length, breeder_outer_length, \
              outer_turning_point_x, outer_turning_point_y, \
              outer_length]

# get the params as hex values 
csv_name = '_'.join([float2hex(i) for i in parameters])
csv_name = csv_name + ".csv"

# now run moose
moose = RunMoose('combined-opt', '/home/adavis/opt/moose/modules/combined', \
                'breeder-pin.i', csv_name)
moose.run()
# run data is the min/max values from the moose problem
moose.collect_output()
moose.output_csv()