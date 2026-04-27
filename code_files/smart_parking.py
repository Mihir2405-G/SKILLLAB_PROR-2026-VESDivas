from machine import Pin, PWM
import time

# -------- SERVO --------
servo = PWM(Pin(18))
servo.freq(50)

def set_angle(angle):
    duty = int(1638 + (angle / 180) * (8192 - 1638))
    servo.duty_u16(duty)

# -------- IR SENSOR --------
ir = Pin(28, Pin.IN)

# -------- ULTRASONIC 1 --------
trig1 = Pin(22, Pin.OUT)
echo1 = Pin(21, Pin.IN)

# -------- ULTRASONIC 2 --------
trig2 = Pin(20, Pin.OUT)
echo2 = Pin(19, Pin.IN)

def get_distance(trig, echo):
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()

    timeout = 30000

    start = time.ticks_us()
    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), start) > timeout:
            return None

    signal_on = time.ticks_us()

    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), signal_on) > timeout:
            return None

    signal_off = time.ticks_us()

    duration = time.ticks_diff(signal_off, signal_on)
    return (duration * 0.0343) / 2


# -------- 7 SEGMENT --------
seg = [
    Pin(5, Pin.OUT),  # a
    Pin(6, Pin.OUT),  # b
    Pin(7, Pin.OUT),  # c
    Pin(8, Pin.OUT),  # d
    Pin(9, Pin.OUT),  # e
    Pin(10, Pin.OUT), # f
    Pin(11, Pin.OUT)  # g
]

digits = {
    0: [1,1,1,1,1,1,0],
    1: [0,1,1,0,0,0,0],
    2: [1,1,0,1,1,0,1]
}

def display(n):
    pattern = digits[n]
    for i in range(7):
        seg[i].value(pattern[i])


# -------- INITIAL --------
set_angle(0)

while True:

    # -------- GATE CONTROL --------
    if ir.value() == 1:
        set_angle(90)
    else:
        set_angle(0)

    # -------- SLOT DETECTION --------
    d1 = get_distance(trig1, echo1)
    d2 = get_distance(trig2, echo2)

    slot1 = 1 if (d1 is not None and d1 < 6) else 0
    slot2 = 1 if (d2 is not None and d2 < 6) else 0

    slots_left = 2 - (slot1 + slot2)

    # -------- DISPLAY --------
    display(slots_left)

    print("Slots left:", slots_left)

    time.sleep(0.5)