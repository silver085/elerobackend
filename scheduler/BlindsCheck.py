import threading
import time

import schedule

from controllers.blind_controller import BlindController
from services.service_radio import RadioService


class BlindsCheckerSchedule:
    radio_service: RadioService
    blind_controller: BlindController

    def __init__(self):
        schedule.every(10).seconds.do(self.scheduled_task)
        self.thread = threading.Thread(target=self.loop_task)

    def loop_task(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_looping(self):
        if self.thread:
            self.thread.start()

    def scheduled_task(self):
        print("Check blind task")
        blinds_rows = self.blind_controller.get_all_blinds()
        for blind in blinds_rows:
            if not blind.is_in_discovery:
                print(f"Checking blind {blind.id}")
                self.radio_service.send_check_signal(channel=blind.channel, remote_id=blind.remote_id, blind_id=blind.id)
