from enum import Enum
from heapq import heapify_max, heappush_max, heappushpop_max

DIMS = 2 #make constants large

type Point = tuple[float, float]

class Axis(Enum):
    X = 0
    Y = 1


#KD tree node
class TreeNode:
    def __init__(self, point: Point, id: int, axis: Axis):
        self._point: Point = point #not changeable
        self.left: TreeNode | None = None
        self.right: TreeNode | None = None
        self._axis: Axis = axis
        self._id: int = id

    @property
    def point(self) -> Point:
        return self._point #we will not be modifying this

    @property
    def axis(self) -> Axis:
        return self._axis #we will not be modifying this

    @property
    def id(self) -> int:
        return self._id


def buildTree(points: list[tuple[int, Point]], left: int, right: int, axisval: Axis) -> TreeNode | None:
    """Build the KD Tree"""
    if left == right: #inclusive exclusive for easier slices
        return None
    mid = (left + right) // 2
    axis = axisval.value
    points[left:right] = sorted(points[left:right], key=lambda p: p[1][axis])  #sort at axis with max covariance
    root_node = TreeNode(points[mid][1], points[mid][0], axisval) 

    #assign children
    root_node.left = buildTree(points, left, mid, Axis(axisval.value ^ 1)) #left <= ind < mid
    root_node.right = buildTree(points, mid + 1, right, Axis(axisval.value ^ 1)) #mid + 1 <= ind < right

    return root_node

def distance_sq(p1: Point, p2: Point) -> float:
    return (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2

def search(root: TreeNode | None, query: Point, k: int, heapy: list[tuple[float, Point]], id: int) -> None:
    if root is None:
        return

    #find distance
    ref_point = root.point
    dist = distance_sq(ref_point, query)

    #update as necessary
    if root.id != id: #it cannot be the same point
        if len(heapy) < k: #python heaps are just lists ata
            heappush_max(heapy, (dist, ref_point))
        elif dist < heapy[0][0]:
            heappushpop_max(heapy, (dist, ref_point))

    #decide where to search
    axisval = root.axis.value
    dist_ax = query[axisval] - ref_point[axisval] 

    if dist_ax <= 0:
        near = root.left
        far = root.right
    else:
        far = root.left
        near = root.right

    #go through the nearest child
    search(near, query, k, heapy, id)

    #check if farther child is worth going through
    #note if x_i < x_rp < x_q so |x_rp - x_q|**2 <= |x_rp - x_i| ** 2 
    #so if maxdist <= dist_ax **2 <= |x_rp - x_i| ** 2  and the heap is full not worth checking
    if len(heapy) < k or (dist_ax) ** 2 <= heapy[0][0]: 
        search(far, query, k, heapy, id)


def KNNOne(root: TreeNode, query: Point, k: int, id: int) -> list[Point]:
    """Given a Point in a K-D Tree, find its K nearest neighbors excluding itself"""
    if k < 0:
        raise ValueError("no we are not corrupt we will not interpolate through nnegative number of points")

    if k == 0:
        return []

    heapy = [] #list of points

    heapify_max(heapy)

    search(root, query, k, heapy, id)

    return [i[1] for i in heapy] #note heap is list

def KNNAll(ipoints: list[Point], k: int) -> list[tuple[Point, list[Point]]]:
    """Given Points in a K-D Tree, find each point's K nearest neighbors excluding itself by building a KD Tree"""

    points = list(enumerate(ipoints))

    root = buildTree(points, 0, len(points), Axis.X)

    return [(points[i][1], KNNOne(root, points[i][1], k, i[0])) for i in range(len(points))]