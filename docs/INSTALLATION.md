# Installationsanleitung

Einbau der Gen1 Hayabusa ECU Rev 3 in eine Suzuki GSX1300R Hayabusa **1999** (Gen 1,
frühes 8-Zahn-Kurbelwellenrad). Die Rev 3 sitzt am Serienstecker; der Kabelbaum bleibt.
Werte und Verfahren für den ersten Start stehen in `tune/Hayabusa-R3/README.md`, dieses
Dokument beschreibt Einbau, Verkabelung und Inbetriebnahme bis zum ersten Zündfunken.

## Sicherheitshinweise

**Warnung**: Ein selbst gebautes Steuergerät greift in Zündung und Kraftstoffzufuhr ein.
Fehler führen zu Motorschaden oder Ausfall während der Fahrt. Im Geltungsbereich der StVZO
erlischt die Betriebserlaubnis, solange kein Gutachten vorliegt.

Vor der Installation:
- Serien-Steuergerät und Kabelbaum unverändert aufbewahren (Rückbau möglich).
- Werkstatthandbuch 1999–2001 (GSX1300R X/Y/K1) griffbereit.
- Feuerlöscher, Notaus für die Kraftstoffpumpe, Laptop mit TunerStudio.
- Innovate LC-2 mit LSU 4.9 eingebaut und funktionsfähig, sonst kein erster Start.

## Werkzeuge

- Multimeter, Oszilloskop (für Kurbel- und Nockensignal), Blitzpistole
- Drehmomentschlüssel (Sensoren, Gehäuse), Crimpwerkzeug, Lötstation
- TunerStudio MS Ultra (VE Analyze Live), PlatformIO für die Firmware

## Steuergerät

### Position und Stecker

Das Serien-Steuergerät der Gen 1 sitzt unter der Sitzbank rechts. Die Rev 3 übernimmt den
Serienstecker (TE 6437288-3, 60-polig) mit der Belegung des Serien-Steuergeräts. Alle
Pins: [HARDWARE.md](HARDWARE.md), Abschnitt „Steckerbelegung J2".

### Was die Serie nicht hat

| Signal | J2 | Anschluss |
|---|---|---|
| Lambda (LC-2 Analogausgang 1, 0–3,3 V) | 38 | LC-2 Analogmasse an J2.54 Sensormasse, LC-2 mit eigener Sicherung an geschaltetem 12 V |
| Lambdaheizung | 46 | **offen lassen**, der LC-2 heizt selbst; der Ausgang schaltet 3 s nach Drehzahl > 0 auf 12 V |
| CAN zum Sensor-Modul | 14 / 15 | 500 kbit/s, verdrillt, Abschluss am Modul |
| USB | 16 / 24 + Datenleitungen | Blatt Comms im Schaltplan |
| Lüfter | 29 | nur wenn der Lüfter von der ECU geschaltet werden soll (Tune: Aus, Serien-Thermoschalter bleibt) |
| Ladedrucksteller, Spare-Ausgang, Flex, Spare-Digital | 30, 47, 39, 60 | unbenutzt |

### Kanal- und Zylinderzuordnung

Der Stecker ist nach Zylindernummer belegt (Spulen J2.1/2/3/10, Düsen J2.7/6/5/4 =
Zylinder 1/2/3/4). Speeduino feuert seine Kanäle in der Zündfolge 1-2-4-3; die Firmware
ordnet Kanal 3 dem Zylinder 4 und Kanal 4 dem Zylinder 3 zu. **Am Kabelbaum nichts
tauschen.** Kontrolle im Hardware-Test: IGN3 muss die Spule von Zylinder 4 klicken lassen.

Zylinder 1 ist links (Generatorseite), Zylinder 4 rechts (Kupplungsseite).

### Sensoren der Serie, wie sie die Rev 3 sieht

| Sensor | J2 | Beschaltung ECU | Kennwerte |
|---|---|---|---|
| Kurbelwelle (VR, 8 Zähne auf dem Generatorrotor) | 43 (+) / 36 (−) | MAX9926 Kanal 1 | 180–280 Ω |
| Nockenwelle (VR, ein Stift auf der Einlassnocke) | 37 (+) / 44 (−) | MAX9926 Kanal 2 | 0,9–1,3 kΩ, sitzt neben Spule 1 (Störungen) |
| Saugrohrdruck IAP 18590-81A00 | 58 | Teiler 12 k/20 k | ≈ 3,6 V bei 100 kPa |
| Atmosphärendruck AP 18590-81A00 | 52 | Teiler 12 k/20 k | im Tune nicht genutzt |
| Drosselklappe | 49 | Teiler 12 k/20 k | ≈ 1,1 V zu, 4,3 V offen |
| Kühlmittel, Ansaugluft (NTC) | 51, 50 | 2,49 kΩ an 3,3 V | 2,3–2,6 kΩ bzw. 2,2–2,7 kΩ bei 20 °C |
| Gangsensor | 57 | 1 kΩ, Teiler | Widerstandsleiter gegen Masse |
| Kippschalter | 59 | Komparator | ≈ 2,5 V aufrecht (Gen-1-Typ 60–64 kΩ) |
| Neutral, Kupplung | 20, 19 | 10 k Pull-up 3,3 V, Teiler | Schalter nach Masse; Low-Pegel nur 1,65 V (Befund 1) |
| Sensorversorgung | 48 (+5 V), 54 (Masse) | TPS7B6950, Polyfuse 150 mA | |

Die Kurbelsensor-Leitungen teilen sich in der Serie den Kabelbaum mit dem Generator.
Bei Sync-Problemen die zwei Adern verdrillt und getrennt vom Generatorkabel führen.

## Firmware

```bash
git submodule update --init
cd speeduino
pio run -e teensy41_hayabusa -t upload
```

Branch `Hayabusa/ECU-R3` mit den Korrekturen vom September 2026 (Kanalzuordnung,
Batteriespannung, INI). Details in [SOFTWARE.md](SOFTWARE.md).

## TunerStudio

1. Projekt `tune/Hayabusa-R3` öffnen. *Project Properties → Settings*: „Hayabusa multi map
   switching = Enabled". COM-Port setzen (`project.properties` steht auf COM1).
2. Erster Verbindungsaufbau mit leerem Kennfeldspeicher: TunerStudio meldet, dass Controller
   und Datei abweichen → **Datei auf den Controller schreiben**, dann *Burn*.
3. ECU aus- und einschalten. Erst jetzt ist Board 57 aktiv. Kontrolle: FI-Lampe geht nach
   2 s aus, *Engine Constants* zeigt „Gen1 Hayabusa ECU R3".
4. Kalibrierungen senden (sie liegen im Kennfeldspeicher, nicht in der .msq):

| Kalibrierung | Einstellung |
|---|---|
| *Calibrate Thermistor Tables*, CLT | Bias 2490 Ω; 20 °C 2450 Ω, 50 °C 811 Ω, 80 °C 318 Ω |
| *Calibrate Thermistor Tables*, IAT | Bias 2490 Ω; 20 °C ≈ 2450 Ω, restliche Punkte messen oder CLT-Kurve übernehmen |
| *Calibrate TPS* | geschlossen und Vollgas am Fahrzeug; Startwerte im Tune 53 / 208 ADC |
| *Calibrate AFR Table* | Preset „Innovate LC-1 / LC-2 Default", LC-2 Analogausgang 1 im LM Programmer auf 0,00 V = AFR 7,35 … 3,30 V = AFR 22,39 |
| MAP | fest im Tune: 10 kPa bei 0 V, 142 kPa bei Vollausschlag (Serien-IAP hinter 12 k/20 k). Bei Zündung an muss der Umgebungsdruck stehen, sonst `mapMax` anpassen |

## Inbetriebnahme

### Statischer Test, Motor aus

| Größe | Sollwert |
|---|---|
| Batteriespannung in TunerStudio | wie Multimeter (±0,3 V) |
| Sensor-5 V an J2.48 | 4,9–5,1 V |
| MAP | Umgebungsdruck 95–102 kPa |
| TPS | 0 % zu, 100 % offen, ohne Sprünge |
| CLT, IAT | Umgebungstemperatur; −40 °C = Kabelbruch oder fehlende Kalibrierung |
| AFR (LC-2 warm, Sonde in Luft) | ≥ 20 |
| Kippschalter | FI-Lampe aus, Hardware-Test feuert; sonst Polarität (`HAYABUSA_TIPOVER_INVERTED`) |

*Tools → Test Output Hardware*: IGN1 → Spule Zylinder 1, IGN2 → 2, **IGN3 → Zylinder 4,
IGN4 → Zylinder 3**, Düsen analog. Kerzenstecker dabei auf gemasseten Kerzen.

### Trigger, ohne Kraftstoff

Kraftstoffpumpen-Sicherung ziehen oder Düsen abstecken.

1. *Tools → Tooth Logger* und *Composite Logger* beim Anlassen: 8 Zähne je Umdrehung, ein
   Nockenpuls je zwei Umdrehungen, Sync stabil, Sync Loss 0. Springt der Sync, zuerst die
   Anlasserdrehzahl vergleichmäßigen (Kerzen raus), dann Filter Off oder Flanken FALLING
   testen.
2. Fixed Timing auf 0° stellen, Kerzen eingebaut, Blitzpistole an Zylinder 1, anlassen: die
   T-Marke im Schauloch des Anlasserdeckels (rechte Kurbelseite) muss stehen. Trigger-Winkel
   so lange ändern, bis sie steht (Startwert 350, Alternative 160). Danach Fixed Timing
   zurück auf 10°, *Burn*.

### Erster Start

Feuerlöscher, Notaus, LC-2 im Blick. Weiter nach `tune/Hayabusa-R3/README.md`, Abschnitt
„Erster Start und danach": Leerlaufgemisch nachziehen, Zündzeitpunkt bei laufendem Motor
prüfen, Fixed Timing aus, später Sequential und Begrenzer anheben.

## Störungssuche

| Symptom | Prüfen |
|---|---|
| Keine Drehzahl beim Anlassen | Tooth Logger; Kurbelsignal am Oszilloskop (> 3 V Spitze beim Anlassen); Flanke; Sensorwiderstand 180–280 Ω |
| Drehzahl, aber kein Sync | Nockensignal (> 0,7 V); Störungen von Spule 1; Nockenleitung getrennt führen |
| Sync, aber kein Funke | FI-Lampe an = Freigabe fehlt (Kippschalter, Watchdog); Hardware-Test |
| Funke, aber kein Kraftstoff | Pumpe läuft 3 s beim Einschalten? `tpsflood` 90 %; Düsen klicken im Hardware-Test |
| Läuft nur auf zwei Zylindern, Fehlzündungen | Kanalzuordnung: IGN3 muss Zylinder 4 sein; Firmware-Stand prüfen |
| Startet in Sequential nicht mehr | Nockenphase 360° verkehrt: Trigger-Winkel ±360 |
| −40 °C / 130 °C | Kabelbruch / Kurzschluss oder fehlende Thermistor-Kalibrierung |
| Batteriespannung ≈ 18 V | Firmware ohne Board-57-Skalierung |

## Rückbau

Serien-Steuergerät wieder anstecken, LC-2 kann bleiben (Analogausgang dann unbenutzt),
Heizerausgang J2.46 war ohnehin offen.

---

**Version**: 4.0
**Stand**: September 2026
