import random
import threading
import time

# Control mouse
# listen for position of mouse
# control keyboard
# listen for keyboard strokes


def controlMouse(): # sends mouse to random locations on a timer
    from pynput.mouse import Controller
    # thread = threading.Thread()
    # thread.daemon = True
    # thread.start
    finish = False
    mouse = Controller()
    #while(not finish):
    for i in range(20):
        mouse.position = (random.randint(0,1920),random.randint(0,1080)) # pixel position on screen
        time.sleep(.25)
        
def controlKeyboard():
    from pynput.keyboard import Controller
    keyboard = Controller()
    keyboard.type("Hello World")

def main():
    print("Enter:\n1 - Mouse Control \n2 - KeyBoard Control \n")
    i = input("> ")
    while True:
        try:
            if (int(i) == 1): 
                controlMouse()
                break
            if (int(i) == 2):
                controlKeyboard()
                break
        except:
            print("Try again.")

main()
