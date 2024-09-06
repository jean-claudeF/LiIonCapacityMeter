# Switchoff voltage:
threshold = 3.0
Idischarge = 1.0

Q_As = 0
Q_mAh = 0

from machine import Pin, ADC, Timer, I2C, PWM
import time

timer = Timer()

btn_start = Pin(15, Pin.IN, Pin.PULL_UP)
btn_stop = Pin(14, Pin.IN, Pin.PULL_UP)
#led = Pin(25, Pin.OUT)
led = Pin('LED', Pin.OUT)

# OLED
from ssd1306 import SSD1306_I2C
i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = SSD1306_I2C(128, 64, i2c)

# DAC via PWM for current setting:
pwm = PWM(Pin(3))
pwm.duty_u16(32767)
pwm.freq(100000)

def set_dac(v):
    duty = int(65535 * v / 3.3)
    pwm.duty_u16(duty)


#--------------------------------------------------------------------
seconds = 0
voltage = 0

# ADC
a0 = Pin(26, Pin.IN) # his is needed to turn input to high impedance
a1 = Pin(27, Pin.IN) # this is needed to turn input to high impedance 
a2 = Pin(28, Pin.IN)
adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)


class LinCalc():
    # y = k0 + k1 * x
    def __init__(self, k0 = 0, k1 = 1):
        self.k0 = k0
        self.k1 = k1
        
    def calc(self, x):
        y = self.k0  + self.k1 * x
        return y
    
def readADC(adc, n = 10):
    # adc = adc0, adc1, adc2
    # n = nb of vallues for mean
    vm = 0
    for i in range(0, n):
        v = adc.read_u16()
        vm += v
    v = vm / n    
    v = v * 3.3 / 65535
    return v
   

clin0 = LinCalc(k0 = -0.02, k1 = 2 * 0.992073)
clin1 = LinCalc(k0 = -0.02, k1 = 2 * 0.992073)
clin2 = LinCalc(k0 = -0.02, k1 = 2 * 0.992073)

def get_adc():
    v0 = readADC(adc0)
    v0 = clin0.calc(v0)
    
    v1 = readADC(adc1)
    v1 = clin1.calc(v1)
    
    v2 = readADC(adc2)
    v2 = clin2.calc(v2)
    return v0, v1, v2

#----------------------------------------------------

def say_hello():
    print("LIon TEST")
    print("# I2C Address      : "+hex(i2c.scan()[0]).upper()) # Display device address
    print("# I2C Configuration: "+str(i2c))                   # Display I2C config
    print("# Waiting for start button")
    oled.fill(0)
    oled.text("ACCU TEST",5,5)
    oled.text("Waiting for start button",5,15)
    oled.show()
    time.sleep(1)



def print_values():
    s = "%i\t%.3f " % (seconds, voltage)
    print(s)

def oled_values():
    oled.fill(0)
    oled.text(str(seconds), 0, 0)
    oled.text("%.3f" % voltage, 0, 20)
    oled.show()
    
def set_current(I):
    set_dac(I)

def measure():
    global voltage
    v0, v1, v2 = get_adc()
    voltage = v0

#-------------------------------------------------------------
# Timer callback function
# This is wher it happens!
def timer_callback(void):
    # This is called via timer interrupt
    global seconds, voltage
    led.on()
    measure()
    print_values()
    oled_values()
    led.off()
    seconds += 1



#--------------------------------------------------------------------------------------
##   MAIN



set_current(0)
say_hello()

# Wait for button start
while btn_start.value():
    measure()
    print("##   %.3fV" % voltage, end = '\r')
    oled_values()
    time.sleep(0.05)

# Init timer and set discharge current
timer.init(period = 1000, callback = timer_callback)      # in ms!
print("\n # Start")
set_current(Idischarge)


# Wait for voltage < threshold or stop button
while btn_stop.value():
    measure()
    
    if voltage < threshold:
        set_current(0)
        break
    time.sleep(0.05)
timer.deinit()
print("# STOPPED at %.3fV" % voltage)    
#---------------------------------------------------------------------------------------
# Callback function must be defined before init timer!
    

#timer.init(freq = 1, mode = timer.PERIODIC, callback = do_it)       # in Hz!


