import os
# Needed for pygame when running from cron
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import time
import requests
import subprocess

# User defined parameters
PIXELBLAZE_IDs = [9213581]
PROGRAM_PARAMS = {"Interactive fireflies": {
						"sparkHue": [0, 1],
						"maxSpeed": [0, 1],
						"decay": [0.9, 0.999]
					},
					"KITT": {}
				}

# Global parameters
JOYSTICK_TIMEOUT = 30 # in seconds for reconnect logic
RANGE_INCREMENT = 0.02
N_PROGRAMS = len(PROGRAM_PARAMS)

# Variables
joystick_lastactive = time.time()
joysticks = []
# 1, 2, 3, 4, L1, R1, L2, R2, Start, Select
button_states = [False, False, False, False, False, False, False, False, False, False] # all boolean
program = 0
range_states = [0, 0, 0, 0, 0]

def init_bluetooth():
    global device1, device2
    try:
        bprocess = subprocess.Popen(["bluetoothctl"], stdin=subprocess.PIPE)
        bprocess.stdin.write(f"connect DB:F6:AB:36:77:85".encode())
        bprocess.stdin.flush()
        bprocess.stdin.close()
        bprocess.wait()
        time.sleep(2)
    except:
        print("couldn't find device1")
    try:
        bprocess = subprocess.Popen(["bluetoothctl"], stdin=subprocess.PIPE)
        bprocess.stdin.write(f"connect FF:6C:F2:BA:E9:AA".encode())
        bprocess.stdin.flush()
        bprocess.stdin.close()
        bprocess.wait()
        time.sleep(2)
    except:
        print("couldn't find device2")

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
        if(event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP):
            if event.type == pygame.JOYBUTTONUP:
                value = False
            else:
                value = True
            if event.button == 6:
                program = 0
            elif event.button == 7:
                program = 1%N_PROGRAMS
            elif event.button == 8:
                program = (program+1)%N_PROGRAMS
            elif event.button == 9:
                program = 2%N_PROGRAMS
            elif event.button == 10:
                program = 3%N_PROGRAMS
            elif event.button == 11:
                program = 4%N_PROGRAMS
            elif event.button == 12:
                program = 5%N_PROGRAMS
            elif event.button in [5,13]:
                button_states[8] = value
            elif event.button in [4,14]:
                button_states[9] = value
            elif event.button == 0:
                button_states[1] = value
            elif event.button == 1:
                button_states[2] = value
            elif event.button == 2:
                button_states[3] = value
            elif event.button == 3:
                button_states[0] = value

        if event.type == pygame.JOYAXISMOTION:
            # Mirror right button logic on same layout
            if event.axis==3 and event.value < 0:
                button_states[0] = True
            if event.axis==3 and event.value > 0:
                button_states[1] = True
            if event.axis == 2 and event.value < 0:
                button_states[3] = True
            if event.axis == 2 and event.value > 0:
                button_states[2] = True
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
	for i in range(len(range_states)):
		range_states[i] = min(1, range_states[i] + 
							button_states[i*2]*RANGE_INCREMENT)
		range_states[i] = max(0, range_states[i] -
							button_states[i*2+1]*RANGE_INCREMENT)

def send_firestorm():
	url = "http://0.0.0.0/"
	var_payload = {}
	program_name = list(PROGRAM_PARAMS)[program]
	for (i, v) in enumerate(PROGRAM_PARAMS[program_name]):
		vrange = PROGRAM_PARAMS[program_name][v]
		var_payload[v] = (vrange[0] + 
							range_states[i]*(vrange[1]-vrange[0]))
	payload = {
		"command": {
			"programName": list(PROGRAM_PARAMS)[program],
			"setVars": var_payload
		},
		"ids": PIXELBLAZE_IDs
	}
	# print(payload)
	response = requests.post(url + 'command', json = payload)
	# print(response)

def main_loop():
    global joysticks, joystick_lastactive, JOYSTICK_TIMEOUT
    
    while True:
        time.sleep(0.5) # firestorm crashes on pi if updated too often

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
