import numpy as np
from math import radians, sin, cos
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression as LR

class Bedframe():
    def __init__(self, x,y,thickness, length, angle):
        '''Design elements'''
        self.t = thickness
        self.l = length
        
        '''Current Position'''
        self.x, self.y = x,y
        '''Angle in degrees, 0 is deployed, 90 is stowed'''
        self.angle = angle

    @property
    def lower_foot(self):
        theta = radians(self.angle)
        return self.x + self.l*cos(theta), self.y + self.l*sin(theta)

    @property
    def upper_foot(self):
        theta = radians(self.angle)
        x = self.x + self.l*cos(theta) - self.t*sin(theta)
        y = self.y + self.l*sin(theta) + self.t*cos(theta)
        return x, y

    @property
    def lower_head(self):
        return self.x, self.y

    @property
    def upper_head(self):
        theta = radians(self.angle)
        x = self.x - self.t*sin(theta)
        y = self.y + self.t*cos(theta)
        return x,y 

    @property
    def left_edge(self):
        return min(self.lower_foot[0], self.lower_head[0], self.upper_foot[0], self.upper_head[0])

    @property
    def right_edge(self):
        return max(self.lower_foot[0], self.lower_head[0], self.upper_foot[0], self.upper_head[0])

    @property
    def top(self):
        return max(self.lower_foot[1], self.lower_head[1], self.upper_foot[1], self.upper_head[1])

    @property
    def bottom(self):
        return min(self.lower_foot[1], self.lower_head[1], self.upper_foot[1], self.upper_head[1])

    @property
    def floor_opening(self):
        if (self.bottom >= 0) or (self.top <= 0):
            return 0
        
        #topside
        if np.sign(self.upper_head[1]) == np.sign(self.upper_foot[1]):
            topside = 0
        else:
            ys = np.array([[self.upper_head[1]], [self.upper_head[1]])
            xs = np.array([[self.upper_head[0]],[self.lower_head[0]]])
            topside = LR().fit(ys, xs).predict([[0]])[0]



        #foot

        #headboard

        #bottomside

    

    # @property
    # def floor_opening(self):
    #     x,y = self.x, self.y
    #     X,Y =self.foot[0]     
    #     if y > 0 and Y > 0: return 0
    #     if Y <= 0: return X
    #     return x - (y * (X-x)/(Y-y))



    def plot(self, ax = None):
        color = 'k'
        plot_here = False
        if not ax:
            ax = plt.figure().add_subplot(111)
            ax.set_aspect('equal')
            plot_here = True

        xs = [self.lower_head[0], self.lower_foot[0], self.upper_foot[0], self.upper_head[0], self.lower_head[0]]
        ys = [self.lower_head[1], self.lower_foot[1], self.upper_foot[1], self.upper_head[1], self.lower_head[1]]
        ax.plot(xs, ys, color = color)

        bounding_xs = [self.left_edge, self.right_edge, self.right_edge, self.left_edge, self.left_edge]
        bounding_ys = [self.bottom, self.bottom, self.top, self.top, self.bottom]

        ax.plot(bounding_xs, bounding_ys, color = 'gray')
        # # ax.scatter(self.CoG[0], self.CoG[1], marker = 'X', color = color)
        # # ax.scatter(self.floor_opening, 0, marker = 'o', color = color)
        # ax.plot([self.extents['left'], self.extents['right'], self.extents['right'], self.extents['left'], self.extents['left']],
        # [self.extents['bottom'], self.extents['bottom'], self.extents['top'], self.extents['top'], self.extents['bottom']], 
        # alpha = .1, color = color)
        if plot_here: plt.show()
        return ax
