from math import cos, sin
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
            lower_foot = (self.x + self.l*cos(rad(self.angle)), self.y + self.l*sin(rad(self.angle)))

    def floor_opening(self, angle):
        '''if bedframe is fully above or fully below floor, opening is zero'''

    def __str__(self):
        return 'Bedframe of length {l}, at {x}{y} and angle {angle}'.format(l = self.l, x = self.x, y = self.y, angle = self.angle)
    def __repr__(self):
        return self.__str__()




if __name__ == '__main__':
    bedframe = Bedframe(10, 72, 24, 10)