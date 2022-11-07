def on_button_pressed_a():
    global total_strength, total_counter, threshold,adj
    basic.show_icon(IconNames.TSHIRT)
    radio.send_value("cali", 0)
    total_strength = 0
    total_counter = 0
    threshold = 0
    adj=1
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_received_value(name, value):
    global total_strength, total_counter, threshold, human, humantime,adj
    if name == "dog" and radio.received_packet(RadioPacketProperty.SIGNAL_STRENGTH) > threshold:
        radio.send_value("violate", value)
        radio.send_string("violate:" + ("" + str(value)) + ":" + ("" + str(RoomNumber)))
        radio.send_value("rssi",
            radio.received_packet(RadioPacketProperty.SIGNAL_STRENGTH))
    if name == "cali" and value == 1 and adj==1:
        total_strength += radio.received_packet(RadioPacketProperty.SIGNAL_STRENGTH)
        total_counter += 1
    if name == "cali" and value == 2 and adj==1:
        avg_sig = total_strength / total_counter
        threshold = avg_sig
        radio.send_value("cali", 3)
        basic.show_number(avg_sig)
        adj=0
    if name == "human" and value == 1:
        human = 1
        humantime = 360
radio.on_received_value(on_received_value)

adj=0
humantime = 0
human = 0
total_counter = 0
total_strength = 0
RoomNumber = 0
threshold = 0
threshold = -50
RoomNumber = 1
timecounter=0
infra=0
radio.set_group(107)
basic.show_icon(IconNames.SQUARE)

def on_forever():
    global humantime, human,timecounter
    basic.pause(1000)
    if humantime > 0:
        humantime = humantime - 1
    if human == 1 and humantime == 0:
        human = 0
    if human==0:
        infrared=pins.analog_read_pin(AnalogPin.P1)
        infrared_d= pins.digital_read_pin(DigitalPin.P1)
        radio.send_string("ir:"+str(infrared_d))
    if timecounter>0:
        timecounter= timecounter-1
        if human==0:
            radio.send_string("time_to_next"+str(timecounter))
    if timecounter<=0 and infrared_d==1 and human <=0:
        radio.send_string("motion:" + ("" + str(1)) + ":" + ("" + str(RoomNumber)))
        timecounter=30
basic.forever(on_forever)