import queue
import random
import threading
import uuid
from time import sleep


# [Step 1]
class Provider:
    def __init__(self, ip, capacity):
        self.provider_status_report = None
        self.result_function = None
        self.ip = ip
        self.id = uuid.uuid4()
        self.capacity = capacity
        self.incoming_queue = queue.Queue(maxsize=self.capacity)
        self.queue_counter = 0
        self.provider_responsive = True  # Simulating if the provider alive or not

    def get(self, request_id):
        if self.provider_responsive:
            print(request_id)
            self.incoming_queue.put(request_id)
            self.queue_counter += 1
            if self.queue_counter >= self.capacity:
                print("provider queue full")
                self.self_check(False)
            if self.incoming_queue.empty():
                self.self_check(True)
            calculate = threading.Thread(target=self.calculate_result, daemon=True)
            calculate.start()

    def get_provider_info(self):
        provider_info = {
            "id": self.id,
            "ip": self.ip,
            "capacity": self.capacity
        }
        return provider_info

    def connection_set(self, provider_status, result_function):
        self.provider_status_report = provider_status
        self.result_function = result_function

    def self_check(self, status):
        self.provider_status_report(self.id, status, "status")

    def calculate_result(self):
        request_id = self.incoming_queue.get()
        number = random.randint(1, 101)
        sleep(number / 10)
        result = {request_id: {
            "provider_id": self.id,
            "result": number
        }}
        self.queue_counter -= 1
        self.incoming_queue.task_done()
        self.result_function(result)
        if self.queue_counter <= 0:
            print("provider queue empty\n")
            self.self_check(True)

    # For simulation
    def set_provider_responsive(self, status):
        # 'status is bool' return false even if 'status' is True or False
        if status is True or status is False:
            self.provider_responsive = status
        else:
            return "Given status variable is not a boolean."

    def check(self):
        if self.provider_responsive:
            return True
        else:
            # show provider as non-responsive
            sleep(10)
