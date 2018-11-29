from math import cos, sin, tan, atan, radians
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
from Murphy.link import Link
from Murphy.bedframe import Bedframe
from Murphy.murphy import Murphy
import sys
import pickle

class MurphyBed():
    '''The MurphyBed Class represents a collection of Murphy objects, all of the same design, solved over the full range of angles from deployed (0) to stowed (90)'''
    def __init__(self, bed, desired_deployed_height, desired_stowed_height):
        self.bed = bed
        self.desired_deployed_height, self.desired_stowed_height = desired_deployed_height, desired_stowed_height
        self.collected_solutions = {}

    def solve_over_full_range(self, steps):
        for angle in np.linspace(0,90, steps):
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

        balance = np.array([5, 7, 2, 1, 1, 1, 50, 50, 1, 1,1])
        
        # When deployed, the bed should be at desired height
        errors.append((deployed.bedframe.y+deployed.bedframe.t-self.desired_deployed_height)**2)
        
        # When deployed, the head of the bed should be close to the wall
        errors.append(deployed.bedframe.x**2)
        
        # When stowed, the bed should be flat up against the wall
        errors.append((stowed.bedframe.x-stowed.bedframe.h_headboard)**2)

        # When stowed, the foot of the bed should be at desired height below the window
        errors.append((stowed.bedframe.y+stowed.bedframe.l - self.desired_stowed_height)**2)

        # No part of the assembly should ever extend outside of the house
        left_most = 0
        for murphy in self.collected_solutions.values():
            for component in [murphy.bedframe, murphy.A, murphy.B]:
                left_most = min(left_most, component.extents['left'])

        errors.append(left_most**2)

        # when stowed, no part of the links should extend forward of the bedframe if it is above the floor
        def stowed_encroachment(link):
            if (link.extents['top'] > 0) and (link.extents['right'] > stowed.bedframe.x):
                return (link.extents['right']-stowed.bedframe.x)**2
            else: return 0

        errors.append(max([stowed_encroachment(link) for link in [stowed.A, stowed.B]]))
        
        # when deployed, no part of the links should extend above/forward of the bedframe
        def deployed_encroachment(link):
            if (link.extents['right'] > deployed.bedframe.x) and (link.extents['top'] > (deployed.bedframe.y+deployed.bedframe.t)):
                return (link.extents['top'] - deployed.bedframe.y+deployed.bedframe.t)**2
            else: return 0

        errors.append(max([deployed_encroachment(link) for link in [deployed.A, deployed.B]]))
        
        # the floor opening should not be much larger than the thickness of the beframe
        floor_opening = 0
        for murphy in self.collected_solutions.values():
            for component in [murphy.bedframe, murphy.A, murphy.B]:
                floor_opening = max(floor_opening, component.floor_opening)

        if floor_opening > stowed.bedframe.x:
            error = floor_opening**2
        else:
            error = 0
        errors.append(error)

        #the bed should be buildable
        errors.append(max([i.ikea_error for i in self.collected_solutions.values()])**2)

        # Link A,B Attachment point must be on the bedframe
        for i in [self.bed.A, self.bed.B]:
            x = i.attachment['x']
            y = i.attachment['y']
            if (0 < x < self.bed.bedframe.l) and (0 < y < self.bed.bedframe.t):
                errors.append(0)
            elif (0 < x < self.bed.bedframe.depth_of_headboard) and (0 < y < self.bed.bedframe.h_headboard):
                errors.append(0)
            else:
                X,Y = self.bed.bedframe.CoG
                errors.append((X-x)**2 + (Y-y)**2)

        errors = (np.array(errors)/balance)
        
        return errors.sum(), errors

def plot_all(murphy_bed):
    ax = plt.figure().add_subplot(111)
    for i in murphy_bed.collected_solutions.values():
        for j in [i.bedframe, i.A, i.B]:
            j.plot(ax)
    plt.show()

def cycles(n=10):
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except:
            pass    
    return n

def plot():
    plt.plot(adjustments)
    plt.show()
    plt.plot(murphy_errors_history)
    plt.show()
    plot_all(murphy_bed)

if __name__ == '__main__':
    angle_steps = 5
    learning_rate = -.08
    # The basic components of a bed
    bedframe = Bedframe(10,4,10, 72, 12, 8)
    A_link = Link(x=0,y=0,length=10,width=4,angle=80, color = 'r', bedframe = bedframe, attachment = (5,2))
    B_link = Link(x=20, y = -1, length = 10, width = 4, angle = 110, color ='g', bedframe = bedframe, attachment = (18,2))

    # A bed assembled at a single position
    assembly = Murphy(bedframe, A_link, B_link)

    # The complete solution of a bed from deployed to stowed
    murphy_bed = MurphyBed(assembly, 15, 40)
    # with open('murphy.pkl','rb') as f:
    #     murphy_bed = pickle.load(f)
    murphy_bed.solve_over_full_range(angle_steps)
    print('Initial Murphy Error: ', murphy_bed.murphy_error[0])

    # initial_design = deepcopy(murphy_bed)

    murphy_error_history = []
    murphy_errors_history = []
    adjustments = []

    for i in range(cycles()):
        print('#'*20+'\n'+str(i)+'\n'+'#'*20)
        murphy_bed.bed = murphy_bed.collected_solutions[0]
        variable = np.random.choice(np.array(['A.x','A.y', "A.attachment['x']", "A.attachment['y']", 'A.length', 'B.x','B.y','B.length', "B.attachment['x']", "B.attachment['y']"]))
        print(variable)
        errors = []
        for step in ['+=0.5', '-=1']:
            exec('murphy_bed.bed.{variable}{step}'.format(variable = variable, step=step))
            murphy_bed.solve_over_full_range(angle_steps)
            errors.append(murphy_bed.murphy_error[0])
        partial_derivative = errors[0]-errors[1]
        adjustment = partial_derivative*learning_rate + 0.5
        exec('murphy_bed.bed.{variable}+={adjustment}'.format(variable = variable, adjustment = adjustment))
        adjustments.append(adjustment)
        murphy_bed.solve_over_full_range(angle_steps)
        print('Adjusted Murphy Error: ', murphy_bed.murphy_error[0])
        murphy_error_history.append(murphy_bed.murphy_error[0])
        murphy_errors_history.append(murphy_bed.murphy_error[1])

        if i%100==0:
            with open('murphy.pkl', 'wb') as f:
                pickle.dump(murphy_bed, f)

with open('murphy.pkl', 'wb') as f:
                pickle.dump(murphy_bed, f)

plot()