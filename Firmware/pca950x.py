from adafruit_register.i2c_struct import UnaryStruct, ROUnaryStruct
from adafruit_register.i2c_struct_array import StructArray
from adafruit_bus_device import i2c_device
from util import timed_function

# This only does input, because we're not using this device for output

class InputLine:
    __slots__ = 'bank', 'line', 'rose', 'fell', 'value'

    def __init__(self, bank, line):
        self.bank = bank
        self.line = line
        self.rose = False
        self.fell = False
        self.value = False

    def set_value(self, new_value):
        if self.value and not new_value:
            self.rose = False
            self.fell = True
        elif not self.value and new_value:
            self.rose = True
            self.fell = False
        else:
            self.rose = False
            self.fell = False

        self.value = new_value


class PCA950x:
    input_port_registers = ROUnaryStruct(0x00 + 0b10000000, '<BBBBB')  # This requires a modified Adafruit_Struct to work properly
    output_port_registers = StructArray(0x08, '<B', 5)
    polarity_registers = StructArray(0x10, '<B', 5)
    io_config_registers = StructArray(0x18, '<B', 5)
    mask_interrupt_registers = StructArray(0x20, '<B', 5)

    input_port_address = bytearray(1)
    input_port_address[0] = 0x00 | 0b10000000
    read_buffer = bytearray(5)

    def __init__(self, i2c_bus, address):
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)  # This must have this name for the UnaryStructs to work
        
        self.input_lines = []

        for bank in range(5):
            for line in range(8):
                self.input_lines.append(InputLine(bank, line))

        self.reset()

    def reset(self, invert=False):
        # Set all ports to inputs
        for register in self.io_config_registers:
            register = 0b11111111  # 0: Output. 1: Input

        if invert:
            for bank in range(len(self.polarity_registers)):
                self.polarity_registers[bank] = (0xFF,)

        self.update()

    def poll(self):
        with self.i2c_device as hw:
            hw.write_then_readinto(self.input_port_address, self.read_buffer)

    # @timed_function
    def update(self):
        self.poll()

        # all_reads = self.input_port_registers
        for bank, reads in enumerate(self.read_buffer):
            for i in range(8):
                self.input_lines[bank * 8 + i].set_value((reads >> i) & 0b00000001)



