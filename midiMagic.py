from pythonosc import dispatcher as osc_dispatcher
from pythonosc import osc_server
import mido
import time
from threading import Thread
import queue


# Setup MIDI
outport = mido.open_output('Logic Pro Virtual In')
REVERB_CC_NUM = 8
PANNING_CC_NUM = 10
active_osc_message = None 

increase_reverb_active = False
decrease_reverb_active = False


# Store current CC values
current_cc_values = {REVERB_CC_NUM: 0, PANNING_CC_NUM: 64}


def pan_left(channel=0, intensity=64):
    new_value = max(0, current_cc_values[PANNING_CC_NUM] - intensity)
    send_control_change(PANNING_CC_NUM, new_value, channel)
    current_cc_values[PANNING_CC_NUM] = new_value
    print(f"Panned Left")

def pan_right(channel=0, intensity=64):
    new_value = min(127, current_cc_values[PANNING_CC_NUM] + intensity)
    send_control_change(PANNING_CC_NUM, new_value, channel)
    current_cc_values[PANNING_CC_NUM] = new_value
    print(f"Panned Right")

def increase_reverb(increase_by=1):
    global increase_reverb_active
    while increase_reverb_active:
        current_value = current_cc_values[REVERB_CC_NUM]
        new_value = min(current_value + 2, 127)
        send_control_change(REVERB_CC_NUM, new_value)
        current_cc_values[REVERB_CC_NUM] = new_value
        print(f"Special Sauce increased to {new_value}")
        time.sleep(0.2)


def decrease_reverb(decrease_by=30):
    global decrease_reverb_active
    while decrease_reverb_active:
        current_value = current_cc_values[REVERB_CC_NUM]
        new_value = max(current_value - 2, 0)
        send_control_change(REVERB_CC_NUM, new_value)
        current_cc_values[REVERB_CC_NUM] = new_value
        print(f"Special Sauce decreased to {new_value}")
        time.sleep(0.2)


def gesture_3_handler(_):
    pan_left()
    time.sleep(1)

def gesture_4_handler(_):
    pan_right()
    time.sleep(1)

def gesture_5_handler(_):
    global decrease_reverb_active
    if not decrease_reverb_active:
        decrease_reverb_active = True
        reverb_thread = Thread(target=decrease_reverb)
        reverb_thread.start()
        time.sleep(1)

def gesture_6_handler(_):
    global increase_reverb_active
    # Start increasing reverb only if it's not already doing so
    if not increase_reverb_active:
        increase_reverb_active = True  # Enable the reverb increase loop
        reverb_thread = Thread(target=increase_reverb)  # Start increase_reverb in a separate thread
        reverb_thread.start()
        time.sleep(1)  # Keep this sleep if needed, or remove if not necessary


def send_control_change(cc_number, value, channel=0):
    cc_message = mido.Message('control_change', control=cc_number, value=value, channel=channel)
    outport.send(cc_message)
    print(f"Sent CC message: {cc_message}")

def osc_message_handler(addr, *args):
    global active_osc_message, increase_reverb_active, decrease_reverb_active
    # When a new OSC message is received, update the active message
    # and stop increasing reverb if the message is not "/output_6", 
    # and stop decreasing reverb if the message is not "/output_5"
    if active_osc_message != addr:
        active_osc_message = addr
        if addr != "/output_6":
            increase_reverb_active = False
        if addr != "/output_5":
            decrease_reverb_active = False

# Setup OSC
dispatcher = osc_dispatcher.Dispatcher()  # Change made here
dispatcher.map("/output_1", osc_message_handler)
dispatcher.map("/output_2", osc_message_handler) 
dispatcher.map("/output_3", osc_message_handler)
dispatcher.map("/output_4", osc_message_handler) 
dispatcher.map("/output_5", osc_message_handler)
dispatcher.map("/output_6", osc_message_handler)
dispatcher.map("/output_3", gesture_3_handler)
dispatcher.map("/output_4", gesture_4_handler)
dispatcher.map("/output_5", gesture_5_handler)
dispatcher.map("/output_6", gesture_6_handler)


# Assuming Wekinator is sending to the default port 12000 on localhost
server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 12000), dispatcher)
print("Serving on {}".format(server.server_address))

# Start the server
server.serve_forever()

