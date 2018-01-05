"""
segment between two points.
"""
import struct
from math import pi, atan
from geo.point import Point
from geo.quadrant import Quadrant
from geo.coordinates_hash import CoordinatesHash



def calcul_clef(segment):
    """
    Retourne la clef (abscisse, angle) du segment pris en paramètres selon le point courant
    """

    if segment is None:
        return None

    #attribution des points de début et fin du segment
    if segment.endpoints[0].coordinates[1] >= segment.endpoints[1].coordinates[1]:
        #XA est l'abscisse la plus petite (la plus à gauche sur notre écran)
        #XB est l'abscisse la plus grande (la plus à droite)
        XA, XB = segment.endpoints[1].coordinates[0], segment.endpoints[0].coordinates[0]
        #YA est l'ordonnée la plus petite (la plus haute sur notre écran)
        #YB est l'ordonnée la plus grande (la plus basse sur notre écran)
        YA, YB = segment.endpoints[1].coordinates[1], segment.endpoints[0].coordinates[1]
    else:
        #XA est l'abscisse la plus petite, XB est l'abscisse la plus grande
        XA, XB = segment.endpoints[0].coordinates[0], segment.endpoints[1].coordinates[0]
        #YA est l'ordonnée la plus petite, YB est l'ordonnée la plus grande
        YA, YB = segment.endpoints[0].coordinates[1], segment.endpoints[1].coordinates[1]

    #calcul de l'angle
    if XB == XA:#cas du segment vertical
        angle = pi/2
    else:
        angle = atan((YB-YA)/(XB-XA))

    if angle < 0: #pas compris ce cas
        angle = pi + angle

    #calcul de l'abscisse
    #si la valeur est déjà dans le cache, on ne la recalcule pas
    if (segment, Segment.current_point.coordinates[1]) in Segment.cache_x:
        abscisse = Segment.cache_x[(segment, Segment.current_point.coordinates[1])]
    else:
        abscisse = XA + ((Segment.current_point.coordinates[1]-YA)/(YB-YA))*(XB-XA)

    #attribution des clefs
    #les segments à droite du point courant ont un angle positif
    if abscisse >= Segment.current_point.coordinates[0]:
        clef = (abscisse, angle)
    #les segments à gauche du point courant ont un anle négatif
    else:
        clef = (abscisse, -angle)

    return clef

class Segment:
    """
    oriented segment between two points.

    for example:

    - create a new segment between two points:

        segment = Segment([point1, point2])

    - create a new segment from coordinates:

        segment = Segment([Point([1.0, 2.0]), Point([3.0, 4.0])])

    - compute intersection point with other segment:

        intersection = segment1.intersection_with(segment2)

    """
    current_point = None
    cache_x = dict() #variable globale qui intervient dans la comparaison des segments


    def __init__(self, points):
        """
        create a segment from an array of two points.
        """
        self.endpoints = points

    def copy(self):
        """
        return duplicate of given segment (no shared points with original,
        they are also copied).
        """
        return Segment([p.copy() for p in self.endpoints])

    def length(self):
        """
        return length of segment.
        example:
            segment = Segment([Point([1, 1]), Point([5, 1])])
            distance = segment.length() # distance is 4
        """
        return self.endpoints[0].distance_to(self.endpoints[1])

    def bounding_quadrant(self):
        """
        return min quadrant containing self.
        """
        quadrant = Quadrant.empty_quadrant(2)
        for point in self.endpoints:
            quadrant.add_point(point)
        return quadrant

    def svg_content(self):
        """
        svg for tycat.
        """
        return '<line x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(
            *self.endpoints[0].coordinates,
            *self.endpoints[1].coordinates)

    def intersection_with(self, other):
        """
        intersect two 2d segments.
        only return point if included on the two segments.
        """
        i = self.line_intersection_with(other)
        if i is None:
            return  None# parallel lines

        if self.contains(i) and other.contains(i) and not (i in self.endpoints and i in other.endpoints):
            return i
        return None

    def line_intersection_with(self, other):
        """
        return point intersecting with the two lines passing through
        the segments.
        none if lines are almost parallel.
        """
        # solve following system :
        # intersection = start of self + alpha * direction of self
        # intersection = start of other + beta * direction of other
        directions = [s.endpoints[1] - s.endpoints[0] for s in (self, other)]
        denominator = directions[0].cross_product(directions[1])
        if abs(denominator) < 0.000001:
            # almost parallel lines
            return
        start_diff = other.endpoints[0] - self.endpoints[0]
        alpha = start_diff.cross_product(directions[1]) / denominator
        return self.endpoints[0] + directions[0] * alpha

    def contains(self, possible_point):
        """
        is given point inside us ?
        be careful, determining if a point is inside a segment is a difficult problem
        (it is in fact a meaningless question in most cases).
        you might get wrong results for points extremely near endpoints.
        """
#        if possible_point == self.endpoints[0] or possible_point == self.endpoints[1]:
#            return False
        distance = sum(possible_point.distance_to(p) for p in self.endpoints)
        return abs(distance - self.length()) < 0.0000001

    def __str__(self):
        return "Segment([" + str(self.endpoints[0]) + ", " + \
            str(self.endpoints[1]) + "])"

    def __repr__(self):
        return "[" + repr(self.endpoints[0]) + ", " + \
            repr(self.endpoints[1]) + "])"

    def __eq__(self, other):
        """
        opérateur d'égalité entre deux segments
        """
        return self is other

    def __hash__(self):
        return hash((self.endpoints[0].coordinates[0], self.endpoints[0].coordinates[1], self.endpoints[1].coordinates[0], self.endpoints[1].coordinates[1]))

    def __lt__(self, other):
        """
        Permet à sortedList de comparer l'objet segment par rapport à la valeur de sa clef
        """
        clef_self = calcul_clef(self)
        clef_other = calcul_clef(other)
#        print("cléself", self, clef_self)
#        print("cléother", other, clef_other)
        return clef_self < clef_other


def load_segments(filename):
    """
    loads given .bo file.
    returns a vector of segments.
    """
    coordinates_struct = struct.Struct('4d')
    segments = []
    adjuster = CoordinatesHash()

    with open(filename, "rb") as bo_file:
        packed_segment = bo_file.read(32)
        while packed_segment:
            coordinates = coordinates_struct.unpack(packed_segment)
            raw_points = [Point(coordinates[0:2]), Point(coordinates[2:])]
            adjusted_points = [adjuster.hash_point(p) for p in raw_points]
            segments.append(Segment(adjusted_points))
            packed_segment = bo_file.read(32)

    return adjuster, segments
