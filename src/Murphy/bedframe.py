from math import radians, sin, cos
import matplotlib.pyplot as plt

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
