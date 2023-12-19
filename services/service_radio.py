import time

from controllers.config_controller import ConfigController
from drivers.cc1101 import CC1101
from drivers.eleroProtocol import EleroProtocol
from models.config import Config
import threading

from utils.printutils import hex_int_to_str, hex_array_to_str, hex_n_array_to_str


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
        self.radio_task = threading.Thread(target=self.loop_radio)
        self.elero = EleroProtocol()

    def start_looping(self):
        if self.radio:
            self.radio_task.start()
        else:
            raise RuntimeError("Radio not initialised.")

    def stop_looping(self):
        if self.radio_task:
            self.radio_task.join()

    def loop_radio(self):
        print("Radio initialized.")
        while True:
            data = self.radio.checkBuffer()
            if data:

                try:
                    (length, cnt, typ, chl, src, bwd, fwd, dests, payload, rssi, lqi, crc) = self.elero.interpretMsg(
                        data)
                    print(
                        f"RP-> len: {length} cnt: {cnt} typ: {hex_int_to_str(typ)} chl: {hex_int_to_str(chl)} src: {hex_array_to_str(src)} bwd: {hex_array_to_str(bwd)} fwd: {hex_array_to_str(fwd)} dests: {hex_n_array_to_str(dests)} payload: {hex_array_to_str(payload)} rssi: {rssi} lqi: {lqi} crc: {crc}")

                except Exception as e:
                    print(f"Exception during radio message decode: {e}")
            time.sleep(0.005)

