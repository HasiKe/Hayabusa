# Installationsanleitung

## Sicherheitshinweise

**Warnung**: Die Installation einer Aftermarket-ECU erfordert umfangreiche Kenntnisse in Elektronik und Motorentechnik. Unsachgemäße Installation kann zu schweren Motor- oder Fahrzeugschäden führen.

**Vor der Installation:**
- Vollständige Sicherung der Original-ECU
- Werkstatthandbuch für das spezifische Modelljahr verfügbar
- Professionelle Diagnose-Ausrüstung vorhanden
- Erfahrung mit Hochspannungs-Zündsystemen

## Werkzeuge

### Spezialwerkzeuge
- Multimeter (True RMS, min. 10 MΩ Eingangswiderstand)
- Oszilloskop (2-Kanal, min. 100 MHz)
- Drehmomentschlüssel (0,5-25 Nm)
- CAN Bus Tester (optional)

### Standardwerkzeuge
- Steckschlüsselsatz (8-17 mm)
- Schraubendreher (Phillips, Schlitz, Torx)
- Abisolierzange mit Crimper
- Lötstation (temperaturgeregelt)

### Verbrauchsmaterial
- Lötzinn (60/40, 0,6 mm)
- Schrumpfschläuche
- Kabelbinder
- Dielektrisches Fett

## ECU Installation

### Schritt 1: Vorbereitung

#### Original-ECU auslesen
```
TunerStudio → File → Read From ECU → Save as "Original_Backup.msq"
```

#### Fahrzeug vorbereiten
1. Motor abkühlen lassen (min. 30 min)
2. Batterie abklemmen (Masse zuerst)
3. Kraftstoffdruck ablassen
4. Zündung aus, Schlüssel abziehen

### Schritt 2: Original-ECU entfernen

#### ECU-Position nach Generation

| Generation | Position | Zugang |
|------------|----------|--------|
| Gen 1 (1999-2007) | Unter Sitz, rechte Seite | Sitzbank und Seitenverkleidung entfernen |
| Gen 2 (2008-2020) | Unter Tank, zentral | Tank anheben, Luftfilterkasten teildemontieren |
| Gen 3 (2021+) | Hinter linker Verkleidung | Verkleidung komplett entfernen |

#### Steckverbinder

| Generation | Stecker |
|------------|---------|
| Gen 1 | 3x: 32-Pin Haupt (grau), 16-Pin Sensor (schwarz), 8-Pin CAN (blau) |
| Gen 2 | 2x: 48-Pin Haupt (grau/schwarz), 12-Pin CAN (blau) |
| Gen 3 | 1x: 64-Pin Gesamt (schwarz) |

### Schritt 3: Dropbear v2 ECU installieren

#### Mechanische Installation
1. Original-Befestigungspunkte verwenden
2. Drehmoment: 8 Nm (M6 Schrauben)
3. Vibrationsdämpfer prüfen
4. Gehäuse-Erdung sicherstellen

#### Kabelführung
- Original-Kabelwege beibehalten
- Abstand zu heißen Oberflächen > 5 cm
- Keine scharfen Kanten
- Bewegliche Teile vermeiden

### Schritt 4: Pinout-Mapping (Gen 1)

#### Stromversorgung
| Original Pin | Dropbear v2 |
|--------------|-------------|
| 1 (+12V Battery) | VIN |
| 2 (+12V Switched) | VIN_SW |
| 3 (Ground) | GND |
| 4 (Analog Ground) | AGND |

#### Sensoren
| Original Pin | Dropbear v2 |
|--------------|-------------|
| 5 (TPS Signal) | TPS |
| 6 (MAP Signal) | MAP |
| 7 (CLT Signal) | CLT |
| 8 (IAT Signal) | IAT |
| 9 (O2 Signal) | O2 |
| 10 (Battery V) | VBAT |

#### Trigger
| Original Pin | Dropbear v2 |
|--------------|-------------|
| 15 (Crank Signal) | CRANK |
| 16 (Cam Signal) | CAM |

#### Einspritzung
| Original Pin | Dropbear v2 |
|--------------|-------------|
| 20-23 (Injector 1-4) | INJ1-4 |

#### Zündung
| Original Pin | Dropbear v2 |
|--------------|-------------|
| 25-28 (Ignition 1-4) | IGN1-4 |

#### CAN Bus (Native auf Teensy 4.1)
| Original Pin | Dropbear v2 |
|--------------|-------------|
| 45 (CAN High) | CAN_H |
| 46 (CAN Low) | CAN_L |

#### Klopfsensor (geplant)
| Signal | Dropbear v2 |
|--------|-------------|
| Knock+ | KNOCK |
| Knock- | AGND |

## Software-Konfiguration

### Base Tune laden
```
TunerStudio → Project → Open → tune/Busa/CurrentTune.msq
Communications → Connect ECU
```

### Grundeinstellungen
| Parameter | Wert |
|-----------|------|
| Board | Dropbear v2 |
| Zylinder | 4 |
| Motortyp | 4-Takt |
| Einspritzung | Sequential |
| Zündung | Wasted Spark |
| Trigger Pattern | Missing Tooth 36-1 |

### Sensor-Kalibrierung

#### MAP Sensor (MPX4250AP)
| Parameter | Wert |
|-----------|------|
| Sensortyp | GM 1 Bar |
| Minimum | 10 kPa |
| Maximum | 250 kPa |
| Spannung @ Min | 0,2 V |
| Spannung @ Max | 4,8 V |

#### TPS Kalibrierung
1. Engine → Sensor Calibration → TPS
2. Drosselklappe geschlossen: Learn Closed
3. Drosselklappe voll offen: Learn WOT
4. Prüfung: 0-100% über gesamten Bereich

#### Temperatursensoren
| Parameter | Wert |
|-----------|------|
| CLT/IAT Sensor | Standard NTC |
| Pull-up Widerstand | 2,7 kΩ |
| Bias-Spannung | 5,0 V |

#### Klopfsensor (geplant)
| Parameter | Wert |
|-----------|------|
| Aktiviert | Ja |
| Schwellwert | 50 |
| Frequenz | 6-8 kHz |
| Retard pro Klopfen | 3° |
| Recovery | 0,5°/s |

### Kraftstoffsystem
| Parameter | Wert |
|-----------|------|
| Injektorgröße | 318 cc/min (Standard) |
| Anzahl Injektoren | 4 |
| Einspritzung | Sequential |
| Öffnungszeit | 1,0 ms |
| Required Fuel | 2,0 ms (berechnet) |

## Inbetriebnahme

### Statischer Test (Motor aus)

#### Spannungsprüfung
| Parameter | Sollwert |
|-----------|----------|
| Batteriespannung | 12,0-14,8 V |
| 5V Sensor Supply | 4,95-5,05 V |
| Analog Ground | < 0,05 V |
| ECU Ground | < 0,1 Ω zu Batterie-Minus |

#### Sensor-Werte prüfen
| Sensor | Erwartung |
|--------|-----------|
| RPM | 0 |
| MAP | ca. 100 kPa (atmosphärisch) |
| TPS | 0% |
| CLT | Umgebungstemperatur |
| IAT | Umgebungstemperatur |
| Batterie | 12-13 V |

### Cranking-Test (Motor startet nicht)

1. Kraftstoffsystem deaktivieren (Relais oder Sicherung entfernen)
2. Motor kurz ankurbeln (5-10 Sekunden)
3. RPM-Signal in TunerStudio beobachten
4. Trigger Errors prüfen (sollen 0 sein)

### Erster Start

**Vorbereitung:**
- Feuerlöscher bereithalten
- Notaus-Schalter installiert
- Laptop mit TunerStudio verbunden

**Prozedur:**
1. Kraftstoffsystem aktivieren
2. Cranking Pulsewidth: 6-10 ms
3. Motor starten und sofort prüfen:
   - AFR: 12-15 (nicht lean!)
   - CLT: steigend
   - MAP: sinnvolle Werte

**Bei Problemen sofort stoppen!**

## Troubleshooting

### Motor startet nicht

| Problem | Prüfung |
|---------|---------|
| Kein Trigger-Signal | Oszilloskop an CRANK/CAM, Pattern prüfen |
| Kein Kraftstoff | Fuel Pump Relais, Injector Wiring, Required Fuel |
| Kein Zündfunke | Ignition Output, Coil Widerstand, Timing |

### Motor läuft schlecht

| Symptom | Mögliche Ursache |
|---------|------------------|
| Unrunder Leerlauf | TPS nicht kalibriert, MAP Sensor defekt, Vacuum-Lecks |
| Keine Leistung | Fuel Map zu mager, Zündung zu spät, MAP falsch |
| Klopfen/Backfire | Timing zu früh, Gemisch zu mager |

### Sensor-Probleme

| Symptom | Ursache |
|---------|---------|
| -40°C Anzeige | Offener Stromkreis (Kabel gebrochen) |
| 150°C Anzeige | Kurzschluss |
| Wert ändert sich nicht | Defekter Sensor oder Pull-up |

## Referenzdaten

### Hayabusa Motor-Spezifikationen

| Parameter | Gen 1 | Gen 2+ |
|-----------|-------|--------|
| Hubraum | 1299 cc | 1340 cc |
| Verdichtung | 11:1 | 12,5:1 |
| Max. Drehzahl | 11.000 | 11.000 |
| Zündfolge | 1-2-4-3 | 1-2-4-3 |
| Einspritzung | Sequential | Sequential |
| Zündung | Wasted Spark | Wasted Spark |

### MAP Sensor (Standard)

| Parameter | Wert |
|-----------|------|
| Teilenummer | MPX4250AP |
| Typ | Absolutdruck |
| Bereich | 20-250 kPa |
| Ausgang | 0,2-4,8 V linear |
| Versorgung | 5 V ±0,25 V |

### Temperatursensoren (CLT/IAT)

| Parameter | Wert |
|-----------|------|
| Typ | NTC Thermistor |
| Widerstand @ 20°C | 2,3 kΩ ±3% |
| β (Beta) | 3435 K |
| Bereich | -40°C bis +130°C |

### Klopfsensor (geplant)

| Parameter | Wert |
|-----------|------|
| Typ | Piezoelektrisch |
| Kompatibel | Bosch 0 261 231 173 |
| Resonanz | 6-8 kHz |
| Montage | Motorblock, M8 Gewinde |
| Drehmoment | 20 Nm |

## Sicherheitsmaßnahmen

### Während Installation
- Batterie abgeklemmt während Verkabelung
- Keine offenen Flammen (Kraftstoffdämpfe)
- ESD-Schutz für elektronische Komponenten
- Doppelte Kontrolle aller Verbindungen

### Nach Installation
- Vollständiger Systemcheck vor erstem Start
- Notaus-Möglichkeit während Tests
- Feuerlöscher griffbereit
- Ersatzteile für Original-Zustand verfügbar

### Straßenverkehr
- Lokale Gesetze beachten (TÜV/ABE)
- Versicherung über Modifikationen informieren
- Backup-Tune für Notfälle
- Diagnose-Laptop für längere Fahrten

---

**Haftungsausschluss**: Diese Anleitung dient nur als Referenz. Jede Modifikation erfolgt auf eigene Verantwortung.

**Version**: 2.0
**Stand**: April 2026
