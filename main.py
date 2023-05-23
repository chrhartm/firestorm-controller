import pygame
import time
import subprocess

# Global parameters
JOYSTICK_TIMEOUT = 30 # in seconds for reconnect logic
N_PROGRAMS = 6 # note that it's hard-coded below for programs 0-5

# Variables
joystick_lastactive = time.time()
joysticks = []
# 1, 2, 3, 4, L1, R1, L2, R2, Start, Select
button_states = [False, False, False, False, False, False, False, False, False, False] # all boolean
program = 0

def init_bluetooth():
    global bluetoothprocess
    bluetoothprocess = subprocess.Popen(['bluetoothctl'],
                                        shell=False,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
    time.sleep(0.02)
    bluetoothprocess.stdin.write('agent on\n'.encode())
    time.sleep(0.02)
    bluetoothprocess.stdin.write('connect DB:F6:AB:36:77:85\n'.encode())
    time.sleep(1)
    bluetoothprocess.stdin.write('connect FF:6C:F2:BA:E9:AA\n'.encode())
    time.sleep(1)
    bluetoothprocess.stdin.write('exit\n'.encode())
    # print(bluetoothprocess.stdout.read().decode())

def init_joystick():
    global joysticks, joystick_lastactive
    # Joystick setup
    pygame.joystick.quit()
    pygame.quit()
    pygame.init()
    pygame.joystick.init()

    for i in range(0, pygame.joystick.get_count()):
        joysticks.append(pygame.joystick.Joystick(i))
        joysticks[-1].init()
        joystick_lastactive = time.time()
        print ("Detected joystick "),joysticks[-1].get_name(),"'"

def read_controller():
    global program, button_states
    for event in pygame.event.get():
        joystick_lastactive = time.time()
        # print(event)
        if(event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP):
            if event.type == pygame.JOYBUTTONUP:
                value = False
            else:
                value = True
            if event.button in [6,7,8,9,10,11,12]:
                button_states[8] = value
            if event.button == 6:
                program = 0
            elif event.button == 7:
                program = 1
            elif event.button == 8:
                program = (program+1)%N_PROGRAMS
            elif event.button == 9:
                program = 2
            elif event.button == 10:
                program = 3
            elif event.button == 11:
                program = 4
            elif event.button == 12:
                program = 5
            elif event.button in [4,5,13,14]:
                button_states[9] = value
            elif event.button == 0:
                button_states[1] = value
            elif event.button == 1:
                button_states[3] = value
            elif event.button == 2:
                button_states[2] = value
            elif event.button == 3:
                button_states[0] = value

        if event.type == pygame.JOYAXISMOTION:
            # Mirror right button logic on same layout
            if event.axis==3 and event.value < 0:
                button_states[0] = True
            if event.axis==3 and event.value > 0:
                button_states[1] = True
            if event.axis == 2 and event.value < 0:
                button_states[2] = True
            if event.axis == 2 and event.value > 0:
                button_states[3] = True
            if event.axis == 3 and event.value == 0:
                button_states[1] = button_states[0] = False
            if event.axis == 2 and event.value == 0:
                button_states[2] = button_states[3] = False
            # Joy hat logic
            if event.axis==0 and event.value < 0:
                button_states[5] = True
            if event.axis==0 and event.value > 0:
                button_states[4] = True
            if event.axis == 1 and event.value < 0:
                button_states[6] = True
            if event.axis == 1 and event.value > 0:
                button_states[7] = True
            if event.axis == 0 and event.value == 0:
                button_states[4] = button_states[5] = False
            if event.axis == 1 and event.value == 0:
                button_states[7] = button_states[6] = False          
        if event.type == pygame.JOYHATMOTION:
            if event.value == (-1, 0):
                button_states[5] = True
            if event.value == (1, 0):
                button_states[4] = True
            if event.value == (0, -1):
                button_states[7] = True
            if event.value == (0, 1):
                button_states[6] = True
            if event.value == (0, 0):
                button_states[4] = button_states[5] = False
                button_states[6] = button_states[7] = False

def process():
	print(button_states)

def send_firestorm():
	print("sending")

def main_loop():
    global joysticks, joystick_lastactive, JOYSTICK_TIMEOUT
    
    while True:
        time.sleep(0.02)
        read_controller()
        process()
        send_firestorm()
                             
        if (time.time() - joystick_lastactive > JOYSTICK_TIMEOUT):
            joysticks = []
            print("lost joystick")
            break

if (__name__ == '__main__'):
    init_bluetooth()
    
    while True:
        try:
            init_joystick()
            print("after init")
            if len(joysticks)<1:
                time.sleep(1)
                pygame.joystick.quit()
            else:
                main_loop()
        except KeyboardInterrupt:
            print("*** Ctrl+C pressed, exiting")
            break
    
    bluetoothprocess.terminate()
