# Hardware-Dokumentation

Steuergerät **Gen1 Hayabusa ECU Rev 3.0** (Schaltplan und Layout in `hardware/ECU/`,
Fertigungsdaten in `hardware/ECU/output/pcbway/`, Stückliste in `hardware/ECU/bom/`).
Die Rev 1 auf Dropbear-Basis ist Geschichte; dieses Dokument beschreibt nur die Rev 3.

## Überblick

| Parameter | Wert |
|---|---|
| Rechenkern | Teensy 4.1 (NXP i.MX RT1062, 600 MHz), USB über J2 auf die Device-Pads |
| Platine | zweilagig, ca. 148 × 112 mm, drei M3-Befestigungen, Gehäuse in `hardware/ECU/case/` (Fusion 360, STL, Kühlkörper) |
| Stecker | J2 = TE 6437288-3, 60-polig, Belegung nach dem Serien-Steuergerät (`hardware/ECU/docs/Pinout.ods`, Blatt `Pinout_ori_ECU`) |
| Endstufen | MC33810 (SPI, GPGD-Modus) → 4 Low-Side-Injektortreiber, 4 Gate-Treiber für ISL9V5036-IGBTs |
| Kleinlasten | 3× ZXMS6006 Low-Side (Kraftstoffpumpe, Lüfter, Starter, Drehzahlmesser, FI-Lampe, Spare), 2× BTF3050TE High-Side (Ladedrucksteller, Lambdaheizung) |
| Leerlaufsteller | DRV8434A Schrittmotortreiber (Serienmotor hat keinen, Ausgang ungenutzt) |
| Kurbel/Nocke | MAX9926, zwei VR-Kanäle |
| Klopfen | TPIC8101 über SPI, Integratorausgang an A17 |
| Lambda | LMV324-Puffer 0–3,3 V, kein Breitband-Frontend (Innovate LC-2 extern) |
| Versorgung | LM74700 + SQM120N06 (Verpolschutz), TPS54360B (5 V Buck), LD1117S33 (3,3 V), TPS7B6950-Q1 (VDDA, Sensor-5 V an J2.48) |
| Watchdog | TPS3823, WDI von D3, RESET verriegelt über 74LVC1G00 mit D2 den MC33810-OUTEN |
| Speicher | W25Q32 SPI-Flash als Kennfeldspeicher (8184 Byte emuliertes EEPROM, 4 Kennfeldsätze) |
| Kommunikation | MCP2562 CAN (CAN1, 500 kbit/s) zum Sensor-Modul, Serial1 auf J1 |
| Sonstiges | ADXL343 bestückt, softwareseitig ungenutzt |

## Teensy-Belegung

Aus der Rev-3.0-Netzliste, identisch mit `speeduino/HAYABUSA_ECU_R3.md`.

| Teensy | Netz / Baustein | Firmware |
|---|---|---|
| D0 / D1 | J1 | Serial1 (sekundäre Schnittstelle) |
| D2 | 74LVC1G00 → MC33810 OUTEN | Ausgabefreigabe, Fuel- und Spark-Kill |
| D3 | TPS3823 WDI | Watchdog |
| D4 | J2.20 | Neutralschalter |
| D5 | IC3.1 → J2.9 | Kraftstoffpumpe |
| D6 | W25Q32 CS | Kennfeldspeicher |
| D7 | ADXL343 CS | ungenutzt |
| D8 | IC3.2 → J2.55 | Drehzahlmesser |
| D9 | DRV8434A nFAULT + BTF3050 Status | Treiberfehler, aktiv low |
| D10 | MC33810 CS | Injektor- und Zündtreiber |
| D11 / D12 / D13 | MOSI / MISO / SCLK | gemeinsamer SPI-Bus |
| D20 | MAX9926 COUT1 | Kurbelwelle |
| D21 | MAX9926 COUT2 | Nockenwelle |
| D22 / D23 | MCP2562 | CAN1 |
| D24 | U13 → J2.30 | Ladedrucksteller |
| D25 | U14 → J2.46 | Lambdaheizung (bei LC-2 offen lassen) |
| D26 | IC2.2 → J2.28 | Starter-Ausgang, frei für programmierbaren Ausgang |
| D27 | IC2.1 → J2.42 | FI-Lampe |
| D28 | IC4.2 → J2.47 | Spare-Ausgang |
| D29 | IC4.1 → J2.29 | Lüfter |
| D30 / D31 / D32 | DRV8434A STEP / DIR / ENABLE+nSLEEP | Schrittmotor |
| D33 | J2.19 | Kupplung: Launch-Eingang und Kennfeldwahl |
| D34 | LMV324-Komparator | Kippschalter |
| D35 | J2.60 | Spare-Digitaleingang, als VSS gemappt |
| D36 / D37 | TPIC8101 INT/HOLD / CS | Klopfsensor-IC |
| A0 / A1 / A2 | J2.58 / J2.52 / J2.49 | MAP / Baro / TPS |
| A3 | J2.38 über LMV324 | Lambda |
| A4 / A5 | J2.50 / J2.51 | IAT / CLT |
| A14 / A15 | J2.39 / 12V-PROT-Teiler | Flex / Batteriespannung |
| A16 | J2.57 | Gangsensor |
| A17 | TPIC8101 OUT | Klopfintegrator |

## Steckerbelegung J2

Die Nummern entsprechen dem Serien-Steuergerät, der Serienkabelbaum passt. Nur die
Pins mit Funktion in der Rev 3 sind gelistet.

| Pin | Serie | Rev 3 | Anmerkung |
|---|---|---|---|
| 1 | Spule Zyl. 1 | IGN1 (GD0, Q2) | Kanalzuordnung siehe unten |
| 2 | Spule Zyl. 2 | IGN2 (GD1, Q1) | |
| 3 | Spule Zyl. 3 | IGN4 (GD2, Q3) | Speeduino-Kanal 4 = vierter in der Zündfolge |
| 10 | Spule Zyl. 4 | IGN3 (GD3, Q4) | Speeduino-Kanal 3 = dritter in der Zündfolge |
| 7 | Düse Zyl. 1 | INJ1 (OUT0) | |
| 6 | Düse Zyl. 2 | INJ2 (OUT1) | |
| 5 | Düse Zyl. 3 | INJ4 (OUT2) | |
| 4 | Düse Zyl. 4 | INJ3 (OUT3) | |
| 8, 31, 32, 45 | 8: VC-Solenoid | Schrittmotor A1/A2/B1/B2 | ungenutzt |
| 9 | Kraftstoffpumpe | Low-Side D5 | |
| 17 | Zündung 12 V | 12V-PROT | Versorgung |
| 18, 26, 27, 35 | Masse | GND | |
| 19 | Starterrelais-Eingang | Kupplung (D33) | 12 V bei Starter, 0 V bei gezogener Kupplung; siehe Befund 1 |
| 20 | Neutral | D4 | 0 V in Neutral |
| 22 | Diagnose | DIAG-IN | nicht verbunden |
| 28 | Starterrelais | Starter-Ausgang D26 | |
| 29 | – | Lüfter D29 | |
| 30 | – | Ladedrucksteller D24 | |
| 36 / 43 | Kurbel − / + | MAX9926 Kanal 1 | VR |
| 37 / 44 | Nocke + / − | MAX9926 Kanal 2 | VR |
| 38 | – | Lambda 0–3,3 V | LC-2 Analogausgang 1 |
| 39 | – | Flex | 2,2 kΩ Pull-up, ungenutzt |
| 42 | Kraftstoff 12 V | FI-Lampe D27 | |
| 46 | – | Lambdaheizung D25 | offen lassen |
| 47 | – | Spare-Ausgang D28 | |
| 48 | Sensor 5 V | VDDA | TPS7B6950, Polyfuse 150 mA |
| 49 | TPS | A2 | |
| 50 | Ansauglufttemperatur | A4 | |
| 51 | Wassertemperatur | A5 | |
| 52 | Atmosphärendruck | A1 (Baro) | im Tune nicht genutzt |
| 53 | – | Spare-Analog | Beschaltung vorhanden, kein ADC-Pin (Befund 2) |
| 54 | Sensormasse | GNDA | |
| 55 | Drehzahlmesser | D8 | |
| 57 | Gangsensor | A16 | 1 kΩ Vorwiderstand, Schwellen in der Firmware |
| 58 | Saugrohrdruck | A0 (MAP) | Serien-IAP 18590-81A00 |
| 59 | Kippschalter | Komparator → D34 | |
| 60 | – | Spare-Digital D35 | |
| 14 / 15 | – | CAN H / L | Sensor-Modul, Cockpit |
| 16 / 24 | Diagnose | USB VBUS / USB GND | USB-Daten siehe Blatt Comms |

### Kanal- und Zylinderzuordnung

Speeduino feuert seine Kanäle in der Zündfolge (0°, 180°, 360°, 540°), der Stecker ist
nach Zylindernummer belegt, die Zündfolge ist 1-2-4-3. Die Firmware legt deshalb Kanal 3
auf Zylinder 4 und Kanal 4 auf Zylinder 3 (`getHayabusaR3Mapping()`); am Kabelbaum wird
nichts getauscht. Zylinder 1 liegt links auf der Generatorseite.

## Analoge Eingangsbeschaltung

| Eingang | Beschaltung | Folge für die Kalibrierung |
|---|---|---|
| MAP, Baro, TPS, Gangsensor | 470 Ω → 100 nF → Teiler 12 k/20 k (0,625) → 10 nF → BAV199 an 3V3/GND | ADC-Vollausschlag = 3,3 V / 0,625 = 5,28 V am Sensor. `mapMax` entsprechend rechnen (Serien-IAP: 10 / 142 kPa) |
| IAT, CLT | Pull-up 2,49 kΩ an **3V3** → 470 Ω → BAV199 | ratiometrisch zur ADC-Referenz, TunerStudio-Bias 2490 Ω exakt |
| Lambda | LMV324-Folger an 3,3 V | Sensor 0–3,3 V, LC-2 Ausgang entsprechend programmieren |
| Batterie | 47 k/10 k von 12V-PROT | Vollausschlag 18,8 V; Firmware skaliert für Board 57 |
| Flex | 2,2 kΩ Pull-up 3V3, 1 kΩ + 1 nF + BAV199 | Frequenzeingang |
| Neutral, Kupplung, Spare-Digital | 10 kΩ Pull-up 3V3, Teiler 12 k/20 k, 100 nF, BAV199 | siehe Befund 1 |
| Kippschalter | LMV324 als Komparator, Schwelle 1,2 V nach Teiler 0,5 | Polarität am Fahrzeug prüfen |

Kurbel und Nocke: MAX9926 datenblattkonform, differenziell bis zum IC, Serienwiderstände
vor den Teensy-Pins, Eingangsfilter 470 pF. Trigger-Flanke RISING.

## Klopfsensor

TPIC8101 am SPI, Konfiguration beim Start durch die Firmware: 4-MHz-Resonator, Kanal 1,
Bandpass Index 39 (6,37 kHz, erste Umfangsmode einer 81-mm-Bohrung), Verstärkung Index 14,
Integrator Index 18 (200 µs). Fenster öffnet mit dem Zündfunken, schließt aus dem
1-kHz-Dienst. Bosch 0 261 231 173 am Block zwischen Zylinder 2 und 3 geplant, noch nicht
verbaut. In TunerStudio Klopfmodus **Analog**, der Pin wird ignoriert.

## Befunde der Rev 3.0

Aus `speeduino/HAYABUSA_ECU_R3.md`, hardwareseitig noch offen:

1. **Schalteingänge erreichen keinen gültigen Low-Pegel.** Neutral (D4), Kupplung (D33)
   und Spare-Digital (D35) liegen über 10 k/10 k zwischen Stecker und 3V3; geschlossener
   Schalter ergibt 1,65 V, Teensy VIL ist 0,9 V. Kennfeldwahl und Launch-Eingang hängen
   davon ab. Abhilfe: unteren Zweig nach Masse oder 10 k in Serie mit 100 k Pull-up.
2. **Spare-Analog (J2.53) endet an keinem ADC-Pin.**
3. **Kein Startanforderungs-Eingang**, deshalb keine Neutral/Kupplungs-Verriegelung; der
   Starter-Ausgang bleibt frei nutzbar.

Unkritisch: MC33810 FB0..3 und RSP werden im GPGD-Modus nicht benutzt; die GIN-Pins sind
nicht angeschlossen, die Spulen werden über SPI geschaltet.

## Stückliste und Fertigung

- `hardware/ECU/bom/ECU-BOM.csv` (107 Positionen) und `Sensor-Modul-BOM.csv` (46), alle
  Bauteile mit Hersteller- und DigiKey-Nummer.
- PCBWay-Pakete (Gerber, CPL, BOM) in `hardware/ECU/output/pcbway/<board>/`.
- Last-Time-Buy-Teile: MCZ33810EK und ZXMS6006DT8TA (2027), Vorrat kaufen.
- Bestellungen und Fahrzeugteile: `docs/BESTELLUNG.ods`.

## Sensor-Modul

Zweite Platine, 120 × 64 mm, STM32G474, Rev 3.0. Vier Abgastemperaturen (MAX31855K),
Öl-, Kraftstoff- und Abgasdruck, Öltemperatur, zwei Wassertemperaturen im
Ladeluftkühlerkreis, Quickshifter-Geber, lokale Regelung des Ladeluftkühler-Lüfters.
Meldet über CAN an die ECU. Schaltplan `hardware/ECU/sensor-module.kicad_sch`, Firmware
und CAN-Protokoll in `speeduino/sensor-module/`.

## Externe Sensorik am Fahrzeug (1999)

| Sensor | Teil | Kennwerte |
|---|---|---|
| Saugrohrdruck | Serien-IAP 18590-81A00 an J2.58 | ≈ 3,6 V bei 100 kPa, Näherung P ≈ 25·V + 10 kPa |
| TPS | Serie | ≈ 1,1 V geschlossen, 4,3 V offen |
| Kühlmittel | Serien-NTC | 2,3–2,6 kΩ bei 20 °C, 811 Ω bei 50 °C, 318 Ω bei 80 °C |
| Ansaugluft | Serien-NTC | 2,2–2,7 kΩ bei 20 °C |
| Kurbelwelle | VR im Generatordeckel, 8 Zähne gleichmäßig auf dem Generatorrotor | 180–280 Ω |
| Nockenwelle | VR auf dem Ventildeckel links, ein Stift auf der Einlassnocke | 0,9–1,3 kΩ |
| Lambda | Innovate LC-2 + Bosch LSU 4.9 | Analogausgang 1 auf 0–3,3 V programmiert |
| Düsen | 15710-24F00, Keihin, hochohmig 11–16 Ω | ≈ 257 cc/min bei 3 bar (Annahme) |
| Spulen | Denso 33410-24F00 Stabspulen ohne Igniter | 0,8–1,2 Ω primär |

---

**Version**: 4.0
**Stand**: September 2026
