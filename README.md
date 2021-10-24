# MiRage Modular Keyboard
## © 2021 Zack Freedman of Voidstar Lab
## Licensed Creative Commons 4.0 Attribution Noncommercial Share-Alike

The MiRage is a 60% ortholinear keyboard with three clickable OLED displays, intended for Kailh Choc switches and running custom CircuitPython firmware on a Seeedstudio Xiao RP2040. 

***THIS PROJECT IS INCOMPLETE. DO NOT MAKE IT.***

The PCB can be populated as-is for a "plank" keyboard or broken in half for a split board. The right half can be used independently as the Rage Pad numberpad/macro pad/stream deck.

This was designed for a YouTube video on my channel: `URL HERE` It will be improved and sold as a kit, and will form part of a larger project called the Fata Morgana cyberdeck.

Fusion 360 model: https://a360.co/3vEh6YI

The PCB, firmware, keymaps, and models have major issues that need to be fixed before moving forward. ***This project is not ready to be reproduced. Do not attempt to make it.*** Keymap instructions, assembly guide, BOM, and other documentation will be provided once the project is ready for release.

My component choices are final. Attempts to change my mind will be roasted in a future video.

Libraries are temporarily included for testing purposes. These will be replaced by references on release.

Keymaps are lists of bindings in the format:
R\[Row #\], K\[Key #\]: \[Key name (optional)\] # Comments start with a hash
	On press: \[Command(s) to perform once as soon as user presses key\]
	On click: \[Command(s) to perform when user presses and releases key within a few hundred milliseconds\]
	On double-click: \[Command(s) to perform when user presses and releases key twice within a few hundred milliseconds. The dash in 'double-click' is not optional.\]
	On hold: \[Command(s) to perform when user holds key for more than a few hundred ms. These generally repeat or remain in effect until the key is released.\]
	On release: \[Command(s) to perform once when user releases key. This is done after On Click and On Double-Click events are finished, and after ongoing On Hold events are cleaned up.\]

Actions you can bind to a key or event:
- `LEFT SHIFT`: Specify key bindings by naming them in all caps. You can see all the available key names in `keynames.py`. Key names must be in all caps. Spaces are optional. If a key is bound inline, it binds all events.
- `Click LEFT SHIFT`: This key will be pressed and instantly released a single time, even if this is called by an On Hold event. Clicking a key that's already Pressed will release, press, and release it.
- `Press LEFT SHIFT`: This key will be pressed indefinitely. Pressing a key that's already Pressed has no effect. Remember to add a way to release it...
- `Release LEFT SHIFT`: This key will be released. No effect if the key is not Pressed.
- `CTRL + ALT + DELETE`: Performs an operation on multiple keys simultaneously. You can Click, Press, Release, or straight-up bind key combos as if they were individual keys! Spaces around the plus signs are optional.
- `Switch to Numpad Layer`: Invokes specified layer indefinitely. This is case-insensitive. You don't need to include the layer's extension. Make sure to read the Layer Gotchas below!
- `Leave Numpad Layer`: If specified layer is currently invoked, dismisses it.
- `Switch to Numpad Layer until released`: Invokes the specified layer as long as this key remains held, and dismisses it when released. Cannot be bound to On Press, On Click, On Double-Click, or On Release events. **While in effect, layers above the one that defined this action do not apply to this key**.
- `Toggle Numpad Layer`: Acts as a Switch To action if specified layer is not currently in effect, and a Leave action if it is. Note that this can be blocked by layers above it, so make sure the new layer leaves this key open!
- `Go home`: Dismisses all invoked layers.
- `Type "Hello world!"`: Types the specified string a single time, one letter at a time. **Don't put double quotes and commas in the string!** Use `[DOUBLE QUOTES]` and `[COMMA]` instead! Any necessary keys that are currently Pressed will be released, pressed, and released again.
- `Type "Hello World!" repeatedly`: When bound to an On Press or On Hold event, types the string over and over. Extremely annoying.
- `wait 200ms`: Blocks everything for that much time. You can specify milliseconds, seconds, or minutes, in full or using ms, msec, sec, s, m, or min. Used in command sequences.
- `Click WIN+R, wait 200ms, type "cmd", click ENTER`: Sequence any combination of actions with commas. Each action is performed in its entirety before moving on. The On Hold behavior of a command sequence is not yet defined.
- `Nothing`: Allows keys on upper layers to block actions on lower layers without any side effects.
- `Pass through`: Sends this operation to the next lowest layer.
- `Reload keymaps`: Triggers a Go Home action, then reloads all the keymaps. 
- `Reset keyboard`: Triggers a software reset - disconnects from PC, reloads keymaps, and reconnects.
- `Bootloader`: Enters UF2 bootloader - disconnects from PC, kills CircuitPython, and reconnects as UF2 flash drive. **There is no way to return from the bootloader to the code without unplugging the keyboard.** This is an inbuilt limit of the bootloader and beyond my control.

Row and key numbers are zero-indexed, and refer to the physical placement of the keys on the keyboard. **These have nothing to do with the schematic. It's common sense numbering** Row 0, Key 0 is the top-left key.

Whitespace and line terminators are irrelevent. You can even use tabs, you sick bastard. UTF-8 encoding is strongly recommended; not sure how well Python handles bigger characters.

You can actually define the same key and same key action multiple times in the same map. This has the same effect as creating Sequences, and is extremely obnoxious to debug. I can't prevent you from doing it, but I can say "I told you so."

Layer Gotchas!
- Each layer's name is the same as the filename of the keymap that defined it, and is case- and extension-insensitive. **If multiple keymap files have the same name with different capitalization, the keyboard will crash on purpose just to spite you.**
- One layer must be called Base Layer. This is not optional. **The keyboard will not boot unless there's an applicable Base Layer.**
- The Base Layer is always in effect. When another layer is invoked, it's "stacked" on top. Invoking another layer stacks it on the other layer, and so on.
- When a key event happens, it's sent to the topmost layer. If that layer doesn't handle it, the next layer is checked, and so on. If you want the event to fall through anyways, such as in a sequence, use the `Pass through` action.
- Layer-related actions **DO NOT** apply immediately. Instead, the system reads every key, completes every Action fired, then applies any layer actions. This makes the layer switching process more predictable if multiple keys were pressed. 
- When a layer is invoked, if it's already in the stack, it's moved to the top.
- You cannot invoke or dismiss the Base Layer. Attempting to do so has no effect.
- The layer(s) selected by Layer Select Widgets have special slots above the Base Layer and just below the layer stack. If multiple clicky displays have Layer Select Widgets, the top screen layer is just below the layer stack and the bottom screen layer just above the Base Layer.
- If a layer selected by a Layer Select Widget is invoked, it moves from its special slot to the top of the stack. If it's dismissed, it returns to its special slot.
- Folders are provided for MiRage and Rage keymaps. Only the relevant ones apply.
- *Needs to be implemented:* When a layer is dismissed, if one or more keys with On Hold events defined by that layer are held, the On Hold ends. If one or more held keys have an On Release event, it's called. Pass Through actions in these events are ignored.

PCB problems to fix:
- VDD and VSS supply pins of PCA9505 I/O expanders are reversed
- RESET pins of PCA9505s must be pulled up
- Choc footprints will be extended to support Cherry MX switches
- Cut relief under microcontroller footprint for Adafruit QT PY. This part is **NOT** currently compatible.
- Increase size and number of breakaway tabs
- Right-angle headers are too far apart
- Add at least 4 keys
- Bottom screws are blocked by lowest row of keycaps
- Split is shifted one row to the left from usual typing position

Enclosure problems to fix: 
- Missing holes to access BOOT and RESET buttons
- Missing holes to view onboard LEDs
- Cutout for USB cable is too small 
- Rubber foot relief diameter too small and prone to sagging
- Bottom feet are too far from edges
- A small amount of PCB text is visible - poor fit and finish
- Magnetic applique falls off too easily
- Plank enclosure has header relief on wrong side
- Display buttons can crack if mashed down very hard

Code problems to fix (that I can remember off the top of my head, there are a lot)
- Rage board not implemented (not detected or automatically switched)
- Unplugging left side during runtime causes crash
- Code needs to be sped up about 200%
- Widget updating code needs to be sped up about 5000%
- Rage keymaps are missing layer switches
- Only key bindings can be defined inline
- Interactions between key event bindings and inline key bindings are unspecified
- Hold events lag, as if a click or double-click event were also bound
- Double-clicking also fires Click event
- Ongoing Hold events end sloppily if a layer switch overrides that binding
- No visual feedback for syntax errors, exceptions, layer switches, modal Lock keys, etc
- We need more widgets
- Fallback behavior in case of keymap errors
- Occasional failure to auto-run code on boot
- Including a comma in a 'Type' command crashes parser 
- If a key down command is sent then a Bootloader command runs, the key is never released
- Configuration setting is needed to redefine WINDOWS and ALT to GUI and OPTION 
- **Poor performance is due to CircuitPython, not I/O expanders. These I/O expanders can be polled over 1,000 times a second. This code would be MASSIVELY slower if a matrix were used instead of I/O expanders.**

Additional things to create:
- Plank enclosure without 3.5mm plug relief
- Split enclosure with header relief
- Rage (right hand) enclosure without 3.5mm plug relief
- Dashboard widget
- Widget that interacts with desktop
- Set typing speed 
- Enable/disable NKRO (hardcoded enabled for now due to nature of boot.py)
- Config file with widget assignments, click/hold timeout, base repeat rate, etc
- ZIF connectors to attach the MiRage to other Fata Morgana components via ribbon cables