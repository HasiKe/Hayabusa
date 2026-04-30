# Hardware-Dokumentation

## ECU Hardware Design

### Übersicht

Die ECU basiert auf dem **Speeduino Dropbear v2** Board mit Teensy 4.1 Mikrocontroller, optimiert für Suzuki Hayabusa Motorräder.

### Board-Spezifikationen

#### Dropbear v2 / Teensy 4.1

| Parameter | Wert |
|-----------|------|
| CPU | 600 MHz ARM Cortex-M7 |
| Flash | 8 MB |
| RAM | 1 MB |
| I/O | USB Host, Ethernet, Native CAN |

#### Features

- Automotive-grade Komponenten
- Native CAN Bus (kein externer Controller nötig)
- 4x Injector-Ausgänge mit Flyback-Protection
- 4x Ignition-Ausgänge mit IGBTs
- Klopfsensor-Eingang (geplant)
- SD-Card Datenlogger
- USB Programmier-Interface

### Pinbelegung

#### Sensor-Eingänge

| Pin | Signal | Typ | Beschreibung |
|-----|--------|-----|--------------|
| A0 | TPS | 0-5V | Throttle Position Sensor |
| A1 | CLT | NTC | Kühlmitteltemperatur |
| A2 | IAT | NTC | Ansauglufttemperatur |
| A3 | MAP | 0-5V | Saugrohrdruck |
| A4 | O2 | 0-1V | Lambda-Sonde |
| A5 | BAT | 0-20V | Batteriespannung |
| A6 | KNOCK | Piezo | Klopfsensor (geplant) |
| D2 | RPM1 | Digital | Kurbelwellensensor |
| D3 | RPM2 | Digital | Nockenwellensensor |

#### Aktuator-Ausgänge

| Pin | Signal | Typ | Beschreibung |
|-----|--------|-----|--------------|
| D6-D9 | INJ1-4 | Low-Side | Einspritzdüsen Zylinder 1-4 |
| D10-D13 | IGN1-4 | Low-Side | Zündspulen 1-4 |

### Klopfsensor (geplant)

#### Spezifikationen

| Parameter | Wert |
|-----------|------|
| Typ | Piezoelektrisch (Bosch-kompatibel) |
| Frequenzbereich | 5-15 kHz |
| Resonanzfrequenz | 6-8 kHz (Hayabusa-typisch) |
| Montage | Motorblock, zwischen Zylinder 2 und 3 |
| Anschluss | Analogeingang A6 |

#### Funktion

- Erkennung von Verbrennungsklopfen
- Automatische Zündzeitpunkt-Rücknahme bei Klopfen
- Schrittweise Wiederherstellung nach Klopfereignis
- Logging aller Klopfereignisse

### PCB-Design

#### Schichtaufbau

| Layer | Funktion |
|-------|----------|
| 1 | Bestückung und Signale |
| 2 | Massefläche |
| 3 | Versorgung (+5V, +12V) |
| 4 | Zusätzliche Leiterbahnen |

#### Design-Merkmale

- EMI-Abschirmung für Analog-Eingänge
- Flyback-Protection für induktive Lasten
- Automotive-Steckverbinder (wasserdicht)
- Status-LEDs für kritische Signale

### Mechanische Spezifikationen

| Parameter | Wert |
|-----------|------|
| PCB-Abmessungen | 100 x 80 mm |
| Gehäuse | Aluminium, Automotive-grade |
| Steckverbinder | Delphi/TE Connectivity |
| Betriebstemperatur | -40°C bis +85°C |
| Luftfeuchtigkeit | bis 95% (nicht kondensierend) |
| Vibration | 20G bei 10-2000 Hz |
| Schutzart | IP67 (mit Gehäuse) |

### Haupt-Steckverbinder (48-Pin)

#### Stromversorgung

| Pin | Signal | Farbe | Beschreibung |
|-----|--------|-------|--------------|
| 1 | +12V | Rot | Hauptversorgung |
| 2 | +5V | Orange | Sensorversorgung |
| 3 | GND | Schwarz | Masse |
| 4 | AGND | Braun | Analog-Masse |

#### Sensoren

| Pin | Signal | Farbe | Beschreibung |
|-----|--------|-------|--------------|
| 5 | TPS | Blau | Drosselklappenstellung |
| 6 | MAP | Grün | Saugrohrdruck |
| 7 | CLT | Gelb | Kühlmitteltemperatur |
| 8 | IAT | Weiß | Ansauglufttemperatur |
| 9 | KNOCK | Grau | Klopfsensor (geplant) |

#### Aktuatoren

| Pin | Signal | Farbe | Beschreibung |
|-----|--------|-------|--------------|
| 10-13 | INJ1-4 | Violett | Einspritzdüsen |
| 14-17 | IGN1-4 | Pink | Zündspulen |

### CAN Bus Steckverbinder

| Pin | Signal | Beschreibung |
|-----|--------|--------------|
| 1 | CAN_H | CAN High |
| 2 | CAN_L | CAN Low |
| 3 | +12V | Stromversorgung |
| 4 | GND | Masse |

## Bestückung

### Hauptkomponenten

| Komponente | Hersteller | Teilenummer | Anzahl | Kosten |
|------------|------------|-------------|--------|--------|
| Dropbear v2 Board | Speeduino | Dropbear v2 | 1 | 150€ |
| Teensy 4.1 | PJRC | Teensy 4.1 | 1 | 35€ |
| Steckverbinder | TE Conn | 1-1123038-2 | 1 | 45€ |
| Klopfsensor | Bosch | 0 261 231 173 | 1 | 25€ |

### Passive Komponenten

| Typ | Wert | Bauform | Anzahl | Kosten |
|-----|------|---------|--------|--------|
| Widerstand | 10 kΩ | 0805 | 20 | 2€ |
| Kondensator | 100 nF | 0805 | 15 | 3€ |
| Spule | 10 µH | 1206 | 8 | 5€ |

**Gesamtkosten BOM**: ca. 280€

## Test und Validierung

### Elektrische Tests

- Durchgangsprüfung
- Isolationswiderstand
- Power-On-Sequenz
- Funktionsvalidierung
- EMV-Konformität

### Umgebungstests

- Temperaturzyklus: -40°C bis +85°C, 100 Zyklen
- Vibration: ISO 16750, 20G bei 10-2000 Hz

## Montagehinweise

### PCB-Bestückung

1. SMD-Komponenten (Reflow-Ofen)
2. Through-Hole Komponenten
3. Teensy 4.1 aufstecken
4. Steckverbinder
5. Funktionstest

### Drehmomente

| Verbindung | Drehmoment |
|------------|------------|
| PCB-Befestigung | 0,8 Nm |
| Gehäuse | 2,5 Nm |
| Steckverbinder | 1,2 Nm |
| Klopfsensor | 20 Nm |

---

**Version**: 2.0
**Stand**: April 2026
