# Hayabusa-R3 — TunerStudio-Projekt für die Gen1 Hayabusa ECU Rev 3

Basisabstimmung für die Suzuki GSX1300R Hayabusa **Baujahr 1999** (Gen 1, Modell X,
originales 8-Zahn-Kurbelwellenrad) mit dem Eigenbau-Steuergerät Rev 3 (Board 57
„Gen1 Hayabusa ECU R3", Speeduino-Fork `HasiKe/speeduino`, Branch `Hayabusa/ECU-R3`, lokal `Hayabusa/ECU-R3-v2`).

Stand: 2026-09-03. Die Kennfelder stammen aus dem originalen Steuergerät
(`tune/setup/maps.ods`), alle übrigen Werte sind Startwerte für die Inbetriebnahme.
**Der Motor ist mit diesem Tune noch nie gelaufen.** Trigger-Winkel, TPS-Kalibrierung,
Thermistor- und Lambda-Kalibrierung müssen am Fahrzeug bestimmt werden, siehe
Abschnitt „Vor dem ersten Start".

## Dateien

| Datei | Inhalt |
|---|---|
| `CurrentTune.msq` | Tune, Signatur `speeduino 202504-dev`, 21 Seiten (Kennfeldsätze 1–4) |
| `projectCfg/mainController.ini` | TunerStudio-INI, Kopie von `speeduino/reference/speeduino.ini` des Fork-Stands unten |
| `projectCfg/project.properties` | Projekt-Einstellungen, Setting-Groups: `mcu_teensy`, `HAYABUSA_MULTIMAP`, `CELSIUS`, `AFR`, `pressure_bar`, `enablehardware_test`, `resetcontrol_standard` |
| `tools/gen_tune.py` | Generator: erzeugt `CurrentTune.msq` und kopiert die INI aus dem Submodul. Parameter im Kopf der Datei (`P`), Einzelwerte im Dict `E` |
| `tools/stockmaps.py` | liest die Stock-Kennfelder aus `maps.ods`, repariert die Achsen-Tippfehler, interpoliert bilinear |
| `tools/iniparse.py`, `tools/msqinfo.py`, `tools/dumptables.py` | INI-Parser, MSQ-Leser, Tabellenanzeige |
| `tools/base_tune_Busa_2026-02-02.msq` | altes TunerStudio-Tune als Format-Gerüst und Quelle für inaktive Einstellungen (Werte, die auf den Motor wirken, kommen nicht von dort) |

Neu erzeugen nach Änderung an Parametern oder INI:

```bash
python3 tune/Hayabusa-R3/tools/gen_tune.py
python3 tune/Hayabusa-R3/tools/dumptables.py tune/Hayabusa-R3/CurrentTune.msq veTable advTable1
```

Der Generator prüft jeden Wert gegen die INI (Optionsliste, Wertebereich, Auflösung) und
bricht bei Fehlern ab. Die Projekt-INI muss immer byteidentisch mit der INI sein, mit
der das Tune erzeugt wurde, sonst werden Konstanten falsch abgelegt.

## Voraussetzung: Firmware-Stand

Das Tune setzt den Fork-Stand mit folgenden Korrekturen voraus (Branch `Hayabusa/ECU-R3`,
lokal `Hayabusa/ECU-R3-v2`, Commits 7e55b2d9 und 13a7e98d vom 2026-09-03). Ohne den ersten Punkt läuft der Motor nicht richtig.

1. **Zylinderzuordnung** in `getHayabusaR3Mapping()`: Speeduino feuert Kanal 3 bei 360° und
   Kanal 4 bei 540° Kurbelwinkel. J2 folgt dem Stock-Pinout (Coil/Injector 1–4 nach
   Zylindernummer), die Zündfolge ist 1-2-4-3. Die Firmware legt deshalb Kanal 3 auf
   Zylinder 4 (J2.10 Spule, J2.4 Düse) und Kanal 4 auf Zylinder 3 (J2.3 Spule, J2.5 Düse).
   Der Kabelbaum bleibt nach Zylindernummer verdrahtet. Zylinder 1 ist links
   (Generatorseite).
2. **Batteriespannung**: A15 hängt an 47k/10k, Endwert 18,8 V statt 24,5 V. Ohne die
   Korrektur zeigt die ECU 14,0 V als 18,2 V und kürzt Dwell und Düsen-Totzeit.
3. **INI**: `ignTrim1..8` lagen auf Seite 6 über `airDenRates`/`boostFreq`/`vvtFreq`/
   `idleFreq`/Launch-Byte (Upstream-Fehler) und stehen jetzt auf Seite 13; Load-Achsen der
   Kennfeldsätze 3/4 folgen dem Last-Algorithmus (TPS) statt fester kPa-Skalierung;
   `boostTable3/4` mit Skalierung 2,0.

Bauen und flashen:

```bash
cd speeduino && pio run -e teensy41_hayabusa -t upload
```

## Herkunft und Umrechnung der Kennfelder

- Quelle `tune/setup/maps.ods`: Blatt `VE_org`, Block „TPS fuelmap" (23 TPS-Spalten 0–100 %,
  42 Drehzahlzeilen 800–12800) und Blatt `IGN_org`, Block „Ignitionmap" (23 × 36, 800–14800).
  Tippfehler in den Drehzahlachsen werden vom Generator korrigiert (1200→12000 in beiden
  Kraftstoffblöcken, 200→2000 und 1400→14000 in der Zündung). Das Blatt `ING` ist **nicht**
  die Stock-Zündung (bis zu 8° mehr Frühzündung bei niedriger Drehzahl, Herkunft unklar)
  und wird nicht verwendet. Die Maps stammen aus ECUeditor, also vom 32-bit-Steuergerät
  der Modelle 2002–2007; der Motor ist mechanisch gleich.
- **VE-Tabelle**: Stock-TPS-Map bilinear auf die neuen Achsen interpoliert und mit
  120/205 = 0,585 skaliert (Maximum 205 → 120 %). Die Zellen 0–4 % TPS unter 2000 rpm sind
  auf 40 gesetzt: dort benutzt das Stock-Steuergerät die IAP-Map (Umschaltpunkt 11 % TPS),
  die TPS-Werte sind dort nicht aussagekräftig. Erwartete Leerlauf-Pulsbreite ca. 2,7 ms je
  Einspritzung, eher fett.
- **Zündung**: `IGN_org` interpoliert, minus 3° in allen Zellen mit Last ≥ 25 % TPS und
  ≥ 2000 rpm (Verdichtung 12:1 statt 11:1, noch kein Klopfsensor). Leerlauf- und
  Schubzellen unverändert (9° bei 800 rpm).
- **reqFuel 8,3 ms**: 1299 cc, 4 Zylinder, AFR 14,7, Düsen 257 cc/min bei 3 bar
  (Stock 15710-24F00, 24,5 lb/h). Die Firmware halbiert den Wert für Semi-Sequential
  selbst; beim Wechsel auf Sequential bleibt 8,3 stehen. Flowbench-Berichte liegen bei
  240–280 cc/min; sind die Düsen größer, wird das Gemisch fetter, nicht magerer.
- **Achsen**: Kraftstoff 800/1200/1600/2000/2400/2800/3400/4000/4800/5600/6400/7200/8000/
  9200/10400/12000 rpm, Zündung 800/1200/1600/2000/2400/2800/3200/3600/4000/4800/5600/6400/
  7200/8400/10000/12000 rpm, Last beide 0/2/4/6/8/10/13/16/20/25/30/40/50/60/75/100 % TPS.
- **Kennfeldsätze 2–4** sind identische Kopien von Satz 1. Wahl beim Einschalten mit
  Vollgas + Kupplung, siehe `speeduino/HAYABUSA_ECU_R3.md`.
- **AFR-Zieltabelle** (nur Anzeige, keine Regelung): 14,2 im Leerlauf, 14,7 Teillast,
  12,8 bei Volllast.

## Erststart-Konfiguration

| Bereich | Einstellung | Grund |
|---|---|---|
| Einspritzung | Semi-Sequential, Paarung „1+3 & 2+4", divider 2 | phasenunabhängig; Paarung passt zur Kanalzuordnung oben |
| Zündung | **Wasted COP**, `IgInv` Going Low | phasenunabhängig, doppelte Spulenbelastung nur für die Inbetriebnahme |
| Fixed Timing | **Ein, 10°** | Trigger-Winkel ist unverifiziert; Zündung fest bis Blitzpistolen-Check |
| Trigger | Dual Wheel, 8 Zähne, Single tooth cam, Winkel **350° ATDC**, RISING/RISING, Filter Weak, Resync Ja, Skip 3, Cranking-Winkel 5° | siehe „Trigger" |
| Dwell | 1,6 ms Lauf, 2,5 ms Start, Limiter 4 ms, Spannungskurve 100 % ab 14 V | Denso-Stabspulen 0,8–1,2 Ω, gemessene Sättigung ≈ 2 ms bei 14 V |
| Begrenzer | weich 5500 (fest 10°), hart 6000, Fuel + Spark | Inbetriebnahme; Stock-Limit 10900 |
| Kraftstoffkorrekturen | Cranking 300/220/160/120 % bei −40/0/30/80 °C, ASE 30–10 %, WUE 160→100 %, IAT-Dichte 126→79 %, AE TPS 50 %/s, Multiplikator | Speeduino-übliche Startwerte |
| Düsen | Totzeit 1,0 ms, Duty-Limit 85 %, Prime 6/4/3/2 ms, Pumpe 3 s vor, Prime-Verzögerung 0,5 s | |
| MAP | Stock-IAP 18590-81A00 hinter 12k/20k: 10 kPa bei 0 V, 142 kPa bei Vollausschlag; `multiplyMAP` Aus; Baro aus MAP beim Einschalten | Kennlinie ≈ 25·V + 10 kPa ist aus den Suzuki-Bändern abgeleitet, am Fahrzeug prüfen |
| TPS | 53 / 208 ADC (1,1 V / 4,3 V) | **muss kalibriert werden** |
| Lambda | Wide Band, keine Regelung, 30 s Verzögerung | LC-2 Ausgang 0–3,3 V, Preset „Innovate LC-1/LC-2" |
| Aus | DFCO, Boost-Cut, Launch, Flat-Shift, Leerlaufregelung, Lüfter, Klopfen, CAN, Nitrous, VVT, WMI, Staging, 2. Tabellen, Logging | |

## Trigger

Das 1999er Rad hat **8 gleichmäßig verteilte Zähne ohne Lücke**, Sensor VR; der
Nockenwellensensor (VR, neben der Spule von Zylinder 1) liefert einen Puls je
Nockenwellenumdrehung. Speeduino: „Dual Wheel", Zahn 1 ist der erste Kurbelzahn nach dem
Cam-Puls, der Trigger-Winkel ist die Kurbelstellung in Grad **nach** OT Zylinder 1, bei der
Zahn 1 den Sensor passiert.

Es gibt keinen verifizierten Wert für dieses Rad. Die für die Hayabusa kursierenden Zahlen
(100/460, −100/260, 105) gelten für das 24-1-Rad ab 2002. Einzige Referenz mit 8+1 und
MAX9926 ist ein Speeduino-Forumsprojekt („Hayabusa Gen1", 2023): 350° mit RISING/RISING,
per Blitzpistole bestätigt; mit FALLING lag der Wert bei 160. Beide sind Startwerte,
Motor-zu-Motor-Streuung liegt bei bis zu 5°. Ein Fehler um einen Zahn (45°) bedeutet
Rückschlag oder kein Start.

## Vor dem ersten Start

1. **Firmware** mit den drei Korrekturen bauen und flashen. TunerStudio: Projekt
   `tune/Hayabusa-R3` öffnen, unter *Project Properties → Settings* muss „Hayabusa multi map
   switching = Enabled" stehen, COM-Port anpassen (`project.properties` steht auf COM1).
2. **Erster Verbindungsaufbau** (leerer SPI-Flash): TunerStudio meldet, dass Controller und
   Datei abweichen → **Datei auf den Controller schreiben** (nicht umgekehrt), *Burn*, danach
   ECU **aus- und einschalten**. Erst nach dem Neustart ist Board 57 aktiv (Watchdog,
   OUTEN, MC33810). Kontrolle: FI-Lampe geht nach 2 s aus, `pinLayout` zeigt „Gen1 Hayabusa
   ECU R3".
3. **Kalibrierungen** (liegen nicht im Tune, sondern nur im Steuergerät):
   - *Tools → Calibrate Thermistor Tables*, CLT und IAT: Bias-Widerstand **2490 Ω**
     (Pull-up gegen 3,3 V = ADC-Referenz, daher exakt). Punkte Stock-ECT: 20 °C 2450 Ω,
     50 °C 811 Ω, 80 °C 318 Ω. IAT: 20 °C 2,2–2,7 kΩ laut Suzuki, restliche Punkte messen
     (Eiswasser, kochendes Wasser) oder ECT-Kurve übernehmen. Danach müssen CLT und IAT
     Umgebungstemperatur zeigen. Ein CLT bei −40 °C bedeutet Kabelbruch oder fehlende
     Kalibrierung und würde 300 % Startanreicherung auslösen.
   - *Tools → Calibrate TPS*: geschlossen und Vollgas. Prüfen: 0 % im Leerlaufanschlag,
     linear bis 100 %. Ohne Kalibrierung läuft der Leerlauf auf der falschen Lastzeile.
   - *Tools → Calibrate AFR Table*: Preset „Innovate LC-1 / LC-2 Default". Voraussetzung:
     LC-2 Analogausgang 1 im LM Programmer auf **0,00 V = AFR 7,35 … 3,30 V = AFR 22,39**
     programmiert (der Eingang J2.38 endet bei 3,3 V). Kontrolle: Sonde in Luft ≥ 20 AFR.
     Heizerausgang J2.46 **offen lassen**, der LC-2 heizt selbst.
   - MAP: Zündung an, Motor aus → Anzeige muss dem Luftdruck entsprechen (95–102 kPa).
     Weicht sie ab, `mapMax` anpassen (Kennlinie ist abgeleitet, nicht Suzuki-Spezifikation).
   - Batteriespannung mit Multimeter vergleichen (nur mit korrigierter Firmware richtig).
4. **Kanalzuordnung prüfen** (*Tools → Test Output Hardware*): IGN3 muss die Spule von
   **Zylinder 4** klicken lassen, IGN4 die von Zylinder 3, INJ3 die Düse von Zylinder 4,
   INJ4 die von Zylinder 3. Kerzenstecker dabei mit gemasseten Kerzen.
5. **Trigger prüfen**, Kraftstoffpumpen-Sicherung gezogen oder Düsen abgesteckt:
   - *Tools → Tooth Logger / Composite Logger* beim Anlassen: 8 Zähne je Umdrehung, ein
     Cam-Puls je zwei Umdrehungen, Sync stabil, Sync Loss 0. Springt der Sync, Filter auf
     Off oder Kanten auf FALLING testen; die Anlasserdrehzahl muss gleichmäßig sein.
   - Fixed Timing auf **0°** stellen, Kerzen eingebaut, Blitzpistole an Zylinder 1, anlassen:
     die T-Marke im Schauloch des Anlasserdeckels muss stehen. Steht sie nicht, Trigger-Winkel
     ändern, bis sie steht (Kandidaten 350, dann 160; sonst in Schritten). Anschließend
     Fixed Timing zurück auf 10°, *Burn*.
6. **Sicherheit**: Feuerlöscher, Notaus, LC-2 angeschlossen und angezeigt, Kühlung
   angeschlossen. Kippschalter-Polarität beachten: geht die FI-Lampe nicht aus oder feuern
   die Spulen im Hardware-Test nicht, meldet die Firmware „umgekippt"
   (`HAYABUSA_TIPOVER_INVERTED` in `platformio.ini`).

## Erster Start und danach

1. Kraftstoff an, anlassen. AFR im Leerlauf 12–14 anstreben; die Zellen 0–4 % TPS unter
   2000 rpm (Wert 40) direkt nach Gehör/AFR nachziehen. Nicht lange im fetten Leerlauf
   stehen lassen. Leerlaufdrehzahl mechanisch an der Anschlagschraube (Stock 1150 ± 100).
2. Zündzeitpunkt bei laufendem Motor mit Blitzpistole gegen die feste Vorgabe von 10°
   prüfen (Abstand zur T-Marke). Stimmt er bei zwei Drehzahlen, sind Winkel und Flanke
   richtig. Dann **Fixed Timing aus, Burn**. Solange Fixed Timing an ist, wirken keine
   Zündkorrekturen und kein weicher Begrenzer; nur der harte Schnitt bei 6000 schützt.
3. Warmlauf: WUE gegen AFR prüfen (kalt 12,5–13, warm 14,7 Teillast).
4. **Sequential**: Einspritzung auf Sequential, Zündung auf Sequential, Burn. Startet oder
   läuft der Motor dann nicht mehr, liegt die Nockenwellenphase um 360° verkehrt: Trigger-
   Winkel um 360 verschieben (350 → −10). Danach halbiert sich die Spulenbelastung.
5. Begrenzer schrittweise anheben, nur mit LC-2 unter Last: oberhalb ca. 9000 rpm reicht
   die Düsenkapazität bei 257 cc/min knapp (Duty > 90 %), das Duty-Limit von 85 % macht das
   Gemisch dort mager. Vor Volllastfahrten Duty-Limit auf 90–95 % und AFR bei Volllast
   12,5–13,0 nachweisen; Stock-Begrenzer 10900.
6. Offene Punkte für später: Klopfsensor (TPIC8101, Modus Analog), DFCO, Lambda-Regelung,
   Sensor-Modul über CAN, Gangsensor-Schwellen (`HAYABUSA_GEAR_THRESHOLDS`),
   MAP-basierte Zweittabelle für Leerlauf und Schub, Lüfter über J2.29.

## Bekannte Abweichungen zur übrigen Dokumentation

`docs/TUNING.md`, `docs/INSTALLATION.md`, `docs/HARDWARE.md` und `docs/SOFTWARE.md`
beschreiben noch den Dropbear-Aufbau (Rev 1) mit anderen Pins, Trigger- und
Kalibrierwerten (2,7 kΩ / 5 V, 36-1, mapMax 100, Dwell 4 ms, reqFuel 13,2). Für die Rev 3
gilt dieses README zusammen mit `speeduino/HAYABUSA_ECU_R3.md`.
