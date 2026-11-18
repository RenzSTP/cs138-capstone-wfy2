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
        self._treedeleted: bool = False #well no subtree under
        self._pushdown: bool = False #check whether to push down to sons
        self.invalidnum: int = 0 #num invalids marked deleted on subtree
        self.treesize: int = 1 #num subtree
        self.xrange: list[int] = [point[0], point[0]] 
        self.xrange: list[int] = [point[1], point[1]]

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
    
    def treedeleted(self):
        return self._treedeleted
        
    @treedeleted.setter
    def treedeleted(self, treedeleted: bool):
        self._treedeleted = treedeleted #lazy delete

    @property
        
    def pushdown(self):
        return self._pushdown
            
    @pushdown.setter
    def pushdown(self, pushdown: bool):
        self._pushdown = pushdown #lazy delete
