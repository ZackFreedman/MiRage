print('Top of the code to ya')

import board
import busio
import time
import usb_hid
import adafruit_ssd1306
import adafruit_framebuf
# from adafruit_hid.keyboard import Keyboard
from bitmap_keyboard import BitmapKeyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from pca950x import PCA950x
from mirage import KeyGrid
from keymapping import Keymap
from clicky_buttons import *
from util import timed_function
import parser

print('MiRage keyboard go!')

i2c = busio.I2C(board.GP7, board.GP6, frequency=576000)
i2c1 = busio.I2C(board.GP1, board.GP0, frequency=576000)
# usb_keyboard = Keyboard(usb_hid.devices) 
usb_keyboard = BitmapKeyboard(usb_hid.devices)
hid_keyboard_locale = KeyboardLayoutUS(usb_keyboard)

while not i2c.try_lock():
    print('Failed to lock I2C')
    time.sleep(0.5)

while not i2c1.try_lock():
    print('Failed to lock I2C1')
    time.sleep(0.5)

print("I2C addresses found on bus 0:", [hex(device_address)
              for device_address in i2c.scan()])

print("I2C addresses found on bus 1:", [hex(device_address)
              for device_address in i2c1.scan()])

i2c.unlock()
i2c1.unlock()

oleds = [adafruit_ssd1306.SSD1306_I2C(128, 64, i2c),
         adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3D),
         adafruit_ssd1306.SSD1306_I2C(128, 64, i2c1)]

for oled in oleds:
    oled.rotation = 2

try:
    oled_cool_lines = [['', '', '', '', '', '', '', ''],
                       ['', '', '', '', '', '', '', ''],
                       ['', '', '', '', '', '', '', '']]

    def cool_ass_parsing_visualizer(text):
        for oled in oleds:
            oled.fill(0)

        line_to_insert = text

        for oled, lines in zip(reversed(oleds), oled_cool_lines):
            lines.insert(0, line_to_insert)
            line_to_insert = lines.pop()

            for i, line in enumerate(reversed(lines)):
                oled.text(line, 0, i * 8, 1, font_name='/font5x8.bin')

            if line_to_insert == '':
                break

        for oled in oleds:
            oled.show()

    # parser.debug_line_callback = cool_ass_parsing_visualizer

    keymap = Keymap(usb_keyboard, hid_keyboard_locale)
    keymap.load('/MiRage Keymaps')  # TODO: Detect and automatically switch to Rage pad

    parser.debug_line_callback = None

    displays = [
        ClickyDisplay(oleds[0], 0),
        ClickyDisplay(oleds[1], 1),
        ClickyDisplay(oleds[2], 2)
    ]

    speedometer = SpeedometerWidget(oleds[0], 1)

    selector = LayerSelector(oleds[1], 1, keymap, wrap_enabled=True)
    selector.add_layer('base layer')
    selector.add_layer('function layer')
    selector.add_layer('numpad layer')
    selector.add_layer('macro pad layer')

    displays[0].attach(speedometer)
    displays[1].attach(selector)

    keeb = KeyGrid(i2c, keymap, displays)
    keeb.setup()

    print("ALL READY! It's time to c-c-c-c-clack!")

    while True:
        #benchmark = time.monotonic_ns()
        
        keeb.update()

        keymap.enact_queues()
        
        """
        try:
            print('Refresh rate: {:.0f}Hz'.format(1/(time.monotonic_ns() - benchmark)*1000000000))
        except ZeroDivisionError:
            pass
        """

finally:
    print('it ded')
    i2c.unlock()
    i2c1.unlock()
    usb_keyboard.release_all()