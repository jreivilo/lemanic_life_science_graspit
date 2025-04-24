<p align="center">
    <img src="images/GraspIt banner.png" width="95%">
</p>

[🛠️ Installation](#get-started) |
[📝 Used references](#reference-papers) | 
[💡 Demonstrations](#demonstrations) |

[![GitHub stars](https://img.shields.io/github/stars/jreivilo/lemanic_life_science_graspit.svg?style=social&label=Star)](https://github.com/jreivilo/lemanic_life_science_graspit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Description of the project
Grasp It is a Python-based software system designed to induce hand movements—specifically grasping—through Functional Electrical Stimulation (FES), without requiring voluntary muscle activation from the user. By applying electrical stimulation to targeted muscles, the system generates predefined movements in the arm.

To ensure accurate and adaptive control, Grasp It incorporates a closed-loop feedback mechanism using an infrared camera. The camera continuously tracks the position and orientation of the hand’s bones, allowing the system to compute joint angles and determine the current state of the grasp. This feedback is compared against a target position, enabling real-time adjustment of the stimulation to achieve or maintain the desired hand posture.

The key innovation lies in this integration of real-time visual tracking with closed-loop stimulation, allowing the system to dynamically compensate for noise, electrode misplacement, individual anatomical differences, or varying skin conditions.

The project is modular, structured into three main nodes:
- **stimulator**: This node receives processed sensor data and delivers precise electrical stimulation through selected electrode channels.
- **sensor**: This node captures and processes data from the infrared camera to calculate joint angles and assess hand posture.
- **commander**: This node listens for verbal cues such as "grasp" or "release" to trigger corresponding hand movements.

These nodes communicate through an MQTT server, which enables a decoupled architecture. This modularity not only enhances code clarity and maintainability but also supports parallel development by multiple contributors.

# Get started
- Install driver for the leap motion controller: `https://leap2.ultraleap.com/downloads/leap-motion-controller/`
- Make sure you have uv package manager installed https://docs.astral.sh/uv/getting-started/installation/
- Download the infrared camera python SDK: `git submodule update --init --recursive`
- Run `uv sync` to install all python packages
- The 3 nodes must be run in parallel
  - Run `uv run src/llsg/sensor/sensor.py` for the **sensor** node responsible to read data from the infrared camera
  - Run `uv run src/llsg/commander/audio.py` for the **commander** node responsible to listen to verbal cues
  - Run `uv run src/llsg/stimulator/stimulator.py` for the **stimulator** node responsible to send the electrical stimulation

# Hardware list
- Leap Motion Controller, an infrared camera sensor.
- MotionStim 8, a device used for FES (Functional Electrical Stimulation).

# Reference papers
We used those to learn more about the state of the art closed loop control of eletrical stimulation for hand grasping.
- TODO

# Demonstrations
TODO add cool gifs
