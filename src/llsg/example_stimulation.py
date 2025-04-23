from __future__ import print_function, division
import llsg.utils.time as qc
import cv2
import numpy as np
import time
import serial
import serial.tools.list_ports
import llsg.driver as fes
from llsg import logger

if __name__ == '__main__':
    # Initialize the FES device
    fes_device = fes.Motionstim8()

    # Open the serial port
    fes_device.OpenSerialPort('COM3')

    # Set the stimulation frequency
    fes_device.SetStimulationFrequency(20)

    # Set the pulse width and amplitude for each channel
    for i in range(fes_device.nChannels):
        fes_device.SetPulseWidth(i, 300)
        fes_device.SetAmplitude(i, 0)

    # Start stimulation
    fes_device.StartStimulation()

    # Wait for a while to observe the stimulation
    time.sleep(10)

    # Stop stimulation
    fes_device.StopStimulation()

    # Close the serial port
    fes_device.CloseSerialPort()