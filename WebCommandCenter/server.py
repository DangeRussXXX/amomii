import serial
import time
import re


# ============================================================
# AMOMII ONE - NATURAL COMMAND ROUTER
# FULL REPLACEMENT VERSION
#
# Python receives natural text / voice transcription
# and converts it into commands understood by the
# AMOMII ONE Arduino Command Center 6.0 sketch.
#
# Arduino:
#   COM9
#   9600 baud
#
# Example:
#
#   trainer LED zero off
#       ->
#   trainer led 0 off
#
#   turn on trainer LED seven
#       ->
#   trainer led 7 on
#
#   all leds on
#       ->
#   all on
#
#   both blink five
#       ->
#   both blink 5
# ============================================================


# ============================================================
# ARDUINO CONNECTION
# ============================================================

ARDUINO_PORT = "COM9"
BAUD = 9600


# ============================================================
# NUMBER WORDS
# ============================================================

NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
    "hundred": "100",
    "oh": "0"
}


# ============================================================
# OPEN ARDUINO
# ============================================================

try:

    arduino = serial.Serial(
        ARDUINO_PORT,
        BAUD,
        timeout=1
    )

    # Arduino usually resets when serial opens.
    time.sleep(2)

    print("[Arduino] Connected:", ARDUINO_PORT)

except Exception as e:

    arduino = None

    print()
    print("[ERROR] Could not open Arduino.")
    print(e)
    print()
    print("Check that:")
    print("  1. Arduino is connected")
    print("  2. COM9 is correct")
    print("  3. Serial Monitor is closed")
    print()


# ============================================================
# NUMBER CONVERSION
# ============================================================

def convert_number_words(words):

    result = []

    i = 0

    while i < len(words):

        word = words[i]

        # ----------------------------------------------------
        # Direct number
        # ----------------------------------------------------

        if word.isdigit():

            result.append(word)

            i += 1

            continue


        # ----------------------------------------------------
        # Simple number word
        # ----------------------------------------------------

        if word in NUMBER_WORDS:

            value = NUMBER_WORDS[word]

            # ------------------------------------------------
            # "one hundred"
            # ------------------------------------------------

            if (
                value != "100"
                and
                i + 1 < len(words)
                and
                words[i + 1] == "hundred"
            ):

                try:

                    number = int(value) * 100

                    result.append(str(number))

                    i += 2

                    continue

                except ValueError:
                    pass


            result.append(value)

            i += 1

            continue


        result.append(word)

        i += 1

    return result


# ============================================================
# NORMALIZE BASIC TEXT
# ============================================================

def clean_text(text):

    text = text.lower().strip()

    # Remove punctuation.

    text = re.sub(
        r"[.,!?;:]",
        "",
        text
    )

    # Normalize common spoken forms.

    text = text.replace(
        "built-in",
        "built in"
    )

    text = text.replace(
        "builtin",
        "built in"
    )

    # Remove common polite/request words.

    text = re.sub(
        r"\bplease\b",
        "",
        text
    )

    # Collapse spaces.

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# NATURAL COMMAND NORMALIZER
# ============================================================

def normalize_command(text):

    text = clean_text(text)

    words = text.split()

    if not words:
        return None


    # ========================================================
    # NUMBER WORDS
    # ========================================================

    words = convert_number_words(words)

    text = " ".join(words)


    # ========================================================
    # REMOVE COMMON VOICE WORDING
    # ========================================================

    # "turn on ..."
    # "turn off ..."

    text = re.sub(
        r"^turn\s+on\s+",
        "",
        text
    )

    text = re.sub(
        r"^turn\s+off\s+",
        "",
        text
    )

    # "switch on ..."
    # "switch off ..."

    text = re.sub(
        r"^switch\s+on\s+",
        "",
        text
    )

    text = re.sub(
        r"^switch\s+off\s+",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    words = text.split()


    # ========================================================
    # ARDUINO / BUILT-IN LED
    # ========================================================

    if "trainer" not in words:

        if (
            "arduino" in words
            or "built" in words
            or "led" in words
        ):

            if "on" in words:

                return "arduino on"

            if "off" in words:

                return "arduino off"


    # ========================================================
    # ALL / BOTH
    # ========================================================

    all_words = (
        "all" in words
        or "both" in words
    )

    if all_words:

        if "on" in words:

            return "all on"

        if "off" in words:

            return "all off"


    # ========================================================
    # TRAINER ALL
    # ========================================================

    if "trainer" in words:

        if (
            "all" in words
            or
            "everything" in words
        ):

            if "on" in words:

                return "trainer all on"

            if "off" in words:

                return "trainer all off"


    # ========================================================
    # TRAINER INDIVIDUAL LED
    #
    # Natural examples:
    #
    # trainer led 0 on
    # trainer led three on
    # turn on trainer led seven
    # trainer seven off
    # ========================================================

    if "trainer" in words:

        index = None


        # ----------------------------------------------------
        # Look after "led"
        # ----------------------------------------------------

        if "led" in words:

            led_position = words.index("led")

            if led_position + 1 < len(words):

                possible_number = words[
                    led_position + 1
                ]

                if possible_number.isdigit():

                    index = int(
                        possible_number
                    )


        # ----------------------------------------------------
        # Look after "trainer"
        # ----------------------------------------------------

        if index is None:

            trainer_position = words.index(
                "trainer"
            )

            if trainer_position + 1 < len(words):

                possible_number = words[
                    trainer_position + 1
                ]

                if possible_number.isdigit():

                    index = int(
                        possible_number
                    )


        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if index is not None:

            if 0 <= index <= 7:

                if "on" in words:

                    return (
                        f"trainer led "
                        f"{index} on"
                    )

                if "off" in words:

                    return (
                        f"trainer led "
                        f"{index} off"
                    )


    # ========================================================
    # ARDUINO BLINK
    # ========================================================

    if words and words[0] == "blink":

        if len(words) >= 2:

            if words[1].isdigit():

                count = int(words[1])

                if 1 <= count <= 1000:

                    return f"blink {count}"


    # ========================================================
    # TRAINER BLINK
    # ========================================================

    if len(words) >= 3:

        if (
            words[0] == "trainer"
            and
            words[1] == "blink"
            and
            words[2].isdigit()
        ):

            count = int(words[2])

            if 1 <= count <= 1000:

                return f"trainer blink {count}"


    # ========================================================
    # BOTH BLINK
    # ========================================================

    if len(words) >= 3:

        if (
            words[0] == "both"
            and
            words[1] == "blink"
            and
            words[2].isdigit()
        ):

            count = int(words[2])

            if 1 <= count <= 1000:

                return f"both blink {count}"


    # ========================================================
    # SPEED
    # ========================================================

    if words and words[0] == "speed":

        if len(words) >= 2:

            if words[1].isdigit():

                speed = int(words[1])

                if 20 <= speed <= 5000:

                    return f"speed {speed}"


    # ========================================================
    # ARDUINO FLASH
    #
    # flash 10 100
    # ========================================================

    if words and words[0] == "flash":

        if len(words) >= 3:

            if (
                words[1].isdigit()
                and
                words[2].isdigit()
            ):

                count = int(words[1])
                speed = int(words[2])

                if (
                    1 <= count <= 1000
                    and
                    20 <= speed <= 5000
                ):

                    return (
                        f"flash "
                        f"{count} "
                        f"{speed}"
                    )


    # ========================================================
    # TRAINER FLASH
    # ========================================================

    if len(words) >= 4:

        if (
            words[0] == "trainer"
            and
            words[1] == "flash"
            and
            words[2].isdigit()
            and
            words[3].isdigit()
        ):

            count = int(words[2])
            speed = int(words[3])

            if (
                1 <= count <= 1000
                and
                20 <= speed <= 5000
            ):

                return (
                    f"trainer flash "
                    f"{count} "
                    f"{speed}"
                )


    # ========================================================
    # BOTH FLASH
    # ========================================================

    if len(words) >= 4:

        if (
            words[0] == "both"
            and
            words[1] == "flash"
            and
            words[2].isdigit()
            and
            words[3].isdigit()
        ):

            count = int(words[2])
            speed = int(words[3])

            if (
                1 <= count <= 1000
                and
                20 <= speed <= 5000
            ):

                return (
                    f"both flash "
                    f"{count} "
                    f"{speed}"
                )


    # ========================================================
    # ARDUINO PULSE
    # ========================================================

    if words and words[0] == "pulse":

        if len(words) >= 2:

            if words[1].isdigit():

                duration = int(words[1])

                if 1 <= duration <= 10000:

                    return (
                        f"pulse "
                        f"{duration}"
                    )


    # ========================================================
    # TRAINER PULSE
    # ========================================================

    if len(words) >= 3:

        if (
            words[0] == "trainer"
            and
            words[1] == "pulse"
            and
            words[2].isdigit()
        ):

            duration = int(words[2])

            if 1 <= duration <= 10000:

                return (
                    f"trainer pulse "
                    f"{duration}"
                )


    # ========================================================
    # BOTH PULSE
    # ========================================================

    if len(words) >= 3:

        if (
            words[0] == "both"
            and
            words[1] == "pulse"
            and
            words[2].isdigit()
        ):

            duration = int(words[2])

            if 1 <= duration <= 10000:

                return (
                    f"both pulse "
                    f"{duration}"
                )


    # ========================================================
    # SOS
    # ========================================================

    if words == ["sos"]:

        return "sos"


    if words == ["trainer", "sos"]:

        return "trainer sos"


    if words == ["both", "sos"]:

        return "both sos"


    if words == ["arduino", "sos"]:

        return "arduino sos"


    # ========================================================
    # MORSE
    # ========================================================

    if words and words[0] == "morse":

        message = " ".join(
            words[1:]
        ).strip()

        if message:

            return (
                f"morse {message}"
            )


    if (
        len(words) >= 3
        and
        words[0] == "trainer"
        and
        words[1] == "morse"
    ):

        message = " ".join(
            words[2:]
        ).strip()

        if message:

            return (
                f"trainer morse {message}"
            )


    if (
        len(words) >= 3
        and
        words[0] == "both"
        and
        words[1] == "morse"
    ):

        message = " ".join(
            words[2:]
        ).strip()

        if message:

            return (
                f"both morse {message}"
            )


    if (
        len(words) >= 3
        and
        words[0] == "arduino"
        and
        words[1] == "morse"
    ):

        message = " ".join(
            words[2:]
        ).strip()

        if message:

            return (
                f"arduino morse {message}"
            )


    # ========================================================
    # COUNTDOWN
    # ========================================================

    if words and words[0] == "countdown":

        if len(words) >= 2:

            if words[1].isdigit():

                seconds = int(words[1])

                if 1 <= seconds <= 60:

                    return (
                        f"countdown "
                        f"{seconds}"
                    )


    if (
        len(words) >= 3
        and
        words[0] == "trainer"
        and
        words[1] == "countdown"
    ):

        if words[2].isdigit():

            seconds = int(words[2])

            if 1 <= seconds <= 60:

                return (
                    f"trainer countdown "
                    f"{seconds}"
                )


    if (
        len(words) >= 3
        and
        words[0] == "both"
        and
        words[1] == "countdown"
    ):

        if words[2].isdigit():

            seconds = int(words[2])

            if 1 <= seconds <= 60:

                return (
                    f"both countdown "
                    f"{seconds}"
                )


    # ========================================================
    # TIMER
    # ========================================================

    if words and words[0] == "timer":

        if len(words) >= 2:

            if words[1].isdigit():

                seconds = int(words[1])

                if 1 <= seconds <= 60:

                    return (
                        f"timer "
                        f"{seconds}"
                    )


    if (
        len(words) >= 3
        and
        words[0] == "trainer"
        and
        words[1] == "timer"
    ):

        if words[2].isdigit():

            seconds = int(words[2])

            if 1 <= seconds <= 60:

                return (
                    f"trainer timer "
                    f"{seconds}"
                )


    if (
        len(words) >= 3
        and
        words[0] == "both"
        and
        words[1] == "timer"
    ):

        if words[2].isdigit():

            seconds = int(words[2])

            if 1 <= seconds <= 60:

                return (
                    f"both timer "
                    f"{seconds}"
                )


    # ========================================================
    # RANDOM
    # ========================================================

    if words == ["random"]:

        return "random"


    if words == ["trainer", "random"]:

        return "trainer random"


    if words == ["both", "random"]:

        return "both random"


    # ========================================================
    # PATTERN
    # ========================================================

    if (
        len(words) >= 2
        and
        words[0] == "pattern"
        and
        words[1].isdigit()
    ):

        pattern = int(words[1])

        if 1 <= pattern <= 5:

            return (
                f"pattern "
                f"{pattern}"
            )


    if (
        len(words) >= 3
        and
        words[0] == "trainer"
        and
        words[1] == "pattern"
        and
        words[2].isdigit()
    ):

        pattern = int(words[2])

        if 1 <= pattern <= 5:

            return (
                f"trainer pattern "
                f"{pattern}"
            )


    if (
        len(words) >= 3
        and
        words[0] == "both"
        and
        words[1] == "pattern"
        and
        words[2].isdigit()
    ):

        pattern = int(words[2])

        if 1 <= pattern <= 5:

            return (
                f"both pattern "
                f"{pattern}"
            )


    # ========================================================
    # SYSTEM COMMANDS
    # ========================================================

    simple_commands = {
        "help": "help",
        "commands": "commands",
        "status": "status",
        "uptime": "uptime",
        "version": "version",
        "about": "about",
        "test": "test",
        "stop": "stop",
        "stop all": "stop all",
        "clear": "clear",
        "reboot": "reboot",
    }

    if text in simple_commands:

        return simple_commands[text]


    # ========================================================
    # ECHO
    # ========================================================

    if text.startswith("echo "):

        return text


    # ========================================================
    # UNKNOWN
    # ========================================================

    return None


# ============================================================
# SEND COMMAND TO ARDUINO
# ============================================================

def send_command(command):

    global arduino


    if arduino is None:

        print()
        print(
            "[ERROR] Arduino is not connected."
        )
        print()

        return False


    try:

        print(
            "[Arduino TX]:",
            command
        )


        # ----------------------------------------------------
        # Send command
        # ----------------------------------------------------

        arduino.write(
            (command + "\n").encode()
        )

        arduino.flush()


        # ----------------------------------------------------
        # Give Arduino time to respond
        # ----------------------------------------------------

        time.sleep(0.1)


        # ----------------------------------------------------
        # Read responses
        # ----------------------------------------------------

        while arduino.in_waiting:

            response = (
                arduino.readline()
                .decode(
                    errors="ignore"
                )
                .strip()
            )

            if response:

                print(
                    "[Arduino RX]:",
                    response
                )


        return True


    except Exception as e:

        print()
        print(
            "[ERROR] Serial communication failed:"
        )
        print(e)
        print()

        return False


# ============================================================
# PRINT EXAMPLES
# ============================================================

def show_examples():

    print()
    print("================================================")
    print("          AMOMII NATURAL COMMAND ROUTER")
    print("================================================")
    print()

    print("ARDUINO LED")
    print("-----------")
    print("  led on")
    print("  led off")
    print("  turn on led")
    print("  turn off led")
    print()

    print("TRAINER LEDS")
    print("------------")
    print("  trainer led zero on")
    print("  trainer led zero off")
    print("  trainer led three on")
    print("  trainer led seven off")
    print("  turn on trainer led three")
    print("  turn off trainer led seven")
    print("  trainer all on")
    print("  trainer all off")
    print()

    print("BOTH")
    print("----")
    print("  all leds on")
    print("  all leds off")
    print("  both blink five")
    print("  both flash ten one hundred")
    print("  both pulse five hundred")
    print("  both sos")
    print("  both morse hello")
    print()

    print("EFFECTS")
    print("-------")
    print("  blink ten")
    print("  trainer blink five")
    print("  speed one hundred")
    print("  flash ten one hundred")
    print("  trainer flash ten one hundred")
    print("  pulse five hundred")
    print("  trainer pulse five hundred")
    print("  sos")
    print("  morse hello")
    print("  countdown ten")
    print("  timer ten")
    print("  random")
    print("  pattern three")
    print()

    print("SYSTEM")
    print("------")
    print("  help")
    print("  status")
    print("  uptime")
    print("  version")
    print("  about")
    print("  test")
    print("  stop")
    print("  clear")
    print()

    print("Type quit to exit.")
    print()
    print("================================================")
    print()


# ============================================================
# MAIN
# ============================================================

show_examples()


while True:

    try:

        voice_text = input("> ")


    except KeyboardInterrupt:

        print()
        print("Stopping...")

        break


    except EOFError:

        print()
        print("Input closed.")

        break


    # --------------------------------------------------------
    # Empty input
    # --------------------------------------------------------

    if not voice_text.strip():

        continue


    # --------------------------------------------------------
    # Quit
    # --------------------------------------------------------

    if voice_text.lower().strip() in (
        "quit",
        "exit"
    ):

        break


    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    command = normalize_command(
        voice_text
    )


    print(
        "[Router]:",
        command
    )


    # --------------------------------------------------------
    # Unknown
    # --------------------------------------------------------

    if command is None:

        print(
            "[Router] I don't understand "
            "that command."
        )

        print(
            "[Router] Try HELP or one of "
            "the examples above."
        )

        continue


    # --------------------------------------------------------
    # Send
    # --------------------------------------------------------

    send_command(command)


# ============================================================
# SHUTDOWN
# ============================================================

if arduino is not None:

    try:

        arduino.close()

    except Exception:
        pass


print()
print("AMOMII router stopped.")
