# firestorm-controller
Control pixelblazes with a gaming controller via firestorm

## Setup

### Install firestorm
Get firestorm [here](https://github.com/simap/Firestorm) and get it to work with your pixelblazes.

### Set up your controller
This project is set up for a Stadia controller. If you have a different one you'll need to change mappings.

On your raspberry, perform these steps to pair all controllers you want to use. This only needs to be done once.
* `sudo bluetoothctl`
* `agent on`
* `scan on` until you find the controller (not a bluetooth controller, it'll be a Device)
* copy the address of your controller (`XX:XX:XX:...`)
* `pair XX:XX:XX:...` 
* paste the addresses in the `main.py` file at `bluetoothprocess.stdin.write('connect YO:UR:AD:DR:ES:S\n')`
* repeat if you have more controllers and add more lines in the code

### Make sure the script is loaded on startup so you don't need a screen
TODO
