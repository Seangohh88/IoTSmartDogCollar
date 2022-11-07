radio.set_group(107)
basic.show_icon(IconNames.STICK_FIGURE)

def on_forever():
    basic.pause(1000)
    radio.send_value("human", 1)
basic.forever(on_forever)