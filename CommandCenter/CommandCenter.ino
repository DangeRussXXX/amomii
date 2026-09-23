// ============================================================
// AMOMII ONE COMMAND CENTER 5.0
// Ultimate USB Command Console
// Arduino UNO / AMOMII ONE
// ============================================================

#include <Arduino.h>
#include <string.h>
#include <stdlib.h>

const byte LED = LED_BUILTIN;

// Trainer LEDs on pins 2–9
const byte TLED0 = 2;
const byte TLED1 = 3;
const byte TLED2 = 4;
const byte TLED3 = 5;
const byte TLED4 = 6;
const byte TLED5 = 7;
const byte TLED6 = 8;
const byte TLED7 = 9;

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

  // Trainer LEDs
  pinMode(TLED0, OUTPUT);
  pinMode(TLED1, OUTPUT);
  pinMode(TLED2, OUTPUT);
  pinMode(TLED3, OUTPUT);
  pinMode(TLED4, OUTPUT);
  pinMode(TLED5, OUTPUT);
  pinMode(TLED6, OUTPUT);
  pinMode(TLED7, OUTPUT);

  digitalWrite(TLED0, LOW);
  digitalWrite(TLED1, LOW);
  digitalWrite(TLED2, LOW);
  digitalWrite(TLED3, LOW);
  digitalWrite(TLED4, LOW);
  digitalWrite(TLED5, LOW);
  digitalWrite(TLED6, LOW);
  digitalWrite(TLED7, LOW);

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
  Serial.println(F("TRAINER LEDS READY (2-9)"));
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

        normalizeVoice(command);   // <-- NEW VOICE NORMALIZER

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
// VOICE NORMALIZER
// ============================================================

void normalizeVoice(char *text) {

  lowerCase(text);

  // Remove spaces → "led 3 on" → "led3on"
  char buffer[80];
  byte idx = 0;

  for (byte i = 0; text[i] != '\0'; i++) {
    if (text[i] != ' ') buffer[idx++] = text[i];
  }
  buffer[idx] = '\0';

  // Convert number words → digits
  struct WordMap { const char *word; const char digit; };
  WordMap map[] = {
    {"zero", '0'}, {"one", '1'}, {"two", '2'}, {"three", '3'},
    {"four", '4'}, {"five", '5'}, {"six", '6'}, {"seven", '7'},
    {"eight", '8'}, {"nine", '9'}
  };

  for (auto &m : map) {
    char *p = strstr(buffer, m.word);
    if (p) { p[0] = m.digit; p[1] = '\0'; }
  }

  // Fix speech glitch "d0on" → "led0on"
  if (buffer[0] == 'd') buffer[0] = 'l';

  strcpy(text, buffer);
}


// ============================================================
// TRAINER LED HELPERS
// ============================================================

void setTrainerLED(byte index, bool state) {

  switch (index) {
    case 0: digitalWrite(TLED0, state ? HIGH : LOW); break;
    case 1: digitalWrite(TLED1, state ? HIGH : LOW); break;
    case 2: digitalWrite(TLED2, state ? HIGH : LOW); break;
    case 3: digitalWrite(TLED3, state ? HIGH : LOW); break;
    case 4: digitalWrite(TLED4, state ? HIGH : LOW); break;
    case 5: digitalWrite(TLED5, state ? HIGH : LOW); break;
    case 6: digitalWrite(TLED6, state ? HIGH : LOW); break;
    case 7: digitalWrite(TLED7, state ? HIGH : LOW); break;
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
  // BUILT-IN LED ON
  // ----------------------------------------------------------

  if (!strcmp(command, "on") ||
      !strcmp(command, "ledon")) {

    stopBlink();

    ledState = true;
    digitalWrite(LED, HIGH);

    Serial.println(F("LED ON"));
    return;
  }


  // ----------------------------------------------------------
  // BUILT-IN LED OFF
  // ----------------------------------------------------------

  if (!strcmp(command, "off") ||
      !strcmp(command, "ledoff")) {

    stopBlink();

    ledState = false;
    digitalWrite(LED, LOW);

    Serial.println(F("LED OFF"));
    return;
  }


  // ----------------------------------------------------------
  // TRAINER LED CONTROL
  // Supports:
  //   led3on
  //   led3off
  //   led0on
  //   led0off
  // ----------------------------------------------------------

  if (!strncmp(command, "led", 3)) {

    char *p = command + 3;

    if (*p >= '0' && *p <= '7') {

      byte index = *p - '0';
      p++;

      bool turnOn  = strstr(p, "on");
      bool turnOff = strstr(p, "off");

      if (turnOn || turnOff) {

        setTrainerLED(index, turnOn);

        Serial.print(F("TRAINER LED "));
        Serial.print(index);
        Serial.println(turnOn ? F(" ON") : F(" OFF"));

        return;
      }
    }
  }


  // ----------------------------------------------------------
  // BLINK
  // ----------------------------------------------------------

  if (!strncmp(command, "blink", 5)) {

    int count = atoi(command + 5);

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

  if (!strncmp(command, "speed", 5)) {

    int speed = atoi(command + 5);

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

  if (!strncmp(command, "pulse", 5)) {

    int duration = atoi(command + 5);

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

  if (!strncmp(command, "flash", 5)) {

    int count;
    int speed;

    if (sscanf(command + 5, "%d %d", &count, &speed) == 2) {

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

  if (!strncmp(command, "countdown", 9)) {

    int seconds = atoi(command + 9);

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

  if (!strncmp(command, "timer", 5)) {

    int seconds = atoi(command + 5);

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

  if (!strncmp(command, "pattern", 7)) {

    byte pattern = atoi(command + 7);

    runPattern(pattern);

    return;
  }


  // ----------------------------------------------------------
  // MORSE
  // ----------------------------------------------------------

  if (!strncmp(command, "morse", 5)) {

    sendMorse(command + 5);

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

  if (!strncmp(command, "echo", 4)) {

    Serial.print(F("ECHO: "));
    Serial.println(command + 4);

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

