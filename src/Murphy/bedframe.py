import numpy as np
from math import radians, sin, cos
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression as LR

from sympy import Point, Polygon
from math import radians


class Bedframe():
    def __init__(self, origin_point, thickness, length, margin, angle):
        '''Design elements'''
        self.lower_head = origin_point
        self._thickness = thickness
        self._length = length
        self._margin = margin
        self._angle = angle%360

    def __repr__(self):
        return str(self.frame)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle):
        self._angle = angle%360

    @property
    def frame(self):
        lower_head = self.lower_head
        lower_foot = self.lower_head + Point(self.length, 0)
        upper_foot = self.lower_head + Point(self.length, self.thickness)
        upper_head = self.lower_head + Point(0, self.thickness)

        return Polygon(lower_head, lower_foot, upper_foot, upper_head).rotate(radians(self.angle), pt = lower_head)

    
    @property
    def length(self):
        return self._length

    @property
    def thickness(self):
        return self._thickness

    @property
    def margin(self):
        return self._margin

    @length.setter
    def length(self, length):
        raise ValueError('length of bedframe cannot be modified')

    @thickness.setter
    def thickness(self, thickness):
        raise ValueError('thickness of bedframe connot be modified')

    @margin.setter 
    def margin(self, margin):
        raise ValueError('margin of bedframe cannot be modified')

    @property
    def active_area(self):
        angle = self.angle 
        margin = self.margin
        p0, p1, p2, p3 = self.frame.rotate(radians(-angle), pt = self.lower_head).vertices
        p0 = p0.translate(margin, margin)
        p1 = p1.translate(-margin, margin)
        p2 = p2.translate(-margin, -margin)
        p3 = p3.translate(margin, -margin)

        return Polygon(p0, p1, p2, p3).rotate(radians(angle), pt = self.lower_head)




    # # @property
    # # def floor_opening(self):
    # #     if (self.bottom >= 0) or (self.top <= 0):
    # #         return 0
        
    # #     #topside
    # #     if np.sign(self.upper_head[1]) == np.sign(self.upper_foot[1]):
    # #         topside = 0
    # #     else:
    # #         ys = np.array([[self.upper_head[1]], [self.upper_head[1]])
    # #         xs = np.array([[self.upper_head[0]],[self.lower_head[0]]])
    # #         topside = LR().fit(ys, xs).predict([[0]])[0]


    # def plot(self, ax = None):
    #     color = 'k'
    #     plot_here = False
    #     if not ax:
    #         ax = plt.figure().add_subplot(111)
    #         ax.set_aspect('equal')
    #         plot_here = True

    #     xs = [self.lower_head[0], self.lower_foot[0], self.upper_foot[0], self.upper_head[0], self.lower_head[0]]
    #     ys = [self.lower_head[1], self.lower_foot[1], self.upper_foot[1], self.upper_head[1], self.lower_head[1]]
    #     ax.plot(xs, ys, color = color)

    #     bounding_xs = [self.left_edge, self.right_edge, self.right_edge, self.left_edge, self.left_edge]
    #     bounding_ys = [self.bottom, self.bottom, self.top, self.top, self.bottom]

    #     ax.plot(bounding_xs, bounding_ys, color = 'gray')

    #     ax.scatter(self.head_lower_margin[0], self.head_lower_margin[1])
    #     ax.scatter(self.head_upper_margin[0], self.head_upper_margin[1])
    #     ax.scatter(self.foot_upper_margin[0], self.foot_upper_margin[1])
    #     ax.scatter(self.foot_lower_margin[0], self.foot_lower_margin[1])
    #     # # ax.scatter(self.CoG[0], self.CoG[1], marker = 'X', color = color)
    #     # # ax.scatter(self.floor_opening, 0, marker = 'o', color = color)
    #     # ax.plot([self.extents['left'], self.extents['right'], self.extents['right'], self.extents['left'], self.extents['left']],
    #     # [self.extents['bottom'], self.extents['bottom'], self.extents['top'], self.extents['top'], self.extents['bottom']], 
    #     # alpha = .1, color = color)
    #     if plot_here: plt.show()
    #     return ax


if __name__ == '__main__':
    b = Bedframe(Point(1,2), 15, 85, 2, 0)

