import time

from controllers.config_controller import ConfigController
from drivers.cc1101 import CC1101
from models.config import Config
import threading


class RadioService:
    configuration: Config
    radio: CC1101

    def __init__(self, config_controller: ConfigController):
        self.config_controller = config_controller
        self.configuration = self.config_controller.config_repo.get_configuration()
        self.radio = CC1101(
            spibus=self.configuration.spibus,
            spics=self.configuration.spics,
            speed=self.configuration.speed,
            gdo0=self.configuration.gdo0,
            gdo2=self.configuration.gdo2
        )
        self.radio_task = None

    def start_looping(self):
        if self.radio:
            self.radio_task = threading.Thread(target=self.loop_radio)
        else:
            raise RuntimeError("Radio not initialised.")

    def loop_radio(self):
        while True:
            data = self.radio.checkBuffer()
            if data:
                print(f"Radio data debug: {data}")

            time.sleep(0.005)
