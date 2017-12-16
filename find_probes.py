# Import all the libraries we need to run
import sys
import logging
import RPi.GPIO as GPIO
import Adafruit_DHT
from config import *

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

possible_pins = {2:[2,3,4,7,8,9,10,11,14,15,17,18,22,23,24,25,27]}
sensor_types = (Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, Adafruit_DHT.AM2302)

logger = logging.getLogger('find_probes')
logging.basicConfig(filename='bee_config.log',level=logging.INFO)


def find():
    used_pins = []
    probes = []
    seconds = len(sensor_types) * len(possible_pins[GPIO.RPI_REVISION])

    msg = "starting... be patient this will take about {} seconds".format(seconds)
    logger.info(msg)
    print(msg)

# Scan for active pins
    for pin in possible_pins[GPIO.RPI_REVISION]:
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        h, t = Adafruit_DHT.read_retry(sensor_types[0], pin, retries=3)
        if h is not None and t is not None:
# if h is valid then add values to probe, don't add pin to used_pins
            if h > 2.0 and h < 101.0:
                probes.append({'sensor': sensor_types[0], 'pin': pin,
                                'outdoor': False})
                msg = "Found for {} on pin, {}".format(sensor_types[0], pin)
                logger.info(msg)
                print(msg)
            else:
                msg = "Found something on pin, {}".format(pin)
                logger.info(msg)
                print(msg)
                used_pins.append(pin)
        else:
            msg = "Nothing found for {} on pin, {}".format(
                sensor_types[0], pin)
            logger.info(msg)
            print(msg)
        GPIO.cleanup(pin)

    for sensor in sensor_types[2:]:
        for pin in used_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            h, t = Adafruit_DHT.read_retry(sensor, pin, retries=3)
            if h is not None:
                if h > 2.0 and h < 101.0:
                    probes.append({'sensor': sensor, 'pin': pin, 'outdoor': False})
                    used_pins.remove(pin)
                    msg = "Found for {} on pin, {}".format(sensor, pin)
                    logger.info(msg)
                    print(msg)
                else:
                    msg = "Found something on pin, {}".format(pin)
                    logger.info(msg)
                    print(msg)
            else:
                msg = "Nothing found for {} on pin, {}".format(sensor,pin)
                logger.info(msg)
                print(msg)

            GPIO.cleanup(pin)

    return probes


if __name__ == '__main__':
    data = loadConfig('config.json')
    data['probes'] = find()
    writeConfig(data, 'config.json')
