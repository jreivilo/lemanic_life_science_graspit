import time
import llsg.driver as fes
from llsg import logger
import llsg.config as config

class Stimulator():

    def __init__(self):
        self.stim: fes.Motionstim8 = fes.Motionstim8()
        self.stim.OpenSerialPort(config.SERIAL_PORT)
        self.stim.InitializeChannelListMode()
        logger.info('Opened FES serial port')
    
    def __del__(self):
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)
        self.stim.CloseSerialPort()
        logger.info('Closed FES serial port')

    def stimulate(self):
        stim_code = [0, 10, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)
        logger.info('FES: Sent Left')
        time.sleep(1)
        stim_code = [0, 0, 0, 0, 0, 0, 0, 0]
        self.stim.UpdateChannelSettings(stim_code)

if __name__ == '__main__':

    logger.info('Starting FES stimulation example')
    # Initialize the FES device
    stimulator = Stimulator()
    # Start the stimulation
    stimulator.stimulate() 

    del stimulator