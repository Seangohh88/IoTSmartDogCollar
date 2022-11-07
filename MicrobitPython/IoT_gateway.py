def on_button_pressed_a():
    global outdoor
    outdoor = 1
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_received_string(receivedString):
    serial.write_line(receivedString)
radio.on_received_string(on_received_string)

def on_button_pressed_b():
    global outdoor
    outdoor = 0
input.on_button_pressed(Button.B, on_button_pressed_b)

def on_received_value(name, value):
    global last_signal
    if name == "dog":
        last_signal = 0
radio.on_received_value(on_received_value)

last_signal = 0
outdoor = 0
gateway_id = 1
radio.set_group(107)

def on_forever():
    global last_signal
    basic.pause(2000)
    last_signal += 1
    if last_signal >= 30 and last_signal % 30 == 0 and outdoor == 0:
        serial.write_line("missing" + ":" + "0" + ":" + ("" + str(gateway_id)))
basic.forever(on_forever)
