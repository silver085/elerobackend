from datetime import datetime

from controllers.blind_controller import BlindController
from models.blind import Blind
from services.service_radio import RadioService


class BlindsCheckerSchedule:
    radio_service: RadioService
    blind_controller: BlindController

    def check_blind_offline(self, blind: Blind):
        last_blind_ping = blind.last_ping
        if last_blind_ping is None: last_blind_ping = blind.date_added
        diff = datetime.utcnow() - last_blind_ping
        print(f"Difference is {diff.seconds}")
        if diff.seconds > 1800:
            # blind is probably offline
            self.blind_controller.put_blind_offline(blind_id=blind.id)
            print(f"Blind {blind.id} didn't respond to ping for more than 30 min, putting offline.")

    def ping_blinds(self):
        print("Check blind task")
        try:
            blinds_rows = self.blind_controller.get_all_blinds()
            for blind in blinds_rows:
                if not blind.is_in_discovery:
                    print(f"Checking blind {blind.id}")

                    self.check_blind_offline(blind)
                    self.radio_service.send_check_signal(channel=blind.channel, remote_id=blind.remote_id,
                                                         blind_id=blind.id)
                else:
                    self.radio_service.send_check_signal(channel=blind.channel, remote_id=blind.remote_id,
                                                         blind_id=blind.id)
        except RuntimeError as e:
            print(f"An exception was raised in blinds_check: {e}")
