# Software-Dokumentation

## Firmware

Fork von [Speeduino](https://github.com/speeduino/speeduino), Stand 2025.04-dev
(TunerStudio-Signatur `speeduino 202504-dev`).

| Parameter | Wert |
|---|---|
| Repository | [HasiKe/speeduino](https://github.com/HasiKe/speeduino), Branch `Hayabusa/ECU-R3` (lokal `Hayabusa/ECU-R3-v2`) |
| Einbindung | Submodul `speeduino/` |
| Board | Teensy 4.1, TunerStudio-Board **57 „Gen1 Hayabusa ECU R3"** |
| PlatformIO-Umgebung | `teensy41_hayabusa` (`-DUSE_SPI_EEPROM -DSPI_FLASH_ATOMIC_TRANSFERS -DHAYABUSA_ECU_R3`) |
| Lizenz | GPL v3 |
| Notizen | `speeduino/HAYABUSA_ECU_R3.md` |

```bash
git submodule update --init
cd speeduino
pio run -e teensy41_hayabusa            # bauen
pio run -e teensy41_hayabusa -t upload  # flashen
```

Nach dem ersten Brennen eines Tunes mit Board 57 die ECU aus- und einschalten: Pinmapping,
MC33810-Initialisierung und Watchdog werden nur beim Start übernommen.

## Was der Fork gegenüber Speeduino ergänzt

Alles in `speeduino/speeduino/src/hayabusa/` und nur aktiv mit `HAYABUSA_ECU_R3` und
Board 57.

| Funktion | Umsetzung |
|---|---|
| Pinmapping | `src/pins/pinMapping.cpp`, `getHayabusaR3Mapping()`: alle Pins fest, Injektoren und Spulen über MC33810-Bits; Kanal 3 → Zylinder 4, Kanal 4 → Zylinder 3 (Zündfolge 1-2-4-3) |
| Kennfeldspeicher | W25Q32 statt EEPROM-Emulation (`board_teensy41.cpp`): 264 Sektoren × 31 Byte = 8184 Byte, Standardlayout unverändert, Zusatztabellen ab Adresse 4096 |
| Watchdog | `hayabusa_r3.cpp`: TPS3823 wird aus dem 1-kHz-Timer bedient, aber nur wenn die Hauptschleife seit dem letzten Kick gelaufen ist; während `initialiseAll()` bedingungslos |
| Ausgabefreigabe | D2 mit Watchdog-Reset über NAND auf MC33810-OUTEN; Kippschalter (D34, 500 ms entprellt) nimmt die Freigabe weg |
| Klopfen | `knock_tpic8101.cpp`: TPIC8101 per SPI konfiguriert, Fenster am Zündfunken, Wert auf 2-ms-Fenster normiert an Speeduinos analoge Klopfrücknahme; Build-Flags `HAYABUSA_KNOCK_BANDPASS_INDEX`, `_GAIN_INDEX`, `_INTEGRATOR_INDEX`, `_WINDOW_US` |
| Motorrad-I/O | Neutral, Kupplung, Gangsensor (Schwellen `HAYABUSA_GEAR_THRESHOLDS`), Kippschalter (`HAYABUSA_TIPOVER_INVERTED`), FI-Lampe, Lambdaheizung (3 s nach Drehzahl > 0 an), Treiberfehler-Eingang |
| Kennfeldsätze | vier Sätze Kraftstoff/Zündung/Ladedruck; Satz 1 = Standardtabellen, Satz 2 = Speeduinos Zweittabellen, Sätze 3/4 = Seiten 16–21; Auswahl in `mapselection.cpp` (`speeduino.ino`: `getActiveFuelTable()`) |
| Batteriespannung | `sensors.cpp readBat()`: Vollausschlag 18,8 V für den 47 k/10 k-Teiler (`HAYABUSA_R3_BATTERY_FULL_SCALE_10`) |
| SPI-Bus | vier Teilnehmer mit eigenen Transaktionen; Flash und Klopf-IC sperren Interrupts, solange ihr CS aktiv ist |

### Kennfeldsatz wählen

Zündung einschalten mit Vollgas und gezogener Kupplung. FI-Lampe blinkt die Satznummer,
Drehzahlmesser zeigt Satz × 1000. Jeder Kupplungszug schaltet weiter (4 → 1), drei
Sekunden gehalten bestätigt (nach mindestens einem Loslassen), zehn Sekunden ohne
Eingabe = Satz 1. Die Auswahl wird nicht gespeichert. Satz 2 schaltet Speeduinos
Zweittabellen-Blending ab; `fuel2Mode` und `spark2Mode` bleiben Aus.

Voraussetzung ist ein gültiger Low-Pegel am Kupplungseingang, siehe Befund 1 in
[HARDWARE.md](HARDWARE.md).

## TunerStudio

- INI: `speeduino/reference/speeduino.ini`. Im Projekt unter *Project Properties →
  Settings* „Hayabusa multi map switching = Enabled" wählen, sonst fehlen die Seiten
  16–21. Nicht mit dem seriellen Kompatibilitätsmodus kombinierbar.
- Setting-Groups des Projekts: `mcu_teensy`, `HAYABUSA_MULTIMAP`, `CELSIUS`, `AFR`,
  `pressure_bar`, `enablehardware_test`, `resetcontrol_standard`.
- Korrekturen der INI auf diesem Branch (September 2026): `ignTrim1..8` von Seite 6 (dort
  überschrieben sie `airDenRates`, `boostFreq`, `vvtFreq`, `idleFreq` und das Launch-Byte)
  auf Seite 13 Offset 42; Load-Achsen der Kennfeldsätze 3/4 folgen dem Last-Algorithmus
  statt fester kPa-Skalierung; `boostTable3/4` mit Skalierung 2,0; `unused0_126` auf
  Bit 0–1.
- Klopfmodus **Analog**; Pin-Einstellung wird auf diesem Board ignoriert.
- Kalibrierungen (Thermistoren, AFR-Sonde, TPS) liegen im Kennfeldspeicher, nicht in der
  .msq. Sie müssen nach jedem Neubeschreiben des Flashs erneut gesendet werden.

## Tune-Projekt und Generator

`tune/Hayabusa-R3/` (siehe dortiges README): `CurrentTune.msq`,
`projectCfg/mainController.ini` (Kopie der Fork-INI), `project.properties`,
`tools/gen_tune.py`. Das Tune wird generiert:

```bash
python3 tune/Hayabusa-R3/tools/gen_tune.py
python3 tune/Hayabusa-R3/tools/dumptables.py tune/Hayabusa-R3/CurrentTune.msq veTable advTable1
```

- `stockmaps.py` liest die Serienkennfelder aus `tune/setup/maps.ods` (Blätter `VE_org`,
  `IGN_org`), korrigiert die Tippfehler der Drehzahlachsen und interpoliert bilinear.
- `iniparse.py` liest die INI mit `#if`-Auswertung; `gen_tune.py` prüft jede Konstante
  gegen Optionsliste, Bereich und Auflösung und schreibt alle 21 Seiten.
- Parameter (Düsen, VE-Skalierung, Zündrücknahme, Trigger, Dwell, Begrenzer) im Dict `P`,
  Einzelwerte im Dict `E`. Änderungen dort, nicht in der .msq von Hand.

## Code-Orientierung

```
speeduino/speeduino/
├── speeduino.ino                 Hauptschleife, getActiveFuelTable()/getActiveIgnitionTable()
├── src/hayabusa/hayabusa_r3.*    Watchdog, OUTEN, Schalter, Gangsensor, Lampe, Heizung
├── src/hayabusa/knock_tpic8101.* Klopf-IC
├── src/hayabusa/mapselection.*   Kennfeldwahl beim Einschalten
├── src/pins/pinMapping.cpp       getHayabusaR3Mapping() (Board 57)
├── acc_mc33810.cpp               MC33810-Treiber, übernimmt die Bit-Arrays aus dem Pinmapping
├── board_teensy41.*              SPI-Flash als EEPROM
├── storage.cpp / pages.cpp       Seiten 16–21 ab Adresse 4096
├── decoders.cpp                  Dual-Wheel-Decoder (8 Zähne + Nockenpuls)
├── sensors.cpp                   readBat() mit Board-57-Skalierung
└── fuel_calcs.cpp                reqFuel = Kraftstoff je Zylinder und Arbeitsspiel bei VE 100 %
speeduino/sensor-module/          STM32G474-Firmware des Sensor-Moduls, CAN-Protokoll im README
speeduino/reference/speeduino.ini TunerStudio-Definition
```

## Offene Punkte

- Kippschalter-Polarität am Fahrzeug prüfen (`HAYABUSA_TIPOVER_INVERTED`); falsch
  gepolt schaltet die Firmware während der Fahrt ab.
- Gangsensor-Schwellen kalibrieren (`hayabusaStatus.gearRaw` beobachten).
- Klopfparameter gegen eine Klopfaufzeichnung prüfen, bevor die Rücknahme scharf ist.
- `hayabusaStatus` (umgekippt, Freigabe, Treiberfehler, Gang) ist in TunerStudio nicht
  sichtbar; ein Statusbyte in den Ausgabekanälen wäre sinnvoll.
- Sensor-Modul-Firmware übersetzt, am Fahrzeug nicht erprobt; CAN-Eingänge im Tune Aus.

---

**Version**: 4.0
**Stand**: September 2026
