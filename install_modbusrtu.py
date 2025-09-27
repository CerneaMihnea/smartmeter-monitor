import network
import time

print("start")
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.ifconfig(("10.10.28.25", "255.255.0.0", "10.10.109.1", "8.8.8.8"))
sta.connect("WiFi", "12345678")
for _ in range(10):
    if sta.isconnected():
        break
    time.sleep(1)
print("Connected to Wi-fi")

import mip
mip.install('github:brainelectronics/micropython-modules')
