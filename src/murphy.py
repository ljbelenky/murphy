from math import cos, sin, tan, atan, radians
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

class Murphy():
    learning_rate = -.1
    threshold = .001
    def __init__(self, bedframe, A_link, B_link, C_link, desired_deployed_height, desired_stowed_height, type = 'Beta', ):
        ''' Basic structure'''
        self.bedframe = bedframe
        self.A = A_link
        self.B = B_link
        self.C = C_link

        '''Design Goals'''
        self.desired_deployed_height = desired_deployed_height
        self.desired_stowed_height = desired_stowed_height

        self.collected_solutions = {}

    @property
    def ikea_error(self):
        '''The total difference between actual positions and intended positions for fixed, rigid components.'''
        return sum([component.ikea_error for component in [A_link, B_link, C_link]])

    @property
    def murphy_error(self):
        '''murphy_error is the sum of all differences between current design and optimal design. Used to optimize fixed, positions and rigid components'''

        # When deployed, the bed should be at desired height with the head of the bed close to the wall

        # When stowed, the bed should be flat up against the wall with the foot of the bed below the window

        # No part of the assembly should ever extend outside of the house

        # when stowed and deployed, no part of the links should extend above/forward of the bedframe

        # the floor opening should be minimized

        # the center of gravity of the bedframe should be as low as possible

    def plot(self):
        ax = plt.figure().add_subplot(111)
        ax.set_aspect('equal')
        for component in [self.bedframe, self.A, self.B, self.C]:
            ax = component.plot(ax)
        ax.set_title(round(self.ikea_error,2))
        plt.show()

    def assemble(self, plot_here = False):
        ''' For a given structure and bed angle, adjust link angles and bed (x,y) to minimize ikea error.'''
        # loop over the following variables, making small adjustments until ikea error is minimized (ideally zero):
        # [bedframe.x, bedframe.y, A_link.angle, B_link.angle, C_link.angle]
        # Note: it is necessary to reposition C_link (x,y) to B_link.distal after B_link.angle is adjusted.
        # while True:
        for i in range(10000):
            for variable in ['A.angle', 'B.angle', 'C.angle', 'bedframe.x', 'bedframe.y']:
                errors  = []
                for step in ['+=0.5', '-=1']:
                    exec('self.{variable} {step}'.format(variable = variable, step = step))
                    self.C.x, self.C.y = self.B.distal
                    errors.append(self.ikea_error)
                partial_derivative = errors[0]-errors[1]
                adjustment = self.learning_rate*partial_derivative + .5
                exec('self.{variable} += {adjustment}'.format(variable = variable, adjustment = adjustment))
            if (i%5000==0) and plot_here:
                self.plot()
        if plot_here: self.plot()
        self.collected_solutions[self.bedframe.angle] = deepcopy(self)

class Link():
    def __init__(self, x, y, length, width, angle, color, attachment = None):
        self.x, self.y = x, y
        self.length, self.width = length, width
        self.angle = angle
        self.color = color
        # Attachment point relative to the bedframe
        if attachment:
            self.attachment = {'x':attachment[0],'y':attachment[1]}
        else: self.attachment = None

    @property
    def room_attachment(self):
        # attachment point relative to the room
        if self.attachment:
            theta = radians(bedframe.angle)
            l = ((self.attachment['x']**2)+(self.attachment['y']**2))**0.5
            phi = atan(self.attachment['y']/self.attachment['x'])
            x = bedframe.x + l*cos(theta + phi)
            y = bedframe.y + l*sin(theta + phi)    
            return {'x':x, 'y':y}
        else: return None

    @property
    def distal(self):
        x, y, l, theta = self.x, self.y, self.length, radians(self.angle)
        X = x + l * cos(theta)
        Y = y + l * sin(theta) 
        return X,Y

    @property
    def edges(self):
        x,y,w, theta = self.x, self.y, self.width/2, radians(self.angle)
        X,Y = self.distal
        x0 = x - w*sin(theta)
        x1 = X - w*sin(theta)
        y0 = y + w*cos(theta)
        y1 = Y + w*cos(theta)

        X0 = x + w*sin(theta)
        X1 = X + w*sin(theta)
        Y0 = y - w*cos(theta)
        Y1 = Y - w*cos(theta)
        return [((x0, y0), (x1, y1)), ((X0, Y0), (X1, Y1))]

    @property
    def extents(self):
        left = min(self.x, self.distal[0]) - self.width/2
        right = max(self.x, self.distal[0]) + self.width/2
        top = max(self.y, self.distal[1]) + self.width/2
        bottom = min(self.y, self.distal[1]) - self.width/2
        return {'left':left, 'right':right, 'top':top, 'bottom':bottom}

    @property
    def floor_opening(self):
        w = r = self.width/2
        theta = radians(self.angle)
        x,y = self.x, self.y
        X,Y = self.distal

        if abs(self.y) < r:
            a0 = self.x + ((r**2)-(self.y)**2)**0.5
        else:
            a0 = 0
        if abs(self.distal[1]) < w:
            a1 = self.distal[0] + ((r**2)-self.distal[1]**2)**0.5
        else:
            a1 = 0
        if y * Y < 0:
            a2 = x - y*(X-x)/(Y-y) + abs(w/sin(theta))
        else: a2 = 0

        return max(a0,a1,a2)

    @property
    def CoG(self):
        return (self.x+self.distal[0])/2, (self.y+self.distal[1])/2

    @property
    def ikea_error(self):
        '''Ikea error is the assembly error, or the distance from the distal point of a link to its intended attachment point,
        plus the CoG of each component should be as low as possible.'''
        if self.attachment:
            fit_error = ((self.distal[0]-self.room_attachment['x'])**2+(self.distal[1]-self.room_attachment['y'])**2)
        else: fit_error = 0 
        return fit_error + self.CoG[1]*.1

    def plot(self, ax = None):
        plot_here = False
        if not ax:
            ax = plt.figure().add_subplot(111)
            ax.set_aspect('equal')
            plot_here = True
            
        r = self.width/2
        for edge in self.edges:
            ax.plot([edge[0][0],edge[1][0]], [edge[0][1], edge[1][1]], c = self.color)

        for x,y in zip([self.x,self.distal[0]], [self.y,self.distal[1]]):
            phi = np.radians(np.linspace(0,360,37))
            ax.plot(r*np.cos(phi)+x, r*np.sin(phi)+y, c = self.color )

        # Extents Box
        ax.plot([self.extents['left'], self.extents['right'], self.extents['right'], self.extents['left'], self.extents['left']],
        [self.extents['bottom'], self.extents['bottom'], self.extents['top'], self.extents['top'], self.extents['bottom']], 
        alpha = .1, c = self.color)

        # Floor Opening Point
        ax.scatter(self.floor_opening, 0, c=self.color)

        # Attachment Point
        if self.attachment:
            ax.scatter(**self.room_attachment, marker = 'x', c = self.color)
            ax.plot([self.distal[0], self.room_attachment['x']], [self.distal[1], self.room_attachment['y']], c = self.color, linestyle = 'dashed')

        if plot_here: plt.show()
        return ax

class Bedframe():
    def __init__(self, x,y,thickness, length, height_of_headboard, depth_of_headboard, angle = 0):
        '''Design elements'''
        self.t = thickness
        self.l = length
        self.h_headboard = height_of_headboard
        self.depth_of_headboard = depth_of_headboard

        '''Current Position'''
        self.x, self.y = x,y
        '''Angle in degrees, 0 is deployed, 90 is stowed'''
        self.angle = 0

    @property
    def foot(self):
        l, t, theta = self.l, self.t, radians(self.angle)
        lower = (self.x + l*cos(theta), self.y + l*sin(theta))
        upper = (lower[0] - t*sin(theta), lower[1] + t*cos(theta)) 
        return (lower, upper)

    @property
    def head(self):
        h, d, theta = self.h_headboard, self.depth_of_headboard, radians(self.angle)
        rear = (self.x - h * sin(theta), self.y + h * cos(theta))
        front = (rear[0] + d * cos(theta), rear[1] + d * sin(theta))
        return rear, front

    @property
    def pillow(self):
        h, d, t, theta = self.h_headboard, self.depth_of_headboard, self.t, radians(self.angle)
        x = self.head[1][0] + (h-t) * sin(theta)
        y = self.head[1][1] - (h-t) * cos(theta)
        return x,y

    @property
    def CoG(self):
        '''Center of Gravity of the main part of the bedframe'''
        X = (self.x + self.foot[1][0])/2
        Y = (self.y + self.foot[1][1])/2
        return X, Y

    def verify(self):
        l, d, theta = self.l, self.depth_of_headboard, radians(self.angle)
        a = round(self.pillow[0] + (l-d) * cos(theta),3)
        a_prime = round(self.foot[1][0],3)
        assert a == a_prime, '{a}, {a_prime}'.format(a=a, a_prime=a_prime)
        b = round(self.pillow[1] + (l-d) * sin(theta),3)
        b_prime = round(self.foot[1][1],3)
        assert b == b_prime, '{b}, {b_prime}'.format(b=b, b_prime = b_prime)

    @property
    def floor_opening(self):
        x,y = self.x, self.y
        X,Y =self.foot[0]     
        if y > 0 and Y > 0: return 0
        if Y <= 0: return X
        return x - (y * (X-x)/(Y-y))

    @property
    def extents(self):
        xs = [self.x, self.foot[0][0], self.foot[1][0], self.head[0][0], self.head[1][0], self.pillow[0]]
        left, right = min(xs), max(xs)
        ys = [self.y, self.foot[0][1], self.foot[1][1], self.head[0][1], self.head[1][1], self.pillow[1]]
        top, bottom = max(ys), min(ys)
        return {'left':left, 'top':top, 'right': right, 'bottom': bottom}

    def plot(self, ax = None):
        color = 'k'
        plot_here = False
        if not ax:
            ax = plt.figure().add_subplot(111)
            ax.set_aspect('equal')
            plot_here = True
        xs = [self.x, self.foot[0][0], self.foot[1][0], self.pillow[0], self.head[1][0], self.head[0][0], self.x]
        ys = [self.y, self.foot[0][1], self.foot[1][1], self.pillow[1], self.head[1][1], self.head[0][1], self.y]
        ax.plot(xs, ys, color = color)
        ax.scatter(self.CoG[0], self.CoG[1], marker = 'X', color = color)
        ax.scatter(self.floor_opening, 0, marker = 'o', color = color)
        ax.plot([self.extents['left'], self.extents['right'], self.extents['right'], self.extents['left'], self.extents['left']],
        [self.extents['bottom'], self.extents['bottom'], self.extents['top'], self.extents['top'], self.extents['bottom']], 
        alpha = .1, color = color)
        if plot_here: plt.show()
        return ax

if __name__ == '__main__':

    bedframe = Bedframe(10,4,10, 72, 24, 10)
    A_link = Link(0,5,12,4,0, 'r', (10,2))
    B_link = Link(2, -10, 30, 4, 0, 'g')
    C_link = Link(B_link.distal[0], B_link.distal[1], 20, 3, 0, 'b', (40,6))
    assembly = Murphy(bedframe, A_link, B_link, C_link, 18, 44)

    for angle in range(0,91,30):
        assembly.bedframe.angle = angle
        assembly.assemble(plot_here=False)