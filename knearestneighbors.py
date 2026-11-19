"""Static two-dimensional k-d tree and exact nearest-neighbor selection.

Use finite coordinates in one common projected CRS with metre units for real
spatial data. IDs must be unique integers; they stay attached to their points
when buildTree reorders its input. PM2.5 values belong in a separate ID-keyed
table. This module selects neighbors; it does not perform IDW interpolation.

Python 3.10+; standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from heapq import heappush, heapreplace

DIMS = 2

Point = tuple[float, float]
# Negated distance and ID put the worst candidate at the min-heap's root.
_Candidate = tuple[float, int, Point]


class Axis(Enum):
    X = 0
    Y = 1


class TreeNode:
    """A point, its original ID, and the axis used to partition its children."""

    def __init__(self, point: Point, id: int, axis: Axis):
        self._point: Point = point
        self.left: TreeNode | None = None
        self.right: TreeNode | None = None
        self._axis: Axis = axis
        self._id: int = id

    @property
    def point(self) -> Point:
        return self._point

    @property
    def axis(self) -> Axis:
        return self._axis

    @property
    def id(self) -> int:
        return self._id


@dataclass(frozen=True)
class Neighbor:
    """A selected point and its squared distance, retaining the original ID."""

    id: int
    point: Point
    distance_sq: float


def buildTree(
    points: list[tuple[int, Point]], left: int, right: int, axisval: Axis
) -> TreeNode | None:
    """Build a median-split tree over [left, right), reordering that slice.

    Splitting axes alternate X/Y. Sorting at each level costs O(n log^2 n)
    overall; the tree has O(log n) depth. Pass a copy to preserve input order.
    """
    if left >= right:
        return None
    mid = (left + right) // 2
    axis = axisval.value
    points[left:right] = sorted(points[left:right], key=lambda p: p[1][axis])
    root_node = TreeNode(points[mid][1], points[mid][0], axisval)

    next_axis = Axis((axisval.value + 1) % DIMS)
    root_node.left = buildTree(points, left, mid, next_axis)
    root_node.right = buildTree(points, mid + 1, right, next_axis)

    return root_node


def distance_sq(p1: Point, p2: Point) -> float:
    """Squared Euclidean distance (m^2 when coordinates are in metres)."""
    return (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2


def search(
    root: TreeNode | None,
    query: Point,
    k: int,
    heapy: list[_Candidate],
    id: int | None,
) -> None:
    """Recursively fill a bounded candidate heap; called by nearest_neighbors.

    Heap entries are (-squared_distance, -original_id, point), not results.
    The ID tie-break keeps the lowest IDs when distances are equal.
    """
    if root is None or k == 0:
        return

    ref_point = root.point
    dist = distance_sq(ref_point, query)

    # Exclude by identity, so a different co-located station remains eligible.
    if root.id != id:
        candidate = (-dist, -root.id, ref_point)
        if len(heapy) < k:
            heappush(heapy, candidate)
        elif candidate > heapy[0]:
            heapreplace(heapy, candidate)

    axisval = root.axis.value
    dist_ax = query[axisval] - ref_point[axisval]

    if dist_ax <= 0:
        near = root.left
        far = root.right
    else:
        far = root.left
        near = root.right

    search(near, query, k, heapy, id)

    # Equality matters: the far side may have a tied distance and a lower ID.
    if len(heapy) < k or dist_ax ** 2 <= -heapy[0][0]:
        search(far, query, k, heapy, id)


def _validate_k(k: int) -> None:
    if not isinstance(k, int):
        raise TypeError("k must be an integer")
    if k < 0:
        raise ValueError("k must be non-negative")


def nearest_neighbors(
    root: TreeNode | None,
    query: Point,
    k: int,
    exclude_id: int | None = None,
) -> list[Neighbor]:
    """Return up to k neighbors sorted by (squared distance, original ID).

    Set exclude_id for leave-one-station-out queries; leave it None for an
    unmeasured query location. Empty trees and k=0 return an empty list. If k
    exceeds the eligible station count, return every eligible station.
    """
    _validate_k(k)
    if k == 0:
        return []

    heapy: list[_Candidate] = []
    search(root, query, k, heapy, exclude_id)
    result = [Neighbor(-entry[1], entry[2], -entry[0]) for entry in heapy]
    return sorted(result, key=lambda neighbor: (neighbor.distance_sq, neighbor.id))


def KNNOne(
    root: TreeNode | None, query: Point, k: int, id: int | None = None
) -> list[Point]:
    """Coordinate-only compatibility wrapper; prefer nearest_neighbors for IDs."""
    return [neighbor.point for neighbor in nearest_neighbors(root, query, k, id)]


def KNNAll(ipoints: list[Point], k: int) -> list[tuple[Point, list[Point]]]:
    """Find each input point's neighbors, excluding its original input ID.

    Results follow input order, even though tree construction reorders its
    working list. Equal coordinates with distinct input IDs are not excluded.
    """
    _validate_k(k)

    points = list(enumerate(ipoints))

    root = buildTree(points, 0, len(points), Axis.X)

    return [
        (point, KNNOne(root, point, k, original_id))
        for original_id, point in enumerate(ipoints)
    ]
