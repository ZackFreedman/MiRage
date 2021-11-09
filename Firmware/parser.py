from actions import *
from enum import Enum
from keynames import key_names
import string

debug_line_callback = None

def debug_out(*args):
    # print(' '.join(args))
    # print(*args)
    if debug_line_callback is not None:
        debug_line_callback(' '.join(args))

class Token(Enum):
    SYM_HASH = 1
    SYM_COMMA = 2
    SYM_COLON = 3
    SYM_QUOTE = 4
    SYM_NEWLINE = 5
    SYM_PLUS = 6
    STRING_LIT = 7
    ROW_LIT = 8
    KEY_LIT = 9
    NUM_LIT = 10
    HEX_LIT = 11
    IDENTIFIER = 12
    OPERATION_PRESS = 13
    OPERATION_CLICK = 14
    OPERATION_HOLD = 15
    OPERATION_DOUBLE_CLICK = 16
    OPERATION_RELEASE = 17
    ACTION_PRESS = 18
    ACTION_RELEASE = 19
    ACTION_CLICK = 20
    ACTION_WAIT = 21
    ACTION_SWITCH_TO = 22
    ACTION_TOGGLE = 23
    ACTION_LEAVE = 24
    ACTION_TYPE = 25
    ACTION_RESET_KEYBOARD = 26
    ACTION_BOOTLOADER = 27
    ACTION_HOME = 28
    ACTION_NOTHING = 29
    ACTION_PASS_THROUGH = 30
    ACTION_RELOAD_KEY_MAPS = 31
    PARAMETER_QUICKLY = 32
    PARAMETER_SLOWLY = 33
    PARAMETER_REPEATEDLY = 34
    PARAMETER_AT_HUMAN_SPEED = 35
    PARAMETER_UNTIL_RELEASED = 36
    PARAMETER_TIME_MS = 37
    PARAMETER_TIME_SEC = 38
    PARAMETER_TIME_MIN = 39
    TOP_OTHER_KEYS_FALL_THROUGH = 40
    TOP_BLOCK_OTHER_KEYS = 41

# Returns the tag of a token 
def t_tag(token):
    return token[0]

# Returns the line number of a token
def t_lineno(token):
    return token[3]

# Returns the string that the token represents
def t_str(source, token):
    return source[token[1]:token[2]]

# Returns the full string between start and end token
# Only use the function for debugging/error purposes
# It is not safe for semantic use as two tokens might
# have a "removed" comment between them
#
# TODO: Update this function to be smart about comments
def t_run_str(source, start, end):
    return source[start[1]: end[2]]

# Takes a string and converts it into a list of tokens representing meaningful
# chunks of characters. This minimizes the amount of on the fly string comparisons,
# reduces the number of string copies, simplifies parsing logic and enables niceties 
# like printing the line number on parsing failure.
#
# type: Array of token 4-tuples
# token type: (0,0,0,0) 
#     t[0]: Token tag from 'Token' class
#     t[1]: Starting index in source of the token
#     t[2]: Index after the last character of the token
#     t[3]: Line number of the token
#
# Note: Use a string slicke to get the string representation of a token
#       i.e. tok_str = source[t[1]:t[2]]
#
# Note: It is not safe to take a multi-token slice as two tokens may cross over a comment line
#       i.e. tokens = [<wait>, <iden>, <row lit>, <comma>, <key lit>, <colon>]
#            str = source[tokens[0][1]:tokens[-1][2]] # this is using start from first token, end from last
#            print(str) # 'Wait 100ms # do a wait [newline] R0, K0:'
def tokenize(source: str):
    tokens = []
    line_number = 1

    index = 0
    while index < len(source):
        char = source[index]

        if char == ' ' or char == '\t':
            index = index + 1
            continue
        if char == '\n':
            line_number = line_number + 1
            index = index + 1
            continue
        if char == '#':
            while(index < len(source) and source[index] != '\n'):
                index = index + 1
            index = index + 1 # eat the \n
            line_number = line_number + 1
            continue
        if char == ',':
            tokens.append((Token.SYM_COMMA, index, index + 1, line_number))
            index = index + 1
            continue
        if char == '+':
            tokens.append((Token.SYM_PLUS, index, index + 1, line_number))
            index = index + 1
            continue
        if char == ':':
            tokens.append((Token.SYM_COLON, index, index + 1, line_number))
            index = index + 1
            continue

        if char == '"':
            start = index
            index = index + 1
            try:
                while(source[index] != '"'):
                    index += 1
                index = index + 1 # eat the "
            except IndexError:
                raise AttributeError('Line {}: Unterminated string'.format(line_number))

            tokens.append((Token.STRING_LIT, start, index, line_number))
            continue

        # Hex/key literal
        if char == '0' and source[index + 1] == 'x':
            start = index
            index += 2 

            if (source[index] not in string.hexdigits):
                raise AttributeError('Line {}: Hex literal must have have all hex digits'.format(line_number))
            
            while(index < len(source) and source[index] in string.hexdigits):
                index += 1

            tokens.append((Token.HEX_LIT, start, index, line_number))
            continue

        # Number literal
        if char.isdigit():
            start = index

            while(index < len(source) and source[index].isdigit()):
                index += 1
            
            tokens.append((Token.NUM_LIT, start, index, line_number))
            continue


        if not char.isalnum():
            raise AttributeError('Line {}: Unexpected character \'{}\''.format(line_number, char))

        start = index
        while(index < len(source) and source[index].isalnum()):
            index += 1

        # Grab Row/Key Literals if they exist (K33, R999)
        if (source[start] == 'R' or source[start] == 'K') and source[start+1:index].isdigit():
            if source[start] == 'R':
                tokens.append((Token.ROW_LIT, start, index, line_number))
            else:
                tokens.append((Token.KEY_LIT, start, index, line_number))
            continue

        # Handle Keywords
        identifier = source[start:index].lower()
        token_type = Token.IDENTIFIER

        if identifier == 'on' and source[index] == ' ':
            # make a restore point
            old_index = index
            
            # move past the space
            index = index + 1 

            # look forward to see if we find the trigger
            while(index < len(source) and (source[index].isalnum() or source[index] == '-')): # '-' for double-click
                index = index + 1

            trigger = source[start:index].lower()
            if trigger == 'on press':
                token_type = Token.OPERATION_PRESS
            if trigger == 'on click':
                token_type = Token.OPERATION_CLICK
            if trigger == 'on hold':
                token_type = Token.OPERATION_HOLD
            if trigger == 'on double-click':
                token_type = Token.OPERATION_DOUBLE_CLICK
            if trigger == 'on release':
                token_type = Token.OPERATION_RELEASE

            # Trigger not found, restore index
            if token_type == Token.IDENTIFIER:
                index = old_index
        if identifier == 'press':
            token_type = Token.ACTION_PRESS
        if identifier == 'release':
            token_type = Token.ACTION_RELEASE
        if identifier == 'click':
            token_type = Token.ACTION_CLICK
        if identifier == 'wait':
            token_type = Token.ACTION_WAIT
        if identifier == 'toggle':
            token_type = Token.ACTION_TOGGLE
        if identifier == 'leave':
            token_type = Token.ACTION_LEAVE
        if identifier == 'type':
            token_type = Token.ACTION_TYPE
        if identifier == 'bootloader':
            token_type = Token.ACTION_BOOTLOADER
        if identifier == 'home':
            token_type = Token.ACTION_HOME
        if identifier == 'nothing':
            token_type = Token.ACTION_NOTHING
        if identifier == 'quickly':
            token_type = Token.PARAMETER_QUICKLY
        if identifier == 'slowly':
            token_type = Token.PARAMETER_SLOWLY
        if identifier == 'repeatedly':
            token_type = Token.PARAMETER_REPEATEDLY
        if (identifier == "ms" or identifier == "milliseconds"):
            token_type = Token.PARAMETER_TIME_MS
        if (identifier == "sec" or identifier == "seconds"):
            token_type = Token.PARAMETER_TIME_SEC
        if (identifier == "min" or identifier == "minutes"):
            token_type = Token.PARAMETER_TIME_MIN
        if identifier == 'switch' and source[index:index + 3].lower() == ' to':
            index = index + 3
            token_type = Token.ACTION_SWITCH_TO
        if identifier == 'reset' and source[index:index + 9].lower() == ' keyboard':
            index = index + 9
            token_type = Token.ACTION_RESET_KEYBOARD
        if identifier == 'pass' and source[index:index + 8].lower() == ' through':
            index = index + 8
            token_type = Token.ACTION_PASS_THROUGH
        if identifier == 'reload' and source[index:index + 9].lower() == ' key maps':
            index = index + 9
            token_type = Token.ACTION_RELOAD_KEY_MAPS
        if identifier == 'at' and source[index:index + 12].lower() == ' human speed':
            index = index + 12
            token_type = Token.PARAMETER_AT_HUMAN_SPEED
        if identifier == 'until' and source[index:index + 9].lower() == ' released':
            index = index + 9
            token_type = Token.PARAMETER_UNTIL_RELEASED
        if identifier == 'other' and source[index:index + 18].lower() == ' keys fall through':
            index = index + 18
            token_type = Token.TOP_OTHER_KEYS_FALL_THROUGH
        if identifier == 'block' and source[index:index + 11].lower() == ' other keys':
            index = index + 11
            token_type = Token.TOP_BLOCK_OTHER_KEYS
        
        tokens.append((token_type, start, index, line_number))

    return tokens

# Takes the full token list and the index of the current token to be parsed
# and returns an array of tokens representing a single action/action list and
# the index for the next token to be parsed
# 
# ex [..., Wait, 100ms, A, B, +, C, R0, ...], index = 7
# => [Wait, 100ms, A, B, +, C], index = 13
def parse_action(source, tokens, index):
    front_disallowed_tokens = [
        Token.SYM_PLUS, 
        Token.SYM_COMMA,
        Token.STRING_LIT,
        Token.PARAMETER_REPEATEDLY,
        Token.PARAMETER_QUICKLY,
        Token.PARAMETER_SLOWLY,
        Token.PARAMETER_AT_HUMAN_SPEED,
        Token.PARAMETER_UNTIL_RELEASED,
    ]

    back_disallowed_tokens = [
        Token.SYM_PLUS, 
        Token.SYM_COMMA,
        Token.NUM_LIT,
    ]

    allowed_tokens = [
        Token.SYM_PLUS, 
        Token.SYM_COMMA,
        Token.STRING_LIT,
        Token.NUM_LIT,
        Token.HEX_LIT,
        Token.IDENTIFIER,
        Token.ACTION_PRESS,
        Token.ACTION_RELEASE,
        Token.ACTION_CLICK,
        Token.ACTION_WAIT,
        Token.ACTION_SWITCH_TO,
        Token.ACTION_TOGGLE,
        Token.ACTION_LEAVE,
        Token.ACTION_TYPE,
        Token.ACTION_RESET_KEYBOARD,
        Token.ACTION_BOOTLOADER,
        Token.ACTION_HOME,
        Token.ACTION_NOTHING,
        Token.ACTION_PASS_THROUGH,
        Token.ACTION_RELOAD_KEY_MAPS,
        Token.PARAMETER_REPEATEDLY,
        Token.PARAMETER_QUICKLY,
        Token.PARAMETER_SLOWLY,
        Token.PARAMETER_AT_HUMAN_SPEED,
        Token.PARAMETER_UNTIL_RELEASED,
        Token.PARAMETER_TIME_MS,
        Token.PARAMETER_TIME_MIN,
        Token.PARAMETER_TIME_SEC,
    ]

    head = tokens[index]
    if t_tag(head) in front_disallowed_tokens:
        raise AttributeError('Line {}: Token not allowed at start of action: {}'.format(t_lineno(head), t_str(source, head)))

    index = index + 1
    start_index = index 
    actions = [head]

    while (index < len(tokens)
          and (t_tag(tokens[index]) in allowed_tokens)):
        actions.append(tokens[index])
        index = index + 1

    # Check for trailing '+' and ','
    if t_tag(actions[-1]) in [Token.SYM_PLUS, Token.SYM_COMMA]:
        raise AttributeError('Line {}: Token not allowed at end of action: {}'.format(t_lineno(actions[-1]), t_str(source, actions[-1])))

    # Check for two '+' in a row
    for i in range(len(actions) - 1): 
        if (t_tag(actions[i]) == Token.SYM_PLUS and t_tag(actions[i+1]) == Token.SYM_PLUS):
            raise AttributeError('Line {}: Cannot have two consecutive \'+\''.format(t_lineno(actions[i])))

    return (actions, index)


# Top level parsing function
# Returns the following parsed token sets
# top_level: List of all top level tokens in source
#            ex: [BLOCK_OTHER_KEYS, OTHER_KEYS_FALL_THROUGH]
# bindings: A maps of all bindings parsed from the tokens. At this point, the 
#           tokens are only grouped into bindings and no action semantics have
#           been extracted.
#           
#           type: (Row, Key) => Event => Values
#           ex: {
#             (0, 0): {
#               'standard': [LEFT, ALT, +, F, +, A],
#               'on hold': [TYPE, "abc", quickly, Wait, 100ms]
#             },
#             (2, 3): { 'standard': [Q] }
#           }
def parse(source, tokens):
    # Build up the output map.
    # (Row, Key) => Event => Values
    bindings = []
    top_level = []

    index = 0
    while index < len(tokens):
        r = tokens[index]

        # If this is a top level statement, extract it into top_level then continue 
        # parsing the bindings.
        if t_tag(r) in [Token.TOP_BLOCK_OTHER_KEYS, Token.TOP_OTHER_KEYS_FALL_THROUGH]:
            top_level.append(r)
            index = index + 1
            continue

        if t_tag(r) != Token.ROW_LIT:
            raise AttributeError('Line {}: Expected row literal, saw \'{}\' instead'.format(t_lineno(r), t_str(source, r)))

        index = index + 1
        if index >= len(tokens) or t_tag(tokens[index]) != Token.SYM_COMMA:
            raise AttributeError('Line {}: Expected comma after \'{}\''
              .format(t_lineno(r), t_str(source, r)))

        index = index + 1

        if index >= len(tokens) or t_tag(tokens[index]) != Token.KEY_LIT:
            raise AttributeError('Line {}: Expected key literal'.format(t_lineno(tokens[index - 1])))

        k = tokens[index]
        index = index + 1
        if index >= len(tokens) or t_tag(tokens[index]) != Token.SYM_COLON:
            raise AttributeError('Line {}: Expected colon after \'{}\''
              .format(t_lineno(k), t_str(source, k)))

        index = index + 1

        key_tuple = (int(t_str(source, r)[1:]), int(t_str(source, k)[1:]))
        binding = { key_tuple: {} }

        inline = True
        # if there is any on-x event, process them all
        while index < len(tokens) and t_tag(tokens[index]) in [Token.OPERATION_PRESS, Token.OPERATION_CLICK, Token.OPERATION_HOLD, Token.OPERATION_DOUBLE_CLICK, Token.OPERATION_RELEASE]:
            inline = False
            operation = tokens[index]
            index = index + 1

            if (index >= len(tokens) or t_tag(tokens[index]) != Token.SYM_COLON):
                raise AttributeError('Line {}: Expected colon after \'{}\''.format(t_lineno(operation), t_str(source, operation)))
            
            index = index + 1
            if index >= len(tokens):
                raise AttributeError('Line {}: Expected action definition after \'{}:\''.format(t_lineno(operation), t_str(source, operation)))

            (operation_actions, index) = parse_action(source, tokens, index)

            operation_str = t_str(source, operation).lower()
            binding[key_tuple][operation_str] = operation_actions

        if inline: # otherwise process the inline statement 
            if index >= len(tokens):
                raise AttributeError('Line {}: Expected action definition after \'{}:\''.format(t_lineno(k), t_str(source, k)))
            (actions, index) = parse_action(source, tokens, index)
            binding[key_tuple]['standard'] = actions
        
        bindings.append(binding)

    return (top_level, bindings)

# Parses a single token into a value of time in seconds
# '100ms' -> 0.1, '1sec'-> 1
# Errors if more than one token, time missing units, chars before units not convertable 
def parse_time(source, tokens):
    if len(tokens) != 2:
        raise AttributeError('Line {}: Expected 2 time parameters, saw {} ({}) paramters instead.'
          .format(t_lineno(tokens[0]), len(tokens), t_run_str(source, tokens[0], tokens[-1])))

    duration = tokens[0]
    units = tokens[1]

    if t_tag(duration) != Token.NUM_LIT:
        raise AttributeError('Line {}: Expected number in time literal'.format(t_lineno(duration)))

    try: 
        time = float(t_str(source, duration))
    except ValueError:
        raise AttributeError('Line {}: Unable to convert \'{}\' to a time'.format(t_lineno(time_token), token))

    if t_tag(units) == Token.PARAMETER_TIME_MS:
        return time / 1000.0

    if t_tag(units) == Token.PARAMETER_TIME_SEC:
        return time

    if t_tag(units) == Token.PARAMETER_TIME_MIN:
        return time * 60.0

    raise AttributeError('Line {}: Expected units in time literal'.format(t_lineno(units)))


# Parse a list of tokens representing a key conbination into the keycode
# [LEFT, ALT, +, F, +, A] -> [0xE2, 0x09, 0x04]
def parse_keycodes(source, tokens):  # TODO: Make this auto-detect shift, alt, cmd, etc placement
    keycodes = []
    subtokens = [[]]

    # Split token list [LEFT, ALT, +, F, +, A]
    # into [[LEFT, ALT], [F], [A]]
    for token in tokens:
        if t_tag(token) == Token.SYM_PLUS:
            subtokens.append([])
            continue
        subtokens[-1].append(token)

    parsed_keys = []
    for token in subtokens:
        if t_tag(token[0]) == Token.HEX_LIT:
            if len(token) != 1:
                raise AttributeError('Line {}: Hex literals must be separated by \'+\''.format(t_lineno(token[0]), t_str(source, token[0])))
            keycodes.append(int(t_str(source, token[0]), 16))
            continue

        # Merge tokens into single name [LEFT, ALT] => 'LEFTALT'
        key_name = ''
        for t in token:
            key_name = key_name + t_str(source, t)

        # Save list of parsed key names to print later
        parsed_keys.append(key_name)

        if not key_name in key_names:
            raise AttributeError('Line {}: Invalid Action or Key \'{}\''.format(t_lineno(token[0]), t_str(source, token[0])))

        keycodes.append(key_names[key_name])

    debug_out('Parsed keycode(s) {}'.format(' and '.join(parsed_keys)))
    return keycodes

# Parses a list of tokens representing a single action (Type "hello" quickly 100ms)
# into the associated 'Action' class
def parse_action_token(source, tokens):
    debug_out('Parsing action token', tokens)

    action_token = tokens[0]
    action_token_type = t_tag(action_token)
    
    debug_out('This token is a(n)', action_token_type, 'action')

    if action_token_type == Token.ACTION_PRESS:
        if len(tokens) == 1:
            raise AttributeError('Line {}: Press action requires key parameter'.format(t_lineno(action_token)))
        keycodes = parse_keycodes(source, tokens[1:])
        return PressKeyAction(keycodes)

    if action_token_type == Token.ACTION_RELEASE:
        if len(tokens) == 1:
            raise AttributeError('Line {}: Release action requires key parameter'.format(t_lineno(action_token)))
        keycodes = parse_keycodes(source, tokens[1:])
        return ReleaseKeyAction(keycodes)

    if action_token_type == Token.ACTION_CLICK:
        if len(tokens) == 1:
            raise AttributeError('Line {}: Click action requires key parameter'.format(t_lineno(action_token)))
        keycodes = parse_keycodes(source, tokens[1:])
        return ClickKeyAction(keycodes)

    if action_token_type == Token.ACTION_WAIT:
        if len(tokens) != 3:
            raise AttributeError('Line {}: Wait action requires 2 parameters'.format(t_lineno(action_token)))
        return DelayAction(parse_time(source, tokens[1:]))

    if action_token_type == Token.ACTION_SWITCH_TO:
        if len(tokens) == 1:
            raise AttributeError('Line {}: Switch to action requires layer parameter'.format(t_lineno(action_token)))
        if len(tokens) == 2 and tokens[1][0] == Token.PARAMETER_UNTIL_RELEASED:
            raise AttributeError('Line {}: Missing layer name for temporary switch: \'{}\''
                  .format(t_lineno(action_token), t_run_str(source, tokens[0], tokens[-1])))

        if t_tag(tokens[-1]) == Token.PARAMETER_UNTIL_RELEASED:
            layer_name = t_run_str(source, tokens[1], tokens[-2]).lower()
            debug_out('This is a temporary layer switch to \'{}\''.format(layer_name))
            return TemporaryLayerAction(layer_name)
        else:
            layer_name = t_run_str(source, tokens[1], tokens[-1]).lower()
            debug_out('This is a regular layer switch to \'{}\''.format(layer_name))
            return SwitchToLayerAction(layer_name)

    if action_token_type == Token.ACTION_TOGGLE:
        if len(tokens) == 1:
            raise AttributeError('Line {}: Toggle action requires layer parameter'.format(t_lineno(action_token)))
        param = t_run_str(source, tokens[1], tokens[-1]) 
        return ToggleLayerAction(param.lower())

    if action_token_type == Token.ACTION_LEAVE:
        if len(tokens) == 1:
            raise AttributeError('Line {}: Leave action requires layer parameter'.format(t_lineno(action_token)))
        param = t_run_str(source, tokens[1], tokens[-1]) 
        return LeaveLayerAction(param.lower())

    if action_token_type == Token.ACTION_RESET_KEYBOARD:
        if len(tokens) != 1:
            raise AttributeError('Line {}: Reset Keyboard action shouldn\'t have any parameters'.format(t_lineno(action_token)))
        return ResetKeebAction()

    if action_token_type == Token.ACTION_BOOTLOADER:
        if len(tokens) != 1:
            raise AttributeError('Line {}: Bootloader action shouldn\'t have any parameters'.format(t_lineno(action_token)))
        return KeebBootloaderAction()

    if action_token_type == Token.ACTION_HOME:
        if len(tokens) != 1:
            raise AttributeError('Line {}: Home action shouldn\'t have any parameters'.format(t_lineno(action_token)))
        return ResetLayersAction()

    if action_token_type == Token.ACTION_NOTHING:
        if len(tokens) != 1:
            raise AttributeError('Line {}: Nothing action shouldn\'t have any parameters'.format(t_lineno(action_token)))
        return NothingburgerAction()

    if action_token_type == Token.ACTION_PASS_THROUGH:
        if len(tokens) != 1:
            raise AttributeError('Line {}: Pass through action shouldn\'t have any parameters'.format(t_lineno(action_token)))
        return PassThroughAction()

    if action_token_type == Token.ACTION_RELOAD_KEY_MAPS:
        if len(tokens) != 1:
            raise AttributeError('Line {}: Reload Key Maps action shouldn\'t have any parameters'.format(t_lineno(action_token)))
        return ReloadKeymapAction()

    if action_token_type == Token.ACTION_TYPE:
        # TODO get these magic numbers outta here
        if len(tokens) == 1:
            raise AttributeError('Line {}: Type action missing text parameter'.format(t_lineno(action_token)))

        string_lit = tokens[1]
        if t_tag(string_lit) != Token.STRING_LIT:
            raise AttributeError('Line {}: Type action\'s first parameter must be quoted text'.format(t_lineno(action_token)))

        delay = 0.01
        
        # Adjust both sides by 1 to remove quotes
        string_to_type = t_str(source, string_lit)[1:-1] 
        repeating = False
        time_keywork_count = 0

        replacements = {
            # '[COMMA]': ',', # Not needed, just type ,
            '[DOUBLE QUOTES]': '"',
            '[SINGLE QUOTE]': '\'',
            '[RETURN]': '\n',
            # TODO: Should escape sequences be allowed? i.e. '\n' in the text
        }
        for match, replace in replacements.items():
            string_to_type = string_to_type.replace(match, replace)

        num_token = None
        unit_token = None

        for token in tokens[2:]:
            param = t_tag(token)
            if param == Token.PARAMETER_REPEATEDLY:  # TODO: 'once' and timing strings are mutually exclusive, improve parsing to catch multiple tokens
                debug_out('Repeat during a hold')
                repeating = True
            if param == Token.PARAMETER_SLOWLY:
                debug_out("Found speed token 'slowly'")
                delay = 0.2
                time_keywork_count += 1
            if param == Token.PARAMETER_QUICKLY:
                debug_out("Found speed token 'quickly'")
                delay = 0
                time_keywork_count += 1
            if param == Token.PARAMETER_AT_HUMAN_SPEED:
                debug_out("Found speed token 'at human speed'")
                delay = 0.05
                time_keywork_count += 1
            if param == Token.NUM_LIT: # Explict speed 
                if num_token != None: # We've previously set this value, trigger a 'too many speeds' error
                    time_keywork_count += 1
                num_token = token
            if param in [Token.PARAMETER_TIME_MS, Token.PARAMETER_TIME_SEC, Token.PARAMETER_TIME_MIN]:
                if unit_token != None: # We've previously set this value, trigger a 'too many speeds' error
                    time_keywork_count += 1
                unit_token = token

        # TODO: Find a more elegant way to do this. This allows wacky things like
        # Type "hello" seconds repeatedly 100
        if (num_token is not None and unit_token is not None):
                delay = parse_time(source, [num_token, unit_token])
                debug_out("Found explicit speed token '{}'".format(t_str(source,token)))
                time_keywork_count += 1

        if (num_token is not None and unit_token is None):
            raise AttributeError('Line {}: time provided without units: \'{}\''.format(t_lineno(num_token), t_str(source, num_token)))

        if (num_token is None and unit_token is not None):
            raise AttributeError('Line {}: unit provided without time: \'{}\''.format(t_lineno(unit_token), t_str(source, unit_token)))

        if time_keywork_count > 1:
            raise AttributeError('Line {}: Multiple speeds set for Type action. Please select one.\n\t{}'.format(t_lineno(action_token), t_run_str(source, tokens[0], tokens[-1])))

        debug_out('String to type: "{}", delay: {}, {}'.format(
            string_to_type, delay, 'repeating' if repeating else 'non-repeating'))

        if repeating:
            return StringTyperAction(string_to_type, delay)
        
        return NonRepeatingStringTyperAction(string_to_type, delay)

    debug_out("Didn't parse to an action. Is it a keycode?")
    keycodes = parse_keycodes(source, tokens)
    debug_out("This is a boring old regular key action!")
    return GenericKeyAction(keycodes)

# Convert a list of tokens representing an action/action sequence 
# i.e (Wait 100ms, Type "hello", Bootloader) into the associated Action() object
def parse_action_list(source, tokens, operation): 
    token_sets = [[]]
 
    # Split the token list on commas, each index into token_sets
    # represents a single action with any params
    for token in tokens:
        if t_tag(token) == Token.SYM_COMMA:
            token_sets.append([])
        else:
            token_sets[-1].append(token)

    debug_out('Action tokens:', token_sets)

    actions = []
    for token_set in token_sets:
        sub_action = parse_action_token(source, token_set)
        if type(sub_action) is TemporaryLayerAction and operation != 'on hold':
            debug_out('TemporaryLayerAction can only be bound to On Hold, not', operation)
            raise AttributeError('Line {}: TemporaryLayerAction can only bind to On Hold'.format(t_lineno(token_set[0])))

        actions.append(sub_action)

    if len(actions) == 1:
        debug_out('This binding is a single action')
        return actions[0]
    
    debug_out('This binding is a sequence')
    action = SequenceAction()
    action.sequence.extend(actions)
    return action

# Parse full source into Layer model
def parse_source(source, layer):
    tokens = tokenize(source)
    (top_level, bindings) = parse(source, tokens)

    for statement in top_level:
        if t_tag(statement) == Token.TOP_OTHER_KEYS_FALL_THROUGH:
            layer.unassigned_keys_fall_through = True
            debug_out('Unassigned keys pass through to lower layer')
            continue        
        if t_tag(statement) == Token.TOP_BLOCK_OTHER_KEYS: 
            layer.unassigned_keys_fall_through = False
            debug_out('Unassigned keys do not pass through')
            continue

    for binding in bindings:
        for key, events in binding.items():
            for event_name, actions in events.items():
                debug_out('Attemping to parse statement \'{}\''
                  .format(t_run_str(source, actions[0], actions[-1])))
                action = parse_action_list(source, actions, event_name)
                layer.bind(key[0], key[1], action, event_name)

    return layer

# Top level parse from file 
def parse_layer_definition(filename, layer):
    debug_out('Parsing', filename)

    layer.reset()
    layer.name = filename.lower()[:filename.rindex('.')] if '.' in filename else filename.lower()

    with open(file, 'r') as f:
        source = f.read()

    return parse_source(source, layer)
