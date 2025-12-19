# Changelog - Hayabusa ECU Project

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Geplant
- CAN Bus Dashboard Integration
- Bluetooth Datenlogger
- Mobile App für grundlegende Überwachung
- Erweiterte Sensorunterstützung (Wideband O2, EGT)

## [2.0.0] - 2025-12-19

### Hinzugefügt
- **Vollständige Projektdokumentation**
  - Umfassendes README mit Projektübersicht
  - Hardware-Dokumentation (HARDWARE.md)
  - Software-Dokumentation (SOFTWARE.md)  
  - Installation Guide (INSTALLATION.md)
  - Tuning Guide (TUNING.md)
  - Changelog (CHANGELOG.md)
- **Projektstruktur**
  - Organisierte Ordnerstruktur
  - .gitignore für saubere Versionskontrolle
  - Professionelle Dokumentation

### Geändert
- **README.md** komplett überarbeitet mit:
  - Klarer Projektbeschreibung
  - Strukturierter Komponentenübersicht
  - Installationsanweisungen
  - Roadmap und Entwicklungsphasen
  - Support-Informationen
- **Speeduino Integration** als Git Submodule

### Hardware
- **ECU PCB Design** (KiCad)
  - 4-Layer Professional PCB
  - Automotive-grade Komponenten
  - CAN Bus Interface
  - Umfangreiche I/O für Sensoren/Aktuatoren
- **Mechanische Komponenten**
  - Airbox System mit integrierter Kühlung
  - Ram-Air Dichtungen
  - Wireless Charging Case

### Software  
- **Speeduino Firmware** Integration
  - Latest stable version (202310)
  - Hayabusa-spezifische Konfiguration
  - PlatformIO Build System
- **TunerStudio Konfigurationen**
  - Base Maps für verschiedene Hayabusa Varianten
  - Custom Dashboards für Analyse
  - Datenlogger Setup

## [1.5.0] - 2025-10-07

### Hinzugefügt
- **Neue Tuning-Konfiguration** für Hayabusa-R1 Hybrid
- **Erweiterte Dashboards** in TunerStudio
  - VE Analysis Dashboard
  - Acceleration Performance Dashboard
  - Ignition Logger Cluster
- **Backup & Restore System** für Tunes

### Geändert
- **ECU Hardware** Rev 1.1 Updates
  - Verbesserte EMI Abschirmung
  - Optimierte Gerber-Dateien für Produktion
  - Erweiterte Dokumentation

### Behoben
- **Trigger Signal** Stabilität verbessert
- **Temperature Sensor** Kalibrierung korrigiert
- **CAN Bus** Kommunikationsfehler behoben

## [1.0.0] - 2025-08-01

### Hinzugefügt
- **Initial Release** des Hayabusa ECU Projekts
- **Hardware Design**
  - Erste Version des ECU PCB Designs
  - KiCad Schaltplan und Layout
  - Bill of Materials (BOM)
- **Software Integration**
  - Speeduino Firmware Anpassung
  - Grundlegende TunerStudio Konfiguration
- **Mechanisches Design**
  - Airbox Design (CAD)
  - Ram-Air Seal System
- **Dokumentation**
  - Grundlegende Hardware-Spezifikationen
  - Pinout-Dokumentation
  - Erste Tuning-Parameter

### Hardware Spezifikationen
- **Mikrocontroller**: Arduino Mega 2560 / Teensy 4.1
- **Eingänge**: 8x Analog, 4x Digital
- **Ausgänge**: 4x Injector, 4x Ignition, 8x Auxiliary
- **Communication**: USB, CAN Bus
- **Power**: 12V Automotive Supply

### Software Features
- **Engine Management**: Fuel + Ignition Control
- **Sensor Support**: MAP, TPS, CLT, IAT, O2
- **Data Logging**: SD Card, Real-time
- **Tuning Interface**: TunerStudio Compatible
- **Safety Features**: Engine Protection, Limits

## [0.9.0] - 2025-06-01

### Hinzugefügt  
- **Prototyp Hardware** erste Tests
- **Speeduino Firmware** Basis-Integration
- **Proof of Concept** erfolgreich

### Entwicklung
- **Hardware Prototyping** auf Breadboard
- **Sensor Integration** Tests
- **Erste Motorläufe** auf Teststand

## [0.1.0] - 2025-05-01

### Hinzugefügt
- **Projekt Initialisierung**
- **Konzept & Planung**
- **Hardware Anforderungen** definiert
- **Software Architektur** geplant

---

## Versioning Scheme

Dieses Projekt verwendet [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Inkompatible API/Hardware Änderungen
- **MINOR** (0.X.0): Neue Features, rückwärts kompatibel  
- **PATCH** (0.0.X): Bugfixes, rückwärts kompatibel

## Release Notes Format

### Kategorien
- **Hinzugefügt** für neue Features
- **Geändert** für Änderungen an bestehenden Features
- **Veraltet** für Features die bald entfernt werden
- **Entfernt** für entfernte Features
- **Behoben** für Bugfixes
- **Sicherheit** für Security-relevante Änderungen

### Hardware vs. Software
- **Hardware**: PCB, mechanische Komponenten, Elektronik
- **Software**: Firmware, Tuning, Konfiguration, Tools
- **Dokumentation**: Handbücher, Guides, API Docs

---

**Maintained by**: Kevin  
**Project Start**: Mai 2025  
**Current Status**: Active Development