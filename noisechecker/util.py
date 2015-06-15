__author__ = 'Ciaran'

import logging
logger = logging.getLogger(__name__)


def find_input_device(pa):
    """
    Attempt to find a recording device and bind to it
    :type  pyaudio.PyAudio pa:
    :return:
    """

    device_index = None
    for i in range(pa.get_device_count()):
        dev_info = pa.get_device_info_by_index(i)
        logger.debug("Device %d: %s" % (i, dev_info["name"]))

        for keyword in ["mic", "input"]:
            if keyword in dev_info["name"].lower():
                logger.debug("Found an input: device %d - %s" % (i, dev_info["name"]))
                device_index = i
                return device_index

    if not device_index:
        logger.debug("No preferred input found; using default input device.")

    return device_index
