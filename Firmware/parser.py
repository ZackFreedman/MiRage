from actions import *
from keynames import key_names

key_binding_operation_tokens = ['on press', 'on click', 'on hold', 'on double-click', 'on release']
key_binding_action_tokens = ['press', 'release', 'click', 'wait', 'switch to',
                             'toggle', 'leave', 'type', 'reset keyboard', 
                             'bootloader', 'home', 'nothing', 'pass through', 'reload key maps']

debug_line_callback = None

def debug_out(*args):
    # print(' '.join(args))
    print(*args)
    if debug_line_callback is not None:
        debug_line_callback(' '.join(args))

def parse_layer_definition(filename, layer):
    debug_out('Parsing', filename)

    layer.reset()

    lines = []
    with open(filename, 'r') as f:
        lines += f.readlines()

    layer.name = filename.lower()[:filename.rindex('.')] if '.' in filename else filename.lower()

    state = None  # 'binding key', 'assigning screen', 'meta'
    current_binding_row = None
    current_binding_col = None
    screen_being_configured = None

    for line in lines:
        line = line.lstrip().strip()

        debug_out("About to parse:", line)
        if '#' in line:  # Strip out comment
            debug_out('Line may have a comment')
            in_a_string = False
            comment_start_index = -1
            for index, char in enumerate(line):
                if char == '"':
                    if in_a_string:
                        debug_out('String closed on char', index)
                        in_a_string = False
                    else:
                        debug_out('String opened on char', index)
                        in_a_string = True
                elif char == '#':
                    if in_a_string:
                        debug_out('Hash in pos {} is in a literal'.format(index))
                    else:
                        debug_out('Hash in pos {} is the start of a commment'.format(index))
                        comment_start_index = index
                        break

            if comment_start_index >= 0:
                line = line[:comment_start_index].strip()
                debug_out("Yup, comment. Removed it, line is now", line)

            debug_out('Now processing line:', line)

            # if line[0] == '#':
            #     debug_out('We got a comment boys')
            #     continue

        if not len(line):
            debug_out('Line handled')
            continue

        if line[0] == 'R':  # Could be a definition
            if ',' in line and 'K' in line and ':' in line:
                try:
                    row = int(line[1 : line.index(',')])
                    col = int(line[line.index('K') + 1 : line.index(':')])
                    state = 'binding key'

                    current_binding_row = row
                    current_binding_col = col  # Do this afterwards in case it fails partway

                    debug_out('Now binding row {} col {}'.format(
                        current_binding_row, current_binding_col))

                    # There could be a boring regular key definition inline, let's see
                    try:
                        keycodes = parse_keycodes(line[line.index(':') + 1:].lstrip())
                        debug_out('This has an inline generic key definition')
                        layer.bind(current_binding_row, current_binding_col,
                            GenericKeyAction(keycodes))
                        debug_out('Line handled - nothing past this point matters')
                        continue
                    except AttributeError:
                        debug_out('No inline generic key definition')
                except (AttributeError, ValueError):
                    debug_out('Nope, not a key definition')

                # Strip out coordinates
                line = line[line.index(':') + 1:]

        elif 'Other keys fall through' in line and line.index('Other keys fall through') == 0:
            layer.unassigned_keys_fall_through = True
            debug_out('Unassigned keys pass through to lower layer')
            debug_out('Line handled')  # TODO: This is crude - add a fallback keybinding instead
            continue        

        elif 'Block other keys' in line and line.index('Block other keys') == 0:
            layer.unassigned_keys_fall_through = False
            debug_out('Unassigned keys do not pass through')
            debug_out('Line handled')
            continue

        # Doesn't make sense to configure screens in a layer - should get its own parser?
        """
        elif 'Top Screen' in line and line.index('Top Screen') == 0:  # TODO: Remove need to capitalize? Performance benefits?
            state = 'assigning screen'
            screen_being_configured = 0
            debug_out('Now configuring top screen')
            line = line[len('Top Screen'):].lstrip()

        elif 'Middle Screen' in line and line.index('Middle Screen') == 0:
            state = 'assigning screen'
            screen_being_configured = 1
            debug_out('Now configuring middle screen')
            line = line[len('Middle Screen'):].lstrip()

        elif 'Bottom Screen' in line and line.index('Bottom Screen') == 0:  # TODO: Remove need to capitalize? Performance benefits?
            state = 'assigning screen'
            screen_being_configured = 'top'
            debug_out('Now configuring top screen')
            line = line[len('Top Screen'):].lstrip()
        """

        # TODO throw error if a layer has passthrough disabled and no way to dismiss itself

        # TODO detect screen and preamble bits here

        # At this point, we know this line is not a new definition.
        # It should continue describing info for the ongoing state.

        line = line.lstrip().strip()
        if not len(line):
            debug_out('Line handled')
            continue

        if state == 'binding key':
            operation, action = parse_binding(line)
            debug_out('Binding a {} to {} on key {}, {}'.format(
                type(action), operation, current_binding_row, current_binding_col))
            layer.bind(current_binding_row, current_binding_col,
                action, operation)

        debug_out('Line handled')

    return layer
        

def parse_binding(line):
    # Assumes whitespace, coordinates already stripped out
    tokens = []
    operation = None
    action = None
    key_combo_in_progress = False

    debug_out('Parsing binding line', line)

    if line.count('"') % 2:
        debug_out('Line has at least one invalid typed string')
        raise AttributeError('Unclosed typed string')

    for token in key_binding_operation_tokens:
        if token + ':' in line.lower() and line.lower().index(token) == 0:
            debug_out('This line is a', token, 'operation')
            operation = token
            line = line[line.index(':') + 1:].lstrip()  # Remove processed operation token
            break

    tokens = line.split(',')
    debug_out('Action tokens:', tokens)

    if len(tokens) > 1:
        debug_out('This binding is a sequence')
        action = SequenceAction()

        for token in tokens:
            sub_action = parse_action_token(token)
            action.sequence.append(sub_action)
    else:
        debug_out('This binding is a single action')
        action = parse_action_token(tokens[0])

    if isinstance(action, TemporaryLayerAction) and not operation == 'on hold':
        debug_out('TemporaryLayerAction can only be bound to On Hold, not', operation)
        raise AttributeError('TemporaryLayerAction can only bind to On Hold')

    # if isinstance(action, GenericKeyAction) and operation is not None:
    #     print ("Regular key behavior can't be bound to a special operation")

    return operation, action


def parse_action_token(token):
    debug_out('Parsing action token', token)

    for action_token in key_binding_action_tokens:
        if action_token in token.lower() and token.lower().index(action_token) == 0:
            param = token[len(action_token) + 1:]

            debug_out('This token is a(n)', action_token, 'action')

            if action_token == 'press':
                keycodes = parse_keycodes(param)
                action = PressKeyAction(keycodes)

            elif action_token == 'release':
                keycodes = parse_keycodes(param)
                action = ReleaseKeyAction(keycodes)

            elif action_token == 'click':
                keycodes = parse_keycodes(param)
                action = ClickKeyAction(keycodes)

            elif action_token == 'wait':
                action = DelayAction(parse_time(param))

            elif action_token == 'switch to':
                param = param.lower()
                if ' until released' in param:
                    debug_out('This is a temporary layer switch')
                    action = TemporaryLayerAction(param[:param.index(' until released')])
                else:
                    debug_out('This is a regular layer switch')
                    action = SwitchToLayerAction(param)

            elif action_token == 'toggle':
                action = ToggleLayerAction(param.lower())

            elif action_token == 'leave':
                action = LeaveLayerAction(param.lower())

            elif action_token == 'type':
                # TODO get these magic numbers outta here
                subtokens = param.split('"')

                delay = 0.01
                string_to_type = ''
                repeating = False

                for raw_token in subtokens:
                    token = raw_token.lstrip().strip()

                    if not len(token):
                        continue

                    if token == 'repeatedly':  # TODO: 'once' and timing strings are mutually exclusive, improve parsing to catch multiple tokens
                        debug_out('Repeat during a hold')
                        repeating = True
                    elif token == 'slowly':
                        debug_out("Found speed token 'slowly'")
                        delay = 0.2
                    elif token == 'at human speed':
                        debug_out("Found speed token 'at human speed'")
                        delay = 0.05
                    elif token == 'quickly':
                        debug_out("Found speed token 'quickly'")
                        delay = 0
                    else:
                        try:
                            delay = parse_time(token)
                            debug_out("Found explicit speed token '{}'".format(token))
                        except AttributeError:
                            if len(string_to_type):
                                raise AttributeError('Parsing error! Either existing string "{}" or new token "{}" is malformed.'.format(string_to_type, token))   
                            string_to_type = token.replace('[COMMA]', ',').replace('[DOUBLE QUOTES]', '"')

                debug_out('String to type: "{}", delay: {}, {}'.format(
                    string_to_type, delay, 'repeating' if repeating else 'non-repeating'))

                if repeating:
                    action = StringTyperAction(string_to_type, delay)
                else:
                    action = NonRepeatingStringTyperAction(string_to_type, delay)

            elif action_token == 'reset keyboard':
                action = ResetKeebAction()

            elif action_token == 'bootloader':
                action = KeebBootloaderAction()

            elif action_token == 'home':
                action = ResetLayersAction()

            elif action_token == 'nothing':
                action = NothingburgerAction()

            elif action_token == 'pass through':
                action = PassThroughAction()

            elif action_token == 'reload key maps':
                action = ReloadKeymapAction()

            else:
                debug_out('/!\\ Zack forgot to implement the', action_token)

            return action

    debug_out("Didn't parse to an action. Is it a keycode?")
    keycodes = parse_keycodes(token)

    debug_out("This is a boring old regular key action!")
    return GenericKeyAction(keycodes)


def parse_keycodes(token):  # TODO: Make this auto-detect shift, alt, cmd, etc placement
    subtokens = token.upper().replace(' ', '').split('+')
    keycodes = []

    for token in subtokens:
        if not token in key_names:
            debug_out(token, 'is not a key name')
            raise AttributeError(token, 'is not a key name')

        keycodes.append(key_names[token])

    debug_out('Parsed keycode(s) {}'.format(' and '.join(subtokens)))
    return keycodes


def parse_time(token):
    debug_out('Parsing time token:', token)

    time = None

    if 'ms' in token or 'milliseconds' in token:
        time = float(token[:token.index('m')]) / 1000.0

    elif 'sec' in token:
        time = float(token[:token.index('s')])

    elif 'min' in token:
        time = float(token[:token.index('m')]) * 60.0

    if time is None:
        debug_out('Parsing failed')
        raise AttributeError('Failed to parse {} to a time'.format(token))

    debug_out('Parsed to {.2d} sec'.format(time))
    return time