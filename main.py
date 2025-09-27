import network, socket, struct, time, json, _thread
from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin

# — Wi‑Fi static —
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.ifconfig(("10.10.28.25", "255.255.0.0", "10.10.109.1", "8.8.8.8"))
sta.connect("WiFi", "12345678")
for _ in range(10):
    if sta.isconnected():
        break
    time.sleep(1)
if sta.isconnected() :
    print("Connected to Wi-fi")
else :
    print("Nu e bine!")

# — Server Flask de date —
SERVER_IP   = "10.10.103.181"
SERVER_PORT = 5000

# — Dispozitive configure (populate via HTTP) —
devices = {}


def config_server():
    s = socket.socket()
    s.bind(("0.0.0.0", 5001))
    s.listen(1)
    print("Server started on port 5001")
    while True:
        cl, _ = s.accept()
        data = b""
        # citim header + body început
        while b"\r\n\r\n" not in data:
            chunk = cl.recv(64)
            if not chunk:
                break
            data += chunk
        try:
            hdr, body = data.split(b"\r\n\r\n", 1)
            # găsim Content-Length
            length = 0
            for line in hdr.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    length = int(line.split(b":")[1])
            # citim restul body-ului
            while len(body) < length:
                body += cl.recv(length - len(body))
            cfg = json.loads(body)
            did = cfg.get("device_id")
            if not did:
                raise ValueError("Missing device_id")
            devices[did] = cfg
            cl.send(b"HTTP/1.1 200 OK\r\n\r\nDevice added")
            print("Configured:", did, cfg)
        except Exception as e:
            print("Config error:", e)
            cl.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
        cl.close()

def modbus_loop():

    while True:
        #if sta.isconnected() :
            #print("Connected to Wi-fi")
        for device_id, configuration in devices.items():
            parity_raw = configuration.get("parity", None)
            if parity_raw in [None, "None"]:
                parity_val = None
            else:
                parity_val = int(parity_raw)

            rtu = ModbusRTUMaster(
                    pins=(Pin(0), Pin(1)),
                    uart_id=0, 
                    baudrate=int(configuration.get("baudrate", 9600)),
                    data_bits=int(configuration.get("data_bits", 8)), 
                    stop_bits=int(configuration.get("stop_bits", 1)),
                    parity = parity_val,
                    ctrl_pin=2
                )

            try:
                
                sid = int(configuration.get("slave_id", 2))
                regs = rtu.read_input_registers(sid, 86, 16)

                regs = [r & 0xFFFF for r in regs]
                
                b = bytes([regs[0] >> 8, regs[0] & 0xFF, regs[1] >> 8, regs[1] & 0xFF])
                import_ergy = struct.unpack(">f", b)[0]
                b = bytes([regs[2] >> 8, regs[2] & 0xFF, regs[3] >> 8, regs[3] & 0xFF])
                export_ergy = struct.unpack(">f", b)[0]
                b = bytes([regs[14] >> 8, regs[14] & 0xFF, regs[15] >> 8, regs[15] & 0xFF])
                run_hour = struct.unpack(">f", b)[0]

                time.sleep_ms(10)

                regs = rtu.read_input_registers(sid, 684, 2)

                regs = [r & 0xFFFF for r in regs]
                
                b = bytes([regs[0] >> 8, regs[0] & 0xFF, regs[1] >> 8, regs[1] & 0xFF])
                serial_nb = struct.unpack(">I", b)[0]

                payload = json.dumps({
                    "device_id": device_id,
                    "serial_nb": serial_nb,
                    "import_energy": import_ergy,
                    "export_energy": export_ergy,
                    "run_hour" : run_hour
                })
                req = (
                    "POST /data HTTP/1.1\r\n"
                    "Host: %s:%d\r\n"
                    "Content-Type: application/json\r\n"
                    "Content-Length: %d\r\n\r\n"
                    "%s"
                ) % (SERVER_IP, SERVER_PORT, len(payload), payload)
                s2 = socket.socket()
                s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s2.connect((SERVER_IP, SERVER_PORT))
                s2.send(req)
                s2.close()
                #print("Sent", device_id, "imp=", import_ergy, "exp=", export_ergy)
            except Exception as e:
                print("Modbus error", device_id, e)
        time.sleep(1)
  
# — pornim server-ul de configurare pe un thread —
_thread.start_new_thread(config_server, ())

if sta.isconnected() :
    print("Connected to Wi-fi")

# — bucla principală Modbus+forwarding —
modbus_loop()