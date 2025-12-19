# Installation Guide - Hayabusa ECU

## 🛠️ Installationsanleitung

### ⚠️ Wichtige Sicherheitshinweise

**WARNUNG**: Die Installation einer Aftermarket-ECU erfordert umfangreiche Kenntnisse in Elektronik und Motorentechnik. Unsachgemäße Installation kann zu schweren Motor- oder Fahrzeugschäden führen.

**Vor der Installation**:
- Vollständige Sicherung der Original-ECU und aller Kalibrierungen
- Werkstatthandbuch für spezifisches Hayabusa Modelljahr verfügbar
- Professionelle Diagnose-Ausrüstung vorhanden
- Erfahrung mit Hochspannungs-Zündsystemen

### 📋 Benötigte Werkzeuge

#### Spezialwerkzeug
- **Multimeter** (True RMS, min. 10MΩ Eingangswiderstand)
- **Oszilloskop** (2-Kanal, min. 100MHz)
- **CAN Bus Tester** (optional)
- **Drehmomentschlüssel** (0.5-25 Nm)

#### Standard Werkzeug
- **Steckschlüsselsatz** (8-17mm)
- **Schraubendreher** (Phillips, Schlitz, Torx)
- **Abisolierzange** mit Crimper
- **Lötstation** (temperaturregelt)
- **Heißluftfön** für Schrumpfschläuche

#### Verbrauchsmaterial
- **Lötzinn** (60/40, 0.6mm)
- **Schrumpfschläuche** (verschiedene Größen)
- **Kabelbinder**
- **Isolierband**
- **Kontaktspray**
- **Dielektrisches Fett**

### 🔌 ECU Installation

#### Schritt 1: Vorbereitung

##### Original-ECU auslesen
```bash
# TunerStudio mit Original-ECU verbinden
# Vollständigen Read der Original-Kalibrierung
File → Read From ECU → Save as "Original_Backup.msq"

# Flash-Backup (falls verfügbar)
Tools → Flash Backup → "Original_Flash.hex"
```

##### Fahrzeug vorbereiten
1. **Motor abkühlen** lassen (min. 30min)
2. **Batterie abklemmen** (Masse zuerst)
3. **Kraftstoffdruck** ablassen
4. **Zündung aus**, Schlüssel abziehen
5. **Arbeitsplatz** gut beleuchten und sauber

#### Schritt 2: Original-ECU entfernen

##### Zugang zur ECU
```
Hayabusa Gen 1 (1999-2007):
- ECU unter Sitz, rechte Seite
- Sitzbank entfernen
- Seitenverkleidung lösen

Hayabusa Gen 2 (2008-2020):  
- ECU unter Tank, zentral
- Tank anheben (nicht entfernen)
- Luftfilterkasten teilweise demontieren

Hayabusa Gen 3 (2021+):
- ECU hinter linker Seitenverkleidung  
- Verkleidung komplett entfernen
- CAN Bus Stecker beachten
```

##### Stecker-Identifikation
```
Gen 1: 3x Stecker
- A: 32-pin Haupt-Harness (grau)
- B: 16-pin Sensor-Harness (schwarz) 
- C: 8-pin Diagnose/CAN (blau)

Gen 2: 2x Stecker  
- A: 48-pin Haupt-Harness (grau/schwarz)
- B: 12-pin CAN/Diagnose (blau)

Gen 3: 1x Stecker
- A: 64-pin Gesamt-Harness (schwarz)
```

##### Entfernung
```bash
# Dokumentation vor Entfernung
1. Fotos aller Steckverbindungen
2. Etikettierung der Kabel
3. Messung aller Spannungen (Zündung AN)
4. Widerstandsmessung aller Sensoren

# Entfernung
1. Stecker vorsichtig lösen (Verriegelung beachten)
2. ECU-Befestigung lösen (meist 3x 8mm Schrauben)
3. ECU vorsichtig entnehmen
```

#### Schritt 3: Speeduino ECU installieren

##### Mechanische Installation
```bash
# ECU-Montage
1. Original-Befestigungspunkte verwenden
2. Drehmoment: 8 Nm (M6 Schrauben)
3. Vibrationsdämpfer prüfen
4. Gehäuse-Erdung sicherstellen

# Kabelführung
1. Original-Kabelwege beibehalten
2. Abstand zu heißen Oberflächen >5cm
3. Keine scharfen Kanten
4. Bewegliche Teile vermeiden
```

##### Elektrische Verbindung

###### Pinout Mapping (Gen 2 Beispiel)
```
Original ECU Pin → Speeduino Pin

Power & Ground:
Pin 1  (+12V Battery)    → VIN
Pin 2  (+12V Switched)   → VIN_SW  
Pin 3  (Ground)          → GND
Pin 4  (Analog Ground)   → AGND

Sensoren:
Pin 5  (TPS Signal)      → A0 (TPS)
Pin 6  (MAP Signal)      → A1 (MAP)
Pin 7  (CLT Signal)      → A2 (CLT)
Pin 8  (IAT Signal)      → A3 (IAT)
Pin 9  (O2 Signal)       → A4 (O2)
Pin 10 (Battery V)       → A5 (BAT)

Trigger:
Pin 15 (Crank Signal)    → D2 (RPM1)
Pin 16 (Cam Signal)      → D3 (RPM2)

Injektoren:
Pin 20 (Injector 1)      → D6 (INJ1)
Pin 21 (Injector 2)      → D7 (INJ2)  
Pin 22 (Injector 3)      → D8 (INJ3)
Pin 23 (Injector 4)      → D9 (INJ4)

Zündung:
Pin 25 (Ignition 1)      → D10 (IGN1)
Pin 26 (Ignition 2)      → D11 (IGN2)
Pin 27 (Ignition 3)      → D12 (IGN3)
Pin 28 (Ignition 4)      → D13 (IGN4)

CAN Bus (optional):
Pin 45 (CAN High)        → CAN_H
Pin 46 (CAN Low)         → CAN_L
```

#### Schritt 4: Verkabelung

##### Adapter-Harness (Empfohlen)
```bash
# Professioneller Ansatz
1. Original-Stecker am Adapter verwenden
2. Neue Verkabelung zu Speeduino
3. Individuelle Adern mit Original-Farben
4. Vollständige Isolierung und Schrumpfschutz

# Qualitätskontrolle
1. Durchgangsprüfung jeder Verbindung
2. Isolationsmessung zwischen den Adern
3. Mechanische Prüfung aller Stecker
4. Dokumentation der finalen Pinbelegung
```

##### Direkte Verdrahtung (Fortgeschritten)
```bash
# NUR für Experten
1. Original-Stecker modifizieren
2. Pin-Extraktion mit Spezialwerkzeug
3. Neue Pins crimpen und einsetzen
4. Stecker-Programmierung anpassen (Gen 3)

# ACHTUNG: Irreversibel!
```

#### Schritt 5: Erste Inbetriebnahme

##### System-Check vor Motorstart
```bash
# Spannungsprüfung
1. Batteriespannung: 12.0-14.8V
2. 5V Sensor Supply: 4.95-5.05V  
3. Analog Ground: <0.05V
4. ECU Ground: <0.1Ω zu Battery-Minus

# Sensor-Test
1. TPS: 0.5-4.5V über Bereich
2. MAP: 1.0V (Vacuum) bis 4.5V (Boost)
3. CLT: Variable je Temperatur
4. IAT: Variable je Temperatur
```

##### Trigger-Signal Validierung
```bash
# Oszilloskop an Crank Signal
1. Motor per Hand drehen
2. Signal sollte saubere Rechteckwelle zeigen
3. Amplitude: 0-5V oder 0-12V
4. 36 Pulse pro Umdrehung mit 1 fehlenden Zahn

# Cam Signal (falls vorhanden)
1. 1 Puls pro 2 Kurbelwellenumdrehungen
2. Synchronisation zu Crank prüfen
```

### ⚙️ Software-Konfiguration

#### Base Tune laden
```bash
# TunerStudio Verbindung
1. COM Port settings: 115200 baud, 8N1
2. Project → Open → tune/Busa/CurrentTune.msq
3. Communications → Connect ECU

# Initial Settings
1. Engine → Basic Settings
   - Cylinders: 4
   - Engine Type: 4-stroke
   - Injection Mode: Sequential
   - Ignition Mode: Wasted Spark

2. Engine → Trigger Setup  
   - Pattern: Missing Tooth
   - Primary Teeth: 36
   - Missing Teeth: 1
```

#### Sensor-Kalibrierung
```bash
# MAP Sensor (Hayabusa Standard: MPX4250AP)
Sensor Type: GM 1 Bar
Min Value: 10 kPa  
Max Value: 250 kPa
Voltage @ Min: 0.2V
Voltage @ Max: 4.8V

# TPS Kalibrierung
1. Engine → Sensor Calibration → TPS
2. Throttle geschlossen: Learn Closed
3. Throttle voll offen: Learn WOT
4. Prüfung: 0-100% über Bereich

# Temperature Sensors
CLT/IAT Sensor: Standard NTC
Pull-up Resistor: 2.7kΩ
Bias Voltage: 5.0V
```

#### Fuel System Setup
```bash
# Injector Settings
Injector Size: 318 cc/min (Standard Hayabusa)
Number of Injectors: 4
Injection Mode: Sequential
Opening Time: 1.0ms

# Required Fuel Calculation
Engine Displacement: 1340cc
Target AFR: 13.5:1
Req Fuel = (Displacement × 6.49) ÷ (AFR × Injector Size)
Req Fuel = (1340 × 6.49) ÷ (13.5 × 318) = 2.03ms
```

### 🧪 Funktionstest

#### Statischer Test (Motor aus)
```bash
# Power-On Test
1. Zündung AN
2. Speeduino Status LEDs prüfen:
   - Power LED: AN (grün)
   - Activity LED: Blinkend (blau)
   - Error LED: AUS (rot)

# Sensor Reading Test  
3. TunerStudio → Gauges
4. Alle Sensor-Werte plausibel:
   - RPM: 0
   - MAP: ~100 kPa (atmospheric)
   - TPS: 0%
   - CLT: Ambient temp
   - IAT: Ambient temp
   - Battery: 12-13V
```

#### Cranking Test (Motor startet nicht)
```bash
# Fuel System deaktivieren
1. Fuel Pump Relay entfernen ODER
2. Injector Fuse entfernen ODER  
3. Fuel Rail drucklos machen

# Crank Signal Test
1. Motor kurz ankurbeln (5-10 Sekunden)
2. RPM Signal in TunerStudio beobachten
3. Erwartung: Smooth RPM reading
4. Trigger Errors prüfen (sollten 0 sein)

# Ignition Test (VORSICHT!)
1. Zündkerzen entfernen
2. Zündkabel mit Funkenstrecke testen
3. Funke bei jedem 2. Crank-Impuls erwarten
4. Timing grob prüfen (TDC Markierung)
```

#### Erster Start (KRITISCH!)
```bash
# Vorbereitung
1. Feuerlöscher bereithalten
2. Notaus-Schalter installieren
3. Mechaniker vor Ort
4. Laptop mit TunerStudio verbunden

# Start-Prozedur
1. Fuel System wieder aktivieren
2. Cranking Pulsewidth: 6-10ms setzen
3. Kurz ankurbeln und RPM stabilisieren lassen
4. SOFORT TunerStudio Readings prüfen:
   - AFR: 12-15 (nicht lean!)
   - CLT: Steigend
   - MAP: Sinnvolle Werte
   - Engine Load: <50%

# Bei Problemen SOFORT stoppen!
```

### 🔍 Troubleshooting

#### Häufige Probleme

##### Motor startet nicht
```bash
Mögliche Ursachen:
1. Trigger Signal fehlt oder falsch
   → Oscilloscope an RPM1/RPM2
   → Trigger Pattern überprüfen
   
2. Kein Fuel
   → Fuel Pump Relay prüfen
   → Injector Wiring prüfen
   → Required Fuel zu niedrig
   
3. Kein Spark  
   → Ignition Output Test
   → Coil Primary Resistance
   → Timing zu weit retarded
```

##### Motor läuft schlecht
```bash
Symptome → Mögliche Ursachen:

Rough Idle:
- TPS nicht kalibriert
- MAP Sensor defekt
- Vacuum Lecks
- Idle Fuel/Timing falsch

Keine Power:
- Fuel Map zu lean
- Ignition Timing zu retarded
- MAP Reading falsch
- Injector Size falsch konfiguriert

Backfire/Knocking:
- Timing zu advanced  
- Fuel Map zu lean
- Knock Sensor nicht connected
- Poor fuel quality
```

##### Sensor-Probleme
```bash
TPS Issues:
- Voltage nicht 0-5V → Wiring oder defekter Sensor
- Noisy Signal → EMI, schlechte Erdung
- Non-linear → Falsche Kalibrierung

MAP Issues:  
- Reading 0 oder max → Vacuum line oder Sensor defekt
- Doesn't change → Vacuum line blocked
- Noisy → Vibration oder EMI

Temperature Issues:
- Reading -40°C → Open circuit (Kabel gebrochen)
- Reading 150°C → Short circuit (Kabel Kurzschluss)
- Doesn't change → Defekter Sensor oder Pull-up
```

#### Diagnose-Tools

##### TunerStudio Error Log
```bash
Tools → Error Log
Häufige Errors:
- Trigger Sync Lost → Trigger Wiring/Configuration
- MAP out of range → MAP Sensor/Vacuum
- TPS out of range → TPS Kalibrierung  
- Temperature Sensor Error → Temp Sensor Wiring
```

##### Real-time Data Analysis
```bash
Tools → Realtime Display
Kritische Parameter überwachen:
- Engine Load: <80% normal operation
- AFR: 12.5-15.5 je nach Load
- Ignition Advance: 10-35° je nach RPM/Load
- Injection Pulse Width: 1-25ms typical
```

### 📚 Referenz-Daten

#### Hayabusa Sensor-Spezifikationen

##### MAP Sensor (Standard)
```
Part Number: MPX4250AP
Type: Absolute Pressure
Range: 20-250 kPa
Output: 0.2-4.8V linear
Supply: 5V ±0.25V
Current: <10mA
```

##### TPS (Throttle Position Sensor)
```
Type: Potentiometer
Resistance: 5kΩ
Range: 0-90° (mechanical)
Output: 0.5-4.5V linear
Linearity: ±2%
```

##### Temperature Sensors (CLT/IAT)
```
Type: NTC Thermistor
Resistance @ 20°C: 2.3kΩ ±3%
β (Beta): 3435K
Range: -40°C to +130°C
Pull-up: 2.7kΩ to 5V
```

#### Hayabusa Engine Specifications
```
Displacement: 1340cc (Gen 2+), 1299cc (Gen 1)
Compression Ratio: 12.5:1
Max RPM: 11,000 (stock)
Firing Order: 1-2-4-3
Injection: Sequential Multi-point
Ignition: Wasted Spark (2 coils)
```

### 🛡️ Sicherheitsmaßnahmen

#### Während Installation
- **Batterie abgeklemmt** während Verkabelung
- **Keine offenen Flammen** (Kraftstoffdämpfe)
- **ESD-Schutz** für elektronische Komponenten
- **Doppelte Kontrolle** aller Verbindungen

#### Nach Installation  
- **Vollständiger System-Check** vor erstem Start
- **Notaus-Möglichkeit** während Tests
- **Feuerlöscher** griffbereit
- **Ersatzteile** für Original-Zustand verfügbar

#### Im Straßenverkehr
- **Lokale Gesetze** beachten (TÜV/ABE)
- **Versicherung** über Modifikationen informieren
- **Backup-Tune** für Notfälle
- **Diagnose-Laptop** für längere Fahrten

---

**⚠️ HAFTUNGSAUSSCHLUSS**  
Diese Anleitung dient nur als Referenz. Jede Modifikation erfolgt auf eigene Verantwortung. Bei Unsicherheiten professionelle Werkstatt konsultieren.

**Letzte Aktualisierung**: Dezember 2025  
**Version**: 2.0  
**Status**: ✅ Production Ready