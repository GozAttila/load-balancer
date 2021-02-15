import threading
import queue
import random
from colorama import Fore, Style
from threading import Thread
from multiprocessing import Pool
from collections import OrderedDict
from time import sleep

from provider import Provider


# From https://cyruslab.net/2020/02/10/pythoncapture-return-values-after-threads-are-finished/
# For returning value from Thread. Advanced Round Robin [Step 5+]
class LBThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._return = None  # child class's variable, not available in parent.

    def run(self):
        """
        The original run method does not return value after self._target is run.
        This child class added a return value.
        :return:
        """
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args, **kwargs):
        """
        Join normally like the parent class, but added a return value which
        the parent class join method does not have.
        """
        super().join(*args, **kwargs)
        return self._return


# TODO: lock round robin adv while heartbeat is running
# TODO: def(provider, property) -> return result


class LoadBalancer:
    def __init__(self):
        self.provider_list = OrderedDict()
        self.robin_counter = -1
        self.robin_adv_counter = -1
        self.heartbeat_interval = 1
        self.heartbeat_timer()
        self.max_robin_queue = 0
        self.robin_queue = queue.Queue(maxsize=self.max_robin_queue)

    # Only one get function should be here without 'get_type' arg and without _temp variables (for printing only).
    def get(self, get_type):
        if get_type == "random":
            random_temp = self.random_invoker()
            print("random get", random_temp)
            return random_temp
        elif get_type == "robin":
            robin_temp = self.round_robin_invoker()
            print("robin get", robin_temp)
            return robin_temp
        elif get_type == "robin_adv":
            adv_robin_temp = self.round_robin_adv_invoker()
            print("robin get adv", adv_robin_temp)
            return adv_robin_temp

    # TODO: just for test, delete it. It is used on the main.py for test reasons
    def prov_list(self):
        for item in self.provider_list:
            print(item, self.provider_list[item])
        print("max queue", self.max_robin_queue)

    # Check the input type (list or simple provider)
    def register_provider(self, provider_elem):
        if type(provider_elem) == Provider:
            self.add_provider(provider_elem)
        else:
            for prov in provider_elem:
                self.add_provider(prov)

    # Add the provider to provider list of the load balancer. [Step 2]
    def add_provider(self, provider_elem):
        if provider_elem.get() in self.provider_list:
            print("Provider already in the list.")
        else:
            if len(self.provider_list) >= 10:
                print("Provider list full, cannot ad more.")
            else:
                if provider_elem.check():
                    status = "Active"
                else:
                    status = "Busy"

                self.provider_list[provider_elem.get()] = {
                    "provider": provider_elem,
                    "ip": provider_elem.get_ip(),
                    "status": status,
                    "active": True,
                    "capacity": provider_elem.get_capacity()
                }
                self.max_robin_queue += provider_elem.get_capacity()
                print("Provider added. Id: {prov}".format(prov=provider_elem.get()))

    # Remove the provider from the provider list.
    def remove_provider(self, provider_elem):
        if provider_elem.get() not in self.provider_list:
            print("Provider not found in the list. Nothing to remove.")
        else:
            self.provider_list.pop(provider_elem.get())
            self.max_robin_queue -= provider_elem.get_capacity()
            print("Provider removed from the provider list.\nRemoved provider Id: {prov}".format(
                prov=provider_elem.get()))

    # Change the activity of a provider (exclusion/inclusion from/to balancer) [Step 5]
    def flip_provider_activity(self, provider_elem):
        if provider_elem.get() not in self.provider_list:
            print("Provider not found in the list. Nothing to change.")
        else:
            if self.provider_list[provider_elem.get()]["active"]:
                self.max_robin_queue -= provider_elem.get_capacity()
            else:
                self.max_robin_queue += provider_elem.get_capacity()
            self.provider_list[provider_elem.get()]["active"] = not self.provider_list[provider_elem.get()]["active"]

    def is_provider_list_empty(self):
        # If/when we don't want to send any comment out of empty provider list, this function is not necessary
        # In the invocations we can replace the function calling with 'if self.provider_list'
        if not self.provider_list:
            print("Provider list empty, add a provider first.")
            return True
        else:
            return False

    # [Step 3] Random invocation
    def random_invoker(self):
        if not self.is_provider_list_empty():
            # return self.provider_list[random.choice(list(self.provider_list.keys()))]["provider"].get()
            # Ip in print is much more followable than Id
            return self.provider_list[random.choice(list(self.provider_list.keys()))]["provider"].get_ip()
        return None

    # [Step 4] Round Robin invocation
    def round_robin_invoker(self):
        if not self.is_provider_list_empty():
            self.robin_counter += 1
            if len(self.provider_list) - 1 < self.robin_counter:
                self.robin_counter = 0
            next_provider_id = list(self.provider_list.keys())[self.robin_counter]
            # return self.provider_list[next_provider_id]["provider"].get()
            # Ip in print is much more followable(readable) than Id
            return self.provider_list[next_provider_id]["provider"].get_ip()

    # [Step 5+] Advanced Round Robin. Get the next available and free provider from the list.
    def active_provider(self, req_type):
        turn = 0
        start = self.robin_adv_counter
        turn_check = self.robin_adv_counter
        while turn < 3:
            self.robin_adv_counter += 1
            if len(self.provider_list) - 1 < self.robin_adv_counter:
                self.robin_adv_counter = 0
            next_provider_id = list(self.provider_list.keys())[self.robin_adv_counter]
            provider_elem = self.provider_list[next_provider_id]
            if provider_elem["status"] == "Active" and provider_elem["active"]:
                if req_type == "check":
                    self.robin_adv_counter = start
                    return True
                elif req_type == "target":
                    return provider_elem["provider"]
            if self.robin_adv_counter == turn_check:
                turn += 1
            if turn_check == -1:
                turn_check = 0
        print("No active and free provider in 3 full check")
        return False

    # [Step 5+] Advanced Round Robin with Thread and Queue with sequential stepping
    # [Step 8] Include max capacity check
    def round_robin_adv_invoker(self):
        if not self.is_provider_list_empty():
            if self.active_provider("check"):
                if not self.robin_queue.full():
                    t = LBThread(target=self.round_robin_adv, daemon=True)
                    t.start()
                    self.robin_queue.put(self.active_provider("target").get_ip())
                    return t.join()
                else:
                    print(Fore.RED + "Queue is full" + Style.RESET_ALL)
                    return "Queue is full."

    # [Step 5+] Advanced Round Robin
    def round_robin_adv(self):
        while True:
            try:
                # sleep(1.5)
                item = self.robin_queue.get()
                return item
            finally:
                self.robin_queue.task_done()

    # [Step 6 & 7] Check the provider list and update their status
    def heartbeat_checker(self):
        print(Fore.RED + "HB tick")
        for provider in self.provider_list:
            provider_is_active = self.provider_list[provider]["provider"].check()
            provider_in_list_is_active = self.provider_list[provider]["status"]
            if provider_is_active and provider_in_list_is_active == "Active":
                pass
            elif not provider_is_active and provider_in_list_is_active == "Busy":
                pass
            elif not provider_is_active:
                self.provider_list[provider]["status"] = "Busy"
            elif provider_is_active and provider_in_list_is_active == "Busy":
                self.provider_list[provider]["status"] = "Standby"
            elif provider_is_active and provider_in_list_is_active == "Standby":
                self.provider_list[provider]["status"] = "Active"
            else:
                print("I missed something :O")
            # print(provider, self.provider_list[provider])
        print(Style.RESET_ALL)

    # [Step 6 & 7] Timer for Heartbeat function
    def heartbeat_timer(self):
        def set_interval(sec):
            def func_wrapper():
                set_interval(sec)
                self.heartbeat_checker()

            t = threading.Timer(sec, func_wrapper)
            t.start()
            return t

        timer = set_interval(self.heartbeat_interval)
