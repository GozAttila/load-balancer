# As I found not too satisfying the previous version, I dive a little bit deeper into this with python, but what I found
# didn't make me happy. If I want returning value, then I can use only blocking codes. If I want to use background
# functions, I cannot return value. None of it is good for me. Albeit I didn't try it with multiprocess, as I found no
# solution (in Windows) to create a callable function. In the previous version, I had to decide between blocking or no
# returning, and I chose blocking (to change it to no returning, I just have to comment out the join part).
# Here, I tried something different. Two separated functions to feed requests and to receive results. Queues to handle
# requests/results. Using Threads in the provider. No Heartbeat checker -> a callback function handle this in real time,
# no waiting for the Heartbeat checker tick. When a provider queue is full, set it's availability to False in the
# Load balancers provider list, and turn it back to True when the list become empty.

from time import sleep

from provider import Provider
from load_balancer import LoadBalancer

load_balancer = LoadBalancer(10)

load_balancer.get("Test_empty")

provider1 = Provider("1.2.3.4", 10)
provider2 = Provider("2.3.4.5", 10)
provider3 = Provider("3.4.5.6", 10)
provider4 = Provider("4.5.6.7", 10)
provider5 = Provider("5.6.7.8", 10)
provider6 = Provider("6.7.8.9", 10)
provider7 = Provider("7.8.9.0", 10)
provider8 = Provider("8.9.0.1", 10)
provider9 = Provider("9.0.1.2", 10)
provider10 = Provider("0.1.2.3", 10)
provider11 = Provider("1.2.3.5", 10)

provider_list = [provider1, provider2, provider3, provider4, provider5, provider6, provider7, provider8, provider9,
                 provider10, provider11]

load_balancer.register_provider(provider1)

load_balancer.get("Test_one_provider")

load_balancer.register_provider(provider_list)

# Feed 100 + 1 request into loader, expect one refuse as all providers full

for x in range(100):
    request_id = "Request ID-{id}".format(id=x)
    result = load_balancer.get(request_id)
    if result is not None:
        print(result)

# counter for counting the results and none_counter to quit from the while loop
counter = 0
none_counter = 0

# give sme time for the providers to calculate
sleep(5)

# get and count the results from the load_balancer
while True:
    result = load_balancer.get_result()
    if result is not None:
        print(result)
    if result:
        counter += 1
    if result is None:
        none_counter += 1
    if none_counter == 10:
        break

print("Finished.")
print("Received results: ", counter)
