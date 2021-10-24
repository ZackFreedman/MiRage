import adafruit_ssd1306
import time
from util import timed_function

class ClickyWidget:
    def __init__(self, oled, position):
        self.oled = oled
        self.position = position  # 0-2
        self.name = 'Unnamed widget'

    def start(self):
        pass

    def on_click(self, direction):
        pass
        # print('{} {} received {} click'.format(
        #     self.position, self.name, 'right' if direction else 'left'))

    def on_keystroke(self, scancode):
        pass
    
    def update(self):
        pass


class SpeedometerWidget(ClickyWidget):
    def __init__(self, oled, position):
        super().__init__(oled, position)
        self.name = 'Speedometer'
        self.keystroke_timestamps = []
        self.time_to_average = 10
        self.time_between_refreshes = 0.5
        self.last_refresh = 0

    def start(self):
        del self.keystroke_timestamps[:]
        self.wpm = 0

    def on_keystroke(self, scancode):
        self.keystroke_timestamps.insert(0, time.monotonic())

    # @timed_function
    def show_wpm(self, wpm):
        self.oled.fill(0)
        self.oled.text('{:.0f} wpm'.format(wpm), 0, 0, 1, size=2)
        self.oled.show()

    # @timed_function
    def update(self):
        timestamp = time.monotonic()
        
        if timestamp - self.last_refresh >= self.time_between_refreshes:
            running_total = 0
            relevant_timestamp_count = 0
            wpm = 0

            for i, ts in enumerate(self.keystroke_timestamps):
                if timestamp - ts >= self.time_to_average:
                    break

                if i > 0:
                    running_total += self.keystroke_timestamps[i - 1] - ts
                    relevant_timestamp_count += 1

            if running_total and relevant_timestamp_count:
                wpm = 1 / (running_total / relevant_timestamp_count) * 60 / 5
            
            self.show_wpm(wpm)

            self.last_refresh = time.monotonic()


class LayerSelector(ClickyWidget):
    def __init__(self, oled, position, keymap, wrap_enabled=False):
        super().__init__(oled, position)
        self.keymap = keymap
        self.wrap_enabled = wrap_enabled
        self.name = 'Layer Selector'

        self.layer_names = []
        self.selected_layer_index = 0
        self.last_layer_index_enacted = None

    def add_layer(self, target_layer_name):
        self.layer_names.append(target_layer_name)

    def on_click(self, direction):
        super().on_click(direction)
        
        last_index = self.selected_layer_index

        if direction:
            self.selected_layer_index += 1
        else:
            self.selected_layer_index -= 1

        if self.wrap_enabled:
            self.selected_layer_index %= len(self.layer_names)
        else:
            self.selected_layer_index = max(0, 
                min(self.selected_layer_index, len(self.layer_names) - 1))

        # print('Selected layer index now {}, was {}'.format(self.selected_layer_index, last_index))

        # if self.selected_layer_index != self.last_layer_index_enacted:
        #     print('Layer will switch next update')

    def update(self):
        super().update()
        
        if self.selected_layer_index != self.last_layer_index_enacted:
            self.keymap.set_layer_from_widget(
                self.position, self.layer_names[self.selected_layer_index])

            self.oled.fill(0)
            self.oled.text(self.layer_names[self.selected_layer_index].replace(' ', '\n').upper(), 0, 0, 1, size=2)
            self.oled.show()

            self.last_layer_index_enacted = self.selected_layer_index


class ClickyDisplay:
    def __init__(self, oled, number):
        self.oled = oled
        self.number = number
        self.widget = None
        
    def reset(self):
        self.oled.fill(0)
        self.oled.show()

    def attach(self, widget):
        self.widget = widget

    def update(self):
        if self.widget is not None:
            self.widget.update()

    def on_click(self, direction):
        if self.widget is not None:
            self.widget.on_click(direction)

    def on_keystroke(self, scancode):
        if self.widget is not None:
            self.widget.on_keystroke(scancode)