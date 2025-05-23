<div align="center">

<p align="center">
    <img src="images/GraspIt banner.png" width="95%">
</p>

[🛠️ Installation](#get-started) |
[📚 Used references](#reference-papers) | 
[🎥 Cool GIFs](#demonstrations) |
[👨‍💻 Authors](#authors)

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
![Version](https://img.shields.io/badge/python_version-3.11-purple)
[![GitHub stars](https://img.shields.io/github/stars/jreivilo/lemanic_life_science_graspit.svg?style=social&label=Star)](https://github.com/jreivilo/lemanic_life_science_graspit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Generic badge](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

> Check out the [presentation](/presentation/GRASPIT-2025.pdf) for an overview of the project

# 📄 Description of the project
GraspIt is a Python-based software system designed to induce hand movements—specifically grasping—through Functional Electrical Stimulation (FES), without requiring voluntary muscle activation from the user. By applying electrical stimulation to targeted muscles, the system generates predefined movements in the arm.

To ensure accurate and adaptive control, Grasp It incorporates a closed-loop feedback mechanism using an infrared camera. The camera continuously tracks the position and orientation of the hand’s bones, allowing the system to compute joint angles and determine the current state of the grasp. This feedback is compared against a target position, enabling real-time adjustment of the stimulation to achieve or maintain the desired hand posture.

The key innovation lies in this integration of real-time visual tracking with closed-loop stimulation, allowing the system to dynamically compensate for noise, electrode misplacement, individual anatomical differences, or varying skin conditions.

The project is modular, structured into three main nodes:
- **stimulator**: This node receives processed sensor data and delivers precise electrical stimulation through selected electrode channels.
- **sensor**: This node captures and processes data from the infrared camera to calculate joint angles and assess hand posture.
- **commander**: This node listens for verbal cues such as "grasp" or "release" to trigger corresponding hand movements.

These nodes communicate through an MQTT server, which enables a decoupled architecture. This modularity not only enhances code clarity and maintainability but also supports parallel development by multiple contributors.

# 🛠️ Get started <a name="get-started"></a>
🐧 If you are on linux, you can run the `run.sh` script that will do all those steps for you and run everything.
- Install driver for the leap motion controller: `https://leap2.ultraleap.com/downloads/leap-motion-controller/`
- Make sure you have uv package manager installed https://docs.astral.sh/uv/getting-started/installation/
- Download the infrared camera python SDK: `git submodule update --init --recursive`
- Run `uv sync` to install all python packages
- Install a MQTT server with https://mosquitto.org/download/, and run the MQTT broker with the command `mosquitto`
- By default, the MQTT server URL is set to localhost, but you can change it with the environnement variable `MQTT_HOSTNAME` (for example "test.mosquitto.org").
- Then, run the 3 nodes in parallel
  - Run `uv run src/llsg/sensor/sensor.py` for the **sensor** node responsible to read data from the infrared camera
  - Run `uv run src/llsg/commander/commander.py` for the **commander** node responsible to listen to verbal cues
  - Run `uv run src/llsg/stimulator/stimulator.py` for the **stimulator** node responsible to send the electrical stimulation

## 🐳 Docker version (unstable)
Alternatively, you can run the complete software using docker.
- Make sure you have docker installed: https://docs.docker.com/engine/install/
- Go inside the docker directory with `cd docker`
- Run all the nodes with `docker compose up`. It will download everything that is necessary.

# 📦 Project structure
Here are the most important folder/files of the project  
```
├── leapc-python-bindings/ (submodule of the leap controller driver)
├── src/ (python source code)
│   └── llsg/
│       ├── sensor/ (code for the infrared camera)
│       ├── commander/ (code for the voice recognition)
│       └── stimulator/ (code for the controller and FES)
├── android-app/ (prototype of a mobile app)
└── run.sh/ (convinience script to run everyhing, linux only)
```

# 🧰 Hardware list

## 📷 Leap Motion Controller ~350$
Infrared camera sensor with software drivers to detect bones position and orientation in the hand.

<img src="images/Leap_Motion_Controller.jpg" width="250"/>

## 🔌 MotionStim 8 ~5000$ (very rough estimate !)
FES device (Functional Electrical Stimulation) to trigger and control specific muscle movements by transcutaneous stimulation.

<img src="images/MotionStim8.jpg" width="350"/>

# 📚 Reference papers <a name="reference-papers"></a>
We used those to learn more about the state of the art closed loop control of eletrical stimulation for hand grasping.
- Ciancibello, J., King, K., Meghrazi, M.A. et al. Closed-loop neuromuscular electrical stimulation using feedforward-feedback control and textile electrodes to regulate grasp force in quadriplegia. Bioelectron Med 5, 19 (2019). https://doi.org/10.1186/s42234-019-0034-y
- C. Lin et al., "Adaptive Closed-Loop Functional Electrical Stimulation System with Visual Feedback for Enhanced Grasping in Neurological Impairments," in IEEE Transactions on Medical Robotics and Bionics, doi: 10.1109/TMRB.2025.3557197. keywords: {Hands;Grasping;Iron;Muscles;Real-time systems;Electrical stimulation;Biomimetics;Monitoring;Medical robotics;Visualization;Neuromuscular Electrical Stimulation;Closed-Loop Control;Visual Perception;Finite State Machine}, 
- Le Guillou, R., Froger, J., Morin, M. et al. Specifications and functional impact of a self-triggered grasp neuroprosthesis developed to restore prehension in hemiparetic post-stroke subjects. BioMed Eng OnLine 23, 129 (2024). https://doi.org/10.1186/s12938-024-01323-y

# 🎥 Demonstrations <a name="demonstrations"></a>


<p align="center">
<img src="images/grasp.gif" width="400"/>
<img src="images/grasp_skeleton.gif" width="200"/>
</p>
<br/>
<p align="center">
<img src="images/release.gif" width="400"/>
<img src="images/release_skeleton.gif" width="200"/>
</p>


# 👨‍💻 Authors <a name="authors"></a>

GraspIt was initially developed during the [Lemanic Life Science Hackathon](https://web.archive.org/web/20250429112730/https://www.epfl.ch/schools/sv/lemanic-life-sciences-hackathon-2025/) 2025 at EPFL, Lausanne, Switzerland.

Participants:
- Johan BENJELLOUN
- Glodi DOMINGOS
- Julie KIEFFER
- Jérémy OLIVIER
- Arash SAL MOSLEHIAN
- Milo SANDERS
- Leandro SARAIVA MAIA
- Bianca ZILIOTTO

Mentor:
- Federico CIOTTI
