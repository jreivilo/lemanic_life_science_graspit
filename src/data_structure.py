from typing import TypedDict
import numpy as np

class HandPose(TypedDict):
    timestamp_ms: int
    grasp_angle: float
    # digits: list[list[np.array]]
