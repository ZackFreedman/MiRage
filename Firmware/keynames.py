key_names = {
	'A': 0x04, # Keyboard a and A
	'B': 0x05, # Keyboard b and B
	'C': 0x06, # Keyboard c and C
	'D': 0x07, # Keyboard d and D
	'E': 0x08, # Keyboard e and E
	'F': 0x09, # Keyboard f and F
	'G': 0x0a, # Keyboard g and G
	'H': 0x0b, # Keyboard h and H
	'I': 0x0c, # Keyboard i and I
	'J': 0x0d, # Keyboard j and J
	'K': 0x0e, # Keyboard k and K
	'L': 0x0f, # Keyboard l and L
	'M': 0x10, # Keyboard m and M
	'N': 0x11, # Keyboard n and N
	'O': 0x12, # Keyboard o and O
	'P': 0x13, # Keyboard p and P
	'Q': 0x14, # Keyboard q and Q
	'R': 0x15, # Keyboard r and R
	'S': 0x16, # Keyboard s and S
	'T': 0x17, # Keyboard t and T
	'U': 0x18, # Keyboard u and U
	'V': 0x19, # Keyboard v and V
	'W': 0x1a, # Keyboard w and W
	'X': 0x1b, # Keyboard x and X
	'Y': 0x1c, # Keyboard y and Y
	'Z': 0x1d, # Keyboard z and Z

	'1': 0x1e, # Keyboard 1 and !
	'2': 0x1f, # Keyboard 2 and @
	'3': 0x20, # Keyboard 3 and #
	'4': 0x21, # Keyboard 4 and $
	'5': 0x22, # Keyboard 5 and %
	'6': 0x23, # Keyboard 6 and ^
	'7': 0x24, # Keyboard 7 and &
	'8': 0x25, # Keyboard 8 and *
	'9': 0x26, # Keyboard 9 and (
	'0': 0x27, # Keyboard 0 and )

	'ENTER': 0x28, # Keyboard Return (ENTER)
	'ESC': 0x29, # Keyboard ESCAPE
	'ESCAPE': 0x29, # Keyboard ESCAPE
	'BACKSPACE': 0x2a, # Keyboard DELETE (Backspace)
	'TAB': 0x2b, # Keyboard Tab
	'SPACE': 0x2c, # Keyboard Spacebar
	'LEFTBRACE': 0x2f, # Keyboard [ and {
	'LEFTBRACKET': 0x2f, # Keyboard [ and {
	'MINUS': 0x2d, # Keyboard - and _
	'EQUAL': 0x2e, # Keyboard = and +
	'EQUALS': 0x2e, # Keyboard = and +
	'PLUS': 0x2e, # Keyboard = and +
	'RIGHTBRACE': 0x30, # Keyboard ] and }
	'RIGHTBRACKET': 0x30, # Keyboard ] and }
	'BACKSLASH': 0x31, # Keyboard \ and |
	'HASHTILDE': 0x32, # Keyboard Non-US # and ~
	'HASHANDTILDE': 0x32, # Keyboard Non-US # and ~
	'SEMICOLON': 0x33, # Keyboard ; and :
	'APOSTROPHE': 0x34, # Keyboard ' and "
	'QUOTE': 0x34, # Keyboard ' and "
	'GRAVE': 0x35, # Keyboard ` and ~
	'BACKTICK': 0x35, # Keyboard ` and ~
	'TILDE': 0x35, # Keyboard ` and ~
	'COMMA': 0x36, # Keyboard , and <
	'DOT': 0x37, # Keyboard . and >
	'PERIOD': 0x37, # Keyboard . and >
	'SLASH': 0x38, # Keyboard / and ?
	'FORWARDSLASH': 0x38, # Keyboard / and ?
	'CAPSLOCK': 0x39, # Keyboard Caps Lock

	'F1': 0x3a, # Keyboard F1
	'F2': 0x3b, # Keyboard F2
	'F3': 0x3c, # Keyboard F3
	'F4': 0x3d, # Keyboard F4
	'F5': 0x3e, # Keyboard F5
	'F6': 0x3f, # Keyboard F6
	'F7': 0x40, # Keyboard F7
	'F8': 0x41, # Keyboard F8
	'F9': 0x42, # Keyboard F9
	'F10': 0x43, # Keyboard F10
	'F11': 0x44, # Keyboard F11
	'F12': 0x45, # Keyboard F12

	'SYSRQ': 0x46, # Keyboard Print Screen
	'SCROLLLOCK': 0x47, # Keyboard Scroll Lock
	'PAUSE': 0x48, # Keyboard Pause
	'INSERT': 0x49, # Keyboard Insert
	'HOME': 0x4a, # Keyboard Home
	'PAGEUP': 0x4b, # Keyboard Page Up
	'DELETE': 0x4c, # Keyboard Delete Forward
	'END': 0x4d, # Keyboard End
	'PAGEDOWN': 0x4e, # Keyboard Page Down
	'RIGHT': 0x4f, # Keyboard Right Arrow
	'RIGHTARROW': 0x4f, # Keyboard Right Arrow
	'LEFT': 0x50, # Keyboard Left Arrow
	'LEFTARROW': 0x50, # Keyboard Left Arrow
	'DOWN': 0x51, # Keyboard Down Arrow
	'DOWNARROW': 0x51, # Keyboard Down Arrow
	'UP': 0x52, # Keyboard Up Arrow
	'UPARROW': 0x52, # Keyboard Up Arrow

	'NUMLOCK': 0x53, # Keyboard Num Lock and Clear
	'KPSLASH': 0x54, # Keypad /
	'NUMPADSLASH': 0x54, # Keypad /
	'KPASTERISK': 0x55, # Keypad *
	'NUMPADASTERISK': 0x55, # Keypad *
	'NUMPADTIMES': 0x55, # Keypad *
	'KPMINUS': 0x56, # Keypad -
	'NUMPADMINUS': 0x56, # Keypad -
	'KPPLUS': 0x57, # Keypad +
	'NUMPADPLUS': 0x57, # Keypad +
	'KPENTER': 0x58, # Keypad ENTER
	'NUMPADENTER': 0x58, # Keypad ENTER
	'KP1': 0x59, # Keypad 1 and End
	'NUMPAD1': 0x59, # Keypad 1 and End
	'KP2': 0x5a, # Keypad 2 and Down Arrow
	'NUMPAD2': 0x5a, # Keypad 2 and Down Arrow
	'KP3': 0x5b, # Keypad 3 and PageDn
	'NUMPAD3': 0x5b, # Keypad 3 and PageDn
	'KP4': 0x5c, # Keypad 4 and Left Arrow
	'NUMPAD4': 0x5c, # Keypad 4 and Left Arrow
	'KP5': 0x5d, # Keypad 5
	'NUMPAD5': 0x5d, # Keypad 5
	'KP6': 0x5e, # Keypad 6 and Right Arrow
	'NUMPAD6': 0x5e, # Keypad 6 and Right Arrow
	'KP7': 0x5f, # Keypad 7 and Home
	'NUMPAD7': 0x5f, # Keypad 7 and Home
	'KP8': 0x60, # Keypad 8 and Up Arrow
	'NUMPAD8': 0x60, # Keypad 8 and Up Arrow
	'KP9': 0x61, # Keypad 9 and Page Up
	'NUMPAD9': 0x61, # Keypad 9 and Page Up
	'KP0': 0x62, # Keypad 0 and Insert
	'NUMPAD0': 0x62, # Keypad 0 and Insert
	'KPDOT': 0x63, # Keypad . and Delete
	'NUMPADDOT': 0x63, # Keypad . and Delete

	'102ND': 0x64, # Keyboard Non-US \ and |
	'COMPOSE': 0x65, # Keyboard Application
	'POWER': 0x66, # Keyboard Power
	'KPEQUAL': 0x67, # Keypad =
	'NUMPADEQUAL': 0x67, # Keypad =
	'NUMPADEQUALS': 0x67, # Keypad =

	'F13': 0x68, # Keyboard F13
	'F14': 0x69, # Keyboard F14
	'F15': 0x6a, # Keyboard F15
	'F16': 0x6b, # Keyboard F16
	'F17': 0x6c, # Keyboard F17
	'F18': 0x6d, # Keyboard F18
	'F19': 0x6e, # Keyboard F19
	'F20': 0x6f, # Keyboard F20
	'F21': 0x70, # Keyboard F21
	'F22': 0x71, # Keyboard F22
	'F23': 0x72, # Keyboard F23
	'F24': 0x73, # Keyboard F24

	'OPEN': 0x74, # Keyboard Execute
	'HELP': 0x75, # Keyboard Help
	'PROPS': 0x76, # Keyboard Menu
	'FRONT': 0x77, # Keyboard Select
	'STOP': 0x78, # Keyboard Stop
	'AGAIN': 0x79, # Keyboard Again
	'UNDO': 0x7a, # Keyboard Undo
	'CUT': 0x7b, # Keyboard Cut
	'COPY': 0x7c, # Keyboard Copy
	'PASTE': 0x7d, # Keyboard Paste
	'FIND': 0x7e, # Keyboard Find
	'MUTE': 0x7f, # Keyboard Mute
	'VOLUMEUP': 0x80, # Keyboard Volume Up
	'VOLUMEDOWN': 0x81, # Keyboard Volume Down
	'KPCOMMA': 0x85, # Keypad Comma
	'KEYPAD EQUAL': 0x86,  # Keypad Equal Sign
	'RO': 0x87, # Keyboard International1
	'KATAKANAHIRAGANA': 0x88, # Keyboard International2
	'YEN': 0x89, # Keyboard International3
	'HENKAN': 0x8a, # Keyboard International4
	'MUHENKAN': 0x8b, # Keyboard International5
	'KPJPCOMMA': 0x8c, # Keyboard International6
	'HANGEUL': 0x90, # Keyboard LANG1
	'HANJA': 0x91, # Keyboard LANG2
	'KATAKANA': 0x92, # Keyboard LANG3
	'HIRAGANA': 0x93, # Keyboard LANG4
	'ZENKAKUHANKAKU': 0x94, # Keyboard LANG5
	'KPLEFTPAREN': 0xb6, # Keypad (
	'KPRIGHTPAREN': 0xb7, # Keypad )

	'CTRL': 0xe0, # Keyboard Left Control # Todo autodetect
	'CONTROL': 0xe0, # Keyboard Left Control
	'LEFTCTRL': 0xe0, # Keyboard Left Control
	'LEFTCONTROL': 0xe0, # Keyboard Left Control
	'SHIFT': 0xe1, # Keyboard Left Shift
	'LEFTSHIFT': 0xe1, # Keyboard Left Shift
	'ALT': 0xe2, # Keyboard Left Alt
	'LEFTALT': 0xe2, # Keyboard Left Alt
	'LEFTMETA': 0xe3, # Keyboard Left GUI
	'WINDOWS': 0xe3, # Keyboard Left GUI
	'GUI': 0xe3, # Keyboard Left GUI  # TODO auto detect side
	'LEFTGUI': 0xe3, # Keyboard Left GUI
	'LEFTWINDOWS': 0xe3, # Keyboard Left GUI
	'RIGHTCTRL': 0xe4, # Keyboard Right Control
	'RIGHTCONTROL': 0xe4, # Keyboard Right Control
	'RIGHTSHIFT': 0xe5, # Keyboard Right Shift
	'RIGHTALT': 0xe6, # Keyboard Right Alt
	'RIGHTMETA': 0xe7, # Keyboard Right GUI
	'RIGHTWINDOWS': 0xe7, # Keyboard Right GUI
	'RIGHTGUI': 0xe7, # Keyboard Right GUI

	'MEDIAPLAYPAUSE': 0xe8,
	'MEDIASTOPCD': 0xe9,
	'MEDIAPREVIOUSSONG': 0xea,
	'MEDIANEXTSONG': 0xeb,
	'MEDIAEJECTCD': 0xec,
	'VOLUMEUP': 0xed,
	'MEDIAVOLUMEDOWN': 0xee,
	'MEDIAMUTE': 0xef,
	'MUTE': 0xef,
	'MEDIAWWW': 0xf0,
	'MEDIABACK': 0xf1,
	'BACK': 0xf1,
	'MEDIAFORWARD': 0xf2,
	'FORWARD': 0xf2,
	'MEDIASTOP': 0xf3,
	'MEDIAFIND': 0xf4,
	'MEDIASCROLLUP': 0xf5,
	'MEDIASCROLLDOWN': 0xf6,
	'MEDIAEDIT': 0xf7,
	'MEDIASLEEP': 0xf8,
	'MEDIACOFFEE': 0xf9,
	'MEDIAREFRESH': 0xfa,
	'MEDIACALC': 0xfb
}