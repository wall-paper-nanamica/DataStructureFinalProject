from typing import List
from collections import namedtuple
import time


class Point(namedtuple("Point", "x y")):
    def __repr__(self) -> str:
        return f'Point{tuple(self)!r}'


class Rectangle(namedtuple("Rectangle", "lower upper")):
    def __repr__(self) -> str:
        return f'Rectangle{tuple(self)!r}'

    def is_contains(self, p: Point) -> bool:
        return self.lower.x <= p.x <= self.upper.x and self.lower.y <= p.y <= self.upper.y


class Node(namedtuple("Node", "location left right")):
    """
    location: Point
    left: Node
    right: Node
    """

    def __repr__(self):
        return f'{tuple(self)!r}'


def _distance(p1: Point, p2: Point):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5


class KDTree:
    """k-d tree"""

    def __init__(self):
        self._root = None
        self._n = 0

    def _create(self, p: List[Point], depth: int):
        if len(p) == 0:
            return None
        if len(p) == 1:
            return Node(p[0], None, None)
        axis = depth % 2
        p.sort(key=lambda x: x[axis])
        median = len(p) // 2
        return Node(p[median], self._create(p[:median], depth + 1), self._create(p[median + 1:], depth + 1))

    def insert(self, p: List[Point]):
        """insert a list of points"""
        self._root = self._create(p, 0)
        self._n = len(p)

    def _range(self, node: Node, rectangle: Rectangle, depth: int, result: List[Point]):
        if node is None:
            return
        if rectangle.is_contains(node.location):
            result.append(node.location)
        axis = depth % 2
        if rectangle.lower[axis] <= node.location[axis]:
            self._range(node.left, rectangle, depth + 1, result)
        if rectangle.upper[axis] >= node.location[axis]:
            self._range(node.right, rectangle, depth + 1, result)

    def range(self, rectangle: Rectangle) -> List[Point]:
        """range query"""
        result = []
        self._range(self._root, rectangle, 0, result)
        return result

    def _nearest(self, node: Node, p: Point, depth: int, best: List[Point]):
        if node is None:
            return best
        if len(best) == 0 or _distance(p, node.location) < _distance(p, best[0]):
            best = [node.location]
        elif _distance(p, node.location) == _distance(p, best[0]):
            best.append(node.location)
        axis = depth % 2
        if p[axis] < node.location[axis]:
            best = self._nearest(node.left, p, depth + 1, best)
            if p[axis] + _distance(p, best[0]) >= node.location[axis]:
                best = self._nearest(node.right, p, depth + 1, best)
        else:
            best = self._nearest(node.right, p, depth + 1, best)
            if p[axis] - _distance(p, best[0]) <= node.location[axis]:
                best = self._nearest(node.left, p, depth + 1, best)
        return best

    def nearest(self, p: Point):
        """nearest neighbor"""
        return self._nearest(self._root, p, 0, [])


def range_test():
    points = [Point(7, 2), Point(5, 4), Point(9, 6), Point(4, 7), Point(8, 1), Point(2, 3)]
    kd = KDTree()
    kd.insert(points)
    result = kd.range(Rectangle(Point(0, 0), Point(6, 6)))
    assert sorted(result) == sorted([Point(2, 3), Point(5, 4)])


def nearest_test():
    points = [Point(x, y) for x in range(0, 20, 4) for y in range(0, 20, 4)]
    query_points = [Point(x, y) for x in range(20) for y in range(20)]
    kd = KDTree()
    kd.insert(points)
    for q in query_points:
        # naive method
        result1 = sorted(points, key=lambda x: _distance(x, q))
        result1 = [p for p in result1 if _distance(p, q) == _distance(result1[0], q)]
        # k-d tree
        result2 = kd.nearest(q)
        assert(sorted(result1) == sorted(result2))


def performance_test():
    points = [Point(x, y) for x in range(1000) for y in range(1000)]

    lower = Point(500, 500)
    upper = Point(504, 504)
    rectangle = Rectangle(lower, upper)
    #  naive method
    start = int(round(time.time() * 1000))
    result1 = [p for p in points if rectangle.is_contains(p)]
    end = int(round(time.time() * 1000))
    print(f'Naive method: {end - start}ms')

    kd = KDTree()
    kd.insert(points)
    # k-d tree
    start = int(round(time.time() * 1000))
    result2 = kd.range(rectangle)
    end = int(round(time.time() * 1000))
    print(f'K-D tree: {end - start}ms')

    assert sorted(result1) == sorted(result2)


if __name__ == '__main__':
    range_test()
    nearest_test()
    performance_test()
