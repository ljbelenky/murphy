
from math import sin, cos, radians, atan
import numpy as np
import matplotlib.pyplot as plt

class Link():
    def __init__(self, x, y, length, width, angle, color, bedframe, attachment = None):
        self.x, self.y = x, y
        self.length, self.width = length, width
        self.angle = angle
        self.color = color
        self.bedframe = bedframe
        # Attachment point relative to the bedframe
        self.attachment = {'x':attachment[0],'y':attachment[1]}

    @property
    def room_attachment(self):
        # attachment point relative to the room
        if self.attachment:
            theta = radians(self.bedframe.angle)
            l = ((self.attachment['x']**2)+(self.attachment['y']**2))**0.5
            phi = atan(self.attachment['y']/self.attachment['x'])
            x = self.bedframe.x + l*cos(theta + phi)
            y = self.bedframe.y + l*sin(theta + phi)    
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
        '''Ikea error is the assembly error, or the distance from the distal point of a link to its intended attachment point'''
        if self.attachment:
            fit_error = ((self.distal[0]-self.room_attachment['x'])**2+(self.distal[1]-self.room_attachment['y'])**2)
        else: fit_error = 0 
        return fit_error

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
            ax.scatter(self.room_attachment['x'], self.room_attachment['y'], marker = 'x', c = self.color)
            ax.plot([self.distal[0], self.room_attachment['x']], [self.distal[1], self.room_attachment['y']], c = self.color, linestyle = 'dashed')

        if plot_here: plt.show()
        return ax
