from math import cos, sin, tan, radians
import matplotlib.pyplot as plt
import numpy as np

def rad(degrees):
    return pi*degrees/180

class Murphy():
    def __init__(self, bedframe, A_link, B_link, C_link, desired_deployed_height, desired_stowed_height, type = 'Beta', ):

        ''' Basic structure'''
        self.bedframe = bedframe
        self.A = A_link
        self.B = B_link
        self.C = C_link
        ''' Alpha type has A and B links at headboard, Beta type has A and B links at foot of bed'''
        self.type = type

        '''Design Goals'''
        self.desired_deployed_height = desired_deployed_height
        self.desired_stowed_height = desired_stowed_height

        '''Status is true when positions of all components are fully defined'''
        self.status = False

        '''Score to optimize on, sum of scores of components. Zero is ideal'''
        self.score = None

    def resolve_positions(self, angle):
        '''determine position of all components given current design and given angle'''
        print('The resolve positions method has not been defined')
        self.status = True

    def plot(self):
        ax = plt.figure().add_subplot(111)
        ax.set_aspect('equal')
        for component in [self.bedframe, self.A, self.B, self.C]:
            ax = component.plot(ax)
        plt.show()

class Link():
    def __init__(self, x, y, length, width, angle, color):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.angle = angle
        self.color = color

    @property
    def distal(self):
        x, y, l, theta = self.x, self.y, self.length, radians(self.angle)
        X = self.x + l * cos(theta)
        Y = self.y + l * sin(theta) 
        return X,Y

    @property
    def edge0(self):
        x,y,w, theta = self.x, self.y, self.width/2, radians(self.angle)
        X,Y = self.distal
        x0 = x - w*sin(theta)
        x1 = X - w*sin(theta)
        y0 = y + w*cos(theta)
        y1 = Y + w*cos(theta)
        return ((x0, y0), (x1, y1))

    @property
    def edge1(self):
        x,y,w, theta = self.x, self.y, self.width/2, radians(self.angle)
        X,Y = self.distal
        x0 = x + w*sin(theta)
        x1 = X + w*sin(theta)
        y0 = y - w*cos(theta)
        y1 = Y - w*cos(theta)
        return ((x0, y0), (x1, y1))   

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
    
    def plot(self, ax):
        r = self.width/2
        ax.plot([self.x, self.distal[0]], [self.y, self.distal[1]], c = self.color, linestyle = 'dashed')
        for edge in [self.edge0, self.edge1]:
            ax.plot([edge[0][0],edge[1][0]], [edge[0][1], edge[1][1]], c = self.color)

        for x,y in zip([self.x,self.distal[0]], [self.y,self.distal[1]]):
            phi = np.radians(np.linspace(0,360,37))
            ax.plot(r*np.cos(phi)+x, r*np.sin(phi)+y, c = self.color )

        ax.plot([self.extents['left'], self.extents['right'], self.extents['right'], self.extents['left'], self.extents['left']],
        [self.extents['bottom'], self.extents['bottom'], self.extents['top'], self.extents['top'], self.extents['bottom']], 
        alpha = .1, c = self.color)

        ax.scatter(self.floor_opening, 0, c=self.color)
        return ax

    
class Bedframe():
    ''' all measurements in inches'''
    def __init__(self, thickness, length, height_of_headboard, depth_of_headboard, angle = 0):
        '''Design elements'''
        self.t = thickness
        self.l = length
        self.h_headboard = height_of_headboard
        self.depth_of_headboard = depth_of_headboard

        '''Current Position'''
        self.x, self.y = 0,0
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

    def floor_opening(self, angle):
        '''if bedframe is fully above or fully below floor, opening is zero'''

    @property
    def score(self):
        '''Sum of all scores for this object'''


    def __str__(self):
        return 'Bedframe of length {l}, at {x}{y} and angle {angle}'.format(l = self.l, x = self.x, y = self.y, angle = self.angle)
    def __repr__(self):
        return self.__str__()

    def plot(self, ax):
        '''code to plot bedframe in matplotlib'''
        xs = [self.x, self.foot[0][0], self.foot[1][0], self.pillow[0], self.head[1][0], self.head[0][0], self.x]
        ys = [self.y, self.foot[0][1], self.foot[1][1], self.pillow[1], self.head[1][1], self.head[0][1], self.y]
        ax.plot(xs, ys)
        ax.scatter(self.CoG[0], self.CoG[1], marker = 'X')
        return ax

    def render(self):
        '''creates POV-Ray render instructions'''
if __name__ == '__main__':
    print('starting murphy')
    bedframe = Bedframe(10, 72, 24, 10)
    A_link = Link(0,5,12,4,45, 'r')
    B_link = Link(2, -10, 30, 4, 40, 'g')
    C_link = Link(B_link.distal[0], B_link.distal[1], 20, 3, -60, 'b')

    assembly = Murphy(bedframe, A_link, B_link, C_link, 18, 44)

    for angle in range(0,91, 30):
        assembly.bedframe.angle = angle
        print(angle)
        assembly.plot()

    