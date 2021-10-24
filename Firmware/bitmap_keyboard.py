from adafruit_hid.keyboard import Keyboard, Keycode

class BitmapKeyboard(Keyboard):
    def __init__(self, devices):
        for device in devices:
            if device.usage == 6 and device.usage_page == 1:
                try:
                    device.send_report(b'\0' * 16)
                except ValueError:
                    print("found device but could not send report")
                    continue
                self._keyboard_device = device
                break
        else:
            raise RuntimeError("Could not find an HID keyboard device.")

        # report[0] modifiers
        # report[1:16] regular key presses bitmask
        self.report = bytearray(16)

        self.report_modifier = memoryview(self.report)[0:1]
        self.report_keys = memoryview(self.report)[1:]

    def _add_keycode_to_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        print (f"{keycode:02x} {modifier:02x}")
        if modifier:
            # Set bit for this modifier.
            self.report_modifier[0] |= modifier
        else:
            self.report_keys[keycode >> 3] |= 1 << (keycode & 0x7)

    def _remove_keycode_from_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            # Set bit for this modifier.
            self.report_modifier[0] &= ~modifier
        else:
            self.report_keys[keycode >> 3] &= ~(1 << (keycode & 0x7))

    def release_all(self):
        for i in range(len(self.report)):
            self.report[i] = 0
        self._keyboard_device.send_report(self.report)