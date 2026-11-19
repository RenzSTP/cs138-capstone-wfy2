"""Spatiotemporal Inverse Distance Weighting (IDW) over a 3D k-d tree.

Implements the spatiotemporal IDW formulation of Li et al. (2014) and
querying nearest neighbors via Elliot's implementation in knearestneighbors.py.
"""

import math

from dataclasses import dataclass
from knearestneighbors import Axis, TreeNode, buildTree, nearest_neighbors


@dataclass(frozen=True)
class SpatiotemporalPoint:
    """Air-quality observatoin at some position and time"""
    id: int
    station_id: int
    x: float
    y: float
    t: float
    w_i: float  # the actual pm2.5 concentration

    @property
    def pm25(self) -> float:
        return self.w_i


def build_spatiotemporal_tree(st_points: list[SpatiotemporalPoint], c: float) -> tuple[TreeNode | None, dict[int, float]]:
    """Build a 3D k-d tree over (x, y, c * t) and return the (root, pm25s)"""
    if c <= 0:
        raise ValueError("Scaling factor c must be positive.")

    tree_points = [
        (stp.id, (stp.x, stp.y, c * stp.t))
        for stp in st_points
    ]

    pm25s = {stp.id: stp.pm25 for stp in st_points}  # for easier access
    root = buildTree(tree_points, 0, len(tree_points), Axis.X, dims=3)

    return (root, pm25s)


def compute_station_weights(distances: list[float], p: float) -> list[float]:
    """Calculate station weights using the inverse distance power law formula."""
    numer = [(1 / d_i) ** p for d_i in distances]
    denom = sum(numer)

    return [num / denom for num in numer]


def get_concentration(
    root: TreeNode | None,
    pm25s: dict[int, float],
    x: float,
    y: float,
    t: float,
    c: float,
    N: int = 5,  # how many neighbors
    p: float = 2.0,
    exclude_id: int | None = None,
    ) -> float:
    """Estimate pollution concentration w(x, y, ct)
    
    """
    # for querying the k-nearest st points
    neighbors = nearest_neighbors(
        root, 
        query=(x, y, c * t),
        k=N,
        exclude_id=exclude_id,
    )

    if not neighbors:
        # not sure yet what value it should be
        print("No neighbors, or k = 0")
        return pm25s[root.id]       # this just returns the exact PM2.5 value at root

    # for exact space-time matches, where the distance is close to 0 to avoid div/zero
    w_exact = [pm25s[nei.id] for nei in neighbors if nei.distance_sq <= 1e-18]

    if w_exact:
        return sum(w_exact) / len(w_exact)

    distances = [math.sqrt(nei.distance_sq) for nei in neighbors]

    # station weight lambda_i
    lambdas = compute_station_weights(distances, p)
    # concentration w_i
    ws = [pm25s[nei.id] for nei in neighbors]

    return sum(lambda_i * w_i for lambda_i, w_i in zip(lambdas, ws))