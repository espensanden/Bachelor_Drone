
from time import sleep
from picozero import pico_temp_sensor, pico_led
from machine import Pin, I2C, ADC
from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import mm_wlan
from pico_i2c_lcd import I2cLcd
import asyncio

#https://projects.raspberrypi.org/en/projects/get-started-pico-w/0
sleep(1)


I2C_ADDR     = 39
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

def lcd_connecting():
    
    lcd.clear()
    lcd.move_to(1,0)
    lcd.putstr("Connecting to")
    lcd.move_to(1,1)
    lcd.putstr(ssid)


ssid = 'ASUS' # house ssid = 'ASUS'
password = '4711942247' # password = '' 




lcd_connecting()
mm_wlan.connect_to_network(ssid, password)
app = Microdot()

pin_charger = Pin(16, mode=Pin.OUT)
green_led1 = Pin(6, mode =Pin.OUT)
green_led2 = Pin(7, mode =Pin.OUT)
red_led1 = Pin(8, mode = Pin.OUT)
red_led2 = Pin(9, mode = Pin.OUT)

def green_led_on():
    green_led1.on()
    green_led2.on()

def green_led_off():
    green_led1.off()
    green_led2.off()

def red_led_on():
    red_led1.on()
    red_led2.on()

def red_led_off():
    red_led1.off()
    red_led2.off()

INA_GAIN=1/10
charger_voltage = ADC(26)

conversion_factor = 3.3 / (4096)
Shunt_resistor = 0.26

red_led_off()
green_led_off()
#Lcd screen
lcd.clear()
lcd.move_to(1,0)
lcd.putstr("Connecting to")
lcd.move_to( 1,1)
lcd.putstr("controlcenter")


@app.route('/ws')
@with_websocket
async def read_sensor(request, ws):
    charger_curent_value_length = 0
    lcd.clear()
    while True:
        data = None
        try:
            data = await asyncio.wait_for(ws.receive(), timeout = 1)
        except asyncio.TimeoutError:
            pass
            
      

        print(data)
        if data == "CHARGING_PLATE_ON":
            pico_led.on()
            pin_charger.on()
        elif data == "CHARGING_PLATE_OFF":
            pico_led.off()
            pin_charger.off()
        elif data == "BUTTON":
            print("Button pressed")
            await ws.send("INDICATOR_LIGHT")
        elif data == "DRONE_IS_FULL_CHARGED":
            green_led_on()
        elif data == "DRONE_IS_CHARING":
            green_led_off()
        elif data == "DRONE_NO_POWER_FOUND":
            red_led_on()
        elif data == "DRONE_GET_POWER":
            red_led_off()
        if pin_charger.value():
            await ws.send("CHARGING_ON")
            print("charger")
        elif pin_charger.value() == False:
            await ws.send("CHARGING_OFF")
            print("charger off")

        
        
        charger_curent_value= round(((charger_voltage.read_u16() * conversion_factor)/ Shunt_resistor) * (INA_GAIN * 0.1)-0.006, 3)
        if charger_curent_value < 0.015:
            charger_curent_value = 0 
        print(charger_curent_value)
        await ws.send("CHARGER_VOLTAGE:"+str(charger_curent_value))
        if len(str(charger_curent_value)) != len(str(charger_curent_value_length)):
            lcd.clear()
        charger_curent_value_length = charger_curent_value
        lcd.move_to(1,0)
        lcd.putstr("Charger curent:")
        lcd.move_to(5,1)
        lcd.putstr(str(charger_curent_value) + "A")
    



app.run(port=80)