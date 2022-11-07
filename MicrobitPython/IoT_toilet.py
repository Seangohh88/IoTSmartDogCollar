def on_button_pressed_b():
    global total_strength, total_counter, threshold, adj
    basic.show_icon(IconNames.TSHIRT)
    radio.send_value("cali", 0)
    total_strength = 0
    total_counter = 0
    threshold = 0
    adj = 1
input.on_button_pressed(Button.B, on_button_pressed_b)

def on_received_value(name, value):
    global intoilet, total_strength, total_counter, threshold, adj
    if name == "dog" and radio.received_packet(RadioPacketProperty.SIGNAL_STRENGTH) <= threshold and toilettime > 0:
        radio.send_value("gotoilet", value)
        radio.send_string("toilettime:" + ("" + str(value)) + ":" + ("" + str(ToiletNumber)))
        intoilet = 0
    if name == "dog" and radio.received_packet(RadioPacketProperty.SIGNAL_STRENGTH) > threshold and toilettime > 0:
        intoilet = 1
    if name == "cali" and value == 1 and adj == 1:
        total_strength += radio.received_packet(RadioPacketProperty.SIGNAL_STRENGTH)
        total_counter += 1
    if name == "cali" and value == 2 and adj == 1:
        avg_sig = total_strength / total_counter
        threshold = avg_sig
        radio.send_value("cali", 3)
        basic.show_number(avg_sig)
        adj = 0
    if name == "toilettime":
        toilettime = 60
radio.on_received_value(on_received_value)

toilettime2 = 0
intoilet = 0
adj = 0
total_counter = 0
total_strength = 0
ToiletNumber = 0
threshold = 0
threshold = -50
ToiletNumber = 1
radio.set_group(107)
basic.show_icon(IconNames.SQUARE)

def on_forever():
    global toilettime2
    basic.pause(1000)
    if intoilet == 1 and toilettime2 > 0:
        toilettime2 = toilettime2 - 1
basic.forever(on_forever)
