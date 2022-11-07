def on_button_pressed_b(): 
    global toilet_func, toilet_TimeCounter 
    toilet_func = 1 
    toilet_TimeCounter = 0 
input.on_button_pressed(Button.B, on_button_pressed_b)

def on_gesture_shake():
    global steps
    steps += 1
input.on_gesture(Gesture.SHAKE, on_gesture_shake)

def on_received_value(name, value): 
    if name == "violate" and value == DogNumber: 
        basic.show_icon(IconNames.SAD) 
        music.play_tone(262, music.beat(BeatFraction.WHOLE)) 
    if name == "gotoilet" and value == DogNumber: 
        basic.show_icon(IconNames.ROLLERSKATE) 
        music.play_tone(265, music.beat(BeatFraction.WHOLE)) 
    if name == "cali" and value == 0: 
        basic.show_icon(IconNames.TSHIRT) 
        basic.pause(500) 
        for index in range(10): 
            radio.send_value("cali", 1) 
            basic.pause(500) 
        radio.send_value("cali", 2) 
    if name == "cali" and value == 3: 
        basic.show_icon(IconNames.YES) 
radio.on_received_value(on_received_value)

toilet_TimeCounter = 0
toilet_func = 0
startbpm = 0
pulse_out = 0
maxloud = 0
time1 = 0
delta_t = 0
bpm = 0
time2 = 0
counter = 0
PulseDet = 0
timeCounteronemin = 0
timeCounter = 0
DogNumber = 0
steps = 0
music.set_volume(177)
radio.set_group(107)
serial.redirect_to_usb()

def on_forever():
    global timeCounter, timeCounteronemin, toilet_TimeCounter, laststeps, maxloud
    basic.pause(1000)
    radio.send_value("dog", DogNumber)
    timeCounter += 1
    timeCounteronemin = 60
    if timeCounter >= 60:
        radio.send_string("steps:" + ("" + str(DogNumber)) + ":" + ("" + str(steps)))
        radio.send_string("loudness:" + ("" + str(DogNumber)) + ":" + ("" + str(maxloud)))
        timeCounter = 0
        maxloud = 0
    if toilet_func == 1: 
        toilet_TimeCounter += 1 
    if toilet_TimeCounter >= 86400: 
        radio.send_value("toilettime", DogNumber) 
        toilet_TimeCounter = 0 
basic.forever(on_forever)

def on_forever2():
    # basic.show_number(pulse_out)
    basic.show_icon(IconNames.HEART)
basic.forever(on_forever2)

def on_forever3():
    global PulseDet
    PulseDet = pins.analog_read_pin(AnalogPin.P0)
basic.forever(on_forever3)

def on_forever4():
    serial.write_value("Pulse diagram", PulseDet)
    basic.pause(100)
basic.forever(on_forever4)

def on_forever5():
    global time2, bpm, delta_t, time1, counter, pulse_out
    if PulseDet > 670 and counter == 0:
        time2 = input.running_time()
        bpm += 1
        delta_t = time2 - time1
        time1 = time2
        counter = 1
        pulse_out = (60000 - 60000 % delta_t) / delta_t
    elif PulseDet <= 510 and counter == 1:
        counter = 0
basic.forever(on_forever5)

def on_forever6():
    global maxloud
    maxloud = max(maxloud,input.sound_level())
    if input.sound_level() > 128:
        radio.send_string("Too loud:" + ("" + str(DogNumber)) + ":" + ("" + str(input.sound_level())))
basic.forever(on_forever6)

def on_forever7():
    global startbpm, bpm
    startbpm = input.running_time()
    basic.pause(60000)
    if input.running_time() - startbpm > 60000:
        serial.write_value("BPM", bpm)
        basic.show_number(bpm)
        radio.send_string("bpm:" + ("" + str(DogNumber)) + ":" + ("" + str(bpm)))
        bpm = 0
basic.forever(on_forever7)
