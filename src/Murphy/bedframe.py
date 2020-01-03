import numpy as np
from math import radians, sin, cos
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression as LR

class Bedframe():
    def __init__(self, x,y, thickness, length, margin, angle):
        '''Design elements'''
        self.t = thickness
        self.l = length
        self.margin = margin # the distance from the edges to the point where a link can be connected
        
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

    def _offset_point(self, p, p1, p2, offset):
        x, y = p
        x1, y1, = p1
        x2, y2 = p2

        #vector1
        d1 = (((x1-x)**2 + (y1-y)**2)**.5)/offset
        v1 = (x1-x)/d1, (y1-y)/d1

        #vector from (x,y) to (x2,y2)
        d2 = (((x2-x)**2 + (y2-y)**2)**.5)/offset
        v2 = (x2-x)/d2, (y2-y)/d2

        return x + v1[0] + v2[0], y + v1[1] + v2[1]


    @property
    def head_lower_margin(self):
        p = self.lower_head
        p1 = self.lower_foot
        p2 = self.upper_head
        return self._offset_point(p, p1, p2, self.margin)


    @property
    def head_upper_margin(self):
        return self._offset_point(self.upper_head, self.lower_head, self.upper_foot, self.margin)

    @property
    def foot_lower_margin(self):
        return self._offset_point(self.lower_foot, self.upper_foot, self.lower_head, self.margin)

    @property
    def foot_upper_margin(self):
        return self._offset_point(self.upper_foot, self.upper_head, self.lower_foot, self.margin)



    # @property
    # def floor_opening(self):
    #     if (self.bottom >= 0) or (self.top <= 0):
    #         return 0
        
    #     #topside
    #     if np.sign(self.upper_head[1]) == np.sign(self.upper_foot[1]):
    #         topside = 0
    #     else:
    #         ys = np.array([[self.upper_head[1]], [self.upper_head[1]])
    #         xs = np.array([[self.upper_head[0]],[self.lower_head[0]]])
    #         topside = LR().fit(ys, xs).predict([[0]])[0]


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

        ax.scatter(self.head_lower_margin[0], self.head_lower_margin[1])
        ax.scatter(self.head_upper_margin[0], self.head_upper_margin[1])
        ax.scatter(self.foot_upper_margin[0], self.foot_upper_margin[1])
        ax.scatter(self.foot_lower_margin[0], self.foot_lower_margin[1])
        # # ax.scatter(self.CoG[0], self.CoG[1], marker = 'X', color = color)
        # # ax.scatter(self.floor_opening, 0, marker = 'o', color = color)
        # ax.plot([self.extents['left'], self.extents['right'], self.extents['right'], self.extents['left'], self.extents['left']],
        # [self.extents['bottom'], self.extents['bottom'], self.extents['top'], self.extents['top'], self.extents['bottom']], 
        # alpha = .1, color = color)
        if plot_here: plt.show()
        return ax


if __name__ == '__main__':
    b = Bedframe(0,0, 15, 80, 2, 10)
    b.plot()
    plt.show()

