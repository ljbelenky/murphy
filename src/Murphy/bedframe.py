from math import radians, sin, cos
import matplotlib.pyplot as plt

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

    

    # @property
    # def CoG(self):
    #     '''Center of Gravity of the main part of the bedframe'''
    #     X = (self.x + self.foot[1][0])/2
    #     Y = (self.y + self.foot[1][1])/2
    #     return X, Y


    # @property
    # def floor_opening(self):
    #     x,y = self.x, self.y
    #     X,Y =self.foot[0]     
    #     if y > 0 and Y > 0: return 0
    #     if Y <= 0: return X
    #     return x - (y * (X-x)/(Y-y))

    # @property
    # def extents(self):
    #     xs = [self.x, self.foot[0][0], self.foot[1][0], self.head[0][0], self.head[1][0], self.pillow[0]]
    #     left, right = min(xs), max(xs)
    #     ys = [self.y, self.foot[0][1], self.foot[1][1], self.head[0][1], self.head[1][1], self.pillow[1]]
    #     top, bottom = max(ys), min(ys)
    #     return {'left':left, 'top':top, 'right': right, 'bottom': bottom}

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
        # # ax.scatter(self.CoG[0], self.CoG[1], marker = 'X', color = color)
        # # ax.scatter(self.floor_opening, 0, marker = 'o', color = color)
        # ax.plot([self.extents['left'], self.extents['right'], self.extents['right'], self.extents['left'], self.extents['left']],
        # [self.extents['bottom'], self.extents['bottom'], self.extents['top'], self.extents['top'], self.extents['bottom']], 
        # alpha = .1, color = color)
        if plot_here: plt.show()
        return ax
