import uuid


class Provider:
    def __init__(self, ip, busy_type, capacity):
        self.ip = ip
        self.id = uuid.uuid4()
        self.busy_type = busy_type
        self.capacity = capacity
        self.heartbeat_counter = 0

    def get(self):
        return self.id

    def get_ip(self):
        return self.ip

    def check(self):
        if self.busy_type == "busy":
            return False
        elif self.busy_type == "free":
            return True
        elif self.busy_type == "heartbeat":
            self.heartbeat_counter += 1
            if self.heartbeat_counter % 3 == 0:
                self.heartbeat_counter = 0  # to avoid counter growing huge over time
                return False
            else:
                return True

    def get_capacity(self):
        return self.capacity

    def availability_text(self):
        if self.busy_type == "busy":
            return "Busy. Always response as occupied for check()."
        elif self.busy_type == "free":
            return "Free. Always response as free for check()."
        elif self.busy_type == "heartbeat":
            return "Heartbeat. Response in free->free->occupied cycle for check()."

    def full_info(self):
        print("Id: {id}, IP: {ip}, Capacity: {cap}, Availability type: {avail}".format(id=self.id, ip=self.ip,
                                                                                       cap=self.capacity,
                                                                                       avail=self.availability_text()))
