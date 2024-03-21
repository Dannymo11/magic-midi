import mido

# List all available MIDI outputs
print("Available MIDI output ports:")
for output in mido.get_output_names():
    print(output)

# List all available MIDI inputs
print("\nAvailable MIDI input ports:")
for input in mido.get_input_names():
    print(input)