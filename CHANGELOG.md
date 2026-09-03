# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Hinzugefügt
- TunerStudio-Projekt `tune/Hayabusa-R3` für die Rev 3 (Board 57), generiert aus den Serienkennfeldern in `tune/setup/maps.ods` (`tools/gen_tune.py`), Erststart-Konfiguration mit Checkliste im README
- Firmware-Fork: Kanalzuordnung nach Zündfolge 1-2-4-3 am Serienstecker, Batteriespannungs-Skalierung für den 47k/10k-Teiler, TunerStudio-INI korrigiert (ignTrim auf Seite 13, Load-Achsen der Kennfeldsätze 3/4, boostTable3/4)

### Geändert
- Dokumentation (HARDWARE, SOFTWARE, INSTALLATION, TUNING, PROJECT_STRUCTURE) komplett auf die Rev 3 und das neue Tune-Projekt umgeschrieben; die Dropbear-Beschreibungen der Rev 1 entfallen

### Geplant
- CAN Bus Dashboard-Integration
- Bluetooth Datenlogger
- Mobile App für Überwachung
- Erweiterte Sensorunterstützung (Wideband O2, EGT)

## [2.0.0] - 2026-04-30

### Hinzugefügt
- Vollständige Projektdokumentation (HARDWARE.md, SOFTWARE.md, INSTALLATION.md, TUNING.md)
- Organisierte Ordnerstruktur mit klarer Trennung von Hardware, Software und Dokumentation

### Geändert
- **Speeduino Submodule**: Wechsel von speeduino/speeduino auf HasiKe/speeduino Fork
- **Verzeichnisstruktur**: Hardware/ umbenannt zu hardware/ (lowercase)
- **teensy.pretty Submodule**: Pfadkorrektur für Submodule-Referenz
- README.md komplett überarbeitet
- Dokumentation auf Deutsch vereinheitlicht

### Hardware
- ECU PCB Design (KiCad, 4-Layer)
- Automotive-grade Komponenten
- CAN Bus Interface
- ISL9V5036P3-F085 Komponenten-Bibliothek hinzugefügt

### Software
- Speeduino Firmware Integration (HasiKe Fork)
- TunerStudio Konfigurationen für Hayabusa und R1-Hybrid
- Custom Dashboards für Analyse

## [1.5.0] - 2025-10-07

### Hinzugefügt
- Tuning-Konfiguration für Hayabusa-R1 Hybrid
- Erweiterte TunerStudio Dashboards (VE Analysis, Acceleration, Ignition Logger)
- Backup & Restore System für Tunes

### Geändert
- ECU Hardware Rev 1.1: Verbesserte EMI-Abschirmung
- Optimierte Gerber-Dateien für Produktion

### Behoben
- Trigger-Signal Stabilität
- Temperature Sensor Kalibrierung
- CAN Bus Kommunikationsfehler

## [1.0.0] - 2025-08-01

### Hinzugefügt
- Initial Release
- ECU PCB Design (KiCad Schaltplan und Layout)
- Bill of Materials (BOM)
- Speeduino Firmware Anpassung
- Grundlegende TunerStudio Konfiguration
- Airbox Design (CAD)
- Ram-Air Seal System
- Pinout-Dokumentation

### Spezifikationen
- Mikrocontroller: Arduino Mega 2560 / Teensy 4.1
- Eingänge: 8x Analog, 4x Digital
- Ausgänge: 4x Injector, 4x Ignition, 8x Auxiliary
- Kommunikation: USB, CAN Bus
- Stromversorgung: 12V Automotive

## [0.9.0] - 2025-06-01

### Hinzugefügt
- Prototyp Hardware Tests
- Speeduino Firmware Basis-Integration
- Proof of Concept

## [0.1.0] - 2025-05-01

### Hinzugefügt
- Projekt Initialisierung
- Konzept und Planung
- Hardware-Anforderungen definiert

---

## Versioning

- **MAJOR** (X.0.0): Inkompatible Änderungen
- **MINOR** (0.X.0): Neue Features, rückwärts kompatibel
- **PATCH** (0.0.X): Bugfixes, rückwärts kompatibel

## Kategorien

- **Hinzugefügt**: Neue Features
- **Geändert**: Änderungen an bestehenden Features
- **Veraltet**: Features die entfernt werden
- **Entfernt**: Entfernte Features
- **Behoben**: Bugfixes
- **Sicherheit**: Security-relevante Änderungen
