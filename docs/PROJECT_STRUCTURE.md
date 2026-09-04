# Projektstruktur

## Verzeichnisübersicht

```
hayabusa/
├── README.md                     Projektübersicht
├── CHANGELOG.md                  Versionshistorie
├── .gitmodules                   drei Submodule
│
├── docs/                         Dokumentation
│   ├── HARDWARE.md               Steuergerät Rev 3, Stecker, Eingangsbeschaltung
│   ├── SOFTWARE.md               Firmware-Fork, Board 57, TunerStudio, Generator
│   ├── INSTALLATION.md           Einbau, Verkabelung, Inbetriebnahme
│   ├── TUNING.md                 Kennfelder, Kalibrierung, Abstimmung
│   ├── PROJECT_STRUCTURE.md      diese Datei
│   ├── BESTELLUNG.ods            Bestell- und Teilelisten
│   ├── Berechnungen.ods          Auslegungsrechnungen
│   ├── Drehmoment.pdf            Anzugsdrehmomente, dazu ARP- und Wössner-Anleitungen
│   ├── Speeduino_manual.pdf      Speeduino-Handbuch
│   └── explosionszeichnung/      Suzuki-Ersatzteilzeichnungen
│
├── hardware/                     nur die beiden Elektronikprojekte
│   ├── ECU/                      Steuergerät und Sensor-Modul (KiCad)
│   │   ├── *.kicad_*             Schaltpläne und Layouts beider Platinen
│   │   ├── bom/                  Stücklisten (CSV): ECU 107, Sensor-Modul 46 Positionen
│   │   ├── case/                 Gehäuse (Fusion 360, STL, Kühlkörper)
│   │   ├── datasheets/           Datenblätter der Hauptbausteine
│   │   ├── docs/                 Pinout.ods (Serienstecker), Kabelplan, Altunterlagen
│   │   ├── lib/                  Symbole, Footprints, 3D — teensy.pretty als Submodul
│   │   └── output/               Schaltplan-PDFs, Gerber, STEP; Fertigungspakete in pcbway/
│   └── exhaust-mic/              Submodul HasiKe/Exhaust-Mic
│
├── speeduino/                    Submodul HasiKe/speeduino, Branch Hayabusa/ECU-R3
│   ├── speeduino/                Firmware, src/hayabusa/ für die Board-Funktionen
│   ├── reference/speeduino.ini   TunerStudio-Definition
│   ├── sensor-module/            STM32G474-Firmware des Sensor-Moduls
│   ├── HAYABUSA_ECU_R3.md        Firmware-Notizen zur Rev 3
│   └── platformio.ini            Umgebung teensy41_hayabusa
│
└── tune/
    ├── Hayabusa-R3/              TunerStudio-Projekt (generiert)
    │   ├── CurrentTune.msq
    │   ├── README.md             Herkunft, Checkliste vor dem ersten Start
    │   ├── projectCfg/           mainController.ini (Kopie der Fork-INI), project.properties
    │   └── tools/                gen_tune.py und Helfer
    └── setup/                    Serienkennfelder (maps.ods), ECUeditor-Screenshot
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
│  │  TPS        │◄──►│  Teensy 4.1 │◄──►│  Injektoren │      │
│  │  MAP        │    │  Speeduino  │    │  Zündung    │      │
│  │  CLT/IAT    │    │  MC33810    │    │  Kraftstoff │      │
│  │  O2 (LC-2)  │    │  CAN        │    │  Lampe/Tach │      │
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
| .ino, .cpp, .h | Firmware | PlatformIO |
| .py | Tune-Generator | Python 3, odfpy |
| .msq | TunerStudio Tune | TunerStudio |
| .ini | ECU Definition | TunerStudio |

### Dokumentation

| Typ | Beschreibung |
|-----|--------------|
| .md | Markdown Dokumentation |
| .ods | Kalkulationen, BOMs |
| .pdf | Handbücher, Datenblätter |

## Entwicklung

### Voraussetzungen

**Hardware:**
- KiCad 10 (Dateien der Rev 3), Fusion 360 für das Gehäuse

**Software:**
- PlatformIO
- TunerStudio MS Ultra
- Python 3 mit odfpy (Tune-Generator)
- Git

### Repository klonen

```bash
# Mit Submodules
git clone --recursive https://github.com/HasiKe/Hayabusa.git

# Submodules aktualisieren
git submodule update --init --recursive

# Pull mit Submodules
git pull --recurse-submodules
```

### Build-Prozess

```bash
# Firmware kompilieren und flashen
cd speeduino
pio run -e teensy41_hayabusa
pio run -e teensy41_hayabusa -t upload

# Tune neu erzeugen
python3 tune/Hayabusa-R3/tools/gen_tune.py
```

## Commit-Konventionen

Kurze, sachliche Betreffzeile ohne Präfix: im Hauptrepository deutsch, im Firmware-Fork
englisch. Der Text erklärt das Warum. Keine Werkzeug- oder Sitzungsverweise.

---

**Version**: 4.0
**Stand**: September 2026
