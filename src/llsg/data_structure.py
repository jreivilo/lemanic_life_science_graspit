import numpy as np
from dataclasses import dataclass

@dataclass
class HandPose:
    timestamp_ms: int
    grasp_angle: float
    # wrist_orientation: np.array
    # digits: list[list[np.array]]
