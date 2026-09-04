# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).
Die Abschnitte folgen der tatsächlichen Repository-Historie (erster Commit
2024-11-06). Vergeben ist bisher nur das Tag **v0.1** (2025-10-01); die übrigen
Überschriften sind Zeitabschnitte, keine Releases.

## [Unreleased]

### Hinzugefügt
- TunerStudio-Projekt `tune/Hayabusa-R3` für die Rev 3 (Board 57), generiert aus den Serienkennfeldern in `tune/setup/maps.ods` (`tools/gen_tune.py`), Erststart-Konfiguration mit Checkliste im README
- Firmware-Fork: Kanalzuordnung nach Zündfolge 1-2-4-3 am Serienstecker, Batteriespannungs-Skalierung für den 47k/10k-Teiler, TunerStudio-INI korrigiert (ignTrim auf Seite 13, Load-Achsen der Kennfeldsätze 3/4, boostTable3/4)
- Exhaust-Mic als Submodul `hardware/exhaust-mic` (HasiKe/Exhaust-Mic)
- Innovate LC-2 mit LSU 4.9 als Lambda-Lösung festgelegt und in `docs/BESTELLUNG.ods` aufgenommen

### Geändert
- Dokumentation (HARDWARE, SOFTWARE, INSTALLATION, TUNING, PROJECT_STRUCTURE) komplett auf die Rev 3 und das neue Tune-Projekt umgeschrieben; die Dropbear-Beschreibungen der Rev 1 entfallen
- Sensor-Modul-Firmware in den Speeduino-Fork verschoben (`speeduino/sensor-module/`)

### Entfernt
- Alte TunerStudio-Projekte (`tune/Busa`, `tune/Hayabusa-R1`) samt Dashboards und Datenlogs
- Verwaistes `smc_test`-Projekt aus `hardware/ECU`
- Repository auf die Elektronik beschränkt: `hardware/` enthält nur noch `ECU/` und `exhaust-mic/`; Zwischenstände des Layouts, extern geladene Werkzeuge und Datenlogs bleiben lokal

### Offen
- Erster Motorlauf mit dem Tune `Hayabusa-R3` (Trigger-Winkel, Kalibrierungen, Kanalzuordnung am Fahrzeug bestätigen)
- Sensor-Modul am Fahrzeug erproben, CAN-Eingänge im Tune aktivieren
- Klopfsensor Bosch 0 261 231 173 verbauen und Schwelle kalibrieren
- Fertigung der Rev-3-Platinen und des Exhaust-Mic

## 2026-08 bis 2026-09

### Hinzugefügt
- Exhaust-Mic: Spezifikation, Schaltpläne (Hauptplatine und Mikrofonkopf), gerenderte PDFs, Layout
- Sensor-Modul-Firmware (STM32G474)

### Geändert
- ECU-Hardware auf den Stand der Revision 3.0 gebracht (Schaltplan und Layout beider Platinen)

## 2026-04 bis 2026-05

### Hinzugefügt
- Explosionszeichnungen der Suzuki-Ersatzteilkataloge, Drehmomenttabelle, ARP- und Wössner-Einbauanleitungen
- Berechnungen zur Auslegung (`docs/Berechnungen.ods`)

### Geändert
- Verzeichnisstruktur: `Hardware/` umbenannt zu `hardware/` (Kleinschreibung)
- Speeduino-Submodul von `speeduino/speeduino` auf den Fork `HasiKe/speeduino` gewechselt, Pfad des `teensy.pretty`-Submoduls korrigiert
- Dokumentation überarbeitet (Dropbear v2, Klopfsensor)

## [v0.1] - 2025-10-01

Erstes Tag. Stand: ECU-Layout der Revision 1 gefertigt, Abstimmung mit dem
TunerStudio-Projekt `Hayabusa-R1`.

### Hinzugefügt
- Serienkennfelder aus dem Original-Steuergerät (`tune/setup/maps.ods`)
- Pinout-Blatt des Serien-Steuergeräts

### Geändert
- ECU-Layout in Schritten v0.1 bis v0.3, überarbeitete 5-V-Versorgung
- KiCad-Projekt auf Version 9 gehoben

## 2024-11 bis 2025-05

### Hinzugefügt
- Projektstart: KiCad-Projekt des Steuergeräts, zweilagige Platine
- Submodule `speeduino` und `hardware/ECU/lib/teensy.pretty`
- Eigene Symbol- und Footprint-Bibliotheken für die Automotive-Bausteine
- Erstes TunerStudio-Projekt

---

## Kategorien

- **Hinzugefügt**: Neue Features
- **Geändert**: Änderungen an bestehenden Features
- **Entfernt**: Entfernte Inhalte
- **Behoben**: Bugfixes
- **Offen**: Noch nicht erledigt
