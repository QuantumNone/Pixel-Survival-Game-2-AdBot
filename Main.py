
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

in_game_buttons: dict[str, ('X', 'Y')] = {
    'Play': (130, 390),
    'First Character': (480, 150),
    'Single Player': (135, 300),
    'Left Movement': (110, 460),
    'Hit Button': (850, 385),
    'Jump Button': (762, 466)
}

import cv2
from ppadb.client import Client as AdbClient
import numpy as np
from os import listdir, mkdir
from time import sleep
from subprocess import Popen, run, DEVNULL, STDOUT
from pywinauto import Desktop, timings, mouse
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

CLONED_APPS_AMOUT: int = 10 #-> indicates how many psg2 cloned applications each instance has (for example if you have 10 cloned apps, then the program will watch ads on each app) !The number of apps must be equal to all other instances!
INSTANCES_TO_START: int = 3 #-> default instances ram allocation is 4 Gb, this means that to run 4 instances you need 16 Gb available!
INSTANCES: tuple = (1, 8) #-> indicates how many instances you have and which instances to use (default: from instance at first place to instance at eighth place)
#OCCHIO A QUESTO VALORE!!!
assert INSTANCES_TO_START <= INSTANCES[1]
try: mkdir('./Screenshots/Before')
except: pass
try: mkdir('./Screenshots/After')
except: pass

instances_status: dict = {
    f'instance_{num}': 'Offline' for num in range(INSTANCES_TO_START)
}
#Possible status: {Offline}, {Online}, {On-Game}, {Waiting-for-Ad}, {Watching-Ad}

INSTANCES_NAMES: list = [ #You have to name each instance like this:
    '1.Bot',
    '2.Bot',
    '3.Bot',
    '4.Bot',
    '5.Bot',
    '6.Bot',
    '7.Bot',
    '8.Bot'
]

#Code variables:
ljust_val = 110
Pywinauto_Window_Connection = lambda window_name: Desktop(backend='uia').window(title=window_name) #Connecting to the application trought its name)

def StartBlueStacks():
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

def ClickInputFixed(method: classmethod): #If the mouse is mooving crazy, then the click won't work and so the program will cause issues.
    """This function fix click_input() method preventing user mouse input to change mouse X, Y while clicking on the button."""
    ENABLE_MOUSE_INPUT = False
    sleep(0.5)
    method()
    sleep(0.5)
    ENABLE_MOUSE_INPUT = True

def StartInstances(n: tuple):
    print(f"[{Colors['Blue']}BlueStacks{Colors['Reset']}]: Starting {n[0]}-{n[1]} instances...".ljust(ljust_val), end="", flush=True)
    for i in range(2, n[1]-n[0]+3):
        #instance_manager.print_control_identifiers() function shows all BlueStacks GUI buttons. Each instance has a checkbox and its name is 'CheckBoxN' where N is the number of the place of the instance + 1. Ex: instance 1 has 'CheckBox2'
        exec(f"instance_manager.CheckBox{i}.click()")
        sleep(0.4)

    ClickInputFixed(method=instance_manager.Start.click_input)
    wait_window(window_name=f"{n[1]}.Bot") #The n[1] instance is the last instance that bluestacks starts
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

    print(f"[{Colors['Green']}Python{Colors['Reset']}]: Connecting with spawned instances...")
    for i in range(n[0], n[1]+1):
        instances_status[f'instance_{i}'] = 'Online'
        print(f"\t[{Colors['Blue']}{i}.Bot{Colors['Reset']}] Instance : ", end=f"-> [{Colors['Red']}Offline{Colors['Reset']}!]", flush=True)
        wait_window(window_name=f"{i}.Bot")
        # globals()[f'instance{i}'] = Pywinauto_Window_Connection(window_name=f'{i}.Bot') #Creating global variables like instance_manager variable; each variable refeeres to each Bot instance
        sleep(0.5)
        print("\b"*9 + f"{Colors['Green']}Online{Colors['Reset']}!]   \n")
    #Arranging button

#--- Not Used ---
def Syncronize_MasterInstance(instance: str):
    print(f"[{Colors['Blue']}BlueStacks{Colors['Reset']}]: Syncronizing all spawned instances under {Colors['Blue']}{instance}{Colors['Reset']} instance...", end="")
    """This function sets a give instance under 'Master' role, which means that every other spawned instance will follow what this Master instance does."""
    global master_instance
    master_instance = Pywinauto_Window_Connection(window_name=instance)
    ClickInputFixed(method=master_instance.Button15.click_input) #This button opens the 'Sync operations' panel in that instance
    master_instance['Select allCheckBox'].click()
    ClickInputFixed(method=master_instance['Start syncButton'].click_input())
    #Now, all spawned instances belongs to this Master instance : each instance follows the inputs (like a macro) of what the master instance does. Obviously, these instances may experience time delays...
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

def Start_MasterInstance_Macro(instance: Desktop): #The problem is that there are 2 different type of Ads : the 30 seconds one and the 30-40 seconds one which requires interactive closure (need to wait 5 seconds to close the ad after closing the 30 second one)
    """This function starts the macro that will automate us the process of opening the game and pickaxing on the Ad chest to watch the 30 seconds Ad -> All other instances will follow what that macro does"""
    
    print(f"[{Colors['Blue']}BlueStacks{Colors['Reset']}]: Starting the macro...", end="")
    ClickInputFixed(method=instance.Button14.click_input) #Opens the Macro Manager window
    sleep(0.5)
    ClickInputFixed(method=instance.Button10.click_input) #Actives the first macro of the list
    sleep(0.5) #From that point, the macro will start and will take around 2 mins to finish, while python will do nothing. -> Python will pause its execution until the macro finishes.
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

    sleep(125) #2 minutes to wait for the macro to finish

#--- _ ---

def EnstablishAdbConnections():
    run("adb kill-server & adb start-server", shell=True, stderr=DEVNULL)
    sleep(1)
    print(f"[{Colors['Green']}Android Debugging Bridge{Colors['Reset']}]: Checking adb-server status...".ljust(ljust_val), flush=True, end=f"-> [{Colors['Red']}Offline{Colors['Reset']}!]")
    global client
    client = AdbClient(host="127.0.0.1", port=5037) #The daemon must run in background already
    devices = client.devices()
    print("\b"*9 + f"{Colors['Green']}Online{Colors['Reset']}!] ")

    #If there are more android devices connected or launched then we won't be able to identify which serial corresponds to which instance
    print(f"[{Colors['Green']}Android Debugging Bridge{Colors['Reset']}]: Checking adb devices...".ljust(ljust_val), flush=True, end=f"-> [{Colors['Red']}Not Found Yet{Colors['Reset']}!]")
    while len(devices) != INSTANCES_TO_START: #This is a slow process, it depends on client.devices
        devices = client.devices()
        sleep(1)
    print("\b"*16 + f"[{Colors['Green']}Found{Colors['Reset']}!]" + " "*10)

    class BS_Instance:
        def __init__(self, device_serialno: AdbClient) -> None:
            self.device: AdbClient.device = client.device(str(device_serialno))
            #Each psg2 app has differt app-package-name (storage/emulated/0/Android/Data/com.cowbeans.(...)), so we get these packages to identify each psg2 app trought the formatting of the output string of .shell() func
            self.psg2_packages: list[str] = [package.strip().split('package:')[1] for package in self.device.shell('pm list packages').split('\n') if 'com.cowbeans.' in package]
            self.current_package: str
#-> Maybe add a better output

    for number, device in enumerate(devices):
        try:
            globals()[f'instance_{number}'] = BS_Instance(device_serialno=device.serial) #We create global variables to indicate each instance connected trought adb so that we can use adb commands directly on each instance
        except Exception as Ex:
            print('Adb setting has not been enabled in your bluestacks\'instance\'settings!')
            input('press enter to quit : ')
            raise Ex
        
    #Once all BlueStacks instances have been connected trought adb client and assigned each connection to a python global variable


def GetScreenshot(instance, name='Screenshot', folder=''):
    result = instance.device.screencap()
    with open(f"./Screenshots/{folder}{name}.png", "wb") as fp:
        fp.write(result)

def CompareScreenshots(first_screenshot, second_screenshot) -> bool:
    """Returns True if both screenshots are different, else False"""
    image1 = cv2.imread(first_screenshot)
    image2 = cv2.imread(second_screenshot)
    #As the ad takes time to load, the screen could change (for example the time-meter and the sky-color) and that tells us that the image changed even if the ad did not' show.
    #That's why comparing both images bytes size doesn't help. So, we need to compare the similarity of the 2 screenshots.
    
    #Code from Chat-GPT : Maybe it can be improved but it does its job for now...
    #Compute the absolute difference between the two images
    difference = cv2.absdiff(image1, image2)
    #Convert the difference to grayscale
    gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
    #Apply a threshold to obtain a binary mask
    _, thresholded = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    #Calculate the number of different pixels (total distance)
    total_diff = cv2.countNonZero(thresholded)
    #Calculate the similarity percentage relative to the reference image
    similarity = 1 - (total_diff / (image1.shape[0] * image1.shape[1])) #From 0.0 to 1.0

    # Display the similarity percentage
    # print(first_screenshot, '\n', second_screenshot)
    # print(f'Similarity: {similarity * 100:.2f}%')

    #The first picture represents the screen istantly after the character Hit the ad-chest, 
    #the second picture is taken after 12-15 seconds and should show the Ad-screen which is totally different from the screenshot before.
    #If the similarity should be less than 25% (even 45% would be fine)
    return similarity <= 0.45

number: int
result: bool
def SyncronizeActions(actions: str, DecFunction=None): #takes in input a str format of some commands (actions) to execute on each instance instances
    for number in range(INSTANCES_TO_START):
        instance = globals()[f'instance_{number}']
        exec(actions)
        if DecFunction: DecFunction(number) #This function adds some code like decorators but inside the function
        sleep(0.2)

def TakeScreenshots(delay: float = 10): #Remember that once took the screenshot, the in-game time changes (Morning, Afternoon, Night...) and that falsificates the screenshots
    SyncronizeActions("""GetScreenshot(instance, name=f'Instance-{number}-BeforeAd-Screenshot', folder='Before/')""")
    sleep(delay) #All instances should get the ad appeard on the screen, if not then the code won't matter. It will just report that this instance did not watch the ad
    SyncronizeActions("""GetScreenshot(instance, name=f'Instance-{number}-AfterHit-Screenshot', folder='After/')""") #After hitting the ad-chest

#We use a generator-func to get each instance's first psg2 app package to be started
def get_package(instance):
    for package in instance.psg2_packages:
        yield package

def StartTheGame():
    
    print(f"[{Colors['Green']}Android Debugging Bridge{Colors['Reset']}]: Starting com.cowbeans.pixelsurvival package on each instance...".ljust(ljust_val), flush=True, end="")
    #For each BlueStacks Instance, we run the first psg2 app

    SyncronizeActions("""instance.current_package = next(get_package(instance)); instance.device.shell(f'monkey -p "{instance.current_package}" -c android.intent.category.LAUNCHER 1')""")

    #TODO: Then we SHOULD check if the app has been booted  -> we wait 13 seconds. The better way would be to screenshot the screen of each instance and check if the game has been booted
    sleep(13) #The time depends on how many Ram left the user has. I tested it on 3 Gb Ram remaining
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

def WalkToAdChest():
    print(f"[{Colors['Red']}In-Game Action{Colors['Reset']}]: Set bots in front of ad-chest...".ljust(ljust_val), flush=True, end="")
    SyncronizeActions("""instance.device.shell(f"input tap {in_game_buttons['Play'][0]} {in_game_buttons['Play'][1]}")""") #Clicks on 'Play' button
    SyncronizeActions("""instance.device.shell(f"input tap {in_game_buttons['First Character'][0]} {in_game_buttons['First Character'][1]}")""")
    SyncronizeActions("""instance.device.shell(f"input tap {in_game_buttons['Single Player'][0]} {in_game_buttons['Single Player'][1]}")""")
    SyncronizeActions("""instance.device.shell(f"input touchscreen swipe {in_game_buttons['Left Movement'][0]} {in_game_buttons['Left Movement'][1]} {in_game_buttons['Left Movement'][0]} {in_game_buttons['Left Movement'][1]} 1350")""")
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

def CheckAdStatus():
    """Checks whatever the ad has been showed on the screen or not"""
    #Once all instances booted the game and hitted the ad-chest, we get a screenshot per each instance and then compare that screenshot with the screenshot of the next 5 seconds.
    #If both screenshots are the same, it means that the ad did not jet appeard (time limit should be of 15 seconds).
    #If they are not, then the ad appeard or the game crashed.
    
    print(f"[{Colors['Red']}In-Game Action{Colors['Reset']}]: Hitting ad-chest one time and wait for ad to come...".ljust(ljust_val), flush=True, end="")
    SyncronizeActions("""instance.device.shell(f"input tap {in_game_buttons['Hit Button'][0]} {in_game_buttons['Hit Button'][1]}")""")
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")
    print('Checking if the ad appeard...')
    #TODO: Make sure all folders are present in the directory when the program has been launched.
    TakeScreenshots()
    def UpdateStatus(number):
        if not result:
            instances_status[f'instance_{number}']='Watching-Ad'
        else:
            instances_status[f'instance_{number}']='Problem: Ad-did-not-show!'

    SyncronizeActions(
        """
before_ad_screenshots: list = [screenshot for screenshot in listdir("./Screenshots/Before")]
after_hit_screenshots: list = [screenshot for screenshot in listdir("./Screenshots/After")]
global result
result=CompareScreenshots("./Screenshots/Before/" + before_ad_screenshots[number], "./Screenshots/After/" + after_hit_screenshots[number])""",
        DecFunction = UpdateStatus
    )

    print(instances_status)

    #From there: there could be one or more instances that did not show the ad, so we have to filter which instance did show the ad.
    #Once there: need to close the ad.

def GetImageMatches(main_image: str, match_image: str, confidence: float = 0.95) -> (bool, np.array):
    """This function let us know if a give image (match_image) is detected inside the main image (main_image)."""
    main_image = cv2.imread(main_image)
    match_image = cv2.imread(match_image)

    #This function does what's explained in that video minute : 
    #https://www.youtube.com/watch?v=vXqKniVe6P8&t=3s -> min 4:30
    result = cv2.matchTemplate(main_image, match_image, cv2.TM_CCOEFF_NORMED)

    #This variable sets the percentage (from 0.0 to 1.0) of how right we want the match to be.
    threshold = confidence

    #This function filters the matches found on the image with the confidence percentage
    locations: ('Y', 'X') = np.where(result >= threshold) #with a high confidence, there should be only 1 result

    #This code just open the main_image and edits it by highlighting with rectagles the found matches.
    # def HighlightMatches():
    #     for pt in zip(*locations[::-1]):
    #         bottom_right = (pt[0] + match_image.shape[1], pt[1] + match_image.shape[0])
    #         cv2.rectangle(main_image, pt, bottom_right, (0, 255, 0), 2)

    #     # Mostra l'immagine con i rettangoli disegnati
    #     cv2.imshow('Corrispondenze', main_image)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    if locations[0].size > 0:
        return True, locations
    else:
        return False, locations
    # return locations, HighlightMatches

skip_buttons: list = ["./Screenshots/Skip-Ad-Buttons/" + skip_button for skip_button in listdir("./Screenshots/Skip-Ad-Buttons") if skip_button.startswith('X-Button')]
def CloseAd():
    print(f"[{Colors['Green']}Python{Colors['Reset']}]: Closing Ads...".ljust(ljust_val), flush=True, end="")
    number = 0
    while number < INSTANCES_TO_START:
        instance = globals()[f'instance_{number}']

        for i in range(3): #Possible times that X button can appear
            GetScreenshot(instance, name=f'Screenshot-Ad-Finished-{number}-searchForX', folder='Before/'),
            result, locations = GetImageMatches(
                main_image=f'./Screenshots/Before/Screenshot-Ad-Finished-{number}-searchForX.png',
                match_image=f'./Screenshots/Items-Bag-23x23.png'
            )
            if result:
                break
            for skip_button in skip_buttons:
                result, locations = GetImageMatches(
                    main_image=f'./Screenshots/Before/Screenshot-Ad-Finished-{number}-searchForX.png',
                    match_image=skip_button
                )
                if result: #If any match was found:
                    instance.device.shell(f'input tap {locations[1][0]} {locations[0][0]}') #Clicks on the X button
                    break #CLOSE THE AD AND THEN CHECK IF OTHER X BUTTONS APPEARD
            else:
                #HERE THE AD IS PROBABLY A 'CLICK ">>" TO PROCEED' BUT THIS BUTTON IS HARD TO BE MATCHED AS IT'S TRANSPARENT AND SO THE BACKGROUND CHANGES EVERYTIME
                instance.device.shell(f'input tap 935.5 20.0') #Clicks on the ">>" button
                #This could also open google play store!
            sleep(1)
        number += 1
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

def JumpForRewards():
    """Once the function has been closed, the chest drops all the rewards which can glitch and not be collected
       So we let the character jump twice to collect all dropped items"""
    SyncronizeActions(
        """
instance.device.shell(f"input tap {in_game_buttons['Jump Button'][0]} {in_game_buttons['Jump Button'][1]}
sleep(0.25)
instance.device.shell(f"input tap {in_game_buttons['Jump Button'][0]} {in_game_buttons['Jump Button'][1]}"""
    )
    pass

def ExitFromTheGame():
    print(f"[{Colors['Green']}Android Debugging Bridge{Colors['Reset']}]: Stopping com.cowbeans.pixelsurvival package on each instance...".ljust(ljust_val), flush=True, end="")
    SyncronizeActions("""instance.device.shell(f'am force-stop "{instance.current_package}"')""")
    print(f"-> [{Colors['Green']}Done{Colors['Reset']}!]")

#--------- Main - Code ---------
StartBlueStacks()
instance_manager = Pywinauto_Window_Connection(INSTANCE_MANAGER_NAME)
# instance_manager.print_control_identifiers()

#This lambdafunction checks if a window is opened on the desktop
wait_window = lambda window_name: timings.wait_until(timeout=60, retry_interval=2, func=lambda: any(process.window_text() == window_name for process in Desktop(backend="uia").windows()))

# StartInstances(n=(1, INSTANCES_TO_START))
EnstablishAdbConnections()
for cloned_app in range(CLONED_APPS_AMOUT): #Once all apps got done, the program will end. If you want to let the program stay in the background and start again once 1 hour passed then add datatime module and work on it.
    StartTheGame()
    WalkToAdChest()
    CheckAdStatus()
    sleep(30) #time required to get all ads done that can be closed (the real time passed is like 40 seconds because of the 10 second delay on CheckAdStatus())
    CloseAd()
    ExitFromTheGame()
    sleep(3)



# Syncronize_MasterInstance(instance=f'{INSTANCES_TO_START}.Bot')
# Start_MasterInstance_Macro(instance=f'{INSTANCES_TO_START}.Bot')

