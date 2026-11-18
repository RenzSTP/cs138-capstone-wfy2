from enum import Enum

DIMS = 2 #make constants large

type Point = tuple[float, float]

class Axis(Enum):
    X = 0
    Y = 1


#KD tree node
class TreeNode:
    def __init__(self, point: Point, axis: Axis):
        self._point: Point = point #not changeable
        self.left: TreeNode | None = None
        self.right: TreeNode | None = None
        self._axis: Axis = axis

    @property
    def point(self) -> Point:
        return self._point #we will not be modifying this

    @property
    def axis(self) -> Point:
        return self._axis #we will not be modifying this


def buildTree(points: list[Point], left: int, right: int, axisval: Axis) -> TreeNode | None:
    """Build the KD Tree"""
    if left == right: #inclusive exclusive for easier slices
        return None
    mid = (left + right) / 2
    axis = axisval.value
    points[left:right].sort(), lambda p: p[axis] #sort at axis with max covariance
    root_node = TreeNode(points[mid], axis) #lazy stuff initialized already

    #assign children
    root_node.left = buildTree(points, left, mid, Axis(axisval.value ^ 1)) #left <= ind < mid
    root_node.right = buildTree(points, mid + 1, right, Axis(axisval.value ^ 1)) #mid + 1 <= ind < right

    #propagate
    root_node.tree_size = root_node.left.tree_size + root_node.right.tree_size

    return root_node
            
        