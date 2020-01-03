class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        if isinstance(other, Point):
            return self._distance_to_point(other)
        elif isinstance(other, LineSegment):
            return self._distance_to_line(other)
        else:
            raise Exception

    def _distance_to_point(self, other):
        return ((self.x-other.x)**2+(self.y-other.y)**2)**.5

    def _distance_to_line(self, line):
        x,y = self.x, self.y
        x1, y1 = line.point1.x, line.point1.y
        x2, y2 = line.point2.x, line.point2.y

        numerator = abs((y2-y1)*x-(x2-x1)*y + x2*y1 - y2*x1)
        denominator = ((y2-y1)**2 + (x2-x1)**2)**.5

        return numerator/denominator

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point(x,y)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x,y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __repr__(self):
        return f'{self.x},{self.y}'


    def is_between_lines(self, line1, line2):
        '''Yields true if the point is in the interior of the rectangle
        defined by the two parallel, flush, lines'''
        pass


class LineSegment:
    def __init__(self, p0, p1):
        points = list(set([p0, p1]))

        self.p0 = points[0]
        self.p1 = points[1]

    @property
    def length(self):
        return self.p0.distance(self.p1)

    def distance_to_point(self, point):
        return point.distance(self)

    def __add__(self, point):
        p0 = self.p0 + point
        p1 = self.p1 + point
        return LineSegment(p0, p1)

    def __sub__(self, point):
        p0 = self.p0 - point
        p1 = self.p1 - point
        return LineSegment(p0, p1)

    def __iadd__(self, point):
        self.p0, self.p1 = self.p0 + point, self.p1 + point
    
    def __isub__(self, point):
        self.p0, self.p1 = self.p0 - point, self.p1 - point

    def __repr__(self):
        return f'({self.p0})<-->({self.p1})'

