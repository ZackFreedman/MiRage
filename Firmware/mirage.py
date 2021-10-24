import time
from pca950x import PCA950x
from util import timed_function

physical_key_assignments = {
    (0, 0, 5): (0, 1),  #  (which PCA9505, which bank, which line): (row, col)
    (0, 0, 6): (0, 2),
    (0, 0, 7): (0, 3),
    (0, 1, 0): (2, 4),
    (0, 1, 1): (1, 4),
    (0, 1, 2): (0, 4),
    (0, 1, 3): (3, 5),
    (0, 1, 4): (2, 5),
    (0, 1, 5): (1, 5),
    (0, 1, 6): (0, 5),
    (0, 1, 7): (4, 4),
    (0, 2, 0): (3, 6),
    (0, 2, 1): (2, 6),
    (0, 2, 2): (1, 6),
    (0, 2, 3): (0, 6),
    (0, 2, 5): (3, 4),
    (0, 2, 6): (4, 3),
    (0, 2, 7): (4, 2),
    (0, 3, 0): (1, 3),
    (0, 3, 1): (2, 3),
    (0, 3, 2): (3, 3),
    (0, 3, 4): (1, 2),
    (0, 3, 5): (2, 2),
    (0, 3, 6): (3, 2),
    (0, 3, 7): (4, 1),
    (0, 4, 0): (1, 1),
    (0, 4, 1): (2, 1),
    (0, 4, 2): (0, 0),
    (0, 4, 3): (3, 1),
    (0, 4, 4): (1, 0),
    (0, 4, 5): (2, 0),
    (0, 4, 6): (3, 0),
    (0, 4, 7): (4, 0),
    (1, 0, 0): (1, 11),
    (1, 0, 1): (1, 10),
    (1, 0, 2): (1, 9),
    (1, 0, 3): (1, 8),
    (1, 0, 4): (1, 7),
    (1, 0, 5): (2, 11),
    (1, 0, 6): (2, 10),
    (1, 0, 7): (2, 9),
    (1, 1, 0): (2, 8),
    (1, 1, 1): (2, 7),
    (1, 1, 2): (3, 11),
    (1, 1, 3): (4, 8),
    (1, 1, 5): (4, 7),
    (1, 1, 6): (4, 6),
    (1, 1, 7): (4, 5),
    (1, 2, 0): (3, 7),
    (1, 2, 1): (3, 8),
    (1, 2, 2): (3, 9),
    (1, 2, 3): (3, 10),
    (1, 3, 1): (0, 7),
    (1, 3, 2): (0, 8),
    (1, 3, 3): (0, 9),
    (1, 3, 4): (0, 10),
    (1, 3, 5): (0, 11)
}

screen_button_assignments = {
    (1, 3, 6): (0, 0),  # Top screen, left button
    (1, 3, 7): (1, 0),
    (1, 4, 0): (2, 0),
    (1, 4, 5): (0, 1),
    (1, 4, 6): (1, 1),
    (1, 4, 7): (2, 1)
}


class IOAssociation:
    __slots__ = 'input_line', 'row', 'col', 'is_a_key'

    def __init__(self, input_line, row, col, is_a_key):
        self.input_line = input_line
        self.row = row
        self.col = col
        self.is_a_key = is_a_key


class KeyGrid:
    def __init__(self, i2c, keymap, clicky_displays, keys=physical_key_assignments, buttons=screen_button_assignments):
        self.io_expanders = []
        self.key_associations = []

        self.i2c = i2c  # Should already be locked
        self.keymap = keymap
        self.clicky_displays = clicky_displays
        self.keys = keys
        self.buttons = buttons

        self.key_down_timestamps = {}
        self.keys_held = []
        self.recent_key_clicks = {}

        self.click_timeout = 0.1  # Release the key within this many seconds to fire a click
        self.double_click_timeout = 0.2  # Click again within this many seconds to fire a double click

    def setup(self):
        self.io_expanders.append(PCA950x(self.i2c, 0x23))
        self.io_expanders.append(PCA950x(self.i2c, 0x20))

        for io_expander in self.io_expanders:
            io_expander.reset()

        for index, io_expander in enumerate(self.io_expanders):
            for input_line in io_expander.input_lines:
                coords = index, input_line.bank, input_line.line

                if coords in self.keys:
                    row, col = self.keys[coords]
                    is_a_key = True
                elif coords in self.buttons:
                    row, col = self.buttons[coords]
                    is_a_key = False
                else:
                    continue

                self.key_associations.append(IOAssociation(input_line, row, col, is_a_key))

    # @timed_function
    def update(self):
        for index, io_expander in enumerate(self.io_expanders):
            io_expander.update()

        for line in self.key_associations:
            if line.input_line.fell:  # Key pressed down
                if line.is_a_key:
                    # print('Row {}, col {} pressed'.format(line.row, line.col))
                    self.keymap.fire_operation(line.row, line.col, 'press')
                    if self.clicky_displays is not None:
                        for display in self.clicky_displays:
                            display.on_keystroke(0x00)  # TODO: Only do something if a key was pressed, and pass in which key

                elif self.clicky_displays is not None:  # Is a clicky screen button
                    # print('Display {} {}-clicked'.format(line.row, 'right' if line.col else 'left'))
                    self.clicky_displays[line.row].on_click(line.col)

                self.key_down_timestamps[line] = time.monotonic()

            elif line.input_line.rose:
                if line in self.key_down_timestamps:
                    hold_length = time.monotonic() - self.key_down_timestamps[line]
                    # print('Held for', hold_length)
                else:
                    hold_length = 666
                    # print('WEIRD SHIT - Key rose without previously falling')

                del self.key_down_timestamps[line]

                if line.is_a_key:
                    # print('Row {}, col {} went high after {}ms'.format(line.row, line.col, hold_length))
                    
                    if hold_length <= self.click_timeout:
                        is_double_click = False

                        # print("That's a click")
                        
                        if line in self.recent_key_clicks:
                            if time.monotonic() - self.recent_key_clicks[line]\
                                <= self.double_click_timeout:
                                del self.recent_key_clicks[line]
                                is_double_click = True
                        else:
                            self.recent_key_clicks[line] = time.monotonic()

                        # TODO: When both a click and double click are assigned, clicking once should delay til DC threshold passed

                        if is_double_click:
                            # print("Row {}, col {} double-clicked".format(line.row, line.col))
                            self.keymap.fire_operation(line.row, line.col, 'double-click')
                        else:
                            # print('Row {}, col {} clicked'.format(line.row, line.col))
                            self.keymap.fire_operation(line.row, line.col, 'click')

                    if line in self.keys_held:
                        # print('Row {}, col {} no longer held'.format(line.row, line.col))
                        self.keymap.fire_operation(line.row, line.col, 'end hold')
                        self.keys_held.remove(line)

                    # print('Row {}, col {} released'.format(line.row, line.col))
                    self.keymap.fire_operation(line.row, line.col, 'release')

                else:
                    # On clicky display release event? 9
                    pass

            elif not line.input_line.value:
                if line in self.key_down_timestamps\
                    and time.monotonic() - self.key_down_timestamps[line] > self.click_timeout:
                    if line in self.keys_held:
                        self.keymap.fire_operation(line.row, line.col, 'continue hold')
                    else:
                        # print('Row {}, col {} now held'.format(line.row, line.col))
                        self.keys_held.append(line)
                        self.keymap.fire_operation(line.row, line.col, 'start hold')

        trash = []
        for line, timestamp in self.recent_key_clicks.items():
            if time.monotonic() - timestamp > self.double_click_timeout:
                trash.append(line)

        for line in trash:
            del self.recent_key_clicks[line]

        if self.clicky_displays is not None:
            for display in self.clicky_displays:
                display.update()