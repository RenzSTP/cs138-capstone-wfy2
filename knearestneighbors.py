from enum import Enum

DIMS = 2 #make constants large

type Point = tuple[int, int]

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
        self._deleted = deleted