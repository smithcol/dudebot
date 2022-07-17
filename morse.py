#! /usr/bin/env python3


import sys
import time


MORSE_CODE_DICT = {
    'A':'.-', 'B':'-...',
    'C':'-.-.', 'D':'-..', 'E':'.',
    'F':'..-.', 'G':'--.', 'H':'....',
    'I':'..', 'J':'.---', 'K':'-.-',
    'L':'.-..', 'M':'--', 'N':'-.',
    'O':'---', 'P':'.--.', 'Q':'--.-',
    'R':'.-.', 'S':'...', 'T':'-',
    'U':'..-', 'V':'...-', 'W':'.--',
    'X':'-..-', 'Y':'-.--', 'Z':'--..',
    '1':'.----', '2':'..---', '3':'...--',
    '4':'....-', '5':'.....', '6':'-....',
    '7':'--...', '8':'---..', '9':'----.',
    '0':'-----', ', ':'--..--', '.':'.-.-.-',
    '?':'..--..', '/':'-..-.', '-':'-....-',
    '(':'-.--.', ')':'-.--.-', ' ': '/'
}


def chr_to_morse(c):
    if c not in MORSE_CODE_DICT:
        return "?"
    return MORSE_CODE_DICT[c]


def to_morse(text):
    return "".join(chr_to_morse(c) for c in text.upper())


TIME_SLOW = 0.5

SHORT_PULSE_PERIOD_SECS     = 0.3 * TIME_SLOW
LONG_PULSE_PERIOD_SECS      = 1.0 * TIME_SLOW
BTWN_WORD_PULSE_PERIOD_SECS = 2.0 * TIME_SLOW
FRAME_WAIT_SECS             = 0.2 * TIME_SLOW


def morse_simulate(text):
    morse = to_morse(text)
    print(morse)
    running = ""
    for m in morse:
        running += m
        state = m == '.' or m == '-'
        char = '#' if state else '_'
        print(f"\033[2K\r{running} {char}", end="")
        sys.stdout.flush()
        if m == '.': # short
            time.sleep(SHORT_PULSE_PERIOD_SECS)
        elif m == '-': # long
            time.sleep(LONG_PULSE_PERIOD_SECS)
        elif m == '/': # very long
            time.sleep(BTWN_WORD_PULSE_PERIOD_SECS)
        print(f"\033[2K\r{running} _", end="")
        sys.stdout.flush()
        time.sleep(FRAME_WAIT_SECS)
    print()
            


def main():
    text = " ".join(sys.argv[1:])
    morse_simulate(text)


if __name__ == "__main__":
    main()