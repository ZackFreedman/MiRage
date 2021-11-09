import time

class BoundAction:
    __slots__ = 'owner'

    def __init__(self):
        self.owner = None

    def associate_with(self, keymap):
        self.owner = keymap

    def one_shot(self):
        pass

    def start_hold(self):
        pass

    def continue_hold(self):
        pass

    def end_hold(self):
        pass


class GenericKeyAction(BoundAction):
    __slots__ = 'keycodes'  # Mysterious memory management malarkey - may not work

    def __init__(self, keycodes):
        super().__init__()
        if isinstance(keycodes, list):
            self.keycodes = keycodes
        elif isinstance(keycodes, int):
            self.keycodes = [keycodes]
        else:
            raise AttributeError('Must be a keycode/list of keycodes')

    def press_key(self, keyboard):
        for code in self.keycodes:
            # print('Pressing', hex(code))
            keyboard.press(code)

    def release_key(self, keyboard):
        for code in self.keycodes:
            # print('Releasing', hex(code))
            keyboard.release(code)

    def one_shot(self):
        self.press_key(self.owner.hid_keyboard)
        self.release_key(self.owner.hid_keyboard)

    def start_hold(self):
        self.press_key(self.owner.hid_keyboard)

    def end_hold(self):
        self.release_key(self.owner.hid_keyboard)

        # This could cause problems if we click a key while the same key is held

    def __eq__(self, obj):
        return isinstance(self, type(obj)) and self.keycodes == obj.keycodes


class PressKeyAction(GenericKeyAction):
    def one_shot(self):
        self.press_key(self.owner.hid_keyboard)

    def start_hold(self):
        self.press_key(self.owner.hid_keyboard)

    def end_hold(self):
        pass


class ReleaseKeyAction(GenericKeyAction):
    def one_shot(self):
        self.release_key(self.owner.hid_keyboard)

    def start_hold(self):
        self.release_key(self.owner.hid_keyboard)

    def end_hold(self):
        pass


class ClickKeyAction(GenericKeyAction):
    def one_shot(self):
        self.press_key(self.owner.hid_keyboard)
        self.release_key(self.owner.hid_keyboard)
        

    def start_hold(self):
        self.press_key(self.owner.hid_keyboard)
        self.release_key(self.owner.hid_keyboard)


    def end_hold(self):
        pass


class SequenceAction(BoundAction): 
    __slots__ = 'sequence'
    # that = not falcon

    def __init__(self):
        super().__init__()
        self.sequence = []

    def one_shot(self):
        for action in self.sequence:
            action.one_shot()

    def start_hold(self):
        for action in self.sequence:
            action.start_hold()

    def continue_hold(self):
        for action in self.sequence:
            action.continue_hold()

    def end_hold(self):
        for keycode in self.sequence:
            action.end_hold()

    def __eq__(self, obj):
        if not isinstance(obj, SequenceAction):
            return False
            
        for action in self.sequence:
            if not action in obj.sequence:
                return False # This will probably fail, fix it

        return True


class DelayAction(BoundAction):
    __slots__ = 'duration'

    def __init__(self, duration):
        super().__init__()
        self.duration = duration

    def one_shot(self):
        # Does this need to be asynchronous?
        time.sleep(self.duration)

    def start_hold(self):
        self.one_shot()

    def __eq__(self, obj):
        return self.duration == obj.duration


class GenericLayerAction(BoundAction):
    __slots__ = 'target_layer'

    def __init__(self, target_layer_name):
        super().__init__()
        self.target_layer = target_layer_name

    def __eq__(self, obj):
        return type(self) is type(obj) and self.target_layer == obj.target_layer


class SwitchToLayerAction(GenericLayerAction):
    def one_shot(self):
        self.owner.queue_switch_to(self.target_layer)

    def start_hold(self):
        self.one_shot()


class TemporaryLayerAction(GenericLayerAction):
    def start_hold(self):
        self.owner.queue_switch_to(self.target_layer)

    def end_hold(self):
        self.owner.queue_dismiss(self.target_layer)


class LeaveLayerAction(GenericLayerAction):
    def one_shot(self):
        self.owner.queue_dismiss(self.target_layer)

    def start_hold(self):
        self.one_shot()


class ToggleLayerAction(GenericLayerAction):
    def one_shot(self):
        if len(self.owner.layer_stack) and\
            self.target_layer.lower() == self.owner.layer_stack[-1].name.lower():
            self.owner.queue_dismiss(self.target_layer)
        else:
            self.owner.queue_switch_to(self.target_layer)

    def start_hold(self):
        self.one_shot()


class StringTyperAction(BoundAction):
    __slots__ = 'payload', 'typing_rate', 'delay_between_repeats', 'last_fire_timestamp'

    def __init__(self, el_stringerino, delay_between_keystrokes, repeat_every=None):
        super().__init__()
        self.payload = el_stringerino.replace('[DOUBLE QUOTES]', '"')
        self.typing_rate = delay_between_keystrokes
        self.delay_between_repeats = repeat_every
        self.last_fire_timestamp = -9999

    def one_shot(self):
        for index, char in enumerate(self.payload):
            if index != 0: # Prevents unnecessary delay after final char
                time.sleep(self.typing_rate)
            self.owner.hid_keyboard_layout.write(char)
        self.last_fire_timestamp = time.monotonic()

    def start_hold(self):
        self.one_shot()

    def continue_hold(self):
        if self.delay_between_repeats is None\
            or time.monotonic() - self.last_fire_timestamp >= self.delay_between_repeats:
            self.one_shot()

    # No equality override - all of these are distinct


# Same as StringTyperAction, but doesn't repeat if used in a Hold
class NonRepeatingStringTyperAction(StringTyperAction):
    def __init__(self, el_stringerino, delay_between_keystrokes):
        super().__init__(el_stringerino, delay_between_keystrokes)

    def continue_hold(self):
        pass

    def __eq__(self, obj):
        return isinstance(obj, NonRepeatingStringTyperAction) \
            and self.payload == obj.payload \
            and self.typing_rate == obj.typing_rate

class ResetKeebAction(BoundAction):
    def one_shot(self):
        supervisor.reload()

    def start_hold(self):
        supervisor.reload()

    def __eq__(self, obj):
        return isinstance(obj, ResetKeebAction)


class KeebBootloaderAction(BoundAction):
    def one_shot(self):
        microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
        microcontroller.reset()

    def start_hold(self):
        microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
        microcontroller.reset()

    def __eq__(self, obj):
        return isinstance(obj, KeebBootloaderAction)

class ResetLayersAction(BoundAction):
    def one_shot(self):
        self.owner.queue_reset()

    def start_hold(self):
        self.owner.queue_reset()

    def __eq__(self, obj):
        return isinstance(obj, ResetLayersAction)


class NothingburgerAction(BoundAction):
    pass


class PassThroughAction(BoundAction):
    pass

    """
    __slots__ = 'layer_number', 'row', 'column'

    _keymap = None

    def __init__(self, keymap, layer_number, row, column):
        super().__init__()
        PassThroughAction._keymap = keymap
        self.layer_number = layer_number
        self.row = row
        self.column = column

    def start_hold(self):
        
        if self.layer_number > 0:
            PassThroughAction._keymap
                .layer_stack[self.layer_number - 1].key_bindings[self.row, self.column].start_hold()

    def continue_hold(self):
        super().continue_hold()
        if self.layer_number > 0::
            PassThroughAction._keymap
                .layer_stack[self.layer_number - 1].key_bindings[self.row, self.column].continue_hold()

    def end_hold(self):
        
        if self.layer_number > 0:
            PassThroughAction._keymap
                .layer_stack[self.layer_number - 1].key_bindings[self.row, self.column].continue_hold()

    def __eq__(self, obj):
        return isinstance(obj, PassThroughAction)
    """

class ReloadKeymapAction(BoundAction):
    def one_shot(self):
        self.owner.queue_reload()

    def start_hold(self):
        self.owner.queue_reload()

    def __eq__(self, obj):
        return isinstance(obj, ReloadKeymapAction)
