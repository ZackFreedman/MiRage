from actions import *
from keynames import key_names
from parser import *

class FakeLayer:
    def __init__(self):
        self.key_bindings = []
        self.unassigned_keys_fall_through = True

    def bind(self, row, col, action, operation=None):
        self.key_bindings.append((row, col, action, operation))

def fail(message, expected, actual):
    print(message)
    print('\tExpected: ' + str(expected))
    print('\t  Actual: ' + str(actual))

def assert_generic_key_action(expected, actual, tag = 'GenericKeyAction'):
    if expected.keycodes != actual.keycodes:
        fail(tag + ' keycodes don\'t match', expected.keycodes, actual.keycodes) 
        return False
    return True

def assert_generic_layer_action(expected, actual, tag = 'GenericLayerAction'):
    if expected.target_layer != actual.target_layer:
        fail(tag + ' target layers don\'t match', expected.target_layer, actual.target_layer)
        return False
    return True

def assert_switch_to_layer_action(expected, actual):
    return assert_generic_layer_action(expected, actual, 'SwitchToLayerAction')

def assert_temporary_layer_action(expected, actual):
    return assert_generic_layer_action(expected, actual, 'TemporaryLayerAction')
    
def assert_leave_layer_action(expected, actual):
    return assert_generic_layer_action(expected, actual, 'LeaveLayerAction')

def assert_toggle_layer_action(expected, actual):
    return assert_generic_layer_action(expected, actual, 'ToggleLayerAction')

def assert_press_key_action(expected, actual):
    return assert_generic_key_action(expected, actual, 'PressKeyAction')

def assert_release_key_action(expected, actual):
    return assert_generic_key_action(expected, actual, 'ReleaseKeyAction')

def assert_click_key_action(expected, actual):
    return assert_generic_key_action(expected, actual, 'ClickKeyAction')

def assert_string_typer_action(expected, actual, tag = 'StringTyperAction'):
    ex_payload = expected.payload
    ac_payload = actual.payload
    ex_typing_rate = expected.typing_rate
    ac_typing_rate = actual.typing_rate

    if ex_payload != ac_payload:
        fail(tag + ': Payload is different', ex_payload, ac_payload)
        return False
    
    if ex_typing_rate != ac_typing_rate:
        fail(tag + ': Typing rate is different', ex_typing_rate, ac_typing_rate)
        return False
    
    return True

def assert_delay_action(expected, actual):
    if expected.duration != actual.duration:
        fail('Durations don\'t match', expected.duration, actual.duration)
        return False

    return True

def assert_non_repeating_string_typer_action(expected, actual):
    return assert_string_typer_action(expected, actual, 'NonRepeatingStringTyperAction')

def assert_sequence_action(expected, actual):
    expected_seq = expected.sequence
    actual_seq = actual.sequence
    if len(expected_seq) != len(actual_seq):
        fail('Sequence length is different', len(expected_seq), len(actual_seq))
        return False

    for i in range(len(actual_seq)):
        e_seq = expected_seq[i]
        a_seq = actual_seq[i]
        if type(a_seq) is GenericKeyAction:
            if not assert_generic_key_action(e_seq, a_seq):
                return False
            continue
        if type(a_seq) is NonRepeatingStringTyperAction:
            if not assert_non_repeating_string_typer_action(e_seq, a_seq):
                return False
            continue
        if type(a_seq) is StringTyperAction:
            if not assert_string_typer_action(e_seq, a_seq):
                return False
            continue
        if type(a_seq) is DelayAction:
            if not assert_delay_action(e_seq, a_seq):
                return False
            continue
        if type(a_seq) is ClickKeyAction:
            if not assert_click_key_action(e_seq, a_seq):
                return False
            continue
        
        fail('Type is not supported in sequence', '---', type(a_seq))
        return False

    return True

def assert_bindings_match(expected_bindings, actual_bindings):
    if len(expected_bindings) != len(actual_bindings):
        fail('Expected number of bindings does\'t match actual number', len(expected_bindings), len(actual_bindings))
        return False

    for i in range(len(expected_bindings)):
        expected_binding = expected_bindings[i]
        actual_binding = actual_bindings[i] 

        if actual_binding[0] != expected_binding[0]:
            fail('Expected row doesn\'t match actual', expected_binding, actual_binding)
            return False

        if type(expected_binding[2]) != type(actual_binding[2]):
            fail('Expected action type doesn\'t match actual', expected_binding, actual_binding)
            return False

        if actual_binding[1] != expected_binding[1]:
            fail('Expected key doesn\'t match actual', expected_binding, actual_binding)
            return False

        if actual_binding[3] != expected_binding[3]:
            fail('Expected operation doesn\'t match actual', expected_binding, actual_binding)
            return False

        expected_action = expected_binding[2]
        actual_action = actual_binding[2]
        checked_action = False

        if type(actual_action) is GenericKeyAction:
            checked_action = True
            if not assert_generic_key_action(expected_action, actual_action):
                return False

        if type(actual_action) is SequenceAction:
            checked_action = True
            if not assert_sequence_action(expected_action, actual_action):
                return False

        if type(actual_action) is PressKeyAction:
            checked_action = True
            if not assert_press_key_action(expected_action, actual_action):
                return False

        if type(actual_action) is ReleaseKeyAction:
            checked_action = True
            if not assert_press_key_action(expected_action, actual_action):
                return False
        
        if type(actual_action) is ClickKeyAction:
            checked_action = True
            if not assert_press_key_action(expected_action, actual_action):
                return False

        if type(actual_action) is GenericLayerAction:
            checked_action = True
            if not assert_generic_layer_action(expected_action, actual_action):
                return False

        if type(actual_action) is SwitchToLayerAction:
            checked_action = True
            if not assert_switch_to_layer_action(expected_action, actual_action):
                return False

        if type(actual_action) is TemporaryLayerAction:
            checked_action = True
            if not assert_temporary_layer_action(expected_action, actual_action):
                return False

        if type(actual_action) is LeaveLayerAction:
            checked_action = True
            if not assert_leave_layer_action(expected_action, actual_action):
                return False

        if type(actual_action) is ToggleLayerAction:
            checked_action = True
            if not assert_toggle_layer_action(expected_action, actual_action):
                return False

        if type(actual_action) is StringTyperAction:
            checked_action = True
            if not assert_string_typer_action(expected_action, actual_action):
                return False

        if type(actual_action) is NonRepeatingStringTyperAction:
            checked_action = True
            if not assert_non_repeating_string_typer_action(expected_action, actual_action):
                return False

        if type(actual_action) is DelayAction:
            checked_action = True
            if not assert_delay_action(expected_action, actual_action):
                return False

        # Actions with no parameters just need to be the same type (checked above)
        if type(actual_action) is ResetKeebAction:
            checked_action = True
        if type(actual_action) is KeebBootloaderAction:
            checked_action = True
        if type(actual_action) is ResetLayersAction:
            checked_action = True
        if type(actual_action) is NothingburgerAction:
            checked_action = True
        if type(actual_action) is PassThroughAction:
            checked_action = True
        if type(actual_action) is ReloadKeymapAction:
            checked_action = True

        if not checked_action:
            fail('failed to check action', type(actual_action).__name__, '-----')
            return False

    return True

def assert_attribute_error(source, err_text):
    layer = FakeLayer()
    try:
        parse_source(source, layer)
    except AttributeError as err:
        if err_text in str(err):
            return True
        fail('Wrong error message', err_text, str(err))
        return False
    except Exception as err:
        fail('Wrong error type', 'AttributeError', str(err))
        raise
        return False

    fail('Error not raised', 'AttributeError', '--- Nothing ---')
    return False

def test_basic():
    source = """
R4,    K0: A
R3,    K1: B
R2,    K2: C
R1,    K3: 1
R0,    K4: 2
R50,   K5: 3
R1000, K6: 4
R1   , K7: EQUALS
R2 ,   K8: UP ARROW
R2 ,   K9: UPARROW
R3    ,K10: LEFT ALT + 3
R0, K0: 0x01
R0, K0:
    0x01+0x02+0xFF
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 0, GenericKeyAction(key_names['A']), 'standard'),
        (3, 1, GenericKeyAction(key_names['B']), 'standard'),
        (2, 2, GenericKeyAction(key_names['C']), 'standard'),
        (1, 3, GenericKeyAction(key_names['1']), 'standard'),
        (0, 4, GenericKeyAction(key_names['2']), 'standard'),
        (50, 5, GenericKeyAction(key_names['3']), 'standard'),
        (1000, 6, GenericKeyAction(key_names['4']), 'standard'),
        (1, 7, GenericKeyAction(key_names['EQUALS']), 'standard'),
        (2, 8, GenericKeyAction(key_names['UPARROW']), 'standard'),
        (2, 9, GenericKeyAction(key_names['UPARROW']), 'standard'),
        (3, 10, GenericKeyAction([key_names['LEFTALT'], key_names['3']]), 'standard'),
        (0, 0, GenericKeyAction(0x01), 'standard'),
        (0, 0, GenericKeyAction([0x01, 0x02, 0xFF]), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_comments():
    source = """
R0, K0: ESC
#R0, K0:
#	On click: Click WINDOWS + A
#	On double-click: Type "Hello # world" slowly  # Try to confuse # "The # parser" lol 
#	On hold: Switch to Layer 2 until released
R1, K11: MINUS  # TODO: Add alias for HYPHEN and DASH
R2, K0: CAPSLOCK  # This should auto-detect to left windows
# TODO: Commented-out lines with another hash inside them confuse the parser
# This comment is here to confuse the parser
# # # # # asdfas asf # asdf"""
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (0, 0, GenericKeyAction(key_names['ESC']), 'standard'),
        (1, 11, GenericKeyAction(key_names['MINUS']), 'standard'),
        (2, 0, GenericKeyAction(key_names['CAPSLOCK']), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)


def test_events():
    source = """
R4, K5:
	On click: A+B+C
	# On click: A+A, type, Switch to ab a s, Type "ab[SINGLE QUOTE][RETURN][DOUBLE QUOTES]cd" repeatedly quickly, Toggle as, Leave asdfasdf adf a sasdf, Reset Keyboard, bootloader, Home, Nothing, pass Through, Reload Key Maps
	On hold: A + A + C
    On double-click: SHIFT
    On Release: F1
    on Press: F2
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, GenericKeyAction([key_names['A'], key_names['B'], key_names['C']]), 'on click'),
        (4, 5, GenericKeyAction([key_names['A'], key_names['A'], key_names['C']]), 'on hold'),
        (4, 5, GenericKeyAction(key_names['SHIFT']), 'on double-click'),
        (4, 5, GenericKeyAction(key_names['F1']), 'on release'),
        (4, 5, GenericKeyAction(key_names['F2']), 'on press'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_fall_through():
    source = """
other keys fall through
R4, K5: G
    """
    layer = FakeLayer()
    layer.unassigned_keys_fall_through = False
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, GenericKeyAction(key_names['G']), 'standard'),
    ]    

    if layer.unassigned_keys_fall_through != True:
        fail('Fall through has wrong value', True, layer.unassigned_keys_fall_through)
        return False

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_block():
    source = """
block other keys
R4, K5: G
    """
    layer = FakeLayer()
    layer.unassigned_keys_fall_through = True
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, GenericKeyAction(key_names['G']), 'standard'),
    ]    

    if layer.unassigned_keys_fall_through != False:
        fail('Fall through has wrong value', False, layer.unassigned_keys_fall_through)
        return False

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_sequence():
    source = """
R4, K5: A, B, C, D, E
    """
    layer = FakeLayer()
    parse_source(source, layer)

    sequence = SequenceAction()
    sequence.sequence.append(GenericKeyAction(key_names['A']))
    sequence.sequence.append(GenericKeyAction(key_names['B']))
    sequence.sequence.append(GenericKeyAction(key_names['C']))
    sequence.sequence.append(GenericKeyAction(key_names['D']))
    sequence.sequence.append(GenericKeyAction(key_names['E']))

    expected_bindings = [
        (4, 5, sequence, 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_press():
    source = """
R4, K5: press A+SHIFT + B
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, PressKeyAction([key_names['A'], key_names['SHIFT'], key_names['B']]), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_release():
    source = """
R4, K5: release A+SHIFT + B
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, ReleaseKeyAction([key_names['A'], key_names['SHIFT'], key_names['B']]), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_click():
    source = """
R4, K5: click A+SHIFT + B
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, ClickKeyAction([key_names['A'], key_names['SHIFT'], key_names['B']]), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_wait():
    source = """
R4, K5: Wait 500ms 
R4, K5: Wait 500 milliseconds 
R4, K5: Wait 500 sec
R4, K5: Wait 5seconds
R4, K5: Wait 1min 
R4, K5: Wait 5minutes
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, DelayAction(0.5), 'standard'),
        (4, 5, DelayAction(0.5), 'standard'),
        (4, 5, DelayAction(500), 'standard'),
        (4, 5, DelayAction(5), 'standard'),
        (4, 5, DelayAction(60), 'standard'),
        (4, 5, DelayAction(300), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)


def test_action_switch_to():
    source = """
R4, K5: switch To My third layer 
    """
    layer = FakeLayer()
    parse_source(source, layer)

    # TODO: Should we really be lower()'ing the layer names?
    expected_bindings = [
        (4, 5, SwitchToLayerAction('my third layer'), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_temporary_switch_to():
    source = """
R4, K5: on hold: switch To My third layer until released
    """
    layer = FakeLayer()
    parse_source(source, layer)

    # TODO: Should we really be lower()'ing the layer names?
    expected_bindings = [
        (4, 5, TemporaryLayerAction('my third layer'), 'on hold'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_toggle():
    source = """
R4, K5: toggle My third layer 
    """
    layer = FakeLayer()
    parse_source(source, layer)

    # TODO: Should we really be lower()'ing the layer names?
    expected_bindings = [
        (4, 5, ToggleLayerAction('my third layer'), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_leave():
    source = """
R4, K5: leave My third layer 
    """
    layer = FakeLayer()
    parse_source(source, layer)

    # TODO: Should we really be lower()'ing the layer names?
    expected_bindings = [
        (4, 5, LeaveLayerAction('my third layer'), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_type_repeating():
    source = """
R4, K5: type "Hello, World!" 50ms repeatedly
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, StringTyperAction('Hello, World!', 0.05), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_type_non_repeating():
    source = """
R4, K5: type "Hello, World!" slowly 
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, NonRepeatingStringTyperAction('Hello, World!', 0.2), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_reset_keyboard():
    source = """
R4, K5: reset Keyboard
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, ResetKeebAction(), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_bootloader():
    source = """
R4, K5: bootloader 
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, KeebBootloaderAction(), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_home():
    source = """
R4, K5: home 
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, ResetLayersAction(), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_nothing():
    source = """
R4, K5: nothing
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, NothingburgerAction(), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_pass_through():
    source = """
R4, K5: pass through 
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, PassThroughAction(), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_action_reload_key_maps():
    source = """
R4, K5: reload key maps 
    """
    layer = FakeLayer()
    parse_source(source, layer)

    expected_bindings = [
        (4, 5, ReloadKeymapAction(), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

def test_error_unterminated_string():
    source = """
    
    R4, K5: Test "missing quote quickly"""
    return assert_attribute_error(source, 'Line 3: Unterminated string')

def test_error_unrecognized_character():
    source = """
R4, K5: $
    """
    return assert_attribute_error(source, 'Line 2: Unexpected character \'$\'')

def test_error_bad_action_start_token():
    source_part = 'R4, K5: '
    return (assert_attribute_error(source_part + '+', 'Line 1: Token not allowed at start of action: +')
        and assert_attribute_error(source_part + ',', 'Line 1: Token not allowed at start of action: ,')
        and assert_attribute_error(source_part + '"text"', 'Line 1: Token not allowed at start of action: "text"')
        and assert_attribute_error(source_part + 'repeatedly', 'Line 1: Token not allowed at start of action: repeatedly')
        and assert_attribute_error(source_part + 'quickly', 'Line 1: Token not allowed at start of action: quickly')
        and assert_attribute_error(source_part + 'slowly', 'Line 1: Token not allowed at start of action: slowly')
        and assert_attribute_error(source_part + 'at human speed', 'Line 1: Token not allowed at start of action: at human speed')
        and assert_attribute_error(source_part + 'until released', 'Line 1: Token not allowed at start of action: until released')) 

def test_error_bad_action_end_token():
    source_part = 'R4, K5: F'
    return (assert_attribute_error(source_part + '+', 'Line 1: Token not allowed at end of action: +')
        and assert_attribute_error(source_part + ',', 'Line 1: Token not allowed at end of action: ,'))

def test_error_duplicate_plus_token():
    source = 'R4, K5: A++F'
    return assert_attribute_error(source, 'Line 1: Cannot have two consecutive \'+\'')

def test_error_bad_key_def():
    return (assert_attribute_error('X0', 'Line 1: Expected row literal, saw \'X0\' instead')
        and assert_attribute_error('R0', 'Line 1: Expected comma after \'R0\'')
        and assert_attribute_error('R0:', 'Line 1: Expected comma after \'R0\'')
        and assert_attribute_error('R0,', 'Line 1: Expected key literal')
        and assert_attribute_error('R0, :', 'Line 1: Expected key literal')
        and assert_attribute_error('R0, X0', 'Line 1: Expected key literal')
        and assert_attribute_error('R0, K0', 'Line 1: Expected colon after \'K0\'')
        and assert_attribute_error('R0, K0,', 'Line 1: Expected colon after \'K0\''))

def test_error_bad_event():
    return (assert_attribute_error('R0, K0:', 'Line 1: Expected action definition after \'K0:\'')
        and assert_attribute_error('R0, K0:\n', 'Line 1: Expected action definition after \'K0:\'')
        and assert_attribute_error('R0, K0: on click', 'Line 1: Expected colon after \'on click\'')
        and assert_attribute_error('R0, K0: on click:', 'Line 1: Expected action definition after \'on click:\''))

def test_error_partial_action_tokens():
    return (assert_attribute_error('R0, K0: switch', 'Line 1: Invalid Action or Key \'switch\'')
        and assert_attribute_error('R0, K0: reset', 'Line 1: Invalid Action or Key \'reset\'')
        and assert_attribute_error('R0, K0: pass', 'Line 1: Invalid Action or Key \'pass\'')
        and assert_attribute_error('R0, K0: reload', 'Line 1: Invalid Action or Key \'reload\'')
        and assert_attribute_error('R0, K0: reload key', 'Line 1: Invalid Action or Key \'reload\'')
        and assert_attribute_error('R0, K0: at', 'Line 1: Invalid Action or Key \'at\'')
        and assert_attribute_error('R0, K0: at human', 'Line 1: Invalid Action or Key \'at\'')
        and assert_attribute_error('R0, K0: until', 'Line 1: Invalid Action or Key \'until\'')
        and assert_attribute_error('R0, K0: other', 'Line 1: Invalid Action or Key \'other\'')
        and assert_attribute_error('R0, K0: other keys', 'Line 1: Invalid Action or Key \'other\'')
        and assert_attribute_error('R0, K0: other keys fall', 'Line 1: Invalid Action or Key \'other\'')
        and assert_attribute_error('R0, K0: block', 'Line 1: Invalid Action or Key \'block\'')
        and assert_attribute_error('R0, K0: block other', 'Line 1: Invalid Action or Key \'block\''))

def test_error_actions():
    return (
        # Invalid Action
        assert_attribute_error('R0, K0: NotAnAction', 'Line 1: Invalid Action or Key \'NotAnAction\'')

        # Press Action
        and assert_attribute_error('R0, K0: press', 'Line 1: Press action requires key parameter')

        # Release Action
        and assert_attribute_error('R0, K0: release', 'Line 1: Release action requires key parameter')

        # Click Action
        and assert_attribute_error('R0, K0: click', 'Line 1: Click action requires key parameter')

        # Wait Action
        and assert_attribute_error('R0, K0: Wait', 'Line 1: Wait action requires 2 parameters')
        and assert_attribute_error('R0, K0: Wait 100', 'Line 1: Wait action requires 2 parameters') # Wait with only 1 param
        and assert_attribute_error('R0, K0: Wait type ms', 'Line 1: Expected number in time literal')
        and assert_attribute_error('R0, K0: Wait 100 repeatedly', 'Line 1: Expected units in time literal')
        and assert_attribute_error('R0, K0: Wait 100mm', 'Line 1: Expected units in time literal')
        and assert_attribute_error('R0, K0: Wait tensec', 'Line 1: Wait action requires 2 parameters')

        # Switch To Action
        and assert_attribute_error('R0, K0: Switch to', 'Line 1: Switch to action requires layer parameter')
        and assert_attribute_error('R0, K0: Switch to until released', 'Line 1: Missing layer name for temporary switch: \'Switch to until released\'')
        and assert_attribute_error("""R0, K0: switch to top until released""", 'Line 1: TemporaryLayerAction can only bind to On Hold')
        and assert_attribute_error("""R0, K0: 
                                        on release: switch to top until released""", 'Line 2: TemporaryLayerAction can only bind to On Hold')
        and assert_attribute_error("""R0, K0: A, switch to top until released""", 'Line 1: TemporaryLayerAction can only bind to On Hold')

        # Toggle Action
        and assert_attribute_error('R0, K0: Toggle', 'Line 1: Toggle action requires layer parameter')

        # Leave Action
        and assert_attribute_error('R0, K0: leave', 'Line 1: Leave action requires layer parameter')

        # Reset Keyboard Action
        and assert_attribute_error('R0, K0: reset keyboard abc', 'Line 1: Reset Keyboard action shouldn\'t have any parameters')

        # Bootloader Action
        and assert_attribute_error('R0, K0: bootloader abc', 'Line 1: Bootloader action shouldn\'t have any parameters')

        # Home Action
        and assert_attribute_error('R0, K0: home abc', 'Line 1: Home action shouldn\'t have any parameters')

        # Nothing Action
        and assert_attribute_error('R0, K0: nothing abc', 'Line 1: Nothing action shouldn\'t have any parameters')

        # Pass Through Action
        and assert_attribute_error('R0, K0: pass through abc', 'Line 1: Pass through action shouldn\'t have any parameters')

        # Reload Key Maps Action
        and assert_attribute_error('R0, K0: reload key maps abc', 'Line 1: Reload Key Maps action shouldn\'t have any parameters')

        # Type Action
        and assert_attribute_error('R0, K0: type', 'Line 1: Type action missing text parameter')
        and assert_attribute_error('R0, K0: type quickly "abc"', 'Line 1: Type action\'s first parameter must be quoted text')
        and assert_attribute_error('R0, K0: type "abc" quickly slowly', 'Line 1: Multiple speeds set for Type action. Please select one.\n\ttype "abc" quickly slowly')
        and assert_attribute_error('R0, K0: type "abc" at human speed slowly', 'Line 1: Multiple speeds set for Type action. Please select one.\n\ttype "abc" at human speed slowly')
        and assert_attribute_error('R0, K0: type "abc" 100ms slowly', 'Line 1: Multiple speeds set for Type action. Please select one.\n\ttype "abc" 100ms slowly')
        and assert_attribute_error('R0, K0: type "abc" quickly at human speed', 'Line 1: Multiple speeds set for Type action. Please select one.\n\ttype "abc" quickly at human speed')
        and assert_attribute_error('R0, K0: type "abc" quickly 100ms', 'Line 1: Multiple speeds set for Type action. Please select one.\n\ttype "abc" quickly 100ms')
        and assert_attribute_error('R0, K0: type "abc" 100ms at human speed', 'Line 1: Multiple speeds set for Type action. Please select one.\n\ttype "abc" 100ms at human speed')
        and assert_attribute_error('R0, K0: type "abc" 100ms 100ms', 'Line 1: Multiple speeds set for Type action. Please select one.\n\ttype "abc" 100ms 100ms')
        and assert_attribute_error('R0, K0: type "abc" 100', 'Line 1: time provided without units: \'100\'')
        and assert_attribute_error('R0, K0: type "abc" seconds', 'Line 1: unit provided without time: \'seconds\'')
    )

def test_large():
    source = """R4, K5:
	On click: A+A
	# On click: A+A, type, Switch to ab a s, Type "ab[SINGLE QUOTE][RETURN][DOUBLE QUOTES]cd" repeatedly quickly, Toggle as, Leave asdfasdf adf a sasdf, Reset Keyboard, bootloader, Home, Nothing, pass Through, Reload Key Maps
	On hold: A+A, B, C, D+A, E, F,type "asdfa" slowly


R0, K0: ESC
#R0, K0:
#	On click: Click WINDOWS + A
#	On double-click: Type "Hello # world" slowly  # Try to confuse # "The # parser" lol 
#	On hold: Switch to Layer 2 until released

other keys fall through
block other keys

R0, K1: 1
R0, K2: 2
R0, K3: 3
R0, K4: 4
R0, K5: 5
R0, K6: 6
R0, K7: 7
R0, K8: 8
R0, K9: 9
R0, K10: 0
R0, K11: EQUALS
R1, K0: TAB
R1, K1: Q
R1, K2: W
R1, K3: E
R1, K4: R
R1, K5: T
R1, K6: Y
R1, K7: U
R1, K8: I
R1, K9: O
R1, K10: P
R1, K11: MINUS  # TODO: Add alias for HYPHEN and DASH
R2, K0: CAPSLOCK  # This should auto-detect to left windows
R2, K1: A
R2, K2: S
R2, K3: D
R2, K4: F
R2, K5: G
R2, K6: H
R2, K7: J
R2, K8: K
R2, K9: L
R2, K10: SEMICOLON
R2, K11: QUOTE
R3, K0: SHIFT  # This should auto-detect to left shift
R3, K1: Z
R3, K2: X
R3, K3: C
R3, K4: V
R3, K5: B
R3, K6: N
R3, K7: M
R3, K8: COMMA
R3, K9: PERIOD
R3, K10: UP ARROW
R3, K11: DOWN ARROW  # This should auto-detect to right shift
R4, K0: WINDOWS
R4, K1: LEFT ALT + 3
R4, K2: LEFT CONTROL
R4, K3: SPACE

R4, K0: Type "QUAG,SIRE" repeatedly
R4, K0: F+R, wait 200ms, type "cmd", click ENTER

R4, K4: BACKSPACE
R4, K5:
	On click: Toggle Function Layer
	On hold: Switch to Function Layer until released
R4, K6: Reset Keyboard
R4, K7: LEFT ARROW
R4, K8: RIGHT ARROW

# TODO: Commented-out lines with another hash inside them confuse the parser
# This comment is here to confuse the parser    
"""
    layer = FakeLayer()
    parse_source(source, layer)

    sequence_1 = SequenceAction()
    sequence_1.sequence.append(GenericKeyAction([key_names['A'], key_names['A']]))
    sequence_1.sequence.append(GenericKeyAction(key_names['B']))
    sequence_1.sequence.append(GenericKeyAction(key_names['C']))
    sequence_1.sequence.append(GenericKeyAction([key_names['D'], key_names['A']]))
    sequence_1.sequence.append(GenericKeyAction(key_names['E']))
    sequence_1.sequence.append(GenericKeyAction(key_names['F']))
    sequence_1.sequence.append(StringTyperAction('asdfa', 0.2))

    sequence_2 = SequenceAction()
    sequence_2.sequence.append(GenericKeyAction([key_names['F'], key_names['R']]))
    sequence_2.sequence.append(DelayAction(0.2))
    sequence_2.sequence.append(StringTyperAction('cmd', 0.01))
    sequence_2.sequence.append(ClickKeyAction(key_names['ENTER']))

    expected_bindings = [
        (4,  5, GenericKeyAction([key_names['A'], key_names['A']]), 'on click'),
        (4,  5, sequence_1, 'on hold'),
        (0,  0, GenericKeyAction(key_names['ESC']), 'standard'),
        (0,  1, GenericKeyAction(key_names['1']), 'standard'),
        (0,  2, GenericKeyAction(key_names['2']), 'standard'),
        (0,  3, GenericKeyAction(key_names['3']), 'standard'),
        (0,  4, GenericKeyAction(key_names['4']), 'standard'),
        (0,  5, GenericKeyAction(key_names['5']), 'standard'),
        (0,  6, GenericKeyAction(key_names['6']), 'standard'),
        (0,  7, GenericKeyAction(key_names['7']), 'standard'),
        (0,  8, GenericKeyAction(key_names['8']), 'standard'),
        (0,  9, GenericKeyAction(key_names['9']), 'standard'),
        (0, 10, GenericKeyAction(key_names['0']), 'standard'),
        (0, 11, GenericKeyAction(key_names['EQUALS']), 'standard'),
        (1,  0, GenericKeyAction(key_names['TAB']), 'standard'),
        (1,  1, GenericKeyAction(key_names['Q']), 'standard'),
        (1,  2, GenericKeyAction(key_names['W']), 'standard'),
        (1,  3, GenericKeyAction(key_names['E']), 'standard'),
        (1,  4, GenericKeyAction(key_names['R']), 'standard'),
        (1,  5, GenericKeyAction(key_names['T']), 'standard'),
        (1,  6, GenericKeyAction(key_names['Y']), 'standard'),
        (1,  7, GenericKeyAction(key_names['U']), 'standard'),
        (1,  8, GenericKeyAction(key_names['I']), 'standard'),
        (1,  9, GenericKeyAction(key_names['O']), 'standard'),
        (1, 10, GenericKeyAction(key_names['P']), 'standard'),
        (1, 11, GenericKeyAction(key_names['MINUS']), 'standard'),
        (2,  0, GenericKeyAction(key_names['CAPSLOCK']), 'standard'),
        (2,  1, GenericKeyAction(key_names['A']), 'standard'),
        (2,  2, GenericKeyAction(key_names['S']), 'standard'),
        (2,  3, GenericKeyAction(key_names['D']), 'standard'),
        (2,  4, GenericKeyAction(key_names['F']), 'standard'),
        (2,  5, GenericKeyAction(key_names['G']), 'standard'),
        (2,  6, GenericKeyAction(key_names['H']), 'standard'),
        (2,  7, GenericKeyAction(key_names['J']), 'standard'),
        (2,  8, GenericKeyAction(key_names['K']), 'standard'),
        (2,  9, GenericKeyAction(key_names['L']), 'standard'),
        (2, 10, GenericKeyAction(key_names['SEMICOLON']), 'standard'),
        (2, 11, GenericKeyAction(key_names['QUOTE']), 'standard'),
        (3,  0, GenericKeyAction(key_names['SHIFT']), 'standard'),
        (3,  1, GenericKeyAction(key_names['Z']), 'standard'),
        (3,  2, GenericKeyAction(key_names['X']), 'standard'),
        (3,  3, GenericKeyAction(key_names['C']), 'standard'),
        (3,  4, GenericKeyAction(key_names['V']), 'standard'),
        (3,  5, GenericKeyAction(key_names['B']), 'standard'),
        (3,  6, GenericKeyAction(key_names['N']), 'standard'),
        (3,  7, GenericKeyAction(key_names['M']), 'standard'),
        (3,  8, GenericKeyAction(key_names['COMMA']), 'standard'),
        (3,  9, GenericKeyAction(key_names['PERIOD']), 'standard'),
        (3, 10, GenericKeyAction(key_names['UPARROW']), 'standard'),
        (3, 11, GenericKeyAction(key_names['DOWNARROW']), 'standard'),
        (4,  0, GenericKeyAction(key_names['WINDOWS']), 'standard'),
        (4,  1, GenericKeyAction([key_names['LEFTALT'], key_names['3']]), 'standard'),
        (4,  2, GenericKeyAction(key_names['LEFTCONTROL']), 'standard'),
        (4,  3, GenericKeyAction(key_names['SPACE']), 'standard'),
        (4,  0, StringTyperAction("QUAG,SIRE", 0.01), 'standard'),
        (4,  0, sequence_2, 'standard'),
        (4,  4, GenericKeyAction(key_names['BACKSPACE']), 'standard'),
        (4,  5, ToggleLayerAction('function layer'), 'on click'),
        (4,  5, TemporaryLayerAction('function layer'), 'on hold'),
        (4,  6, ResetKeebAction(), 'standard'),
        (4,  7, GenericKeyAction(key_names['LEFTARROW']), 'standard'),
        (4,  8, GenericKeyAction(key_names['RIGHTARROW']), 'standard'),
    ]    

    return assert_bindings_match(expected_bindings, layer.key_bindings)

test_cases = [
    test_basic,
    test_comments,
    test_events,
    test_fall_through,
    test_block,
    test_action_sequence,
    test_action_press,
    test_action_release,
    test_action_click,
    test_action_wait,
    test_action_switch_to,
    test_action_temporary_switch_to,
    test_action_toggle,
    test_action_leave,
    test_action_type_repeating,
    test_action_type_non_repeating,
    test_action_reset_keyboard,
    test_action_bootloader,
    test_action_home,
    test_action_nothing,
    test_action_pass_through,
    test_action_reload_key_maps,
    test_error_unterminated_string,
    test_error_unrecognized_character,
    test_error_bad_action_start_token,
    test_error_bad_action_end_token,
    test_error_duplicate_plus_token,
    test_error_bad_key_def,
    test_error_bad_event,
    test_error_partial_action_tokens,
    test_error_actions,
    test_large,
]

any_failure = False
for case in test_cases:
    print('Running test: ' + case.__name__ + '.....')
    if case():
         print('\tPassed!')
    else:
         print('\tFailed!')
         any_failure = True

if any_failure:
    print('\n--- Some Tests Failed ---')
else: 
    print('\n--- All Tests Passed ---')
