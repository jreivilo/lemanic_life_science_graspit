from typing import TypedDict

import numpy as np


class HandPose(TypedDict):
    timestamp: int
    grasp_angle: float
    # digits: list[list[np.array]]
