class Murphy():
    '''The Murphy Object represents a bed assembly at a particular angle'''
    learning_rate = -.1
    threshold = .001
    def __init__(self, bedframe, A_link, B_link, C_link):
        ''' Basic structure'''
        self.bedframe = bedframe
        self.A = A_link
        self.B = B_link
        self.C = C_link

    @property
    def ikea_error(self):
        '''The total difference between actual positions and intended positions for fixed, rigid components.'''
        return sum([component.ikea_error for component in [self.A, self.B, self.C]])

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
            if self.ikea_error < 0.125: break
        print('Assembled in {} steps with Ikea error {}'.format(i,round(self.ikea_error,3)))
        if plot_here: self.plot()
