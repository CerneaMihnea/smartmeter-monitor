import struct, time
from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin
import asyncio

def modbus_loop():
    rtu = ModbusRTUMaster(
        pins=(Pin(0), Pin(1)),
        uart_id=0, baudrate=9600,
        data_bits=8, stop_bits=1,
        parity=None, ctrl_pin=2
    )
    while True:
        try:
            # Adresa corectă: 30684 - 30001 = 683
            regs = rtu.read_input_registers(2, 86, 2)
            print("Raw registers:", regs)

            # Convertim la uint16 dacă apar valori negative
            regs = [r & 0xFFFF for r in regs]

            # Formăm uint32 (big endian)
            b = bytes([
                regs[0] >> 8, regs[0] & 0xFF,
                regs[1] >> 8, regs[1] & 0xFF
            ])
            serial_number = struct.unpack(">f", b)[0]
            print("Serial Number:", serial_number)

            time.sleep(0.1)

            regs = rtu.read_input_registers(2, 684, 2)
            print("Raw registers:", regs)

            # Convertim la uint16 dacă apar valori negative
            regs = [r & 0xFFFF for r in regs]

            # Formăm uint32 (big endian)
            b = bytes([
                regs[0] >> 8, regs[0] & 0xFF,
                regs[1] >> 8, regs[1] & 0xFF
            ])
            serial_number = struct.unpack(">I", b)[0]
            print("Serial Number:", serial_number)

        except Exception as e:
            print("Modbus error:", e)
        time.sleep(1)


modbus_loop()