# !/usr/bin/python

import logging
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Dummy Log to get debug logs to work windows
logging.info('Dummy')

SHORT_NORMALIZE = (1.0 / 32768.0)
ROLLING_AVERAGE_LIMIT = 10

from threading import Thread


class NoiseChecker(Thread):
    """
    Loop on listen and store the sound amplitude in a rolling average
    """

    def __init__(self):
        super().__init__()
        self.listen = True
        self.pa = pyaudio.PyAudio()

        import collections
        self.deque = collections.deque([], ROLLING_AVERAGE_LIMIT)

    def get_average(self):
        average = 0

        for sample in self.deque:
            average += sample

        return average / ROLLING_AVERAGE_LIMIT

    def run(self):
        from noisechecker.util import find_input_device

        device_index = find_input_device(self.pa)
        stream = self.pa.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              input=True,
                              input_device_index=device_index,
                              frames_per_buffer=CHUNK)

        while self.listen:
            data = stream.read(CHUNK)
            noise = self.get_rms(data)

            self.deque.append(noise)
            logger.debug("{0:.3f}".format(noise))

        stream.close()
        self.pa.close()

    @staticmethod
    def get_rms(data):
        # RMS amplitude is defined as the square root of the
        # mean over time of the square of the amplitude.
        # so we need to convert this string of bytes into
        # a string of 16-bit samples...

        # we will get one short out for each
        # two chars in the string.
        count = len(data) / 2
        fmt = "%dh" % count
        import struct

        shorts = struct.unpack(fmt, data)

        # iterate over the block.
        sum_squares = 0.0
        for sample in shorts:
            # sample is a signed short in +/- 32768.
            # normalize it to 1.0
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n

        import math
        return math.sqrt(sum_squares / count)



def start_and_monitor():
    noise_checker = NoiseChecker()
    noise_checker.start()

    class NoisePrinter(Thread):
        def run(self):
            while True:
                from time import sleep
                sleep(1)
                average = noise_checker.get_average()
                logger.info("{0:.3f}".format(average))

    NoisePrinter().start()

if __name__ == "__main__":
    start_and_monitor()