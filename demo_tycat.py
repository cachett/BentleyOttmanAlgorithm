#!/usr/bin/env python3
"""
script de demonstration pour tycat.
"""

from random import random
from itertools import combinations, product
from geo.point import Point
from geo.segment import Segment
from geo.tycat import tycat

def main():
    """
    tycat example
    """
    points = [[Point([random(), random()]) for _ in range(5)] for _ in range(2)]
    segments = [[Segment(endpoints) for endpoints in combinations(p, r=2)] for p in points]
    print("tycat(points, segments)")
    tycat(points, segments)
    print("tycat(zip(iter(points), iter(segments)))")
    tycat(zip(iter(points), iter(segments)))
    print("tycat(*zip(iter(points), iter(segments)))")
    tycat(*zip(iter(points), iter(segments)))
    intersections = filter(None, (c[0].intersection_with(c[1]) for c in product(*segments)))
    print("intersections entre rouge et vert")
    tycat(segments[0], segments[1], intersections)

main()
