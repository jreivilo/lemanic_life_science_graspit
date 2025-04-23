from typing import TypedDict
import numpy as np

class HandPose(TypedDict):
    timestamp_ms: int
    grasp_angle: float
    # wrist_orientation: np.array
    # digits: list[list[np.array]]
