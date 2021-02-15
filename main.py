from time import sleep
import time
from colorama import Fore, Style
from provider import Provider
from loadbalancer import LoadBalancer


# TEST AREA

# For console coloring
def task_w_color(color, text):
    color = color.lower()
    if color == "red":
        print(Fore.RED + "\n" + text + "\n" + Style.RESET_ALL)
    elif color == "green":
        print(Fore.GREEN + "\n" + text + "\n" + Style.RESET_ALL)
    elif color == "yellow":
        print(Fore.YELLOW + "\n" + text + "\n" + Style.RESET_ALL)
    elif color == "blue":
        print(Fore.BLUE + "\n" + text + "\n" + Style.RESET_ALL)
    else:
        print("\n" + text + "\n")


task_w_color("yellow", "*Start of test.")

time1 = time.ctime()

task_w_color("yellow", "*Create load balancer.")

load_balancer = LoadBalancer()

task_w_color("yellow", "*Call load balancer get() with random.")
task_w_color("red", "Expect error message.")

load_balancer.get("random")

task_w_color("yellow", "*Create 11 providers (1 busy, 6 free, 4 heartbeat), each with capacity of 2.")
task_w_color("yellow", "*For types of busy, free and heartbeat, please check provider.py availability_text().")

provider1 = Provider("1.2.3.4", "busy", 2)
provider2 = Provider("2.3.4.5", "free", 2)
provider3 = Provider("3.4.5.6", "heartbeat", 2)
provider4 = Provider("4.5.6.7", "free", 2)
provider5 = Provider("5.6.7.8", "free", 2)
provider6 = Provider("6.7.8.9", "heartbeat", 2)
provider7 = Provider("7.8.9.0", "heartbeat", 2)
provider8 = Provider("8.9.0.1", "heartbeat", 2)
provider9 = Provider("9.0.1.2", "free", 2)
provider10 = Provider("0.1.2.3", "free", 2)
provider11 = Provider("1.2.3.5", "free", 2)

task_w_color("yellow", "*Create outer provider list (for registering providers to the load balancer from list).")

provider_list = [provider1, provider2, provider3, provider4, provider5, provider6, provider7, provider8, provider9,
                 provider10, provider11]

task_w_color("yellow", "*Register provider 1 to load balancer.")

load_balancer.register_provider(provider1)

task_w_color("yellow", "*Call load balancer get() with random invocation.")
task_w_color("green", "Expect returning IP (instead of ID, because of readability).")

load_balancer.get("random")

task_w_color("yellow", "*Try to register again provider 1 to load balancer.")
task_w_color("red", "Expect error message.")

load_balancer.register_provider(provider1)

task_w_color("yellow", "*Register outer provider list to load balancer.")
task_w_color("red", "Expect error messages too.")

load_balancer.register_provider(provider_list)

task_w_color("yellow", "*List of registered providers in load balancer at start.")
task_w_color("red", "Expect one 'Busy' status.")
task_w_color("green", "Check max queue size. 10 provider * 2 capacity = 20")

load_balancer.prov_list()

print("------------------------------------------------------------")
task_w_color("yellow", "*Call load balancer get() with random 15 times.")
task_w_color("red", "*No availability or capacity check.")

for x in range(15):
    # sleep(0.3)
    task_w_color("", "*------------------------*")
    print("Checking random. Turn: {turn}.".format(turn=x + 1))
    load_balancer.get("random")

print("------------------------------------------------------------")
task_w_color("yellow", "*Call load balancer get() with round robin 15 times.")
task_w_color("red", "*No availability or capacity check.")
task_w_color("green", "Expect sequential steps.")

for x in range(15):
    # sleep(0.3)
    task_w_color("", "*------------------------*")
    print("Checking round-robin. Turn: {turn}.".format(turn=x + 1))
    load_balancer.get("robin")

print("------------------------------------------------------------")
task_w_color("yellow", "*Call load balancer get() with round robin adv 15 times.")
task_w_color("yellow", "*2.5 seconds waiting time to wait two 1 second cycle of Heartbeat function.")

sleep(2.5)
task_w_color("green", "Flip activity to off of provider 2.")
load_balancer.flip_provider_activity(provider2)
task_w_color("green", "Expected IPs start with 4, 5, 9 and 0. All other are busy or not active.")
task_w_color("green", "Remove comment from sleep(0.3) and see, how it changed because of Heartbeat ticks.")
for x in range(15):
    # sleep(0.3)
    task_w_color("", "*------------------------*")
    print("Checking adv round-robin. Turn: {turn}.".format(turn=x + 1))
    load_balancer.get("robin_adv")

task_w_color("yellow", "*List of registered providers in load balancer after Heartbeat checks.")
task_w_color("red", "See max queue size reduced as provider 2 is not active")

load_balancer.prov_list()

task_w_color("", "------------------------------------------------------------")

task_w_color("yellow", "*Flip provider activity.")

load_balancer.flip_provider_activity(provider1)

task_w_color("yellow", "*Flip back provider activity.")

load_balancer.flip_provider_activity(provider1)

task_w_color("yellow", "*Try flip provider activity (provider not in the list).")
task_w_color("red", "Expect error message.")

load_balancer.flip_provider_activity(provider11)

task_w_color("", "------------------------------------------------------------")

task_w_color("green", "Red 'HB tick' means Heartbeat function running every 1 second.")

task_w_color("yellow", "*End of test.")

print(time1, time.ctime())
