import queue
from collections import OrderedDict

from provider import Provider


class LoadBalancer:
    def __init__(self, number_of_providers=10):
        self.queue_size = 0
        self.actual_queue = 0
        self.result_queue = queue.Queue()
        self.provider_list = OrderedDict()
        self.number_of_providers = number_of_providers
        self.position = 0

    def get(self, request_id):
        if not self.provider_list:
            print("Provider list empty, add a provider first.")
            return "No provider."
        elif self.actual_queue >= self.queue_size:
            print("Queue full.")
            return "Queue full."
        else:
            next_provider_id = self.find_next_available_provider()
            if not next_provider_id:
                print("All provider busy.")
                return request_id
            else:
                provider = self.provider_list[next_provider_id]["provider"]
                provider.get(request_id)

    def find_next_available_provider(self):
        check_turn = 0
        start_position = self.position
        provider_keys_list = list(self.provider_list.keys())
        while check_turn < 3:
            provider_id = provider_keys_list[self.position]
            if self.provider_list[provider_id]["status"] and self.provider_list[provider_id]["active"]:
                return provider_id
            self.position += 1
            if len(self.provider_list) - 1 < self.position:
                self.position = 0
            if start_position == self.position:
                check_turn += 1
        print("No active and/or free provider found in 3 full check.")
        return False

    # Check the input type (list or simple provider)
    def register_provider(self, provider_registree):
        if type(provider_registree) == Provider:
            self.add_provider(provider_registree)
        else:
            for provider in provider_registree:
                self.add_provider(provider)

    def add_provider(self, provider):
        provider_info = provider.get_provider_info()
        provider_id = provider_info["id"]
        provider_ip = provider_info["ip"]
        provider_capacity = provider_info["capacity"]
        if provider_id in self.provider_list:
            print("Provider already in the list.")
        elif len(self.provider_list) >= self.number_of_providers:
            print("Provider list full, cannot ad more.")
        else:
            provider.connection_set(self.provider_stat_change, self.add_result_to_queue)
            self.provider_list[provider_id] = {
                "provider": provider,
                "ip": provider_ip,
                "status": True,
                "active": True,
                "capacity": provider_capacity
            }
            self.queue_size += provider_capacity
            print("Provider added. Id: {id}".format(id=provider_id))

    def remove_provider(self, provider):
        provider_info = provider.get_info()
        provider_id = provider_info["id"]
        provider_capacity = provider_info["capacity"]
        if provider_id not in self.provider_list:
            print("Provider not found in the list. Nothing to remove.")
        else:
            self.provider_list.pop(provider_id)
            self.queue_size -= provider_capacity
            print("Provider removed from the provider list.\nRemoved provider Id: {id}".format(id=provider_id))

    def provider_stat_change(self, provider_id, provider_status, stat):
        # find provider by Id in provider dict and set availability to status
        self.provider_list[provider_id][stat] = provider_status

    def change_provider_activity(self, provider):
        provider_info = provider.get_info()
        provider_id = provider_info["id"]
        if provider_id not in self.provider_list:
            print("Provider not found in the list. Nothing to change.")
        else:
            provider_capacity = provider_info["capacity"]
            provider_activity = self.provider_list[provider_id]["active"]
            if provider_activity:
                self.queue_size -= provider_capacity
            else:
                self.queue_size += provider_capacity
            self.provider_stat_change(provider_id, not provider_activity, "active")

    def add_result_to_queue(self, result):
        self.result_queue.put(result)

    def get_result(self):
        try:
            result = self.result_queue.get(timeout=1)
            print(result)
            return result
        except queue.Empty:
            return None
