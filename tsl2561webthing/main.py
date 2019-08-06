from __future__ import division, print_function
from webthing import SingleThing, Property, Thing, Value, WebThingServer
import logging
import random
import tornado.ioloop
# TODO does one of these need to be try catch? for a decent log message
import board
import busio
import adafruit_tsl2561
# TODO replace with actual error
import socket


def get_sensor():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_tsl2561.TSL2561(i2c)
    return sensor

sensor = get_sensor()

class LuxSensor(Thing):
    """A lux sensor which updates its measurement every few seconds."""

    def __init__(self, poll_delay):
        Thing.__init__(
            self,
            "urn:dev:ops:tsl2561-lux-sensor",
            "TSL2561 Lux Sensor",
            ["MultiLevelSensor"],
            "A web connected light/lux sensor",
        )

        self.level = Value(0.0)
        self.add_property(
            Property(
                self,
                "level",
                self.level,
                metadata={
                    "@type": "LevelProperty",
                    "title": "Lux",
                    "type": "number",
                    "description": "The current light in lux",
                    "minimum": 0,
                    "maximum": 1000,  # apparently 1000 is an Overcast day; typical TV studio lighting
                    "unit": "lux",
                    "readOnly": True,
                },
            )
        )

        logging.debug("starting the sensor update looping task")
        self.timer = tornado.ioloop.PeriodicCallback(self.update_level, poll_delay)
        self.timer.start()

    def update_level(self):

        try:
            new_level = self.read_from_i2c()
            logging.debug("setting new humidity level: %s", new_level)
            self.level.notify_of_external_update(new_level)
        except: socket.error:  # TODO update to appropriate IO error
            logging.error("failed to read a lux value from sensor")

    def cancel_update_level_task(self):
        self.timer.stop()

    @staticmethod
    def read_from_i2c():
        """Mimic an actual sensor updating its reading every couple seconds."""
        return sensor.lux or 0


def run_server(port=8888, poll_delay=3.0):

    sensor = LuxSensor(poll_delay=poll_delay)

    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(SingleThing(sensor), port=port)
    try:
        logging.info("starting the server")
        server.start()
    except KeyboardInterrupt:
        logging.debug("cancelling the sensor update looping task")
        sensor.cancel_update_level_task()
        logging.info("stopping the server")
        server.stop()
        logging.info("done")


if __name__ == "__main__":
    logging.basicConfig(
        level=10, format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()
