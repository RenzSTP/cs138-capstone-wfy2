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
        self._deleted: bool = False
        self._tree_deleted: bool = False #well no subtree under
        self._pushdown: bool = False #check whether to push down to sons
        self.invalid_num: int = 0 #num invalids marked deleted on subtree
        self.tree_size: int = 1 #num subtree
        self.x_range: list[int] = [point[0], point[0]] 
        self.y_range: list[int] = [point[1], point[1]]

    @property
    def point(self) -> Point:
        return self._point #we will not be modifying this

    @property
    def axis(self) -> Point:
        return self._axis #we will not be modifying this

    @property

    def deleted(self):
        return self._deleted
    
    @deleted.setter
    def deleted(self, deleted: bool):
        self._deleted = deleted #lazy delete

    @property
    
    def tree_deleted(self):
        return self._tree_deleted
        
    @tree_deleted.setter
    def tree_deleted(self, tree_deleted: bool):
        self._tree_deleted = tree_deleted #lazy delete

    @property
        
    def pushdown(self):
        return self._pushdown
            
    @pushdown.setter
    def pushdown(self, pushdown: bool):
        self._pushdown = pushdown #lazy delete


def compute_variance(points: list[Point], numpoints: int, axis: Axis) -> float:
    """Given a list of points and their axis compute the variance across the axis"""
    a_mean = sum(point[axis.value] for point in points) / numpoints
    a_variance = sum((point[axis.value] - a_mean) ** 2 for point in points) / numpoints
    return a_variance

def max_axis_variance(points: list[Point], numpoints: int) -> Axis:
    """Given a list of points, find the axis where the values at that axis has most variance"""
    var_x = compute_variance(points, numpoints, Axis.X)
    var_y = compute_variance(points, numpoints, Axis.Y)
    if (var_x < var_y):
        return var_y
    else:
        return var_x

def buildTree(points: list[Point], left: int, right: int) -> TreeNode | None:
    """Build the Original Node Tree"""
    if left == right: #inclusive exclusive for easier slices
        return None
    mid = (left + right) / 2
    axis = max_axis_variance(points, left, right)
    points[left:right].sort(), lambda p: p[axis.value] #sort at axis with max covariance
    root_node = TreeNode(points[mid], axis) #lazy stuff initialized already

    #assign children
    root_node.left = buildTree(points, left, mid) #left <= ind < mid
    root_node.right = buildTree(points, mid + 1, right) #mid + 1 <= ind < right

    #propagate
    root_node.tree_size = root_node.left.tree_size + root_node.right.tree_size
    root_node.x_range = [min(root_node.left.x_range[0], root_node.right.x_range[0]), max(root_node.left.x_range[1], root_node.right.x_range[1])]
    root_node.y_range = [min(root_node.left.y_range[0], root_node.right.y_range[0]), max(root_node.left.y_range[1], root_node.right.y_range[1])]

    return root_node