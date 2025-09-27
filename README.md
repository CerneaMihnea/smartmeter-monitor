# smartmeter-monitor

**Smartmeter Monitor** is a lightweight system for reading Modbus RTU (RS-485) energy meters using a **Raspberry Pi Pico 2 W** running MicroPython. It forwards telemetry to a **Flask server** which stores and displays values in a simple web interface.



## Features

- Pico-side data collector
  - Connects to Wi-Fi
  - Polls Modbus RTU registers over RS-485
  - Sends telemetry as JSON to the server
- Server-side backend
  - Flask-based web UI
  - Add new devices via `/add_device`
  - Stores latest readings in memory
- Configuration
  - Pico exposes `/device_config` (port `5001`) to accept settings
  - Server forwards form-based configs to Pico
- Tools
  - Works with [VS Code MicroPico extension](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) for file upload, REPL, and debugging



## Requirements

- Server
  - Python **3.8+**
  - `Flask`, `requests`
- Device
  - Raspberry Pi Pico W / Pico 2 W
  - MicroPython firmware installed
  - `umodbus` MicroPython package uploaded
- Network
  - Server and Pico reachable over LAN
  - Pico must reach server `/data`
  - Server must reach Pico `/device_config` (port `5001`)
- Optional
  - VS Code + `MicroPico` extension



## Quick Install

1. **Clone repository**  
   Download the repository to your local machine:
```bash
git clone https://your.git.repo/smartmeter-monitor.git
cd smartmeter-monitor
```

2. **Setup server environment**  
   Create and activate a Python virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Flash Pico with MicroPython**  
   Copy the appropriate UF2 firmware for Pico W / Pico 2 W to your device.

4. **Upload files to Pico**  
   Upload `main.py` and the `umodbus` package:
```bash
mpremote connect usb: cp main.py :
mpremote connect usb: cp -r umodbus :
```
   Alternatively, use VS Code MicroPico extension to sync files.

5. **Configure settings**  
   - Edit `main.py` with your Wi-Fi credentials and server IP/port.  
   - Optionally configure a static IP.  
   - Update the server `pico_url` to match your Pico endpoint.

6. **Run components**  
   Start the Flask server:
```bash
source venv/bin/activate
python3 server.py
```
   Reboot the Pico to run `main.py`. You can monitor the Pico logs using:


## Repository structure

```
smartmeter-monitor/
│
├── server.py        # Flask backend, web UI + config forwarding
├── main.py          # Pico MicroPython program
├── install_modbusrtu.py # Script for setting up Wi-Fi and installing MicroPython modules
├── test_registers.py # Script for testing Modbus RTU registers
├── umodbus/modbus.py        # Part of umodbus package
├── templates/       # Flask templates (index.html, device_detail.html)
└── requirements.txt # Python server dependencies
```



## Pico Configuration

- Wi-Fi: Configure credentials in `main.py` or use `install_mod.py`  
- Server: Set the `SERVER_IP` and `SERVER_PORT`  
- Static IP (optional): Use `sta.ifconfig(...)`  
- Modbus registers: Adjust in `main.py` based on your meter



## Additional Utilities

### 1. `install_modbusrtu.py`
This script helps set up Wi-Fi connectivity on the Pico and installs any additional MicroPython modules needed for your project. Users should edit it with their Wi-Fi credentials and run it once before running `main.py`.

### 2. `test_registers.py`
This script allows users to test communication with the Modbus RTU energy meter. It reads specific registers, interprets raw data, and prints results to the console. It's useful for debugging and verifying that your wiring and Modbus configuration are correct before integrating with the main program.



## VS Code MicroPico extension (recommended)

- Simplifies file upload and syncing to the Pico.  
- Provides REPL access for debugging.  
- Allows restarting the Pico and monitoring logs directly from VS Code.  



## Testing & API examples

- Users can simulate sending telemetry from the Pico to the server using HTTP POST requests.  
- The server can forward JSON configuration to the Pico via its `/device_config` endpoint.  
- Telemetry JSON includes values like device ID, serial number, import/export energy, and runtime hours.

## Troubleshooting

- Pico not connecting → check Wi-Fi credentials and network.  
- Server not receiving data → verify server IP, firewall, and network connectivity.  
- Configuration not reaching Pico → ensure the correct Pico endpoint URL is set.  
- `umodbus` import errors → make sure the full package is uploaded to the Pico.  
- Modbus read errors (nothing appers on the server end) → check wiring, DE/RE pin, slave ID, baud rate, and parity settings.



## Credits

- Author: Cernea Mihnea-Ioan  
- Libraries: [`umodbus`](https://github.com/brainelectronics/micropython-modbus/tree/develop/umodbus) (MicroPython), `Flask`  
- VS Code extension: `MicroPico` by paulober
