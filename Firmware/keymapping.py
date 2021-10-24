import os
from actions import *
import parser
from util import timed_function

action_pool = []  # Reuse actions to save memory


class KeyBinding:
    __slots__ = 'on_press_actions', 'on_click_actions', 'on_hold_actions',\
        'on_double_click_actions', 'on_release_actions', 'standard_behavior_actions'

    def __init__(self):
        self.on_press_actions = []
        self.on_click_actions = []
        self.on_hold_actions = []
        self.on_double_click_actions = []
        self.on_release_actions = []
        self.standard_behavior_actions = []

    def bind_action(self, operation, action):
        # print('Binding {} to {}'.format(action, operation))

        if operation == 'on press':
            self.on_press_actions.append(action)
        elif operation == 'on click':
            self.on_click_actions.append(action)
        elif operation == 'on hold':
            self.on_hold_actions.append(action)
        elif operation == 'on double-click':
            self.on_double_click_actions.append(action)
        elif operation == 'on release':
            self.on_release_actions.append(action)
        elif operation == 'standard' or operation is None:
            self.standard_behavior_actions.append(action)
        else:
            raise AttributeError('{} is not an operation'.format(operation))

    def reset(self):
        # print('Resetting binding')
        del self.on_press_actions[:]
        del self.on_click_actions[:]
        del self.on_hold_actions[:]
        del self.on_double_click_actions[:]
        del self.on_release_actions[:]
        del self.standard_behavior_actions[:]

    @staticmethod
    # @timed_function
    def _fire_actions(actions, how='one shot'):
        #should_fall_through = True
        fall_through_override = False

        for action in actions:
            if isinstance(action, PassThroughAction):
                fall_through_override = True 
                # print('Firing PassThroughAction')
                continue
            #should_fall_through = False
            if how is 'one shot':
                action.one_shot()
            elif how is 'start':
                action.start_hold()
            elif how is 'continue':
                action.continue_hold()
            elif how is 'end':
                action.end_hold()

        #return should_fall_through or fall_through_override
        return fall_through_override

    def press(self):
        if len(self.on_press_actions):
            return KeyBinding._fire_actions(self.on_press_actions)
        else:
            return KeyBinding._fire_actions(self.standard_behavior_actions, how='start')

    def click(self):
        return KeyBinding._fire_actions(self.on_click_actions)

    def start_hold(self):
        return KeyBinding._fire_actions(self.on_hold_actions, how='start')

    def continue_hold(self):
        return KeyBinding._fire_actions(self.on_hold_actions, how='continue')

    def end_hold(self):
        return KeyBinding._fire_actions(self.on_hold_actions, how='end')

    def double_click(self):
        return KeyBinding._fire_actions(self.on_double_click_actions)

    def release(self):
        if len(self.on_release_actions):
            return KeyBinding._fire_actions(self.on_release_actions)
        else:
            return KeyBinding._fire_actions(self.standard_behavior_actions, how='end')

    def needs_timing(self):
        return len(self.on_click_actions) \
            + len(self.on_hold_actions) \
            + len(self.on_double_click_actions) > 0

    def does_anything(self):
        return len(self.on_press_actions) \
            + len(self.on_click_actions) \
            + len(self.on_hold_actions) \
            + len(self.on_double_click_actions) \
            + len(self.on_release_actions) \
            + len(self.standard_behavior_actions) > 0


class Layer:
    def __init__(self, owner):
        self.owner = owner

        self.key_bindings = {}
        self.name = None
        self.unassigned_keys_fall_through = True

    def bind(self, row, col, action, operation=None):
        global action_pool
        action_to_bind = None

        # print('Binding {} to R{}, K{} {} op'.format(
            #str(action), row, col, operation if operation is not None else 'standard behavior'))

        for existing_action in action_pool:
            if action == existing_action:
                action_to_bind = existing_action
                # print('Reusing existing action')
                break

        if action_to_bind is None:
            # print('Creating new action')
            action_to_bind = action
            action_pool.append(action)

        if (row, col) in self.key_bindings:
            # print('Reusing existing binding')
            binding = self.key_bindings[row, col]
        else:
            # print('Creating new binding')
            binding = KeyBinding()
            self.key_bindings[row, col] = binding

        action_to_bind.associate_with(self.owner)

        binding.bind_action(operation, action_to_bind)

    def reset(self):
        self.key_bindings.clear()
        self.name = None
        self.unassigned_keys_fall_through = True

    def fire_operation(self, row, col, operation):
        # print('Firing a {} on R{}, K{} of layer {}'.format(operation, row, col, self.name))

        try:
            if operation == 'press':
                return self.key_bindings[row, col].press()
            elif operation == 'click':
                return self.key_bindings[row, col].click()
            elif operation == 'start hold':
                return self.key_bindings[row, col].start_hold()
            elif operation == 'continue hold':
                return self.key_bindings[row, col].continue_hold()
            elif operation == 'end hold':
                return self.key_bindings[row, col].end_hold()
            elif operation == 'double-click':
                return self.key_bindings[row, col].double_click()
            elif operation == 'release':
                return self.key_bindings[row, col].release()
            else:
                raise AttributeError('{} is not an operation'.format(operation))
        except KeyError:
            if not (row, col) in self.key_bindings:
                pass
                # print('This key has no bindings')
            elif not self.key_bindings[row, col].does_anything():
                pass
                # print('This key has no actions')

        return self.unassigned_keys_fall_through


class Keymap:
    def __init__(self, keyboard, keyboard_layout):
        self.hid_keyboard = keyboard
        self.hid_keyboard_layout = keyboard_layout

        self.base_layer = None
        self.all_layers = {}
        self.layer_stack = []
        self.switch_queue = []
        self.dismissal_queue = []
        self.layer_stack_reset_queued = False
        self.reload_queued = False
        self.widget_layers = {'top': None, 'middle': None, 'bottom': None}

    def load(self, folder):
        os.chdir(folder)
        layer_files = os.listdir()

        if 'base layer' not in map(lambda x: 
            x.lower()[:x.rindex('.')] if '.' in x else x.lower(), 
            layer_files):
            
            raise RuntimeError('Major problem - Base Layer not present')
        else:
            # print('Found layer files', ', '.join(layer_files))

            layers_to_reuse = list(self.all_layers.values())

            self.reset()
                
            for filename in layer_files:
                with open(filename, 'r') as f:
                    if len(layers_to_reuse):
                        working_layer = layers_to_reuse[0]
                        working_layer.reset()
                        del layers_to_reuse[0]
                    else:
                        working_layer = Layer(self)

                    # print('Parsing', filename)
                    parser.parse_layer_definition(filename, working_layer)
                    # print('Success! Parsed layer', working_layer.name)

                    self.add_layer(working_layer)

                # print('Successfully loaded all layer definitions')
        
        os.chdir('..')

    def add_layer(self, layer):
        if layer.name.lower() == 'base layer':
            self.base_layer = layer
            # print('This is the super special base layer')
        
        self.all_layers[layer.name] = layer
        # print('Adding {}', layer.name)

    def fire_operation(self, row, col, operation):
        # print('Firing {} on R{}, K{}'.format(operation, row, col))

        if len(self.layer_stack):
            for layer in reversed(self.layer_stack):
                # print('Trying {}'.format(operation, row, col, layer.name))
                if not layer.fire_operation(row, col, operation):
                    # Firing operation returns true if it should fall through
                    return
                # print("{} didn't handle it, falling through".format(layer.name))
        
        for position in ['top', 'middle', 'bottom']:
            if self.widget_layers[position] is not None:
                # print('Trying {} widget layer {}'.format(position, self.widget_layers[position].name))
                if not self.widget_layers[position].fire_operation(row, col, operation):
                    return
                # print("{} didn't handle it, falling through".format(self.widget_layers[position].name))

        # print('Using base layer')
        self.base_layer.fire_operation(row, col, operation)

    def queue_switch_to(self, target_layer):
        # print('Queuing switch to', target_layer)
        if target_layer in self.all_layers:
            self.switch_queue.append(self.all_layers[target_layer])

    def queue_dismiss(self, target_layer):
        # print('Queuing dismiss', target_layer)
        if target_layer in self.all_layers:
            self.dismissal_queue.append(self.all_layers[target_layer])

    def queue_reset(self):
        # print('Queuing reset')
        self.layer_stack_reset_queued = True

    def enact_queues(self):
        for layer in self.switch_queue:
            if layer in self.layer_stack:
                # print('Removing {} from stack to move to top'.format(layer.name))
                self.layer_stack.remove(layer)

            # print('Moving {} to top of stack'.format(layer.name))
            self.layer_stack.append(layer)

        for layer in self.dismissal_queue:
            if layer in self.layer_stack:
                # print('Dismissing layer', layer.name)
                self.layer_stack.remove(layer)
                # if len(self.layer_stack):
                    # print(self.layer_stack[-1].name, 'is now on top')
                # else:
                    # print('Layer stack is empty - now on base layer')
            # else:
                # print("Couldn't dismiss layer {} - not in stack".format(layer.name))
        
        if self.reload_queued:
            # print('Reloading keymap')
            self.load()

        if self.layer_stack_reset_queued:
            # print('Resetting layer stack')
            del self.layer_stack[:]

        del self.switch_queue[:]
        del self.dismissal_queue[:] 
        self.layer_stack_reset_queued = False
        self.reload_queued = False

    def set_layer_from_widget(self, position, layer_name):
        # print('{} widget layer is now {}'.format(position, layer_name))
        self.widget_layers[position] = self.all_layers[layer_name]

    def reset(self):
        self.base_layer = None
        self.all_layers.clear()
        del self.layer_stack[:]
        del self.switch_queue[:]
        del self.dismissal_queue[:]
        self.layer_stack_reset_queued = False
        self.reload_queued = False
