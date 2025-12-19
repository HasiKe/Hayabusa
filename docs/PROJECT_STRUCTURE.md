# Project Structure - Hayabusa ECU

## 📁 Ordnerstruktur

```
Hayabusa/
├── README.md                    # Haupt-Projektdokumentation
├── CHANGELOG.md                 # Versionshistorie
├── .gitignore                   # Git ignore rules
│
├── docs/                        # Dokumentation
│   ├── HARDWARE.md              # Hardware-Dokumentation
│   ├── SOFTWARE.md              # Software-Dokumentation
│   ├── INSTALLATION.md          # Installations-Guide
│   ├── TUNING.md                # Tuning-Guide
│   ├── PROJECT_STRUCTURE.md     # Diese Datei
│   ├── Kabelplan.png           # Verkabelungsdiagramm
│   ├── Kabelplan.pdn           # Paint.NET Quelldatei
│   ├── Speeduino_manual.pdf    # Speeduino Handbuch
│   └── *.jpg                   # Referenzbilder
│
├── Hardware/                    # Hardware Design & CAD
│   ├── ECU/                    # ECU Elektronik Design
│   │   ├── *.kicad_*           # KiCad Projekt Dateien
│   │   ├── lib/                # KiCad Bibliotheken
│   │   ├── docs/               # Hardware Dokumentation
│   │   ├── output/             # Produktionsdateien
│   │   │   ├── gerber files/   # Gerber für PCB Produktion
│   │   │   ├── cut files/      # Schneidedateien
│   │   │   ├── *.pdf           # Schaltpläne & PCB
│   │   │   └── *.csv           # Bill of Materials
│   │   └── ECU-backups/        # Automatische Backups
│   │
│   ├── Airbox/                 # Luftbox System
│   │   ├── *.stp               # CAD Dateien (STEP)
│   │   ├── aircooler/          # Kühlsystem Komponenten
│   │   └── *.jpg               # Referenzfotos
│   │
│   ├── Ram-Air-Seal/           # Ram-Air Dichtungen
│   │   ├── *.SLDPRT            # SolidWorks Parts
│   │   ├── *.x_t               # Parasolid Exchange
│   │   └── suzuki-*/           # Original Referenzen
│   │
│   ├── Abgasstopfen/           # Auspuff-Stopfen
│   │   ├── *.step              # CAD Dateien
│   │   ├── *.dxf               # 2D Zeichnungen
│   │   └── *.png               # Skizzen
│   │
│   ├── wireless charging/      # Wireless Charging Case
│   │   └── *.step              # CAD Dateien
│   │
│   └── Parts & Cost.ods        # Teile & Kostenübersicht
│
├── speeduino/                   # Speeduino Firmware (Git Submodule)
│   ├── speeduino/              # Haupt-Firmware
│   │   ├── speeduino.ino       # Main Arduino Sketch
│   │   ├── *.cpp               # C++ Source Files
│   │   ├── *.h                 # Header Files
│   │   └── src/                # Externe Bibliotheken
│   ├── test/                   # Unit Tests
│   ├── platformio.ini          # PlatformIO Konfiguration
│   ├── reference/              # Referenz-Dateien
│   └── README.md               # Speeduino Dokumentation
│
├── tune/                       # TunerStudio Konfigurationen
│   ├── *.ini                   # Speeduino INI Dateien
│   │
│   ├── Busa/                   # Standard Hayabusa Tune
│   │   ├── CurrentTune.msq     # Aktuelle Tune-Datei
│   │   ├── projectCfg/         # TunerStudio Projektkonfiguration
│   │   ├── dashboard/          # Custom Dashboards
│   │   ├── restorePoints/      # Backup Tunes
│   │   ├── DataLogs/          # Datenlogger Aufzeichnungen
│   │   └── TuneView/          # TuneView Dateien
│   │
│   ├── Hayabusa-R1/           # R1 Hybrid Konfiguration
│   │   ├── CurrentTune.msq     # R1 Tune-Datei
│   │   ├── projectCfg/         # R1 Projektkonfiguration
│   │   ├── dashboard/          # R1-spezifische Dashboards
│   │   ├── restorePoints/      # R1 Backup Tunes
│   │   └── DataLogs/          # R1 Datenlogger
│   │
│   ├── setup/                  # Setup Dokumentation
│   │   ├── maps.ods           # Kennfeld-Übersicht
│   │   └── sensor setup.url   # Sensor Setup Referenz
│   │
│   ├── online/                 # Online Tune Archive
│   └── TunerStudioAppDebug.txt # TS Debug Log
│
└── TÜV/                        # TÜV Gutachten & Zertifikate
    ├── *_ABG_*.pdf            # Allgemeine Betriebserlaubnis
    ├── *_abe.pdf              # Teilegutachten
    └── *.pdf                  # Weitere Zertifikate
```

## 🏗️ Architektur-Übersicht

### Hardware-Architektur
```
┌─────────────────────────────────────────────────────────────────┐
│                         HARDWARE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Sensors       │    │   ECU Board     │    │  Actuators   │ │
│  │                 │    │                 │    │              │ │
│  │ • TPS           │◄──►│ Arduino Mega    │◄──►│ • Injectors  │ │
│  │ • MAP           │    │ Speeduino FW    │    │ • Ignition   │ │
│  │ • CLT/IAT       │    │ CAN Interface   │    │ • Fuel Pump  │ │
│  │ • O2 Sensor     │    │ I/O Drivers     │    │ • Idle Valve │ │
│  │ • RPM/Cam       │    │                 │    │              │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Software-Architektur
```
┌─────────────────────────────────────────────────────────────────┐
│                         SOFTWARE STACK                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  TunerStudio    │    │   Speeduino     │    │   Hardware   │ │
│  │                 │    │   Firmware      │    │   Drivers    │ │
│  │ • GUI Interface │◄──►│ • Engine Logic  │◄──►│ • PWM/ADC    │ │
│  │ • Tuning Maps   │    │ • Calculations  │    │ • Interrupts │ │
│  │ • Data Logging  │    │ • Scheduling    │    │ • Timers     │ │
│  │ • Real-time     │    │ • Corrections   │    │ • Serial I/O │ │
│  │   Monitoring    │    │ • Safety        │    │ • Storage    │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📋 Dateitypen & Verwendung

### Hardware Files

#### KiCad Projekt (.kicad_pro, .kicad_sch, .kicad_pcb)
- **Zweck**: PCB Design und Schaltpläne
- **Software**: KiCad EDA Suite
- **Bearbeitung**: Erfordert KiCad Installation
- **Version Control**: Text-basiert, Git-friendly

#### Gerber Files (.gbr, .drl)
- **Zweck**: PCB Produktion
- **Verwendung**: Direkt an PCB-Hersteller
- **Format**: Industrie-Standard
- **Viewer**: GerbView, Online Gerber Viewer

#### CAD Files (.step, .stp, .SLDPRT)
- **Zweck**: 3D mechanische Komponenten
- **Software**: SolidWorks, Fusion 360, FreeCAD
- **Austausch**: STEP universeller als SLDPRT
- **3D Druck**: STL Export erforderlich

### Software Files

#### Arduino Sketch (.ino)
- **Zweck**: Haupt-Firmware Entry Point
- **Compiler**: Arduino IDE oder PlatformIO
- **Sprache**: C++ (Arduino Framework)
- **Dependencies**: Externe Libraries in src/

#### TunerStudio Files (.msq, .ini)
- **MSQ**: Tune-Datei mit Maps und Einstellungen
- **INI**: ECU Definition und Interface
- **Kompatibilität**: TunerStudio MS versions
- **Backup**: Automatisch durch TunerStudio

#### Dashboard Files (.dash)
- **Zweck**: Custom TunerStudio Dashboards
- **Format**: XML-basiert
- **Anpassung**: TunerStudio Dashboard Editor
- **Sharing**: Zwischen Projekten kopierbar

### Dokumentation Files

#### Markdown (.md)
- **Zweck**: Dokumentation und README
- **Syntax**: GitHub Flavored Markdown
- **Viewing**: GitHub, VS Code, oder Markdown Viewer
- **Version Control**: Diff-friendly

#### Spreadsheets (.ods)
- **Zweck**: Kalkulationen, BOMs, Listen
- **Software**: LibreOffice Calc, Excel
- **Format**: Open Document Standard
- **Export**: PDF, CSV, XLSX möglich

## 🔄 Workflow & Build Process

### Hardware Development Workflow
```bash
1. Schematic Design (KiCad)
   ├── Component Selection
   ├── Electrical Rules Check (ERC)
   └── Netlist Generation

2. PCB Layout (KiCad) 
   ├── Component Placement
   ├── Routing (Auto + Manual)
   ├── Design Rules Check (DRC)
   └── 3D Visualization

3. Production Files
   ├── Gerber Generation
   ├── Drill Files
   ├── Pick & Place
   └── BOM Export

4. Assembly & Test
   ├── PCB Manufacturing
   ├── Component Assembly  
   ├── Functional Test
   └── Integration Test
```

### Software Development Workflow
```bash
1. Firmware Development
   ├── speeduino/ (Git Submodule)
   ├── Local modifications
   ├── PlatformIO Build
   └── Upload to ECU

2. Tuning Development
   ├── Base Map Creation
   ├── TunerStudio Project Setup
   ├── Dashboard Design
   └── Validation Testing

3. Documentation
   ├── Markdown Writing
   ├── Screenshot Generation
   ├── Diagram Creation
   └── Review & Update
```

### Release Process
```bash
1. Version Increment
   ├── Update CHANGELOG.md
   ├── Tag Git Release
   └── Update Documentation

2. Hardware Release
   ├── Finalize Gerber Files
   ├── Validate BOM
   ├── Assembly Instructions
   └── Test Procedures

3. Software Release
   ├── Firmware Compilation
   ├── Tune File Packaging
   ├── Documentation Update
   └── Distribution
```

## 🔧 Development Setup

### Required Software

#### Hardware Development
```bash
# PCB Design
- KiCad 7.0+ (Free)
- KiCad Library Management

# 3D CAD  
- FreeCAD (Free) OR
- SolidWorks (Commercial) OR
- Fusion 360 (Commercial/Free for personal)

# Viewers
- GerbView (included with KiCad)
- FreeCAD for STEP files
```

#### Software Development  
```bash
# Firmware Development
- PlatformIO (VS Code Extension)
- Arduino IDE (Alternative)
- Git (Version Control)

# Tuning Software
- TunerStudio MS (Commercial)
- MegaLogViewer (Data analysis)

# Documentation
- VS Code with Markdown extensions
- LibreOffice (Spreadsheets)
```

### Git Workflow

#### Repository Setup
```bash
# Clone with submodules
git clone --recursive https://github.com/user/Hayabusa.git

# Update submodules
git submodule update --init --recursive

# Pull latest changes including submodules  
git pull --recurse-submodules
```

#### Branch Strategy
```bash
main/          # Production-ready releases
├── develop/   # Integration branch
├── feature/*  # New features
├── hotfix/*   # Critical fixes
└── release/*  # Release preparation
```

#### Commit Guidelines
```bash
# Format: type(scope): description
feat(hardware): add CAN bus interface
fix(firmware): correct trigger timing calculation  
docs(install): update wiring diagram
style(tuning): reformat fuel maps
test(ecu): add sensor validation tests
```

## 📚 Documentation Standards

### File Naming
```bash
# Descriptive, lowercase, hyphen-separated
hardware-specs.md       ✓ Good
HARDWARE_SPECS.md      ✗ Avoid
hardwareSpecs.md       ✗ Avoid

# Version in filename if needed
tune-v2.1-hayabusa.msq  ✓ Good
CurrentTune.msq         ✓ Acceptable for latest
```

### Documentation Structure
```markdown
# Title (H1 - One per document)
## Major Section (H2)  
### Subsection (H3)
#### Details (H4)

- Use bullet points for lists
- **Bold** for emphasis
- `code` for technical terms
- [Links](url) for references
```

### Code Documentation
```cpp
/**
 * Brief description of function
 * @param param1 Description of parameter
 * @param param2 Description of parameter  
 * @return Description of return value
 */
int calculateFuel(int map, int rpm) {
    // Detailed comments for complex logic
    return fuelMap[map][rpm];
}
```

---

**Maintained by**: Kevin  
**Last Updated**: Dezember 2025  
**Version**: 2.0