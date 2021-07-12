import ssd1306
import machine
from machine import Pin, I2C, SPI
from sx127x import SX127x
import time
import os
import esp
import esp32
import ds18x20
from onewire import OneWire
from machine import Pin

powerpin = Pin(32, Pin.OUT)
datapin = Pin(25)
ds_sensor = ds18x20.DS18X20(OneWire(datapin))

lora_default = {
    'frequency': 868500000,
    'frequency_offset':0,
    'tx_power_level': 14,
    'signal_bandwidth': 125e3,
    'spreading_factor': 9,
    'coding_rate': 5,
    'preamble_length': 8,
    'implicitHeader': False,
    'sync_word': 0x34,
    'enable_CRC': True,
    'invert_IQ': False,
    'debug': False,
}

lora_pins = {
    'dio_0':26,
    'ss':18,
    'reset':16,
    'sck':5,
    'miso':19,
    'mosi':27,
}

esp.osdebug(None)
esp.osdebug(0)

print("Hello from micropython!")

oled_width = 128
oled_height = 64

i2c_rst = Pin(16, Pin.OUT)

i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1)

i2c_scl = Pin(15, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)

i2c = I2C(scl=i2c_scl, sda=i2c_sda)

oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)

oled.text('HELLO WiFi ESP32', 0, 25)
oled.show()
time.sleep(3)

#oled.line(0, 0, 50, 25, 1)


lora_spi = SPI(
    baudrate=10000000, polarity=0, phase=0,
    bits=8, firstbit=SPI.MSB,
    sck=Pin(lora_pins['sck'], Pin.OUT, Pin.PULL_DOWN),
    mosi=Pin(lora_pins['mosi'], Pin.OUT, Pin.PULL_UP),
    miso=Pin(lora_pins['miso'], Pin.IN, Pin.PULL_UP),
)

lora = SX127x(lora_spi, pins=lora_pins, parameters=lora_default)
powerpin.value(1)
print("AAAAAAAAAAAAAAAAAAa")
roms = ds_sensor.scan()
print('Found DS devices: ', roms)

def send(lora, oled):
    counter = 0
    oled.text("Sender", 0, 25)
    data = 0
    while True:
        ds_sensor.convert_temp()
        time.sleep_ms(750)
        for rom in roms:
            print(rom)
            data = ds_sensor.read_temp(rom)
        time.sleep(5)
        #photoresPowerPin.off()
        payload = str(data)
        oled.fill(0)
        oled.text("ph: {}".format(str(data)), 0, 25)
        oled.text('TX: {}'.format(str(counter)), 0, 50)
        oled.show()
        lora.println(payload)
        counter -= 1
        time.sleep(1)

def recv(lora, oled):
    oled.text("Reciever", 0, 25)
    while True:
        if lora.receivedPacket():
            try:
                payload = lora.readPayload().decode()
                rssi = lora.packetRssi()
                oled.fill(0)
                oled.text("RX: {}".format(payload), 0, 25)
                oled.text("RSSI: {}".format(rssi), 0, 55)
                oled.show()
            except Exception as e:
                time.sleep_ms(1)


if "recv" in os.listdir():
    recv(lora, oled)
else:
    send(lora, oled)

