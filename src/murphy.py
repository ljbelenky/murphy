from math import cos, sin, radians
pi = 3.141592653

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
        rear = (self.x - h * sin(theta), self.y - h * cos(theta))
        front = (rear[0] + d * cos(theta), rear[1] + d * sin(theta))
        return rear, front

    @property
    def CoG(self):
        '''Center of Gravity of the main part of the bedframe'''
        X = (self.x + self.foot[1][0])/2
        Y = (self.y + self.foot[1][1])/2
        return X, Y

    def floor_opening(self, angle):
        '''if bedframe is fully above or fully below floor, opening is zero'''

    def __str__(self):
        return 'Bedframe of length {l}, at {x}{y} and angle {angle}'.format(l = self.l, x = self.x, y = self.y, angle = self.angle)
    def __repr__(self):
        return self.__str__()

if __name__ == '__main__':
    print('starting murphy')
    bedframe = Bedframe(10, 72, 24, 10)