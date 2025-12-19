# Hardware Dokumentation - Hayabusa ECU

## 🔧 ECU Hardware Design

### Übersicht
Die custom ECU basiert auf dem Speeduino Open-Source Design und wurde speziell für Suzuki Hayabusa Motorräder optimiert.

### Board Spezifikationen

#### Mikrocontroller Optionen
- **Arduino Mega 2560** (Standard)
  - 16 MHz ATmega2560
  - 256KB Flash, 8KB SRAM
  - 54 Digital I/O Pins
  
- **Teensy 4.1** (Performance Option)
  - 600 MHz ARM Cortex-M7
  - 8MB Flash, 1MB RAM
  - USB Host, Ethernet, CAN

#### Key Features
- **Automotive Grade Komponenten**
- **CAN Bus Interface** für moderne Diagnose
- **8x Injector Outputs** mit flyback protection
- **8x Ignition Outputs** mit IGBTs
- **Multiple Sensor Inputs**
- **SD Card Datenlogger**
- **USB Programming Interface**

### Eingänge (Sensoren)

| Pin | Signal | Typ | Beschreibung |
|-----|--------|-----|--------------|
| A0  | TPS    | 0-5V | Throttle Position Sensor |
| A1  | CLT    | NTC  | Coolant Temperature |
| A2  | IAT    | NTC  | Intake Air Temperature |
| A3  | MAP    | 0-5V | Manifold Absolute Pressure |
| A4  | O2     | 0-1V | Lambda Sensor |
| A5  | BAT    | 0-20V | Battery Voltage |
| D2  | RPM1   | Digital | Crank Position Sensor |
| D3  | RPM2   | Digital | Cam Position Sensor |

### Ausgänge (Aktuatoren)

| Pin | Signal | Typ | Beschreibung |
|-----|--------|-----|--------------|
| D6  | INJ1   | Low-side | Injector Zylinder 1 |
| D7  | INJ2   | Low-side | Injector Zylinder 2 |
| D8  | INJ3   | Low-side | Injector Zylinder 3 |
| D9  | INJ4   | Low-side | Injector Zylinder 4 |
| D10 | IGN1   | Low-side | Ignition Coil 1 |
| D11 | IGN2   | Low-side | Ignition Coil 2 |
| D12 | IGN3   | Low-side | Ignition Coil 3 |
| D13 | IGN4   | Low-side | Ignition Coil 4 |

### PCB Design Details

#### Schichten
- **4-Layer PCB**
- **Layer 1**: Component placement & signals
- **Layer 2**: Ground plane
- **Layer 3**: Power plane (+5V, +12V)
- **Layer 4**: Additional routing

#### Besonderheiten
- **EMI Shielding** für sensible Analog-Eingänge
- **Flyback Protection** für alle induktiven Lasten
- **Automotive Connectors** (wasserdicht)
- **Status LEDs** für alle kritischen Signale

### Mechanische Spezifikationen

#### Abmessungen
- **PCB**: 100mm x 80mm
- **Gehäuse**: Automotive-grade Aluminium
- **Steckverbinder**: Delphi/TE Connectivity

#### Umgebungsbedingungen
- **Betriebstemperatur**: -40°C bis +85°C
- **Luftfeuchtigkeit**: bis 95% (nicht kondensierend)
- **Vibration**: 20G bei 10-2000Hz
- **IP Rating**: IP67 (mit Gehäuse)

## 🏭 Mechanische Komponenten

### Airbox System

#### Design Features
- **Integrierte Kühlung** mit Alphacool Radiator
- **Ram-Air Optimierung** für hohe Geschwindigkeiten
- **Filteroptimierung** für Performance und Haltbarkeit

#### Materialien
- **Hauptkörper**: 6061 Aluminium
- **Dichtungen**: Viton (temperaturbeständig)
- **Filter**: K&N Performance Filter

#### CAD Dateien
```
Hardware/Airbox/
├── airbox.stp          # Haupt-Assembly
├── aircooler/
│   ├── radiator.stp    # Kühlsystem
│   └── *.pdf          # Specs
└── *.jpg              # Referenzbilder
```

### Ram-Air Seal System

#### Zweck
Optimierung der Luftzufuhr bei hohen Geschwindigkeiten durch präzise Abdichtung des Ram-Air Systems.

#### Komponenten
- **Primärdichtung**: Hauptabdichtung zur Airbox
- **Sekundärdichtung**: Feinabstimmung des Luftstroms
- **Befestigungselemente**: Edelstahl Hardware

#### Installation
```
1. Original Airbox entfernen
2. Oberflächen reinigen und prüfen
3. Neue Dichtungen mit Dichtpaste installieren
4. Airbox-Assembly montieren
5. Funktionstest durchführen
```

### Wireless Charging Case

#### Features
- **Qi-Standard kompatibel**
- **Wasserdicht** (IPX7)
- **Vibrationsresistent**
- **Integration** in Hayabusa Cockpit

#### Spezifikationen
- **Input**: 12V DC (Motorrad Bordnetz)
- **Output**: 5V/2A Qi Wireless
- **Effizienz**: >85%
- **Temperaturschutz**: Aktive Überwachung

## 🔌 Steckverbindungen

### Haupt-Harness (48-pin)

#### Power & Ground
| Pin | Signal | Farbe | Beschreibung |
|-----|--------|-------|--------------|
| 1   | +12V   | Rot   | Haupt-Versorgung |
| 2   | +5V    | Orange| Sensor-Versorgung |
| 3   | GND    | Schwarz| Ground |
| 4   | AGND   | Braun | Analog Ground |

#### Sensoren
| Pin | Signal | Farbe | Beschreibung |
|-----|--------|-------|--------------|
| 5   | TPS    | Blau  | Throttle Position |
| 6   | MAP    | Grün  | Manifold Pressure |
| 7   | CLT    | Gelb  | Coolant Temp |
| 8   | IAT    | Weiß  | Intake Air Temp |

#### Aktuatoren
| Pin | Signal | Farbe | Beschreibung |
|-----|--------|-------|--------------|
| 9-12| INJ1-4 | Violett| Injektoren |
| 13-16| IGN1-4| Pink  | Zündspulen |

### CAN Bus Connector

#### Pinout
| Pin | Signal | Beschreibung |
|-----|--------|--------------|
| 1   | CAN_H  | CAN High |
| 2   | CAN_L  | CAN Low |
| 3   | +12V   | Power |
| 4   | GND    | Ground |

## 🛠️ Assembly Instructions

### PCB Assembly

#### Komponenten Bestückung
1. **SMD Komponenten** zuerst (Reflow Oven)
2. **Through-hole** Komponenten
3. **Steckverbinder** zuletzt
4. **Funktionstest** vor Einbau

#### Test Procedure
```bash
# Basic functionality test
1. Power-on test (LED indicators)
2. Sensor input verification
3. Output driver test
4. CAN Bus communication test
5. Programming interface test
```

### Gehäuse Assembly

#### Schritte
1. **PCB** in Gehäuse einsetzen
2. **Dichtungen** prüfen und montieren
3. **Steckverbinder** installieren
4. **Abschluss-Test** durchführen

#### Drehmomente
- **PCB Befestigung**: 0.8 Nm
- **Gehäuse**: 2.5 Nm
- **Steckverbinder**: 1.2 Nm

## 🧪 Testing & Validation

### Electrical Tests

#### Pre-Assembly
- **Component verification** (alle Bauteile)
- **PCB continuity test**
- **Insulation resistance test**

#### Post-Assembly
- **Power-on sequence test**
- **Functional verification**
- **EMC compliance test**
- **Automotive stress test**

### Environmental Tests

#### Temperature Cycling
- **-40°C bis +85°C**
- **100 Zyklen minimum**
- **Funktionstest** bei Extremtemperaturen

#### Vibration Testing
- **Automotive standard** (ISO 16750)
- **20G bei 10-2000Hz**
- **2 Millionen Zyklen**

## 📋 Bill of Materials (BOM)

### Hauptkomponenten

| Komponente | Hersteller | Part Number | Menge | Kosten |
|------------|------------|-------------|-------|--------|
| Mikrocontroller | Arduino | Mega 2560 | 1 | 25€ |
| MOSFET Driver | MC33810 | MC33810AE | 2 | 15€ |
| CAN Controller | MCP2515 | MCP2515T | 1 | 3€ |
| Steckverbinder | TE Conn | 1-1123038-2 | 1 | 45€ |

### Passive Komponenten

| Typ | Wert | Package | Menge | Kosten |
|-----|------|---------|-------|--------|
| Widerstand | 10kΩ | 0805 | 20 | 2€ |
| Kondensator | 100nF | 0805 | 15 | 3€ |
| Spule | 10µH | 1206 | 8 | 5€ |

**Gesamt BOM Kosten**: ~150€ (Prototyp)
**Production Costs** (100+ Stück): ~75€

---

**Letzte Aktualisierung**: Dezember 2025  
**Version**: 2.0  
**Status**: ✅ Production Ready