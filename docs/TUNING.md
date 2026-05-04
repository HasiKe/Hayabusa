# Tuning-Guide

Vollständige TunerStudio-Konfiguration für die Hayabusa-ECU auf Basis von Speeduino 2025.04-dev (HasiKe-Fork) mit Dropbear v2 / Teensy 4.1.

> **Stand:** April 2026 — abgeleitet aus `tune/Busa/CurrentTune.msq` (Snapshot 2026-02-02) und abgestimmt auf das verbaute Setup.

---

## 1. Fahrzeug- und Setup-Daten

| Komponente | Zustand |
|---|---|
| Modell | Suzuki Hayabusa Gen1 (1999-2007) |
| Baujahr | **1999** |
| Hubraum | 1299 cc, 4-Takt, Reihen-4 |
| Verdichtung | **12 : 1** (überarbeiteter Motor mit verstärkten Komponenten) |
| Mods | Motor-Refresh mit verstärkten Pleueln/Lagern (Details siehe `hardware/Parts & Cost.ods`) |
| Airbox | **Original Suzuki**, eine zentrale Drosselklappe + Sekundär-Drosselklappen (STV) stillgelegt/passiv |
| Einspritzdüsen | **OEM Suzuki Hayabusa Gen1** (Annahme: ~211 cc/min @ 3 bar — TODO verifizieren) |
| Kraftstoffdruck | **3,0 bar**, geregelt (Aftermarket-Regler, Filter MANN WK 830/7) |
| Zündung | **Stock COP** (4× coil-on-plug, einzeln angesteuert) |
| Kurbelwellen-Trigger | Stock Hayabusa Gen1 Pickup |
| Nockenwellen-Trigger | Stock Hayabusa Gen1 Cam-Sensor |
| MAP-Sensor | MPX4250AP (250 kPa absolut) — derzeit nur 20-100 kPa genutzt (NA) |
| TPS | OEM Hayabusa |
| CLT / IAT | OEM Hayabusa NTC |
| Lambda | **noch nicht verbaut** — Wideband Nachrüstung geplant |
| Klopfsensor | **noch nicht verbaut** — Bosch 0 261 231 173 geplant |
| IAC / Idle-Steuerung | OEM passiv (FIAV Wachs-Element + Anschlagschraube) — keine ECU-Steuerung |
| Lüfter | OEM Thermoschalter (separater Kreis, nicht über ECU) |
| Quickshifter | externes Modul (eigenständig, ohne ECU-Eingriff) |
| Turbo | nicht verbaut |
| TunerStudio-Lizenz | **MS Ultra** — VE Analyze Live + AutoTune verfügbar |
| Datenlogger | **SD-Karte auf Dropbear v2** (on-board RTC + Logger) |

---

## 2. Projekt in TunerStudio öffnen

```text
File → Open Project → tune/Busa/Hayabusa-R1_2025-10-07_22.56.34.tsproj
                  oder direkt:
File → Open → tune/Busa/CurrentTune.msq
Communications → Connect → COMx (115200 Baud, RS232 Serial Interface)
```

Die Projekt-INI liegt in `tune/Busa/projectCfg/mainController.ini` — sie enthält den Fork-spezifischen Pin-Layout-Eintrag **„Hayabusa Gen1"**, der in der Standard-Speeduino-INI nicht existiert. Niemals diese INI durch eine offizielle Speeduino-INI ersetzen, sonst geht das Pin-Mapping verloren.

---

## 3. Engine Constants

Pfad: `Engine → Engine Constants → Engine and Sequential Settings`.

| Parameter | Wert | Begründung |
|---|---|---|
| `nCylinders` | 4 | Reihen-4 |
| `engineType` | Even fire | gleichmäßige Zündabstände |
| `twoStroke` | Four-stroke | |
| `nInjectors` | 4 | je Zylinder eine Düse |
| `injLayout` | **Sequential** | je Düse eigener Ausgang, in Phase mit Einlasshub |
| `injType` | **Port** | Düse hinter Drosselklappe vor Einlassventil — Hinweis: aktuell steht „Throttle Body" im Tune; **auf „Port" umstellen** |
| `inj4CylPairing` | 1+4 & 2+3 | nur relevant bei wasted-Inj — bleibt aus Sicherheit gesetzt |
| `pinLayout` | **Hayabusa Gen1** | Fork-Pinout |
| `algorithm` (Fuel Load) | **TPS (Alpha-N)** | Stock-Airbox liefert kaum sauberen MAP im Teillastbereich → Alpha-N stabiler |
| `multiplyMAP` | Baro | kompensiert Höhe/Wetter ohne MAP-basiertes Fuel |
| `mapSample` | Cycle Average | |
| `baroCorr` | Off | wird über `multiplyMAP=Baro` abgedeckt |
| `stoich` | 14,7 | Benzin E5/E10-Mittel |

### Required Fuel

In TunerStudio über `Tools → Calibrate Engine Constants → Calculate Required Fuel`:

| Eingabe | Wert |
|---|---|
| Displacement | 1299 cc |
| Cylinders | 4 |
| Injector flow | **211 cc/min @ 3 bar** (TODO verifizieren) |
| Target AFR | 14,7 |
| Injector layout | Sequential |

Aktueller Wert im Tune: `reqFuel = 13,2 ms`, `divider = 4`. Nach Bestätigung der Düsengröße neu berechnen — VE-Tabelle wird sich entsprechend skalieren, deshalb **vor jedem Reqfuel-Wechsel ein Restore-Point speichern**.

---

## 4. Trigger Setup

Pfad: `Engine → Triggers → Primary / Secondary`.

| Parameter | Wert |
|---|---|
| `TrigPattern` | Dual Wheel |
| `numTeeth` (primary) | 8 |
| `missingTeeth` | 1 |
| `trigPatternSec` | Single tooth cam |
| `TrigEdge` | FALLING |
| `TrigEdgeSec` | FALLING |
| `TrigSpeed` | Crank Speed |
| `TrigAng` | 102° |
| `FixAng` | 10° |
| `CrankAng` | 7° |
| `TrigFilter` | Off |
| `SkipCycles` | 3 |
| `useResync` | No |

**Verifikation nach Verkabelung (Pflicht):**

1. `Tools → Tooth Logger` starten.
2. Motor manuell durchdrehen (Anlasser, Kerzen raus, Kraftstoff aus).
3. Trigger-Muster prüfen: 7 echte Zähne + 1 Lücke pro Kurbelwellen-Umdrehung; Cam-Puls einmal pro Nockenwellen-Umdrehung.
4. `Sync Loss` und `Trigger Errors` müssen 0 sein.

Falls Sync nicht gefunden wird: `TrigEdge` auf RISING wechseln und erneut testen. Bei weiterhin keinem Sync → Stock-Pickup-Signal mit Oszilloskop kontrollieren (siehe `docs/INSTALLATION.md`).

---

## 5. Zündungs-Setup

Pfad: `Spark → Spark Settings`.

| Parameter | Wert | Anmerkung |
|---|---|---|
| `sparkMode` | **Sequential** | 4× COP einzeln |
| `IgInv` | Going Low | IGBT-Treiber active-low |
| `useDwellLim` | On | Schutz bei Aussetzern |
| `useDwellMap` | No | konstante Dwell-Tabelle reicht |
| `dwellErrCorrect` | On | Korrektur bei Trigger-Jitter |
| `sparkDur` | 1,2 ms | |
| **`dwellrun`** | **2,5 ms** | Stock-COP — vorhandener Wert 1,5 ms ist knapp; 2,5 ms gibt sauberen Funken ohne Spulen-Stress |
| **`dwellcrank`** | **4,0 ms** | **WARNUNG: Tune hat aktuell 15,0 ms — Stock-COP wird damit überlastet, runterstellen** |
| `dwellLim` | 6 ms | Hard-Cap |
| `Dwell Compensation` (Battery) | Standard-Tabelle | bei Spannungseinbruch im Cranking nötig |

### Hardware-Zündzeitpunkt-Kalibrierung (Pflicht beim ersten Aufbau)

1. `Spark → Base Timing` → `Fixed Timing` aktivieren, Wert **10°** (entspricht `FixAng`).
2. Stroboskop auf Zylinder 1.
3. Motor starten, Markierung am Polrad ablesen.
4. `TrigAng` so verstellen, dass Stroboskop exakt 10° vor OT zeigt.
5. Fixed Timing wieder ausschalten — ab jetzt arbeitet die Tabelle.

---

## 6. Kraftstoff-Setup

### 6.1 Düsen

| Parameter | Wert |
|---|---|
| `injOpen` (Dead-Time) | 1,2 ms @ 13,2 V — **bei Ladekurve nachjustieren, sobald wir eine echte Charakteristik haben** |
| `injBatRates` | Standard-Kurve (Spannungs-Korrektur) |
| `dutyLim` | 90 % | Schutz vor statischem Anliegen |

### 6.2 Cranking

| Parameter | Wert |
|---|---|
| `crankingPct` | 0 % (separate Cranking-Pulsewidth-Tabelle wird verwendet) |
| `Cranking PW` (Tabelle) | 6-10 ms je nach CLT — kalt höher, warm niedriger |
| `crkngAddCLTAdv` | No |

### 6.3 After-Start Enrichment (ASE)

`asePct` (4 Punkte über CLT), Standard-Speeduino-Werte als Start: 30 / 20 / 10 / 0 %, je 5 s. Anpassen wenn Motor nach Start kurz fett bleibt oder absäuft.

### 6.4 Warmup Enrichment (WUE)

10 Punkte über CLT (-40 °C bis 100 °C). Startwerte:

| CLT (°C) | -40 | -20 | 0 | 20 | 40 | 60 | 80 | 90 | 95 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| WUE (%) | 155 | 145 | 135 | 125 | 115 | 108 | 102 | 100 | 100 | 100 |

Während des Warmlaufens AFR per Wideband (sobald nachgerüstet) gegenchecken — AFR-Ziel kalt 12,5-13,0; warm 14,7 (Cruise) bzw. 12,8-13,2 (WOT).

### 6.5 Acceleration Enrichment (AE)

| Parameter | Wert |
|---|---|
| `aeMode` | TPS |
| `taeThresh` | 70 %/s |
| `taeMinChange` | 4 % |
| `aeTime` | 450 ms |
| `aeApplyMode` | PW Adder |
| `aeColdPct` | 100 % @ 0 °C → 0 % @ 60 °C |

### 6.6 DFCO (Schubabschaltung)

Aktivieren wie folgt:

| Parameter | Wert | Bemerkung |
|---|---|---|
| `dfcoEnabled` | **On** | |
| `dfcoRPM` | 3000 RPM | unter dieser Drehzahl wieder einspritzen |
| `dfcoHyster` | 250 RPM | Wiedereinsetz-Hysterese |
| `dfcoTPSThresh` | 2,0 % | unter diesem TPS gilt „Schub" |
| `dfcoMinCLT` | 60 °C | nicht im Kaltlauf |
| `dfcoDelay` | 1,0 s | Verzögerung vor Cut |

Funktion erst nach erfolgreicher Lambda-Nachrüstung scharf machen — ohne AFR-Überwachung kann zu mageres Wiedereinsetzen klopfen verursachen. Bis dahin `dfcoEnabled = Off` lassen.

---

## 7. Sensor-Kalibrierung

Pfad: `Tools → Calibrate Thermistor Tables` und `Tools → Calibrate TPS / MAP`.

### 7.1 TPS

1. Drosselklappe geschlossen → `Calibrate TPS → Get Current` → **Closed**.
2. Drosselklappe Vollgas → `Get Current` → **Full**.
3. Aktueller Tune: `tpsMin = 54 ADC`, `tpsMax = 214 ADC`. Werte werden bei Kalibrierung überschrieben.
4. Prüfung: TPS-% steigt linear 0 → 100 ohne Rücksprünge.

### 7.2 MAP — MPX4250AP

| Parameter | Wert |
|---|---|
| Sensortyp | MPX4250 (kann unter „Custom" angelegt werden) |
| Min | 20 kPa @ 0,2 V |
| Max | 250 kPa @ 4,8 V |
| `mapMin` | 20 kPa |
| `mapMax` | **100 kPa** (NA — bei Turbo später auf 250 erhöhen) |
| Stillstand | ~95-101 kPa je nach Wetter |

### 7.3 CLT / IAT — Stock Hayabusa NTC

| Parameter | Wert |
|---|---|
| Pull-up | 2,7 kΩ (Dropbear v2 default) |
| Bias | 5,0 V |
| Beta | 3435 K |
| Widerstand @ 20 °C | 2,3 kΩ |

Über `Tools → Calibrate Thermistor Tables → Built-in: Standard Bosch (β=3435)` auswählen, oder eigene 3-Punkt-Kalibrierung mit Eiswasser (0 °C), Raumtemperatur und kochendem Wasser (100 °C).

### 7.4 Baro

`baroPin = A0` im Hayabusa-Gen1-Pinout — wird vom Fork intern auf den Baro-Eingang gemappt (nicht mit dem TPS-Pin verwechseln). Beim ersten Schlüssel-an wird der MAP einmalig als Baro-Referenz gelesen.

### 7.5 Lambda (zukünftig)

Aktuell: `egoType = Wide Band`, `egoAlgorithm = No correction` → Sensor wird gelesen aber kein Closed-Loop. Sobald Wideband eingebaut:

| Parameter | Empfehlung |
|---|---|
| `egoAlgorithm` | Simple oder PID |
| `egoKP / egoKI / egoKD` | 80 / 60 / 50 (Startwerte für Simple) |
| `egoLimit` | 15 % |
| `egoRPM` | > 1500 |
| `egoTPSMax` | 70 % (kein Closed-Loop bei WOT) |
| `egoTemp` | 60 °C (CLT-Mindesttemperatur) |
| `ego_sdelay` | 30 s (Sensor-Aufheizen) |

---

## 8. Idle Control

Stock Hayabusa Gen1 hat **kein** ECU-gesteuertes IAC-Ventil. Kaltlauf-Anhebung erfolgt mechanisch über Wachs-Element (FIAV) am Drosselklappenkörper, Leerlaufdrehzahl wird mit der Anschlagschraube eingestellt.

| Parameter | Wert |
|---|---|
| `iacAlgorithm` | **None** |
| `idleAdvEnabled` | Off (zunächst) |

Sollte sich der Leerlauf bei warmem Motor als unstabil erweisen, kann **Idle Advance** (zusätzliche Zündverstellung im Leerlauf) als sanfte Stabilisierung aktiviert werden — siehe Abschnitt 12.

---

## 9. Drehzahlbegrenzer

| Parameter | Wert |
|---|---|
| `SoftRevLim` | 11 300 RPM |
| `SoftLimRetard` | 20° (Zündung zurück) |
| `SoftLimMax` | 2,0 s |
| `SoftLimitMode` | Fixed |
| `hardRevLim` | 11 500 RPM |
| `hardCutType` | Full (Spark + Fuel) |

Stock Hayabusa Gen1 Werks-Limit: 11 000 RPM. Werte oben geben minimalen Puffer ohne Mechanik zu überfordern.

---

## 10. Klopfregelung (geplant)

Aktuell: `knock_mode = Off`. Sobald Bosch 0 261 231 173 verbaut ist:

| Parameter | Empfehlung |
|---|---|
| `knock_mode` | On (Analog) |
| `knock_pullup` | Off (Sensor liefert eigenes Signal) |
| `knock_threshold` | 1,5 V (Startwert, am Klopfprüfstand kalibrieren) |
| `knock_maxRPM` | 9000 |
| `knock_maxMAP` | 100 kPa (NA) |
| Frequenz-Fenster | 6-8 kHz |
| `knock_firstStep` | 3° Retard pro Event |
| `knock_maxRetard` | 8° |

Bis dahin **alle Werte auf 0 lassen**, Kanal bleibt unbeschaltet.

---

## 11. AFR-Ziel-Tabelle (`afrTable`)

16×16, Achsen: RPM × TPS%. Konservative Startwerte:

| Bereich | Ziel-AFR |
|---|---|
| Idle (0-15 % TPS, 800-1500 RPM) | 14,2 |
| Cruise (10-40 %, 2000-6000 RPM) | 14,7 |
| Übergang (40-70 %, 3000-9000 RPM) | 13,5 |
| WOT (70-100 %, 5000-11 000 RPM) | 12,8 |

Diese Tabelle ist nur **Zielvorgabe** — bei `egoAlgorithm = No correction` wird sie nicht aktiv geregelt, dient aber als Referenz für VE Analyze Live (siehe Abschnitt 12).

---

## 12. Tuning-Workflow

### 12.1 Reihenfolge

1. **Statischer Test** (Motor aus): Spannungen, Sensorwerte, Trigger-Logger ohne Motorlauf.
2. **Trigger-Sync** beim Cranking: ohne Kraftstoff durchdrehen, RPM muss sauber stehen.
3. **Erststart**: Cranking PW konservativ, Wideband bereithalten (sobald verfügbar).
4. **Zündzeitpunkt-Kalibrierung** mit Stroboskop → Abschnitt 5.
5. **Warmlauf-Tuning**: WUE-Tabelle so anpassen, dass AFR während Aufwärmphase im Ziel bleibt.
6. **Leerlauf-Tuning**: VE-Zellen im Idle-Bereich justieren, Anschlagschraube falls nötig.
7. **Teillast-Tuning** (Cruise): VE Analyze Live im Cruise-Bereich, eine Variable pro Test.
8. **Volllast-Tuning** (WOT): **Prüfstand dringend empfohlen**, Logger an, fett starten und schrittweise mager werden.

### 12.2 VE Analyze Live (Ultra-Lizenz)

Pfad: `Tuning → VE Analyze Live`.

| Einstellung | Wert |
|---|---|
| Target | `afrTable` (siehe Abschnitt 11) |
| Filter | EGO active, RPM stabil, MAP/TPS stabil, CLT > 75 °C |
| Min Change | 1 % |
| Max Change | 5 % pro Iteration |
| Modus | Manual Approve (nicht Auto-Apply, bis VE-Tabelle gut gefüllt ist) |

Erst nach Lambda-Nachrüstung sinnvoll. Bis dahin VE-Tabelle manuell auf Basis von Stock-Hayabusa-Maps befüllen (Restore-Point `Busa_2025-10-07_23.39.55.msq`).

### 12.3 AutoTune (Ultra-Lizenz)

Im Datenlog-Modus: SD-Karte aus Dropbear v2 entnehmen → in TunerStudio öffnen → `Tools → Re-Tune VE Table from datalog`. Pflicht-Filter: nur stationäre Punkte (RPM-Stdabw < 50, AFR < 1,0 vom Ziel).

### 12.4 Datenlogging

| Parameter | Wert |
|---|---|
| Speicher | **SD-Karte auf Dropbear v2** (`rtc_mode = On-board`) |
| Lograte | 50 Hz (Standard reicht; bei Trigger-Debugging hochsetzen) |
| Pflicht-Kanäle | RPM, MAP, TPS, CLT, IAT, Battery, Sync Loss, Trigger Errors, AFR (sobald da), VE, Advance, Inj PW, Dwell, DFCO-Status, Knock-Status |

Logs nach jeder Sitzung mit `git lfs` (oder lokal außerhalb des Repos) sichern; nicht ins Hauptrepo committen — `tune/Busa/DataLogs/` ist `.gitignore`-kandidat.

---

## 13. Tune-Dateien und Backups

```
tune/Busa/
├── CurrentTune.msq               # aktive Konfiguration (live)
├── projectCfg/
│   ├── mainController.ini        # Fork-INI mit Hayabusa-Gen1-Pinout — NICHT überschreiben
│   └── project.properties        # Comm-Settings, Fenstergrößen
├── restorePoints/                # automatische Backups vor jeder Schreib-Aktion
│   ├── Busa_2025-10-07_23.39.55.msq
│   └── Busa_2026-01-26_21.07.19.msq
├── DataLogs/                     # SD-Karte + Live-Logs
└── TuneView/                     # TS-Layout (Fenster, Dashboards)
```

**Regeln:**
1. Vor jeder größeren Änderung manuell `File → Save As → restorePoints/Busa_<Datum>_<Beschreibung>.msq`.
2. Nach jeder erfolgreich getesteten Änderung committen — Message-Format: `tune(busa): <Bereich> <Was geändert>`.
3. Nicht zwei Personen gleichzeitig den Tune editieren.
4. Stratosphärisch wichtige Restore-Points zusätzlich auf SD-Karte ablegen.

---

## 14. Troubleshooting

### Motor startet nicht

| Symptom | Prüfen |
|---|---|
| Kein RPM beim Cranken | Tooth Logger → Trigger-Muster + Edges; Pickup-Spannung mit Skop |
| RPM aber kein Funke | `IgInv` korrekt? Coils mit LED-Tester; Dwell zu kurz? |
| Funke aber kein Sprit | Fuel Pump-Relais; Cranking PW; `injOpen`; Düsen klickern hörbar? |
| Sofort hohe RPM dann aus | Trigger-Sync verloren; `SkipCycles` zu niedrig; Cam-Edge falsch |

### Unrunder Leerlauf

1. Vakuum-Lecks Stock-Airbox / Drosselklappen-Wellen-Dichtung.
2. TPS-Kalibrierung neu machen.
3. VE-Zellen 800-1500 RPM × 5-15 % TPS prüfen.
4. Mechanische Anschlagschraube — Stock-Hayabusa hat keine ECU-IAC.

### Klopfen / Backfire

1. Zündungstabelle 5° zurück über betroffenen RPM/Last-Bereich.
2. AFR im Ziel? Zu mager → VE anheben.
3. Kraftstoffqualität (mind. 98 ROZ bei 12:1 Verdichtung).
4. Nach Klopfsensor-Einbau: Logs nach Klopf-Events durchsuchen.

### Sensor zeigt -40 °C oder 130 °C

| Anzeige | Ursache |
|---|---|
| -40 °C | offener Stromkreis (Kabelbruch, Stecker) |
| 130 °C+ | Kurzschluss gegen Masse oder defekter NTC |

---

## 15. Offene Punkte / TODO

- [ ] **Düsen-Größe verifizieren** (211 cc/min vermutet) → `Required Fuel` neu rechnen.
- [ ] **`dwellcrank` von 15 ms auf 4 ms reduzieren** — sicherheitskritisch für COPs.
- [ ] **`injType` auf „Port" umstellen** (aktuell „Throttle Body").
- [ ] Wideband-Lambda nachrüsten + EGO-Closed-Loop konfigurieren.
- [ ] Klopfsensor Bosch 0 261 231 173 verbauen + Schwellwert kalibrieren.
- [ ] DFCO erst nach Lambda scharfschalten.
- [ ] Lüfter-Schaltung später auf ECU umlegen (wenn gewünscht).
- [ ] Logging: `tune/Busa/DataLogs/` aus Repo ausschließen (`.gitignore`).

---

## 16. Ressourcen

- Speeduino Wiki: https://wiki.speeduino.com
- Speeduino Forum: https://speeduino.com/forum
- TunerStudio Manuals: http://tunerstudio.com/index.php/manuals
- HasiKe-Fork: https://github.com/HasiKe/speeduino
- Projekt-Doku:
  - [HARDWARE.md](HARDWARE.md)
  - [INSTALLATION.md](INSTALLATION.md)
  - [SOFTWARE.md](SOFTWARE.md)

---

**Version:** 3.0
**Stand:** April 2026
