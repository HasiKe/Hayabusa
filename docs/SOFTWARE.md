# Software-Dokumentation

## Speeduino Firmware

### Übersicht

Das Speeduino Engine Management System ist eine Open-Source ECU-Firmware, hier auf dem Teensy 4.1 (Dropbear v2) ausgeführt.

### Version

| Parameter | Wert |
|-----------|------|
| Fork | [HasiKe/speeduino](https://github.com/HasiKe/speeduino) |
| Board | Dropbear v2 / Teensy 4.1 |
| Plattform | PlatformIO |
| Lizenz | GPL v3 |
| Pfad | `speeduino/` (Git Submodule) |

### Teensy 4.1 Vorteile

- 600 MHz ARM Cortex-M7 (37x schneller als Mega 2560)
- Native CAN Bus (kein MCP2515 nötig)
- 8 MB Flash, 1 MB RAM
- Bessere Timing-Präzision
- Mehr I/O für zukünftige Erweiterungen

### Funktionen

#### Motor-Management
- **Einspritzung**: Sequential, Semi-Sequential, Batch
- **Zündung**: Advance/Retard Maps, Klopferkennung
- **Leerlauf**: PWM-Ventil, Schrittmotor, Closed-Loop

#### Erweiterte Funktionen
- Native CAN Bus
- Datenlogger (SD-Card)
- Echtzeit-Tuning
- Staged Injection
- Launch Control
- Boost Control
- Klopfregelung (geplant)

## Konfiguration

### Hayabusa-Einstellungen

#### Motor
```cpp
configPage2.nCylinders = 4;           // 4 Zylinder
configPage2.engineType = 0;           // 4-Takt
configPage2.fuelAlgorithm = 1;        // Speed Density
configPage4.sparkMode = 2;            // Wasted Spark
configPage2.nInjectors = 4;           // Sequential
```

#### Trigger
```cpp
configPage4.TrigPattern = 1;          // Missing Tooth
configPage4.triggerTeeth = 36;        // 36-1 Geberrad
configPage4.triggerMissingTeeth = 1;  // 1 fehlender Zahn
```

#### Sensoren
```cpp
configPage2.mapType = 1;              // MPX4250
configPage2.mapMin = 10;              // kPa
configPage2.mapMax = 250;             // kPa
configPage2.tpsMin = 150;             // ADC Counts
configPage2.tpsMax = 850;             // ADC Counts
```

#### Klopfsensor (geplant)
```cpp
configPage10.knock_enabled = 1;       // Aktiviert
configPage10.knock_threshold = 50;    // Schwellwert
configPage10.knock_retard = 3;        // Rücknahme in °
configPage10.knock_recovery = 0.5;    // °/s Erholung
```

## Build-System

### PlatformIO Konfiguration

```ini
[platformio]
default_envs = teensy41
src_dir = speeduino

[common]
lib_deps =
    SD
    SPI
    FlexCAN_T4

[env:teensy41]
platform = teensy
board = teensy41
framework = arduino
lib_deps = ${common.lib_deps}
build_flags =
    -DCORE_TEENSY
    -DBOARD_DROPBEAR
monitor_speed = 115200
```

### Befehle

```bash
# Build für Teensy 4.1
pio run -e teensy41

# Build und Upload
pio run -e teensy41 -t upload

# Tests
pio test

# Clean
pio run -t clean
```

## Code-Struktur

### Hauptkomponenten

```
speeduino/speeduino/
├── speeduino.ino      # Haupteinstiegspunkt
├── globals.h/.cpp     # Globale Variablen
├── init.h/.cpp        # Initialisierung
├── auxiliaries.h/.cpp # Hilfsausgänge
├── comms.h/.cpp       # Kommunikation
├── corrections.h/.cpp # Korrekturen
├── decoders.h/.cpp    # Trigger-Decoder
├── idle.h/.cpp        # Leerlaufregelung
├── scheduler.h/.cpp   # Event-Scheduling
├── sensors.h/.cpp     # Sensorverarbeitung
├── storage.h/.cpp     # EEPROM
├── table2d.h/.cpp     # 2D Tabellen
└── table3d.h/.cpp     # 3D Kennfelder
```

### Trigger-Decoder

```cpp
void triggerPri_missingTooth() {
    curTime = micros();
    curGap = curTime - lastTooth;

    if (curGap < triggerFilterTime) { return; }

    // Missing Tooth Erkennung
    if (curGap > (triggerSecFilterTime * 3)) {
        toothCurrentCount = 1;
        currentStatus.hasSync = true;
    }
}
```

### Kraftstoffberechnung

```cpp
uint16_t calculatePW() {
    uint16_t pw = table3D_getValue(&fuelTable,
                                   currentStatus.MAP,
                                   currentStatus.RPM);
    pw = correctionsFuel(pw);
    return pw;
}
```

## TunerStudio

### Projektstruktur

```
tune/Busa/
├── CurrentTune.msq      # Aktuelle Tune-Datei
├── projectCfg/          # Projektkonfiguration
├── dashboard/           # Custom Dashboards
├── restorePoints/       # Backup Tunes
└── DataLogs/            # Datenlogger
```

### Kommunikation

```ini
[Communications]
port = COM3
baud = 115200
protocol = ms2
```

## Datenlogger

### Echtzeit-Parameter

```cpp
struct statuses {
    uint16_t RPM;           // Drehzahl
    uint16_t MAP;           // Saugrohrdruck (kPa)
    uint8_t  TPS;           // Drosselklappe (%)
    int16_t  IAT;           // Ansaugluft (°C)
    int16_t  CLT;           // Kühlmittel (°C)
    uint16_t AFR;           // Lambda × 100
    int8_t   advance;       // Zündwinkel (°)
    uint16_t PW1;           // Einspritzzeit (µs)
    uint8_t  dutyCycle;     // Tastgrad (%)
    uint16_t battery;       // Spannung (V × 10)
    uint8_t  knockLevel;    // Klopfpegel (geplant)
};
```

### SD-Card Format

```csv
Time,RPM,MAP,TPS,IAT,CLT,AFR,ADV,PW1,DUTY,BATT,KNOCK
0,800,30,0,25,80,14.7,15,2000,25,13.2,0
100,850,32,2,25,82,14.5,14,2100,27,13.1,0
```

## Sicherheitsparameter

### Motorschutz

```cpp
#define CLT_WARN_TEMP     95    // °C
#define CLT_CUTOFF_TEMP   105   // °C
#define MAP_MAX_KPA       250   // kPa
#define RPM_HARD_LIMIT    11500 // U/min
#define RPM_SOFT_LIMIT    11000 // U/min
```

### Klopfschutz (geplant)

```cpp
#define KNOCK_RETARD_MAX    15   // Max. Rücknahme in °
#define KNOCK_RECOVERY_RATE 0.5  // °/s Erholung
#define KNOCK_WINDOW_START  10   // ° nach ZOT
#define KNOCK_WINDOW_END    70   // ° nach ZOT
```

### Fail-Safe

```cpp
if (MAP > 300 || MAP < 10) {
    MAP = 100;  // Atmosphärisch
    setError(ERR_MAP_SENSOR);
}

if (CLT > 150 || CLT < -40) {
    CLT = 80;   // Normaltemperatur
    setError(ERR_CLT_SENSOR);
}
```

## Performance

### Speichernutzung (Teensy 4.1)

| Bereich | Nutzung |
|---------|---------|
| Flash | 15% (1,2 MB / 8 MB) |
| RAM | 25% (256 KB / 1 MB) |

### Timing

| Parameter | Wert |
|-----------|------|
| Trigger Jitter | < ±0,1° |
| Injection Accuracy | ±10 µs |
| Ignition Accuracy | ±0,05° |
| Loop Time | 20 µs |

---

**Version**: 2.0
**Stand**: April 2026
