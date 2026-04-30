# Projektstruktur

## Verzeichnisübersicht

```
hayabusa/
├── README.md                     # Haupt-Projektdokumentation
├── CHANGELOG.md                  # Versionshistorie
├── .gitmodules                   # Git Submodule-Konfiguration
│
├── docs/                         # Dokumentation
│   ├── HARDWARE.md               # Hardware-Dokumentation
│   ├── SOFTWARE.md               # Software-Dokumentation
│   ├── INSTALLATION.md           # Installationsanleitung
│   ├── TUNING.md                 # Tuning-Guide
│   ├── PROJECT_STRUCTURE.md      # Diese Datei
│   └── Kabelplan.png             # Verkabelungsdiagramm
│
├── hardware/                     # Hardware Design
│   ├── ECU/                      # ECU Elektronik
│   │   ├── *.kicad_*             # KiCad Projektdateien
│   │   ├── lib/                  # KiCad Bibliotheken
│   │   ├── docs/                 # Hardware-Dokumentation
│   │   └── output/               # Produktionsdateien (Gerber, BOM)
│   ├── Airbox/                   # Luftbox mit Kühlung
│   ├── Ram-Air-Seal/             # Ram-Air Dichtungen
│   └── ...                       # Weitere mechanische Projekte
│
├── speeduino/                    # Speeduino Firmware (Git Submodule)
│   ├── speeduino/                # Haupt-Firmware
│   ├── test/                     # Unit Tests
│   └── platformio.ini            # Build-Konfiguration
│
├── tune/                         # TunerStudio Konfigurationen
│   ├── Busa/                     # Standard Hayabusa
│   │   ├── CurrentTune.msq       # Aktuelle Tune-Datei
│   │   ├── dashboard/            # Custom Dashboards
│   │   └── DataLogs/             # Datenlogger-Aufzeichnungen
│   └── Hayabusa-R1/              # R1 Hybrid Konfiguration
│
└── TÜV/                          # TÜV-Gutachten und Zertifikate
```

## Architektur

### Hardware

```
┌─────────────────────────────────────────────────────────────┐
│                        HARDWARE                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │  Sensoren   │    │  ECU Board  │    │  Aktuatoren │      │
│  │             │    │             │    │             │      │
│  │  TPS        │◄──►│  Arduino    │◄──►│  Injektoren │      │
│  │  MAP        │    │  Speeduino  │    │  Zündung    │      │
│  │  CLT/IAT    │    │  CAN        │    │  Kraftstoff │      │
│  │  O2         │    │  I/O        │    │  Leerlauf   │      │
│  │  RPM/Cam    │    │             │    │             │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Software

```
┌─────────────────────────────────────────────────────────────┐
│                      SOFTWARE STACK                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ TunerStudio │    │  Speeduino  │    │  Hardware   │      │
│  │             │    │  Firmware   │    │  Treiber    │      │
│  │  GUI        │◄──►│  Engine     │◄──►│  PWM/ADC    │      │
│  │  Maps       │    │  Logic      │    │  Interrupts │      │
│  │  Logging    │    │  Scheduler  │    │  Timer      │      │
│  │  Monitoring │    │  Safety     │    │  Serial     │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Dateitypen

### Hardware

| Typ | Beschreibung | Software |
|-----|--------------|----------|
| .kicad_pro, .kicad_sch, .kicad_pcb | PCB Design | KiCad |
| .gbr, .drl | Gerber/Drill für Produktion | GerbView |
| .step, .stp | 3D CAD | FreeCAD, SolidWorks |

### Software

| Typ | Beschreibung | Software |
|-----|--------------|----------|
| .ino | Arduino Sketch | PlatformIO, Arduino IDE |
| .msq | TunerStudio Tune | TunerStudio |
| .ini | ECU Definition | TunerStudio |
| .dash | Dashboard | TunerStudio |

### Dokumentation

| Typ | Beschreibung |
|-----|--------------|
| .md | Markdown Dokumentation |
| .ods | Kalkulationen, BOMs |
| .pdf | Handbücher, Datenblätter |

## Entwicklung

### Voraussetzungen

**Hardware:**
- KiCad 7.0+
- FreeCAD oder SolidWorks

**Software:**
- PlatformIO (VS Code Extension)
- TunerStudio MS
- Git

### Repository klonen

```bash
# Mit Submodules
git clone --recursive https://github.com/user/hayabusa.git

# Submodules aktualisieren
git submodule update --init --recursive

# Pull mit Submodules
git pull --recurse-submodules
```

### Build-Prozess

```bash
# Firmware kompilieren
cd speeduino
pio run -e megaatmega2560

# Firmware hochladen
pio run -e megaatmega2560 -t upload

# Tests ausführen
pio test
```

## Commit-Konventionen

```
feat(hardware): CAN Bus Interface hinzugefügt
fix(firmware): Trigger-Timing korrigiert
docs(install): Verkabelungsdiagramm aktualisiert
```

| Präfix | Verwendung |
|--------|------------|
| feat | Neue Features |
| fix | Bugfixes |
| docs | Dokumentation |
| style | Formatierung |
| test | Tests |

---

**Version**: 2.0
**Stand**: April 2026
