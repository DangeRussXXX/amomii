// ================================================================
// AMOMII ONE COMMAND CENTER 5.0 - REBUILT WITH VOICE/TEXT COMMANDS
// ================================================================

String input = "";
bool patternRunning = false;
int currentPattern = 0;

// Built-in LED
const int BUILTIN_LED = LED_BUILTIN;

// Trainer LEDs (adjust pins to match your board)
const int LED0 = 2;
const int LED1 = 3;
const int LED2 = 4;
const int LED3 = 5;
const int LED4 = 6;
const int LED5 = 7;
const int LED6 = 8;
const int LED7 = 9;

// System name
String systemName = "AMOMII ONE";
String userName   = "User";

// ================================================================
// SETUP
// ================================================================
void setup() {
    Serial.begin(9600);

    pinMode(BUILTIN_LED, OUTPUT);

    pinMode(LED0, OUTPUT);
    pinMode(LED1, OUTPUT);
    pinMode(LED2, OUTPUT);
    pinMode(LED3, OUTPUT);
    pinMode(LED4, OUTPUT);
    pinMode(LED5, OUTPUT);
    pinMode(LED6, OUTPUT);
    pinMode(LED7, OUTPUT);

    Serial.println("================================================");
    Serial.println("        AMOMII ONE COMMAND CENTER 5.0");
    Serial.println("================================================");
    Serial.println();
    Serial.println("SYSTEM ONLINE");
    Serial.println("USB CONNECTION ACTIVE");
    Serial.println("BUILT-IN LED READY");
    Serial.println();
    Serial.println("Type HELP for commands.");
}

// ================================================================
// LOOP
// ================================================================
void loop() {
    if (Serial.available()) {
        input = Serial.readStringUntil('\n');
        input.trim();
        processCommand(input);
    }

    if (patternRunning) {
        runPattern(currentPattern);
    }
}

// ================================================================
// NORMALIZE
// ================================================================
String normalize(String s) {
    s.toLowerCase();
    s.trim();
    s.replace(".", "");
    s.replace("!", "");
    s.replace(",", "");
    s.replace("?", "");
    return s;
}

// ================================================================
// MAIN COMMAND PARSER (TEXT + VOICE PHRASES)
// ================================================================
void processCommand(String raw) {
    String cmd = normalize(raw);

    // -------- HELP / WHAT CAN YOU DO --------
    if (cmd == "help" || cmd == "what can you do") {
        Serial.println("I can control AMOMII ONE, manage music and video,");
        Serial.println("work with the calendar, tell you the time and date,");
        Serial.println("run diagnostics, and respond to voice commands.");
        Serial.println();
        Serial.println("You can say or type:");
        Serial.println("connect, disconnect, status, system test,");
        Serial.println("led on, led off, blink five, sos, stop,");
        Serial.println("play music, pause music, next song, previous song,");
        Serial.println("play video, pause video, next video,");
        Serial.println("open calendar, add an event,");
        Serial.println("what events do I have today,");
        Serial.println("what is my name, change my name,");
        Serial.println("what is your name, change your name,");
        Serial.println("and what can you do.");
        return;
    }

    // -------- STATUS / SYSTEM TEST --------
    if (cmd == "status" || cmd == "system status") {
        Serial.println("SYSTEM STATUS:");
        Serial.println("Name: " + systemName);
        Serial.println("User: " + userName);
        Serial.println("USB: CONNECTED");
        Serial.println("LED: READY");
        Serial.println(patternRunning ? "Pattern: RUNNING" : "Pattern: IDLE");
        return;
    }

    if (cmd == "system test") {
        Serial.println("Running system test...");
        digitalWrite(BUILTIN_LED, HIGH);
        delay(200);
        digitalWrite(BUILTIN_LED, LOW);
        delay(200);
        digitalWrite(BUILTIN_LED, HIGH);
        delay(200);
        digitalWrite(BUILTIN_LED, LOW);
        Serial.println("System test complete.");
        return;
    }

    // -------- CONNECT / DISCONNECT (placeholders) --------
    if (cmd == "connect") {
        Serial.println("Connecting to AMOMII ONE services...");
        // your PC/web app can react to this
        return;
    }

    if (cmd == "disconnect") {
        Serial.println("Disconnecting from AMOMII ONE services...");
        return;
    }

    // -------- BUILT-IN LED --------
    if (cmd == "led on") {
        digitalWrite(BUILTIN_LED, HIGH);
        Serial.println("BUILT-IN LED ON");
        return;
    }

    if (cmd == "led off") {
        digitalWrite(BUILTIN_LED, LOW);
        Serial.println("BUILT-IN LED OFF");
        return;
    }

    // -------- TRAINER LEDS: led0 on / led3 off etc. --------
    if (cmd.startsWith("led") && cmd.length() >= 6 && isDigit(cmd.charAt(3))) {
        int ledNum = cmd.substring(3, 4).toInt(); // single digit 0–7
        bool turnOn = cmd.endsWith("on");

        if (ledNum < 0 || ledNum > 7) {
            Serial.println("ERROR: LED index must be 0–7");
            return;
        }

        int pin = LED0 + ledNum;
        digitalWrite(pin, turnOn ? HIGH : LOW);

        Serial.print("LED ");
        Serial.print(ledNum);
        Serial.println(turnOn ? " ON" : " OFF");
        return;
    }

    // -------- BLINK FIVE (built-in LED) --------
    if (cmd == "blink five") {
        Serial.println("Blinking built-in LED five times...");
        for (int i = 0; i < 5; i++) {
            digitalWrite(BUILTIN_LED, HIGH);
            delay(200);
            digitalWrite(BUILTIN_LED, LOW);
            delay(200);
        }
        Serial.println("Blink complete.");
        return;
    }

    // -------- SOS (trainer LEDs) --------
    if (cmd == "sos") {
        Serial.println("SOS pattern on trainer LEDs...");
        sosPattern();
        Serial.println("SOS complete.");
        return;
    }

    // -------- PATTERNS / STOP --------
    if (cmd == "knight rider") {
        startKnightRider();
        Serial.println("PATTERN: Knight Rider");
        return;
    }

    if (cmd == "heartbeat") {
        startHeartbeat();
        Serial.println("PATTERN: Heartbeat");
        return;
    }

    if (cmd == "stop") {
        stopPatterns();
        Serial.println("PATTERN: Stopped");
        return;
    }

    // -------- MUSIC CONTROL (placeholders) --------
    if (cmd == "play music") {
        Serial.println("MUSIC: Play");
        return;
    }

    if (cmd == "pause music") {
        Serial.println("MUSIC: Pause");
        return;
    }

    if (cmd == "next song") {
        Serial.println("MUSIC: Next song");
        return;
    }

    if (cmd == "previous song") {
        Serial.println("MUSIC: Previous song");
        return;
    }

    // -------- VIDEO CONTROL (placeholders) --------
    if (cmd == "play video") {
        Serial.println("VIDEO: Play");
        return;
    }

    if (cmd == "pause video") {
        Serial.println("VIDEO: Pause");
        return;
    }

    if (cmd == "next video") {
        Serial.println("VIDEO: Next video");
        return;
    }

    // -------- CALENDAR (placeholders) --------
    if (cmd == "open calendar") {
        Serial.println("CALENDAR: Open");
        return;
    }

    if (cmd == "add an event") {
        Serial.println("CALENDAR: Add event");
        return;
    }

    if (cmd == "what events do i have today") {
        Serial.println("CALENDAR: Query today’s events");
        return;
    }

    // -------- NAME HANDLING --------
    if (cmd == "what is my name") {
        Serial.println("Your name is: " + userName);
        return;
    }

    if (cmd.startsWith("change my name")) {
        // e.g. "change my name to Russ"
        int idx = raw.indexOf("to ");
        if (idx != -1) {
            userName = raw.substring(idx + 3);
            userName.trim();
            Serial.println("Your name has been changed to: " + userName);
        } else {
            Serial.println("To change your name, say: change my name to <name>");
        }
        return;
    }

    if (cmd == "what is your name") {
        Serial.println("My name is: " + systemName);
        return;
    }

    if (cmd.startsWith("change your name")) {
        int idx = raw.indexOf("to ");
        if (idx != -1) {
            systemName = raw.substring(idx + 3);
            systemName.trim();
            Serial.println("My name has been changed to: " + systemName);
        } else {
            Serial.println("To change my name, say: change your name to <name>");
        }
        return;
    }

    // -------- FALLBACK --------
    Serial.print("ERROR: Unknown command: ");
    Serial.println(raw);
}

// ================================================================
// PATTERN CONTROL
// ================================================================
void startKnightRider() {
    patternRunning = true;
    currentPattern = 1;
}

void startHeartbeat() {
    patternRunning = true;
    currentPattern = 2;
}

void stopPatterns() {
    patternRunning = false;

    digitalWrite(BUILTIN_LED, LOW);
    for (int i = LED0; i <= LED7; i++) {
        digitalWrite(i, LOW);
    }
}

// ================================================================
// PATTERN ENGINE
// ================================================================
void runPattern(int p) {
    if (p == 1) { // Knight Rider
        for (int i = LED0; i <= LED7; i++) {
            digitalWrite(i, HIGH);
            delay(40);
            digitalWrite(i, LOW);
        }
        for (int i = LED7; i >= LED0; i--) {
            digitalWrite(i, HIGH);
            delay(40);
            digitalWrite(i, LOW);
        }
    }

    if (p == 2) { // Heartbeat
        for (int i = LED0; i <= LED7; i++) digitalWrite(i, HIGH);
        delay(120);
        for (int i = LED0; i <= LED7; i++) digitalWrite(i, LOW);
        delay(120);
        for (int i = LED0; i <= LED7; i++) digitalWrite(i, HIGH);
        delay(60);
        for (int i = LED0; i <= LED7; i++) digitalWrite(i, LOW);
        delay(400);
    }
}

// ================================================================
// SOS PATTERN (trainer LEDs)
// ================================================================
void sosPattern() {
    // S: three short
    for (int i = 0; i < 3; i++) {
        for (int p = LED0; p <= LED7; p++) digitalWrite(p, HIGH);
        delay(150);
        for (int p = LED0; p <= LED7; p++) digitalWrite(p, LOW);
        delay(150);
    }

    // O: three long
    for (int i = 0; i < 3; i++) {
        for (int p = LED0; p <= LED7; p++) digitalWrite(p, HIGH);
        delay(400);
        for (int p = LED0; p <= LED7; p++) digitalWrite(p, LOW);
        delay(400);
    }

    // S: three short
    for (int i = 0; i < 3; i++) {
        for (int p = LED0; p <= LED7; p++) digitalWrite(p, HIGH);
        delay(150);
        for (int p = LED0; p <= LED7; p++) digitalWrite(p, LOW);
        delay(150);
    }
}
