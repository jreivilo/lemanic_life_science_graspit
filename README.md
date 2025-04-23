# Get started
* Install driver for the leap motion controller: `https://leap2.ultraleap.com/downloads/leap-motion-controller/`
* Make sure you have uv package manager install https://docs.astral.sh/uv/getting-started/installation/
* Download the infrared camera python SDK: `git submodule update --init --recursive`
* Run `uv sync` to install all python packages
* Our software is composed of 3 nodes
    * The infrared camera sensor. Run it with `uv run src/llsg/sensor/sensor.py`
    * The vocal detection. Run it with `uv run src/llsg/commander/vocal.py`
    * The stimulator to send current commands to the FES. Run it with `uv run src/llsg/stimulator/stimulator.py`

# Hardware list
* Leap Motion Controller
* FES

# Presentation

You can find the project presentation [here](https://docs.google.com/presentation/d/1YEtW47rBTa9S73A4l6LQ9Tdh1YrbPj_eL7_1DmbkJ4Q/edit?usp=sharing).