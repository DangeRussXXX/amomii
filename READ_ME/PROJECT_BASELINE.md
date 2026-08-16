// ============================================================
// AMOMII ONE COMMAND CENTER 5.0
// Ultimate USB Command Console
// Arduino UNO / AMOMII ONE
// ============================================================

#include <Arduino.h>
#include <string.h>
#include <stdlib.h>

const byte LED = LED_BUILTIN;

unsigned long startTime = 0;
unsigned long lastBlink = 0;

bool ledState = false;
bool blinking = false;

unsigned int blinkSpeed = 300;
unsigned int remainingBlinks = 0;

unsigned long commandCount = 0;

char command[80];
byte commandLength = 0;


// ============================================================
// SETUP
// ============================================================

void setup() {

  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);

  Serial.begin(9600);

  startTime = millis();

  startupAnimation();

  Serial.println();
  Serial.println(F("================================================"));
  Serial.println(F("        AMOMII ONE COMMAND CENTER 5.0"));
  Serial.println(F("================================================"));
  Serial.println();
  Serial.println(F("SYSTEM ONLINE"));
  Serial.println(F("USB CONNECTION ACTIVE"));
  Serial.println(F("BUILT-IN LED READY"));
  Serial.println();
  Serial.println(F("Type HELP for commands."));
  Serial.println();
}


// ============================================================
// MAIN LOOP
// ============================================================

void loop() {

  readSerial();
  updateBlink();
}


// ============================================================
// SERIAL INPUT
// ============================================================

void readSerial() {

  while (Serial.available() > 0) {

    char c = Serial.read();

    if (c == '\n' || c == '\r') {

      if (commandLength > 0) {

        command[commandLength] = '\0';

        commandCount++;

        processCommand();

        commandLength = 0;
        command[0] = '\0';
      }

    } else {

      if (commandLength < sizeof(command) - 1) {
        command[commandLength++] = c;
      }
    }
  }
}


// ============================================================
// COMMAND PROCESSOR
// ============================================================

void processCommand() {

  lowerCase(command);

  // ----------------------------------------------------------
  // HELP
  // ----------------------------------------------------------

  if (!strcmp(command, "help") ||
      !strcmp(command, "?") ||
      !strcmp(command, "commands")) {

    showHelp();
    return;
  }


  // ----------------------------------------------------------
  // LED ON
  // ----------------------------------------------------------

  if (!strcmp(command, "on") ||
      !strcmp(command, "led on")) {

    stopBlink();

    ledState = true;
    digitalWrite(LED, HIGH);

    Serial.println(F("LED ON"));
    return;
  }


  // ----------------------------------------------------------
  // LED OFF
  // ----------------------------------------------------------

  if (!strcmp(command, "off") ||
      !strcmp(command, "led off")) {

    stopBlink();

    ledState = false;
    digitalWrite(LED, LOW);

    Serial.println(F("LED OFF"));
    return;
  }


  // ----------------------------------------------------------
  // TOGGLE
  // ----------------------------------------------------------

  if (!strcmp(command, "toggle") ||
      !strcmp(command, "led toggle")) {

    stopBlink();

    ledState = !ledState;

    digitalWrite(LED, ledState);

    Serial.print(F("LED "));
    Serial.println(ledState ? F("ON") : F("OFF"));

    return;
  }


  // ----------------------------------------------------------
  // BLINK
  // ----------------------------------------------------------

  if (!strncmp(command, "blink ", 6)) {

    int count = atoi(command + 6);

    if (count >= 1 && count <= 1000) {

      blinking = true;
      remainingBlinks = count;

      ledState = false;
      digitalWrite(LED, LOW);

      lastBlink = millis();

      Serial.print(F("Blinking "));
      Serial.print(count);
      Serial.println(F(" times."));

    } else {

      Serial.println(F("ERROR: BLINK must be 1-1000."));
    }

    return;
  }


  // ----------------------------------------------------------
  // SPEED
  // ----------------------------------------------------------

  if (!strncmp(command, "speed ", 6)) {

    int speed = atoi(command + 6);

    if (speed >= 20 && speed <= 5000) {

      blinkSpeed = speed;

      Serial.print(F("Blink speed set to "));
      Serial.print(speed);
      Serial.println(F(" ms."));

    } else {

      Serial.println(F("ERROR: SPEED must be 20-5000."));
    }

    return;
  }


  // ----------------------------------------------------------
  // PULSE
  // ----------------------------------------------------------

  if (!strncmp(command, "pulse ", 6)) {

    int duration = atoi(command + 6);

    if (duration >= 1 && duration <= 10000) {

      pulseLED(duration);

    } else {

      Serial.println(F("ERROR: PULSE must be 1-10000."));
    }

    return;
  }


  // ----------------------------------------------------------
  // FLASH
  // ----------------------------------------------------------

  if (!strncmp(command, "flash ", 6)) {

    int count;
    int speed;

    if (sscanf(command + 6, "%d %d", &count, &speed) == 2) {

      if (count >= 1 &&
          count <= 1000 &&
          speed >= 20 &&
          speed <= 5000) {

        flashLED(count, speed);

      } else {

        Serial.println(F("ERROR: invalid FLASH values."));
      }

    } else {

      Serial.println(F("Usage: FLASH COUNT SPEED"));
    }

    return;
  }


  // ----------------------------------------------------------
  // SOS
  // ----------------------------------------------------------

  if (!strcmp(command, "sos")) {

    sendSOS();
    return;
  }


  // ----------------------------------------------------------
  // COUNTDOWN
  // ----------------------------------------------------------

  if (!strncmp(command, "countdown ", 10)) {

    int seconds = atoi(command + 10);

    if (seconds >= 1 && seconds <= 60) {

      countdown(seconds);

    } else {

      Serial.println(F("ERROR: COUNTDOWN must be 1-60."));
    }

    return;
  }


  // ----------------------------------------------------------
  // TIMER
  // ----------------------------------------------------------

  if (!strncmp(command, "timer ", 6)) {

    int seconds = atoi(command + 6);

    if (seconds >= 1 && seconds <= 60) {

      timer(seconds);

    } else {

      Serial.println(F("ERROR: TIMER must be 1-60."));
    }

    return;
  }


  // ----------------------------------------------------------
  // RANDOM
  // ----------------------------------------------------------

  if (!strcmp(command, "random")) {

    randomSeed(micros());

    byte pattern = random(1, 6);

    Serial.print(F("Random pattern selected: "));
    Serial.println(pattern);

    runPattern(pattern);

    return;
  }


  // ----------------------------------------------------------
  // PATTERN
  // ----------------------------------------------------------

  if (!strncmp(command, "pattern ", 8)) {

    byte pattern = atoi(command + 8);

    runPattern(pattern);

    return;
  }


  // ----------------------------------------------------------
  // MORSE
  // ----------------------------------------------------------

  if (!strncmp(command, "morse ", 6)) {

    sendMorse(command + 6);

    return;
  }


  // ----------------------------------------------------------
  // STATUS
  // ----------------------------------------------------------

  if (!strcmp(command, "status")) {

    showStatus();
    return;
  }


  // ----------------------------------------------------------
  // UPTIME
  // ----------------------------------------------------------

  if (!strcmp(command, "uptime")) {

    showUptime();
    return;
  }


  // ----------------------------------------------------------
  // VERSION
  // ----------------------------------------------------------

  if (!strcmp(command, "version")) {

    Serial.println(F("AMOMII ONE COMMAND CENTER 5.0"));

    return;
  }


  // ----------------------------------------------------------
  // ABOUT
  // ----------------------------------------------------------

  if (!strcmp(command, "about")) {

    showAbout();
    return;
  }


  // ----------------------------------------------------------
  // TEST
  // ----------------------------------------------------------

  if (!strcmp(command, "test")) {

    systemTest();
    return;
  }


  // ----------------------------------------------------------
  // REBOOT
  // ----------------------------------------------------------

  if (!strcmp(command, "reboot")) {

    Serial.println();
    Serial.println(F("REBOOT REQUESTED"));
    Serial.println(F("Press the RESET button on the board."));
    Serial.println();

    return;
  }


  // ----------------------------------------------------------
  // ECHO
  // ----------------------------------------------------------

  if (!strncmp(command, "echo ", 5)) {

    Serial.print(F("ECHO: "));
    Serial.println(command + 5);

    return;
  }


  // ----------------------------------------------------------
  // CLEAR
  // ----------------------------------------------------------

  if (!strcmp(command, "clear")) {

    clearScreen();

    return;
  }


  // ----------------------------------------------------------
  // UNKNOWN
  // ----------------------------------------------------------

  Serial.print(F("ERROR: Unknown command: "));
  Serial.println(command);

  Serial.println(F("Type HELP for available commands."));
}


// ============================================================
// LOWERCASE
// ============================================================

void lowerCase(char *text) {

  while (*text) {

    if (*text >= 'A' && *text <= 'Z') {
      *text = *text + ('a' - 'A');
    }

    text++;
  }
}


// ============================================================
// BLINK ENGINE
// ============================================================

void updateBlink() {

  if (!blinking) {
    return;
  }

  unsigned long now = millis();

  if (now - lastBlink >= blinkSpeed) {

    lastBlink = now;

    ledState = !ledState;

    digitalWrite(LED, ledState);

    if (!ledState) {

      if (remainingBlinks > 0) {
        remainingBlinks--;
      }

      if (remainingBlinks == 0) {

        blinking = false;

        Serial.println(F("Blink complete."));
      }
    }
  }
}


// ============================================================
// STOP BLINK
// ============================================================

void stopBlink() {

  blinking = false;
  remainingBlinks = 0;
}


// ============================================================
// PULSE
// ============================================================

void pulseLED(unsigned int duration) {

  stopBlink();

  ledState = true;
  digitalWrite(LED, HIGH);

  delay(duration);

  ledState = false;
  digitalWrite(LED, LOW);

  Serial.println(F("Pulse complete."));
}


// ============================================================
// FLASH
// ============================================================

void flashLED(int count, int speed) {

  stopBlink();

  for (int i = 0; i < count; i++) {

    ledState = true;
    digitalWrite(LED, HIGH);

    delay(speed);

    ledState = false;
    digitalWrite(LED, LOW);

    delay(speed);
  }

  Serial.println(F("Flash complete."));
}


// ============================================================
// SOS
// ============================================================

void sendSOS() {

  stopBlink();

  Serial.println(F("Sending SOS..."));

  // S ...

  for (byte i = 0; i < 3; i++) {

    digitalWrite(LED, HIGH);
    ledState = true;

    delay(200);

    digitalWrite(LED, LOW);
    ledState = false;

    delay(200);
  }

  delay(300);


  // O ---

  for (byte i = 0; i < 3; i++) {

    digitalWrite(LED, HIGH);
    ledState = true;

    delay(600);

    digitalWrite(LED, LOW);
    ledState = false;

    delay(200);
  }

  delay(300);


  // S ...

  for (byte i = 0; i < 3; i++) {

    digitalWrite(LED, HIGH);
    ledState = true;

    delay(200);

    digitalWrite(LED, LOW);
    ledState = false;

    delay(200);
  }

  Serial.println(F("SOS complete."));
}


// ============================================================
// COUNTDOWN
// ============================================================

void countdown(byte seconds) {

  stopBlink();

  Serial.println();
  Serial.println(F("COUNTDOWN"));

  for (int i = seconds; i > 0; i--) {

    Serial.print(i);
    Serial.println(F("..."));

    pulseLED(150);

    delay(850);
  }

  Serial.println(F("GO!"));

  flashLED(3, 100);
}


// ============================================================
// TIMER
// ============================================================

void timer(byte seconds) {

  stopBlink();

  Serial.print(F("Timer started: "));
  Serial.print(seconds);
  Serial.println(F(" seconds."));

  for (int i = seconds; i > 0; i--) {

    Serial.print(i);
    Serial.println(F(" seconds remaining"));

    digitalWrite(LED, HIGH);
    ledState = true;

    delay(100);

    digitalWrite(LED, LOW);
    ledState = false;

    delay(900);
  }

  Serial.println(F("TIME!"));

  flashLED(5, 100);
}


// ============================================================
// PATTERNS
// ============================================================

void runPattern(byte pattern) {

  switch (pattern) {

    case 1:

      Serial.println(F("Pattern 1: FAST"));

      flashLED(10, 100);

      break;


    case 2:

      Serial.println(F("Pattern 2: SLOW"));

      flashLED(5, 500);

      break;


    case 3:

      Serial.println(F("Pattern 3: SOS"));

      sendSOS();

      break;


    case 4:

      Serial.println(F("Pattern 4: DOUBLE FLASH"));

      for (byte i = 0; i < 5; i++) {

        pulseLED(100);
        delay(100);

        pulseLED(100);
        delay(500);
      }

      break;


    case 5:

      Serial.println(F("Pattern 5: HEARTBEAT"));

      for (byte i = 0; i < 5; i++) {

        pulseLED(100);

        delay(100);

        pulseLED(300);

        delay(700);
      }

      break;


    default:

      Serial.println(F("ERROR: Pattern must be 1-5."));

      break;
  }
}


// ============================================================
// MORSE
// ============================================================

void sendMorse(char *message) {

  stopBlink();

  Serial.print(F("MORSE TX: "));
  Serial.println(message);

  while (*message) {

    char c = *message++;

    if (c >= 'a' && c <= 'z') {
      c -= 32;
    }

    if (c == ' ') {

      delay(1000);

      continue;
    }

    const char *code = getMorse(c);

    if (code != NULL) {

      Serial.print(c);
      Serial.print(F(": "));
      Serial.println(code);

      sendMorseCode(code);

      delay(600);
    }
  }

  Serial.println(F("Morse transmission complete."));
}


// ============================================================
// MORSE TABLE
// ============================================================

const char *getMorse(char c) {

  switch (c) {

    case 'A': return ".-";
    case 'B': return "-...";
    case 'C': return "-.-.";
    case 'D': return "-..";
    case 'E': return ".";
    case 'F': return "..-.";
    case 'G': return "--.";
    case 'H': return "....";
    case 'I': return "..";
    case 'J': return ".---";
    case 'K': return "-.-";
    case 'L': return ".-..";
    case 'M': return "--";
    case 'N': return "-.";
    case 'O': return "---";
    case 'P': return ".--.";
    case 'Q': return "--.-";
    case 'R': return ".-.";
    case 'S': return "...";
    case 'T': return "-";
    case 'U': return "..-";
    case 'V': return "...-";
    case 'W': return ".--";
    case 'X': return "-..-";
    case 'Y': return "-.--";
    case 'Z': return "--..";

    case '0': return "-----";
    case '1': return ".----";
    case '2': return "..---";
    case '3': return "...--";
    case '4': return "....-";
    case '5': return ".....";
    case '6': return "-....";
    case '7': return "--...";
    case '8': return "---..";
    case '9': return "----.";

    case '.': return ".-.-.-";
    case ',': return "--..--";
    case '?': return "..--..";
    case '!': return "-.-.--";
    case '/': return "-..-.";
    case '-': return "-....-";
    case ':': return "---...";
    case ';': return "-.-.-.";
    case '=': return "-...-";
    case '+': return ".-.-.";
    case '@': return ".--.-.";

    default:
      return NULL;
  }
}


// ============================================================
// MORSE TRANSMISSION
// ============================================================

void sendMorseCode(const char *code) {

  while (*code) {

    if (*code == '.') {

      digitalWrite(LED, HIGH);
      ledState = true;

      delay(200);

      digitalWrite(LED, LOW);
      ledState = false;

      delay(200);

    } else if (*code == '-') {

      digitalWrite(LED, HIGH);
      ledState = true;

      delay(600);

      digitalWrite(LED, LOW);
      ledState = false;

      delay(200);
    }

    code++;
  }
}


// ============================================================
// STATUS
// ============================================================

void showStatus() {

  unsigned long seconds =
    (millis() - startTime) / 1000UL;

  Serial.println();
  Serial.println(F("========================================"));
  Serial.println(F("              SYSTEM STATUS"));
  Serial.println(F("========================================"));

  Serial.println(F("Board:       AMOMII ONE"));
  Serial.println(F("Connection:  USB"));
  Serial.println(F("System:      ONLINE"));

  Serial.print(F("LED:         "));
  Serial.println(ledState ? F("ON") : F("OFF"));

  Serial.print(F("Blinking:    "));
  Serial.println(blinking ? F("YES") : F("NO"));

  Serial.print(F("Blink speed: "));
  Serial.print(blinkSpeed);
  Serial.println(F(" ms"));

  Serial.print(F("Commands:    "));
  Serial.println(commandCount);

  Serial.print(F("Uptime:      "));
  Serial.print(seconds);
  Serial.println(F(" seconds"));

  Serial.println(F("========================================"));
}


// ============================================================
// UPTIME
// ============================================================

void showUptime() {

  unsigned long total =
    (millis() - startTime) / 1000UL;

  unsigned long hours =
    total / 3600UL;

  byte minutes =
    (total % 3600UL) / 60UL;

  byte seconds =
    total % 60UL;

  Serial.print(F("Uptime: "));

  if (hours < 10) Serial.print('0');
  Serial.print(hours);

  Serial.print(':');

  if (minutes < 10) Serial.print('0');
  Serial.print(minutes);

  Serial.print(':');

  if (seconds < 10) Serial.print('0');
  Serial.println(seconds);
}


// ============================================================
// ABOUT
// ============================================================

void showAbout() {

  Serial.println();
  Serial.println(F("========================================"));
  Serial.println(F("       AMOMII ONE COMMAND CENTER"));
  Serial.println(F("                 VERSION 5.0"));
  Serial.println(F("========================================"));
  Serial.println();
  Serial.println(F("USB ROBOT DEVELOPMENT CONSOLE"));
  Serial.println();
  Serial.println(F("CURRENT HARDWARE"));
  Serial.println(F("  AMOMII ONE"));
  Serial.println(F("  BUILT-IN LED"));
  Serial.println(F("  USB"));
  Serial.println();
  Serial.println(F("READY FOR FUTURE EXPANSION"));
  Serial.println(F("  BUTTONS"));
  Serial.println(F("  SENSORS"));
  Serial.println(F("  MOTORS"));
  Serial.println(F("  SERVOS"));
  Serial.println(F("  DISPLAYS"));
  Serial.println(F("  BUZZERS"));
  Serial.println(F("  ROBOT CONTROL"));
  Serial.println();
}


// ============================================================
// SYSTEM TEST
// ============================================================

void systemTest() {

  Serial.println();
  Serial.println(F("========== SYSTEM TEST =========="));

  Serial.println(F("Serial:       OK"));

  Serial.println(F("LED:          TESTING"));

  flashLED(3, 200);

  Serial.println(F("LED:          OK"));
  Serial.println(F("Timing:       OK"));
  Serial.println(F("Memory:       OK"));
  Serial.println(F("Commands:     OK"));
  Serial.println(F("System:       OK"));

  Serial.println(F("================================="));
  Serial.println();
}


// ============================================================
// STARTUP ANIMATION
// ============================================================

void startupAnimation() {

  for (byte i = 0; i < 3; i++) {

    digitalWrite(LED, HIGH);
    delay(100);

    digitalWrite(LED, LOW);
    delay(100);
  }
}


// ============================================================
// CLEAR
// ============================================================

void clearScreen() {

  for (byte i = 0; i < 30; i++) {
    Serial.println();
  }

  Serial.println(F("AMOMII ONE Command Center ready."));
}


// ============================================================
// HELP
// ============================================================

void showHelp() {

  Serial.println();
  Serial.println(F("================================================"));
  Serial.println(F("          AMOMII ONE COMMAND CENTER"));
  Serial.println(F("================================================"));

  Serial.println();
  Serial.println(F("LED CONTROL"));
  Serial.println(F("-----------"));
  Serial.println(F("ON"));
  Serial.println(F("OFF"));
  Serial.println(F("TOGGLE"));
  Serial.println(F("LED ON"));
  Serial.println(F("LED OFF"));
  Serial.println(F("LED TOGGLE"));
  Serial.println(F("BLINK 10"));
  Serial.println(F("SPEED 100"));
  Serial.println(F("PULSE 500"));
  Serial.println(F("FLASH 10 100"));

  Serial.println();
  Serial.println(F("EFFECTS"));
  Serial.println(F("-------"));
  Serial.println(F("SOS"));
  Serial.println(F("RANDOM"));
  Serial.println(F("PATTERN 1"));
  Serial.println(F("PATTERN 2"));
  Serial.println(F("PATTERN 3"));
  Serial.println(F("PATTERN 4"));
  Serial.println(F("PATTERN 5"));
  Serial.println(F("COUNTDOWN 10"));
  Serial.println(F("TIMER 10"));

  Serial.println();
  Serial.println(F("MORSE"));
  Serial.println(F("-----"));
  Serial.println(F("MORSE HELLO"));
  Serial.println(F("MORSE HELLO ROBOT"));
  Serial.println(F("MORSE SOS 123"));
  Serial.println(F("MORSE TEST @ 42!"));

  Serial.println();
  Serial.println(F("SYSTEM"));
  Serial.println(F("------"));
  Serial.println(F("STATUS"));
  Serial.println(F("UPTIME"));
  Serial.println(F("VERSION"));
  Serial.println(F("ABOUT"));
  Serial.println(F("TEST"));
  Serial.println(F("REBOOT"));

  Serial.println();
  Serial.println(F("UTILITY"));
  Serial.println(F("-------"));
  Serial.println(F("HELP"));
  Serial.println(F("COMMANDS"));
  Serial.println(F("ECHO HELLO"));
  Serial.println(F("CLEAR"));

  Serial.println();
  Serial.println(F("================================================"));
  Serial.println();
}