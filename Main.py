
# Colors for String formatting :
Colors: dict[str, str] = {
    "Reset": "\033[0m",

    "Red": "\033[1;31m",
    "Green": "\033[1;32m",
    "Yellow": "\033[1;33m",
    "Blue": "\033[1;34m",
    "Magenta": "\033[1;35m",
    "Cyan": "\033[1;36m",
    "White": "\033[1;37m",
}

from time import sleep
from subprocess import Popen, run, DEVNULL, STDOUT
from pywinauto import Desktop, timings
from pyautogui import FAILSAFE as ENABLE_MOUSE_INPUT #Need to be installed as a dependency

INSTANCE_MANAGER_NAME = 'BlueStacks Multi Instance Manager' #The name of the instance manager process
IM_PROCESS = 'HD-MultiInstanceManager.exe'
INSTANCE_MANAGER_PATH = 'C:\\Program Files\\BlueStacks_nxt\\HD-MultiInstanceManager.exe'

#Instances details :        -> Please, edit these details in base of your preferences. These informations are needed in case of debugging.
#CPU cores: 2 Cores
#RAM allocation: 4Gb
#Frame rate 20 Fps
#Display resolution: 960x540
#Pixel density: 160 DPI

#Normally PSG 2 runs good at 1 Core and 1Gb of Ram but all depends on how many cores your CPU has and what's the Clock speed of your CPU and RAM.

INSTANCES_TO_START: int = 4 #-> default instances ram allocation is 4 Gb, this means that to run 4 instances you need 16 Gb available!
INSTANCES: tuple = (1, 8) #-> indicates how many instances you have and which instances to use (default: from instance at first place to instance at eighth place)
#OCCHIO A QUESTO VALORE!!!
assert INSTANCES_TO_START < INSTANCES[1]

INSTANCES_NAMES: list = [ #You have to name each instance like this:
    "1.Bot",
    "2.Bot",
    "3.Bot",
    "4.Bot",
    "5.Bot",
    "6.Bot",
    "7.Bot",
    "8.Bot"
]

#Code variables:
ljust_val = 110
Pywinauto_Window_Connection = lambda window_name: Desktop(backend='uia').window(title=window_name) #Connecting to the application trought its name)

def Start_BlueStacks():
    input(f"[{Colors['Red']}System{Colors['Reset']}]: Press enter to kill BlueStacks services : ")

    try:
        run(f"taskkill /f /im \"{IM_PROCESS}\"", shell=False, stdout=DEVNULL, stderr=STDOUT)
        sleep(3)
    except Exception:
        print(Exception)

    print(f"[{Colors['Green']}Python{Colors['Reset']}]: Starting BlueStacks Multi Instance Manager...".ljust(ljust_val), end="")
    Popen(INSTANCE_MANAGER_PATH, shell=True)
    sleep(3)
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

def Click_Input_Fixed(method: classmethod): #If the mouse is mooving crazy, then the click won't work and so the program will cause issues.
    """This function fix click_input() method preventing user mouse input to change mouse X, Y while clicking on the button."""
    ENABLE_MOUSE_INPUT = False
    sleep(0.5)
    method()
    ENABLE_MOUSE_INPUT = True
    sleep(0.5)

def Start_Instances(n: tuple):
    print(f"[{Colors['Blue']}BlueStacks{Colors['Reset']}]: Starting {n[0]}-{n[1]} instances...".ljust(ljust_val), end="")
    for i in range(2, n[1]-n[0]+3): #instance_manager.print_control_identifiers() function shows all BlueStacks GUI buttons. Each instance has a checkbox and its name is 'CheckBoxN' where N is the number of the place of the instance + 1. Ex: instance 1 has 'CheckBox2'
        exec(f"instance_manager.CheckBox{i}.click()")
        sleep(0.4)

    Click_Input_Fixed(method=instance_manager.Start.click_input)
    wait_window(window_name=f"{n[1]}.Bot") #The n[1] instance is the last instance that bluestacks starts
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

    print(f"[{Colors['Green']}Python{Colors['Reset']}]: Connecting with spawned instances...")
    for i in range(n[0], n[1]+1):
        print(f"\t[{Colors['Blue']}{i}.Bot{Colors['Reset']}] Instance : ", end=f"[{Colors['Red']}Offline{Colors['Reset']}!]", flush=True)
        wait_window(window_name=f"{i}.Bot")
        # globals()[f'instance{i}'] = Pywinauto_Window_Connection(window_name=f'{i}.Bot') #Creating global variables like instance_manager variable; each variable refeeres to each Bot instance
        sleep(0.5)
        print(f"\b\b\b\b\b\b\b\b\b{Colors['Green']}Online{Colors['Reset']}!")

def Syncronize_MasterInstance(instance: str):
    print(f"[{Colors['Blue']}BlueStacks{Colors['Reset']}]: Syncronizing all spawned instances under {Colors['Blue']}{instance}{Colors['Reset']} instance...", end="")
    """This function sets a give instance under 'Master' role, which means that every other spawned instance will follow what this Master instance does."""
    global master_instance
    master_instance = Pywinauto_Window_Connection(window_name=instance)
    Click_Input_Fixed(method=master_instance.Button15.click_input) #This button opens the 'Sync operations' panel in that instance
    master_instance['Select allCheckBox'].click()
    Click_Input_Fixed(method=master_instance['Start syncButton'].click_input())
    #Now, all spawned instances belongs to this Master instance : each instance follows the inputs (like a macro) of what the master instance does. Obviously, these instances may experience time delays...
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

def Start_MasterInstance_Macro(instance: Desktop): #The problem is that there are 2 different type of Ads : the 30 seconds one and the 30-40 seconds one which requires interactive closure (need to wait 5 seconds to close the ad after closing the 30 second one)
    """This function starts the macro that will automate us the process of opening the game and pickaxing on the Ad chest to watch the 30 seconds Ad -> All other instances will follow what that macro does"""
    
    print(f"[{Colors['Blue']}BlueStacks{Colors['Reset']}]: Starting the macro...", end="")
    Click_Input_Fixed(method=instance.Button14.click_input) #Opens the Macro Manager window
    sleep(0.5)
    Click_Input_Fixed(method=instance.Button10.click_input) #Actives the first macro of the list
    sleep(0.5) #From that point, the macro will start and will take around 2 mins to finish, while python will do nothing. -> Python will pause its execution until the macro finishes.
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

    sleep(125) #2 minutes to wait for the macro to finish


#--------- Main - Code ---------
# Start_BlueStacks()
instance_manager = Pywinauto_Window_Connection(INSTANCE_MANAGER_NAME)

#This lambdafunction checks if a window is opened on the desktop
wait_window = lambda window_name: timings.wait_until(timeout=60, retry_interval=2, func=lambda: any(process.window_text() == window_name for process in Desktop(backend="uia").windows()))

# Start_Instances(n=(1, INSTANCES_TO_START))
# Syncronize_MasterInstance(instance=f'{INSTANCES_TO_START}.Bot')
# Start_MasterInstance_Macro(instance=f'{INSTANCES_TO_START}.Bot')


#Code an Arrange All button activation after launching the instances.
