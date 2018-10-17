from math import cos, sin, tan, atan, radians
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
from Murphy.link import Link
from Murphy.bedframe import Bedframe
from Murphy.murphy import Murphy

class MurphyBed():
    '''The MurphyBed Class represents a collection of Murphy objects, all of the same design, solved over the full range of angles from deployed (0) to stowed (90)'''
    def __init__(self, bed, desired_deployed_height, desired_stowed_height):
        self.bed = bed
        self.desired_deployed_height, self.desired_stowed_height = desired_deployed_height, desired_stowed_height
        self.collected_solutions = {}

    def solve_over_full_range(self, steps):
        for angle in np.linspace(0,90, steps):
            print('Solving at angle ', angle)
            self.bed.bedframe.angle = angle
            self.bed.assemble()
            self.collected_solutions[angle] = deepcopy(self.bed)

    @property
    def murphy_error(self):
        '''murphy_error is the sum of all differences between current design and optimal design. Used to optimize fixed, positions and rigid components. 
        Calculation of Murphy Error requires collected_solutions for all angles between 0 and 90'''
        deployed = self.collected_solutions[0]
        stowed = self.collected_solutions[90]

        errors = []
        # When deployed, the bed should be at desired height
        errors.append((deployed.bedframe.y+deployed.bedframe.t-self.desired_deployed_height)**2)
        
        # When deployed, the head of the bed should be close to the wall
        errors.append(deployed.bedframe.x**2)
        
        # When stowed, the bed should be flat up against the wall
        errors.append((stowed.bedframe.x-stowed.bedframe.t)**2)

        # When stowed, the foot of the bed should be at desired height below the window
        errors.append((stowed.bedframe.y+stowed.bedframe.l - self.desired_stowed_height)**2)

        # No part of the assembly should ever extend outside of the house
        left_most = 0
        for murphy in self.collected_solutions.values():
            for component in [murphy.bedframe, murphy.A, murphy.B, murphy.C]:
                left_most = min(left_most, component.extents['left'])

        errors.append(left_most**2)

        # when stowed, no part of the links should extend forward of the bedframe if it is above the floor
        def stowed_encroachment(link):
            if (link.extents['top'] > 0) and (link.extents['right'] > stowed.bedframe.x):
                return link.extents['right']-stowed.bedframe.x
            else: return 0

        errors.append(max([stowed_encroachment(link) for link in [stowed.A, stowed.B, stowed.C]])**2)
        
        # when deployed, no part of the links should extend above/forward of the bedframe
        def deployed_encroachment(link):
            if (link.extents['right'] > deployed.bedframe.x) and (link.extents['top'] > (deployed.bedframe.y+deployed.bedframe.t)):
                return link.extents['top'] - deployed.bedframe.y+deployed.bedframe.t
            else: return 0

        errors.append(max([deployed_encroachment(link) for link in [deployed.A, deployed.B, deployed.C]])**2)
        
        # the floor opening should not be much larger than the thickness of the beframe
        floor_opening = 0
        for murphy in self.collected_solutions.values():
            for component in [murphy.bedframe, murphy.A, murphy.B, murphy.C]:
                floor_opening = max(floor_opening, component.floor_opening)

        if floor_opening > stowed.bedframe.x:
            error = floor_opening**2
        else:
            error = 0

        errors.append(error)
        
        return sum(errors) #, errors


if __name__ == '__main__':
    angle_steps = 5
    learning_rate = -.001
    # The basic components of a bed
    bedframe = Bedframe(10,4,10, 72, 24, 10)
    A_link = Link(0,5,12,4,0, 'r', bedframe, (10,2))
    B_link = Link(2, -10, 30, 4, 0, 'g', bedframe)
    C_link = Link(B_link.distal[0], B_link.distal[1], 20, 3, 0, 'b', bedframe, (40,6))
    
    # A bed assembled at a single position
    assembly = Murphy(bedframe, A_link, B_link, C_link)

    # The complete solution of a bed from deployed to stowed
    murphy_bed = MurphyBed(assembly, 14, 48)
    murphy_bed.solve_over_full_range(angle_steps)
    print('Initial Murphy Error: ', murphy_bed.murphy_error)

    initial_design = deepcopy(murphy_bed)

    murphy_error_history = []

    for i in range(200):
        murphy_bed.bed = murphy_bed.collected_solutions[0]
        for variable in ['A.x','A.y', "A.attachment['x']", "A.attachment['y']", "C.attachment['x']", 
        "C.attachment['y']", 'A.length', 'B.x','B.y','B.length', 'C.length']:
            print(variable)
            errors = []
            for step in ['+=0.5', '-=1']:
                exec('murphy_bed.bed.{variable}{step}'.format(variable = variable, step=step))
                murphy_bed.solve_over_full_range(angle_steps)
                print('Murphy error: ', murphy_bed.murphy_error)
                errors.append(murphy_bed.murphy_error)
            partial_derivative = errors[0]-errors[1]
            adjustment = partial_derivative*learning_rate + 0.5
            exec('murphy_bed.bed.{variable}+={adjustment}'.format(variable = variable, adjustment = adjustment))
            print(variable, adjustment-.5)
            murphy_bed.solve_over_full_range(angle_steps)
            print('Adjusted Murphy Error: ', murphy_bed.murphy_error)
            murphy_error_history.append(murphy_bed.murphy_error)

plt.plot(murphy_error_history)
plt.show()
