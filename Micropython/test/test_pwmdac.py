from machine import PWM, Pin
pwm = PWM(Pin(3))
pwm.duty_u16(32767)
pwm.freq(100000)

def set_dac(v):
    duty = int(65535 * v / 3.3)
    pwm.duty_u16(duty)

while True:
    v = float(input("Voltage (0...3.3V): "))
    set_dac(v)
    
