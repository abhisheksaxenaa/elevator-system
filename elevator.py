import time
from threading import Lock, Condition
from request import Request
from direction import Direction

# class bcolors:
#     HEADER = '\033[95m'
#     OKBLUE = 
#     OKCYAN = 
#     OKGREEN = 
#     WARNING = 
#     FAIL = 
#     ENDC = '\033[0m'
#     BOLD = 
#     UNDERLINE = '\033[4m'
ALL_COLORS = ['\033[31m', '\033[32m', '\033[33m','\033[92m','\033[93m', '\033[91m']

class Elevator:
    def __init__(self, id: int, capacity: int):
        self.id = id
        self.capacity = capacity
        self.current_floor = 1
        self.current_direction = Direction.UP
        self.requests = []
        self.lock = Lock()
        self.condition = Condition(self.lock)
        self.color = ALL_COLORS[(id-1) % len(ALL_COLORS)]
        self.end_color = '\033[0m'

    def add_request(self, request: Request):
        # create queue like [current, requests]
        current_requests = [self.current_floor] + self.requests
        with self.lock:
            if len(self.requests) < self.capacity:
                source_index = -1
                destination_index = -1
                # Adding source request
                for i in range(len(current_requests) - 1):
                    # if the request is to go up
                    if current_requests[i] < request.source_floor <= current_requests[i + 1] and request.source_floor < request.destination_floor:
                        self.requests.insert(i, request.source_floor)
                        source_index = i
                        break
                    # if the request is to go down
                    elif current_requests[i] > request.source_floor >= current_requests[i + 1] and request.source_floor > request.destination_floor:
                        self.requests.insert(i, request.source_floor)
                        source_index = i
                        break
                # Adding destination request
                if source_index != -1:
                    for i in range(source_index, len(current_requests) - 1):
                        # already in request queue?
                        # if the request is to go up
                        if request.source_floor < request.destination_floor and current_requests[i] < request.destination_floor <= current_requests[i + 1]:
                            destination_index = i
                            self.requests.insert(i + 1, request.destination_floor)
                            break
                        # if the request is to go down
                        elif request.source_floor > request.destination_floor and current_requests[i] > request.destination_floor >= current_requests[i + 1]:
                            destination_index = i
                            self.requests.insert(i + 1, request.destination_floor)
                            break
                if source_index == -1:
                    # if the request is not fitted in middle, then add at last
                    self.requests.append(request.source_floor)
                if destination_index == -1:
                    # if the request is not fitted in middle, then add at last or the source is fitted in middle and destination at last
                    self.requests.append(request.destination_floor)
                # self.requests.append(request)
                print(
                    f"Elevator {self.id} added request: {request.source_floor} to {request.destination_floor}. Request QUEUE : {self.requests}"
                )
                self.condition.notify_all()
    # def add_request(self, request: Request):
        # TODO: Fit request in current execution state
        # with self.lock:
        #     if len(self.requests) < self.capacity:
        #         self.requests.append(request)
        #         print(
        #             f"Elevator {self.id} added request: {request.source_floor} to {request.destination_floor}"
        #         )
        #         self.condition.notify_all()

    def get_next_request(self) -> int:
        with self.lock:
            while not self.requests:
                self.condition.wait()
            return self.requests[0]

    def process_requests(self):
        while True:
            request = self.get_next_request()  # This will wait until there's a request
            # print(f'{self.color}Fulfiling request for{self.current_floor} <> {request}')
            self.process_request(request)

    def process_request(self, destination_floor: int):
        # TODO: While processing request, need to check any change in request
        # TODO: Need to print for stoppages
        start_floor = self.current_floor
        end_floor = destination_floor

        if start_floor <= end_floor:
            self.current_direction = Direction.UP
            for i in range(start_floor, end_floor + 1):
                self.current_floor = i
                print(f"{self.color}Elevator {self.id} reached floor {self.current_floor}{self.end_color}")
                if i == self.requests[0]:
                    self.requests.pop(0)
                    print(f"{self.color}Elevator {self.id} stoppage on {self.current_floor}{self.end_color}")
                    time.sleep(2)
                time.sleep(1)  # Simulating elevator movement
        elif start_floor > end_floor:
            self.current_direction = Direction.DOWN
            for i in range(start_floor, end_floor - 1, -1):
                self.current_floor = i
                print(f"{self.color}Elevator {self.id} reached floor {self.current_floor}{self.end_color}")
                if i == destination_floor:
                    self.requests.pop(0)
                    print(f"{self.color}Elevator {self.id} stoppage on {self.current_floor}{self.end_color}")
                    time.sleep(2)
                time.sleep(1)  # Simulating elevator movement

    def run(self):
        self.process_requests()