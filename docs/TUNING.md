# Tuning-Guide

TunerStudio-Konfiguration der Gen1 Hayabusa ECU Rev 3 (Speeduino-Fork, Board 57) für die
Hayabusa 1999. Quelle der Wahrheit für alle Zahlen ist `tune/Hayabusa-R3/tools/gen_tune.py`;
dieses Dokument erklärt die Zusammenhänge und die Reihenfolge der Abstimmung.

> **Stand:** September 2026. Erststart-Tune erzeugt, Motor damit noch nicht gelaufen.
> Trigger-Winkel, TPS und Kalibrierungen sind am Fahrzeug zu bestimmen.

## 1. Fahrzeug- und Setup-Daten

| Komponente | Zustand |
|---|---|
| Modell | Suzuki Hayabusa Gen 1, **Baujahr 1999** (Modell X, 16-bit-Serien-ECU, frühes Kurbelrad) |
| Hubraum | 1299 cc, Reihen-4, Zündfolge 1-2-4-3, Zylinder 1 links |
| Verdichtung | **12 : 1** (Wössner-Kolben; Serie 11 : 1) |
| Airbox | Serie, zentrale Drosselklappen, Sekundärklappen passiv |
| Einspritzdüsen | Serie 15710-24F00, Keihin, hochohmig; **Annahme 257 cc/min bei 3 bar** (24,5 lb/h), Flowbench-Berichte 240–280 |
| Kraftstoffdruck | 3,0 bar Differenzdruck (Serienregler mit Unterdruckreferenz bei 1999/2000) |
| Zündung | Serien-Stabspulen Denso 33410-24F00, 0,8–1,2 Ω, ohne Igniter, direkt an den ISL9V5036 |
| Kurbeltrigger | Serie: **8 Zähne gleichmäßig, keine Lücke**, VR |
| Nockentrigger | Serie: ein Stift auf der Einlassnocke, VR |
| MAP | Serien-IAP 18590-81A00 an J2.58 |
| TPS, CLT, IAT | Serie |
| Lambda | Innovate LC-2 + Bosch LSU 4.9, Analogausgang 1 auf 0–3,3 V an J2.38 |
| Klopfsensor | TPIC8101 auf der Platine, Sensor Bosch 0 261 231 173 noch nicht verbaut |
| Leerlauf | mechanisch (Wachselement, Anschlagschraube), keine ECU-Regelung |
| Lüfter | Serien-Thermoschalter |
| Turbo | nicht verbaut |
| TunerStudio | MS Ultra |

## 2. Projekt

```text
File → Open Project → tune/Hayabusa-R3
Project Properties → Settings → Hayabusa multi map switching = Enabled
Communications → Connect
```

Die Projekt-INI `tune/Hayabusa-R3/projectCfg/mainController.ini` ist eine Kopie von
`speeduino/reference/speeduino.ini` des passenden Fork-Stands und muss byteidentisch
bleiben. Niemals eine offizielle Speeduino-INI einsetzen: Board 57, Seiten 16–21 und die
INI-Korrekturen fehlen dort.

Änderungen am Tune über den Generator:

```bash
python3 tune/Hayabusa-R3/tools/gen_tune.py
```

Was TunerStudio live verändert (Kalibrierungen, VE Analyze), wird in der .msq gespeichert
und beim nächsten Generatorlauf überschrieben, wenn es nicht in `gen_tune.py` nachgezogen
wird. Restore-Points vor jeder Änderung.

## 3. Engine Constants

| Parameter | Erststart | danach |
|---|---|---|
| `pinLayout` | Gen1 Hayabusa ECU R3 | |
| `nCylinders` / `engineType` / `twoStroke` | 4 / Even fire / Four-stroke | |
| `nInjectors` / `injType` | 4 / Port | |
| `injLayout` | **Semi-Sequential**, Paarung „1+3 & 2+4", `divider` 2 | Sequential, `divider` 4 |
| `algorithm` / `ignAlgorithm` | TPS (Alpha-N) für beides | |
| `multiplyMAP` | Off | offen; die Stock-Map ist nicht auf MAP/Baro normiert |
| `mapSample` | Cycle Average | |
| `stoich` | 14,7 | |
| `reqFuel` | **8,3 ms** (1299 cc, 4 Zyl., 14,7, 257 cc/min) | bei bestätigtem Düsendurchsatz neu rechnen |
| `injOpen` | 1,0 ms bei 14 V | messen |
| `dutyLim` | 85 % | 90–95 % nach Volllastnachweis |

`reqFuel` ist der Kraftstoff je Zylinder und Arbeitsspiel bei VE 100 %. Die Firmware
halbiert ihn selbst für Semi-Sequential; beim Wechsel auf Sequential bleibt der Wert.

## 4. Trigger

| Parameter | Wert |
|---|---|
| `TrigPattern` | Dual Wheel |
| `numTeeth` / `missingTeeth` | 8 / 0 |
| `trigPatternSec` | Single tooth cam |
| `TrigEdge` / `TrigEdgeSec` | RISING / RISING (MAX9926) |
| `TrigSpeed` | Crank Speed |
| `TrigAng` | **350° ATDC**, unverifiziert |
| `TrigFilter` / `useResync` / `SkipCycles` | Weak / Ja / 3 |
| `CrankAng` | 5° |
| `fixAngEnable` / `FixAng` | **On / 10°** bis der Trigger-Winkel bestätigt ist |

Zahn 1 ist der erste Kurbelzahn nach dem Nockenpuls; `TrigAng` ist seine Position in Grad
nach OT Zylinder 1. Für das 8-Zahn-Rad gibt es keinen belegten Wert; die kursierenden
Zahlen (100/460, −100/260) gehören zum 24-1-Rad ab 2002. Ein Speeduino-Projekt mit 8+1 und
MAX9926 lief mit 350 (RISING) bzw. 160 (FALLING). Ein Zahn Fehler sind 45°.

Verfahren: siehe [INSTALLATION.md](INSTALLATION.md), Abschnitt „Trigger". Kurz: Tooth
Logger ohne Kraftstoff, dann Fixed Timing 0° und Blitzpistole auf die T-Marke, Winkel
korrigieren, Fixed Timing 10° zum Start. Läuft der Motor später in Sequential nicht, Winkel
um 360 verschieben (350 → −10).

## 5. Zündung

| Parameter | Erststart | danach |
|---|---|---|
| `sparkMode` | **Wasted COP** | Sequential, sobald die Nockenphase stimmt |
| `IgInv` | Going Low | |
| `dwellrun` / `dwellcrank` | 1,6 / 2,5 ms | |
| `useDwellLim` / `dwellLim` | On / 4 ms | |
| `sparkDur` | 1,0 ms | |
| Dwell-Spannungskurve | 240/200/150/130/100/100 % bei 6/8/10/12/14/20 V | oberhalb 14 V flach als Schutz gegen falsche Spannungsanzeige |
| `perToothIgn` / `dwellErrCorrect` | Ja / On | |

Die Serienspulen sättigen bei etwa 2 ms und 14 V; der Serien-ECU-Wert am Begrenzer liegt
bei 1,5 ms. Wasted COP verdoppelt die Spulenbelastung, deshalb 1,6 ms und so bald wie
möglich Sequential.

Zündkennfeld: Stock-Map `IGN_org` aus `tune/setup/maps.ods`, bilinear auf die 16×16-Achsen
interpoliert, **−3° bei Last ≥ 25 % und ≥ 2000 rpm** wegen 12:1 ohne Klopfsensor. Leerlauf
9° bei 800 rpm (Serie: 4° bei 1200 rpm). Das Blatt `ING` in der ODS ist nicht die
Serienzündung und wird nicht verwendet.

## 6. Kraftstoff

### 6.1 VE-Tabelle

Stock-TPS-Kennfeld (23 × 42) bilinear auf 16 × 16 interpoliert und mit 120/205 skaliert
(Maximum 120 %). Zellen 0–4 % TPS unter 2000 rpm auf 40 gesetzt: das Serien-Steuergerät
nutzt dort die IAP-Map (Umschaltpunkt ≈ 11 % TPS), die TPS-Werte sind dort nicht
aussagekräftig. Erwartung im Leerlauf ≈ 2,7 ms je Einspritzung, eher fett; mit dem LC-2
auf 13,5–14 ziehen.

Achsen: Drehzahl 800/1200/1600/2000/2400/2800/3400/4000/4800/5600/6400/7200/8000/9200/
10400/12000, Last 0/2/4/6/8/10/13/16/20/25/30/40/50/60/75/100 % TPS.

### 6.2 Korrekturen

| Funktion | Startwerte |
|---|---|
| Cranking | 300/220/160/120 % bei −40/0/30/80 °C, `crankRPM` 500, `tpsflood` 90 % |
| Prime | 6/4/3/2 ms bei −40/0/30/80 °C, 0,5 s nach Pumpenstart, Pumpe 3 s |
| ASE | 30/25/20/10 % für 8/6/5/3 s bei −40/0/20/60 °C |
| WUE | 160/152/145/138/130/123/116/108/102/100 % bei −40 … 80 °C |
| IAT-Dichte | 126 → 79 % von −40 bis 100 °C (ideales Gas) |
| Düsen-Spannungskurve | 250/200/150/120/100/100 % bei 6/8/10/12/14/20 V |
| AE | TPS-Modus, Schwelle 50 %/s, Mindeständerung 3 %, 250 ms, Multiplikator 10/25/45/70 % bei 0/60/150/400 %/s, kalt 120 % bis 60 °C |
| DFCO | Aus, erst nach Lambda-Regelung: 2500 rpm, Hysterese 250, TPS < 2 %, CLT > 60 °C, 1 s |
| Baro-Korrektur | Aus |

### 6.3 Volllast

Mit 257 cc/min liegt die Düsenauslastung oberhalb 9000 rpm über 90 %; das Duty-Limit von
85 % magert dort ab. Vor Volllastfahrten: AFR 12,5–13,0 unter Last nachweisen, Duty-Limit
anheben, Sequential (spart eine Totzeit je Arbeitsspiel), Begrenzer erst dann über 9500.

## 7. Sensoren

| Sensor | Einstellung |
|---|---|
| TPS | `tpsMin` 53 / `tpsMax` 208 als Startwert, **am Fahrzeug kalibrieren** (1,1 V / 4,3 V hinter 12 k/20 k) |
| MAP | `mapMin` 10 / `mapMax` 142 kPa (Serien-IAP ≈ 25·V + 10 kPa, Vollausschlag 5,28 V). Kennlinie ist abgeleitet; bei Zündung an muss der Umgebungsdruck stehen |
| Baro | aus MAP beim Einschalten (`useExtBaro` No) |
| CLT / IAT | Thermistor-Kalibrierung mit Bias **2490 Ω**: 20 °C 2450 Ω, 50 °C 811 Ω, 80 °C 318 Ω. Pull-up hängt an 3,3 V wie die ADC-Referenz, daher exakt |
| Batterie | Firmware skaliert für den 47 k/10 k-Teiler; `batVoltCorrect` 0 |
| Lambda | LC-2 Analogausgang 1: **0,00 V = AFR 7,35 … 3,30 V = AFR 22,39** (Innovate-Standard-AFR, nur Endspannung 5 → 3,3 V). TunerStudio *Calibrate AFR Table* Preset „Innovate LC-1 / LC-2 Default". `egoType` Wide Band, `egoAlgorithm` No correction, `ego_sdelay` 30 s. Analogausgang 2 isolieren, LC-2-Analogmasse an J2.54, Heizerausgang J2.46 offen |

Einbau der Sonde: Edelstahl-Stutzen M18×1,5 im Akrapovič-Mittelrohr, 10–2 Uhr, ≥ 45 cm
hinter dem Auslass, vor dem Dämpfer (im Sammler kollidiert die Sonde mit dem Motor).
Alternative bei Turbo: Downpipe hinter dem Lader. CAN statt analog (AEM X-Series 0x180,
rusEFI-WBO, `canWBO`) bleibt möglich.

Lambda-Regelung, sobald Sonde und VE grob passen: `egoAlgorithm` Simple, KP/KI/KD 80/60/50,
`egoLimit` 15 %, `egoRPM` 1500, `egoTPSMax` 70 %, `egoTemp` 60 °C.

## 8. Leerlauf

Kein IAC-Ventil: `iacAlgorithm` None, Leerlaufdrehzahl an der Anschlagschraube (Serie
1150 ± 100). Bei unruhigem warmen Leerlauf: Zellen 0–4 % TPS bei 800–1600 rpm, dann
`idleAdvEnabled` Added mit kleiner Kurve. Der Schrittmotortreiber auf der Platine bleibt
ungenutzt.

## 9. Begrenzer und Schutz

| Parameter | Erststart | Ziel |
|---|---|---|
| `SoftRevLim` / Modus | 5500, fest 10° für 1,5 s | 10500 |
| `hardRevLim` / `hardCutType` | 6000 / Full | 10900 (Serie), `engineProtectType` Both |
| `boostCutEnabled` | **Off** (Saugmotor); `boostLimit` 200 kPa | |
| AFR-Schutz | Aus | nach vertrauenswürdigem LC-2: Tabellenmodus, +1,5 AFR, > 4000 rpm, > 80 % TPS |
| Öldruck-Schutz | Aus | mit Sensor-Modul |

Solange Fixed Timing an ist, wirken weder Zündkorrekturen noch der weiche Begrenzer.

## 10. Klopfregelung

Der TPIC8101 wird von der Firmware konfiguriert (6,37 kHz, Verstärkung Index 14, 200 µs);
Fenster am Zündfunken. Tune: `knock_mode` **Off** bis der Sensor verbaut ist, dann
**Analog** (Pin wird ignoriert), Schwelle am Motor mit Klopfaufzeichnung bestimmen, Rücknahme
3° je Ereignis, maximal 8°, oberhalb 9000 rpm aus. Bis dahin bleibt die Zündung 3° unter
Serie.

## 11. AFR-Zieltabelle

16 × 16, nur Referenz für VE Analyze (`incorporateAFR` No): 14,2 im Leerlauf, 14,7 bei
15–30 % TPS, 13,8 bei 50 %, 12,8 bei 100 %.

## 12. Ablauf der Abstimmung

1. Statischer Test, Kalibrierungen, Hardware-Test (Kanalzuordnung!).
2. Trigger ohne Kraftstoff: Tooth Logger, Blitzpistole, `TrigAng`.
3. Erststart mit Fixed Timing 10°, Wasted COP, Semi-Sequential; Leerlaufzellen mit LC-2
   nachziehen; Zündzeitpunkt bei zwei Drehzahlen prüfen; Fixed Timing aus, Burn.
4. Sequential für Einspritzung und Zündung; startet der Motor nicht, `TrigAng` ± 360.
5. Warmlauf: WUE gegen AFR.
6. Teillast: VE Analyze Live, Ziel `afrTable`, Filter CLT > 75 °C, Änderung ≤ 5 % je
   Durchlauf, manuell freigeben.
7. Volllast nur auf dem Prüfstand, Begrenzer schrittweise, Düsenauslastung beobachten.
8. Danach: Lambda-Regelung, DFCO, Klopfsensor, Sensor-Modul, Kennfeldsätze 2–4 mit
   eigenen Inhalten (bisher Kopien von Satz 1), MAP-basierte Zweittabelle für Leerlauf
   und Schub.

Datenlogging: TunerStudio-Log über USB (On-board-Logging im Tune aus). Pflichtkanäle RPM,
TPS, MAP, CLT, IAT, Battery, Sync Loss, AFR, VE, Advance, PW, Dwell. Logs nicht ins
Repository.

## 13. Dateien und Backups

```
tune/Hayabusa-R3/
├── CurrentTune.msq               generiert
├── README.md                     Herkunft, Checkliste, Verfahren
├── projectCfg/mainController.ini Kopie der Fork-INI, nicht ersetzen
├── projectCfg/project.properties
└── tools/                        gen_tune.py, stockmaps.py, iniparse.py, msqinfo.py, dumptables.py
tune/setup/maps.ods               Serienkennfelder (VE_org, IGN_org)
```

Restore-Points vor jeder Änderung (`File → Save As`), TunerStudio legt `restorePoints/`
selbst an. Änderungen nach erfolgreichem Test in den Generator übernehmen und committen.

## 14. Störungssuche

| Symptom | Prüfen |
|---|---|
| Keine Drehzahl | Tooth Logger, Flanke, Sensorwiderstand, Kabelführung Kurbelsensor |
| Sync springt | Anlasserdrehzahl, Filter Off, Nockenleitung getrennt von Spule 1 |
| Funke, kein Sprit | Pumpenlauf 3 s, `tpsflood`, Düsen im Hardware-Test |
| Zwei Zylinder, Fehlzündungen in den Auspuff | Kanalzuordnung IGN3 = Zylinder 4, Firmware-Stand |
| Sequential startet nicht | `TrigAng` ± 360 |
| Zu fett im Leerlauf | Zellen 0–4 % TPS senken, TPS-Kalibrierung |
| Mager bei hoher Drehzahl | Düsenauslastung, `dutyLim`, `reqFuel` gegen echten Düsendurchsatz |
| −40 °C / 130 °C | Kabel oder fehlende Thermistor-Kalibrierung |
| Batterie 18 V | Firmware ohne Board-57-Skalierung |

## 15. Offene Punkte

- [ ] Trigger-Winkel und Flanke am Motor bestätigen.
- [ ] TPS, Thermistoren, AFR kalibrieren.
- [ ] Düsendurchsatz belegen (Teilenummer ablesen, Flowbench), `reqFuel` nachrechnen.
- [ ] IAP-Kennlinie gegen Umgebungsdruck prüfen.
- [ ] Kippschalter-Polarität, Gangsensor-Schwellen.
- [x] LC-2 + LSU 4.9 beschafft (2026-09-01, `docs/BESTELLUNG.ods`); Einbau offen.
- [ ] Klopfsensor Bosch 0 261 231 173 verbauen, Schwelle kalibrieren.
- [ ] Sequential, Begrenzer anheben, DFCO, Lambda-Regelung.

## 16. Quellen

- Speeduino-Wiki: https://wiki.speeduino.com · Forum: https://speeduino.com/forum
- TunerStudio: http://tunerstudio.com
- Fork: https://github.com/HasiKe/speeduino, Branch `Hayabusa/ECU-R3`
- Projekt: [HARDWARE.md](HARDWARE.md), [INSTALLATION.md](INSTALLATION.md),
  [SOFTWARE.md](SOFTWARE.md), `tune/Hayabusa-R3/README.md`

---

**Version:** 4.0
**Stand:** September 2026
