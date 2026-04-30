# Hayabusa ECU Projekt

Ein Open-Source Engine Management System für Suzuki Hayabusa Motorräder, basierend auf der Speeduino-Plattform.

## Projektübersicht

Dieses Repository enthält die komplette Entwicklung einer Custom-ECU für Suzuki Hayabusa Motorräder der ersten Generation (1999-2007). Das Projekt umfasst Hardware-Design, Firmware-Integration, Tuning-Konfigurationen und begleitende mechanische Komponenten.

### Hauptkomponenten

| Komponente | Beschreibung |
|------------|--------------|
| **ECU Hardware** | 4-Layer PCB Design in KiCad mit Automotive-grade Komponenten |
| **Speeduino Firmware** | Open-Source Engine Management auf Basis des HasiKe-Forks |
| **Tuning** | TunerStudio-Konfigurationen für verschiedene Hayabusa-Varianten |
| **Mechanik** | Airbox, Ram-Air-Dichtungen, Wireless Charging Case |

## Projektstruktur

```
hayabusa/
├── hardware/                 # Hardware-Design und mechanische Komponenten
│   ├── ECU/                  # KiCad PCB-Design der ECU
│   ├── Airbox/               # Luftbox mit integrierter Kühlung
│   ├── Ram-Air-Seal/         # Ram-Air Dichtungssystem
│   └── ...                   # Weitere mechanische Projekte
├── speeduino/                # Speeduino Firmware (Git Submodule)
├── tune/                     # TunerStudio Konfigurationen
│   ├── Busa/                 # Standard Hayabusa Tune
│   └── Hayabusa-R1/          # R1 Hybrid Konfiguration
├── docs/                     # Projektdokumentation
└── TÜV/                      # TÜV-Gutachten und Zertifikate
```

## Hardware

### ECU-Spezifikationen

| Parameter | Wert |
|-----------|------|
| Mikrocontroller | Teensy 4.1 |
| Injector-Ausgänge | 4x Low-Side mit Flyback-Protection |
| Zündungsausgänge | 4x IGBT-Treiber |
| Analog-Eingänge | TPS, MAP, CLT, IAT, O2, Batterie |
| Digital-Eingänge | Crank, Cam (36-1 Trigger) |
| Kommunikation | USB, CAN Bus |
| PCB | 4-Layer, 100x80mm |

Detaillierte Hardware-Dokumentation: [docs/HARDWARE.md](docs/HARDWARE.md)

## Software

### Speeduino Firmware

Das Projekt verwendet den [HasiKe Speeduino Fork](https://github.com/HasiKe/speeduino) als Git-Submodule.

**Unterstützte Funktionen:**
- Sequential Fuel Injection
- Wasted Spark Ignition
- Closed-Loop Idle Control
- Launch Control / Rev Limiter
- CAN Bus Kommunikation
- SD-Card Datenlogger


## Installation

Eine vollständige Installationsanleitung mit Pinout-Mapping, Sensor-Kalibrierung und Inbetriebnahme-Checkliste findet sich unter: [docs/INSTALLATION.md](docs/INSTALLATION.md)

## Tuning

Base-Maps und Tuning-Anleitungen für TunerStudio: [docs/TUNING.md](docs/TUNING.md)

## Projektstatus

| Phase | Status |
|-------|--------|
| ECU Hardware Design | ✓ Abgeschlossen |
| Speeduino Integration | ✓ Abgeschlossen |
| Base Tune | In Arbeit |
| Fahrzeugintegration | In Arbeit |

## Dokumentation

| Dokument | Inhalt |
|----------|--------|
| [HARDWARE.md](docs/HARDWARE.md) | PCB-Design, Steckerbelegung, mechanische Spezifikationen |
| [SOFTWARE.md](docs/SOFTWARE.md) | Firmware-Architektur, Build-System, Code-Struktur |
| [INSTALLATION.md](docs/INSTALLATION.md) | Einbau, Verkabelung, Inbetriebnahme |
| [TUNING.md](docs/TUNING.md) | Kennfelder, Kalibrierung, Optimierung |
| [CHANGELOG.md](CHANGELOG.md) | Versionshistorie |

## Ressourcen

- [Speeduino Wiki](https://wiki.speeduino.com)
- [Speeduino Forum](https://speeduino.com/forum)
- [TunerStudio](http://tunerstudio.com)

## Lizenz

- **Hardware**: Open Source (siehe Komponenten-Lizenzen)
- **Speeduino**: GPL v3
- **Dokumentation**: CC BY-SA 4.0

## Haftungsausschluss

Dieses Projekt dient Bildungs- und Enthusiasten-Zwecken. Die Nutzung erfolgt auf eigene Verantwortung. Alle Modifikationen müssen den lokalen Gesetzen und Vorschriften entsprechen.

---

**Version**: 2.0
**Stand**: April 2026
