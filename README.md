# Hayabusa ECU Projekt

Ein umfassendes Engine Management System (ECU) Projekt für Suzuki Hayabusa Motorräder basierend auf der Speeduino Plattform.

## 🏍️ Projektübersicht

Dieses Projekt umfasst die komplette Entwicklung einer kundenspezifischen ECU für Suzuki Hayabusa Motorräder. Es beinhaltet Hardware-Design, Firmware, Tuning-Konfigurationen und mechanische Komponenten.

### Hauptkomponenten:
- **Custom ECU Hardware** - KiCad PCB Design mit professionellen Automotive-Komponenten
- **Speeduino Firmware** - Open-source Engine Management Software
- **Tuning Konfigurationen** - TunerStudio Setups für verschiedene Hayabusa Varianten
- **Mechanische Teile** - 3D-Design für Luftboxen, Dichtungen und Zubehör

## 📋 Projektstruktur

```
Hayabusa/
├── Hardware/              # Hardware Design & Mechanik
│   ├── ECU/              # KiCad PCB Design für ECU
│   ├── Airbox/           # Luftbox Design & Kühlung
│   ├── Ram-Air-Seal/     # Ram-Air Dichtungen
│   ├── Abgasstopfen/     # Auspuff-Stopfen
│   └── wireless charging/ # Wireless Charging Case
├── speeduino/            # Speeduino Firmware (Submodule)
├── tune/                 # TunerStudio Konfigurationen
│   ├── Busa/            # Standard Hayabusa Tune
│   ├── Hayabusa-R1/     # R1 Hybrid Konfiguration
│   └── setup/           # Setup-Dokumentation
├── docs/                 # Projekt Dokumentation
├── TÜV/                 # TÜV-Gutachten & Zertifikate
└── README.md            # Diese Datei
```

## 🔧 Hardware

### ECU Board
- **Plattform**: Arduino Mega 2560 / Teensy 4.1
- **Design Tool**: KiCad
- **Features**: 
  - Automotive-grade Komponenten
  - CAN Bus Unterstützung
  - Umfangreiche I/O für Sensoren und Aktuatoren
  - Professionelle PCB mit Gerber-Dateien

### Mechanische Komponenten
- **Airbox System** mit integrierter Kühlung
- **Ram-Air Dichtungen** für optimierte Luftzufuhr
- **Wireless Charging Case** für moderne Konnektivität

## ⚙️ Software

### Speeduino Firmware
- **Version**: Latest (Submodule)
- **Platform**: PlatformIO
- **Unterstützte Boards**: AVR2560, STM32, Teensy 3.5/4.1
- **Features**: Vollständiges EMS mit:
  - Fuel injection control
  - Ignition timing
  - Idle control
  - Launch control
  - Datenlogger

### Tuning
- **Software**: TunerStudio
- **Konfigurationen**:
  - Standard Hayabusa (alle Generationen)
  - Hayabusa-R1 Hybrid Setup
- **Dashboards**: Umfangreiche Analyse-Tools

## 📐 Installation & Setup

### Hardware Setup
1. **ECU Montage**:
   ```bash
   # Siehe docs/installation.md für detaillierte Anweisungen
   ```

2. **Verkabelung**:
   - Siehe `docs/Kabelplan.png` für vollständigen Schaltplan
   - Pinout-Referenz in `Hardware/ECU/docs/Pinout.ods`

### Firmware Installation
```bash
cd speeduino
# PlatformIO verwenden für Compilation und Upload
pio run -t upload
```

### Tuning Setup
1. TunerStudio öffnen
2. Projekt aus `tune/Busa/` oder `tune/Hayabusa-R1/` laden
3. Base Maps entsprechend Motor-Setup verwenden

## 🔬 Testing & Validation

### Hardware Tests
- **PCB Validation**: Alle Schaltkreise getestet
- **Automotive Standards**: EMV-Compliance
- **Umgebungstests**: Vibration, Temperatur

### Software Tests
```bash
cd speeduino
# Unit Tests ausführen
pio test
```

## 📊 Performance

### Aktuelle Spezifikationen:
- **Injection Timing**: ±0.1ms Präzision
- **RPM Range**: 0-15,000 RPM
- **Sensor Support**: MAP, MAF, TPS, CLT, IAT, O2
- **Output Channels**: 8x Injector, 8x Ignition

## 🛡️ Zertifizierungen

### TÜV Gutachten
- Philips LED Scheinwerfer (siehe `TÜV/`)
- Brembo RCS Bremsen
- Metzeler Reifen Freigaben

## 🚀 Roadmap

### Phase 1 - Hardware ✅
- [x] ECU PCB Design
- [x] Mechanische Komponenten
- [x] Prototyp Tests

### Phase 2 - Software ✅
- [x] Speeduino Integration
- [x] Base Tune Development
- [x] Dashboard Creation

### Phase 3 - Integration 🔄
- [ ] Vollständige Fahrzeug Integration
- [ ] Straßentests
- [ ] Performance Optimierung

### Phase 4 - Documentation 📝
- [ ] Vollständige Installations-Anleitung
- [ ] Video Tutorials
- [ ] Community Support

## 🤝 Beitragen

Contributions sind willkommen! Bitte beachte:

1. **Hardware Änderungen**: Vollständige Simulation und Tests erforderlich
2. **Software**: Speeduino Coding Standards befolgen
3. **Dokumentation**: Deutsch/Englisch
4. **Testing**: Alle Änderungen müssen getestet werden

## 📞 Support

### Community
- **Discord**: [Speeduino Discord](https://discord.gg/YWCEexaNDe)
- **Forum**: [Speeduino Forum](https://speeduino.com/forum)

### Technische Unterstützung
- **Hardware**: Siehe Schaltpläne in `Hardware/ECU/docs/`
- **Software**: [Speeduino Wiki](https://wiki.speeduino.com)
- **Tuning**: TunerStudio Dokumentation

## 📄 Lizenz

- **Hardware**: Open Source (siehe einzelne Komponenten-Lizenzen)
- **Speeduino**: GPL v3
- **Dokumentation**: CC BY-SA 4.0

## ⚠️ Haftungsausschluss

Dieses Projekt ist für Bildungs- und Enthusiasten-Zwecke. Eigenverantwortliche Nutzung. Alle Modifikationen müssen den lokalen Gesetzen und Vorschriften entsprechen.

---

**Projekt Status**: 🟢 Aktive Entwicklung  
**Letzte Aktualisierung**: Dezember 2025  
**Version**: 2.0-dev