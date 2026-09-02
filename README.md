# Hayabusa

Eigenbau-Motorsteuerung und Umbauprojekte für die Suzuki Hayabusa der ersten
Generation (1999–2007).

Das Repository hält alles an einer Stelle: die Schaltpläne und Layouts der
Steuergeräte, die Firmware, die Abstimmung, die mechanischen Umbauten und die
Papiere dazu. Die Speeduino-Firmware ist dabei der Ausgangspunkt, nicht das
Ergebnis — Platinen, Sensorik und die Motorrad-spezifischen Funktionen sind
eigene Arbeit.

---

## Inhalt

| Pfad | Inhalt |
|---|---|
| [`hardware/ECU/`](hardware/ECU) | Steuergerät: Schaltplan, Layout, Fertigungsdaten, Gehäuse |
| [`sensor-module/`](sensor-module) | Firmware des Sensor-Moduls (STM32G474) |
| [`speeduino/`](https://github.com/HasiKe/speeduino/tree/Hayabusa/ECU-R3) | Motorsteuerungs-Firmware, Submodul auf den eigenen Fork |
| [`hardware/exhaust-mic/`](hardware/exhaust-mic) | Zweikanalige Tonaufnahme von Motor und Auspuff |
| [`hardware/`](hardware) | Airbox, Turbo, Bremsen, Quickshifter, Verkleidung, Sitz |
| [`tune/`](tune) | TunerStudio-Projekte und Kennfelder |
| [`docs/`](docs) | Dokumentation und Spezifikationen |
| [`TÜV/`](TÜV) | Gutachten und Betriebserlaubnisse der verbauten Teile |

---

## Das Steuergerät

Ersetzt das Seriensteuergerät vollständig. Zweilagige Platine von rund
148 × 112 mm mit einem Teensy 4.1 als Rechenkern, Schaltplanstand
**Revision 3.0 (Entwurf)**.

### Leistungsteil

| Baustein | Aufgabe |
|---|---|
| MC33810 | Einspritzung und Zündung über SPI, vier Kanäle je Pfad |
| 4× ISL9V5036 | Zünd-IGBTs an den Gate-Treibern des MC33810 |
| 3× ZXMS6006 | Low-Side für Kraftstoffpumpe, Lüfter, Starter, Drehzahlmesser, FI-Lampe |
| 2× BTF3050TE | High-Side für Ladedrucksteller und Lambdaheizung, mit Stromfühler |
| DRV8434A | Schrittmotor für den Leerlaufsteller |

### Signalaufbereitung

| Baustein | Aufgabe |
|---|---|
| MAX9926 | Zwei Kanäle Induktivgeber für Kurbelwelle und Nockenwelle |
| TPIC8101 | Klopfsensor mit programmierbarem Bandpass und Integrator |
| LMV324 | Puffer für Lambda, Komparator für den Kippschalter |
| SP720 / BAV199 | Klemmung sämtlicher Sensoreingänge |

### Versorgung und Infrastruktur

| Baustein | Aufgabe |
|---|---|
| LM74700 + SQM120N06 | Verpolschutz als aktive Diode |
| TPS54360B | Abwärtswandler auf 5 V, automotive-tauglich |
| TPS3823 | Externer Watchdog, verriegelt bei Ausfall die Endstufen |
| W25Q32 | SPI-Flash als Kennfeldspeicher |
| MCP2562 | CAN zum Sensor-Modul und zum Cockpit |
| ADXL343 | Beschleunigungssensor, bestückt, softwareseitig ungenutzt |

Vollständige Pinbelegung, Kalibrierhinweise und die offenen Punkte der
Revision 3.0: **[HAYABUSA_ECU_R3.md](https://github.com/HasiKe/speeduino/blob/Hayabusa/ECU-R3/HAYABUSA_ECU_R3.md)**

---

## Firmware

Fork von [Speeduino](https://github.com/speeduino/speeduino), Branch
[`Hayabusa/ECU-R3`](https://github.com/HasiKe/speeduino/tree/Hayabusa/ECU-R3),
eingebunden als Submodul.

```bash
git submodule update --init
cd speeduino && pio run -e teensy41_hayabusa
```

In TunerStudio Board **57 „Gen1 Hayabusa ECU R3"** wählen.

Was über den Serienstand von Speeduino hinausgeht:

- **Vier umschaltbare Kennfeldsätze** für Kraftstoff, Zündung und Ladedruck.
  Auswahl beim Einschalten über Kupplung und Vollgas, Rückmeldung über
  FI-Lampe und Drehzahlmesser.
- **Klopfregelung** mit dem TPIC8101: Konfiguration über SPI,
  Integrationsfenster am Zündfunken, Auswertung über Speeduinos
  Zündrücknahme.
- **Externer Watchdog**, der nur bedient wird, solange die Hauptschleife
  läuft — bleibt sie hängen, fallen Einspritzung und Zündung ab.
- **Motorrad-Ein- und Ausgänge**: Neutral, Kupplung, Gangsensor,
  Kippschalter, FI-Lampe, Lambdaheizung.
- **Kennfelder im SPI-Flash** statt in der EEPROM-Emulation des Teensy, die
  für vier Sätze zu klein ist.

---

## Sensor-Modul

Zweite Platine, 120 × 64 mm, eigener STM32G474. Nimmt der Motorsteuerung alles
ab, was langsam ist, und meldet es über CAN.

- vier Abgastemperaturen über MAX31855K-Thermoelementwandler
- Öldruck, Kraftstoffdruck, Abgasdruck, Öltemperatur
- zwei Wassertemperaturen im Ladeluftkühlerkreis
- Quickshifter-Geber
- Regelung des Ladeluftkühler-Lüfters, lokal und damit unabhängig vom CAN-Bus

Firmware, CAN-Protokoll und die Zuordnung zu Speeduinos Eingangskanälen:
[`sensor-module/README.md`](sensor-module/README.md)

---

## Exhaust-Mic

Eigenständiges Projekt: zweikanalige Tonaufnahme von Motor- und
Auspuffgeräuschen. Zwei Mikrofonköpfe mit 135 dBSPL Grenzschalldruck an einem
24-bit-Stereo-ADC, aufgezeichnet von einem ESP32-S3 auf microSD, mit
Zeitstempeln zur Synchronisation mit Videomaterial.

Schaltpläne, Layout, Gehäuse und Firmware entstehen aus Python-Generatoren —
Pinbelegung und Netznamen stehen dadurch nur an einer Stelle.

[`hardware/exhaust-mic/README.md`](hardware/exhaust-mic/README.md) ·
[Auslegung und Rauschbudget](docs/specs/2026-08-28-exhaust-mic-design.md)

---

## Mechanik

| Projekt | Inhalt |
|---|---|
| [Airbox](hardware/Airbox) | Airbox mit integriertem Ladeluftkühler, CAD |
| [Turbo](hardware/Turbo) | Aufladung mit GT3071R, Auslegung und Teileplanung |
| [Bremsen](hardware/brakes) | Brembo-Umbau |
| [Quickshifter](hardware/quick-shifter) | Schaltautomat |
| [Carbon-Verkleidung](hardware/Carbon-Verkleidung) · [Sitz](hardware/sitz) · [Reifen](hardware/Reifen) | Fahrwerk und Aufbau |
| [Wireless Charging](hardware/wireless%20charging) · [High-Beam-Flash](hardware/High-Beam-Flash) | Kleinigkeiten |

---

## Stand

| Bereich | Stand |
|---|---|
| Steuergerät, Schaltplan | Revision 3.0 im Entwurf, Revision 1 gefertigt |
| Steuergerät, Firmware | Läuft, auf aktuellem Speeduino-Stand |
| Sensor-Modul, Hardware | Revision 3.0 im Entwurf |
| Sensor-Modul, Firmware | Übersetzt, noch nicht am Fahrzeug erprobt |
| Exhaust-Mic | Schaltplan und Layout fertig, Fertigung offen |
| Grundabstimmung | In Arbeit |
| Turbo-Umbau | In Planung |

Was vor der ersten Fahrt noch geprüft werden muss — Polarität des
Kippschalters, Kennlinien der Temperaturgeber, Klopfschwellen — steht in
[HAYABUSA_ECU_R3.md](https://github.com/HasiKe/speeduino/blob/Hayabusa/ECU-R3/HAYABUSA_ECU_R3.md)
und im [README des Sensor-Moduls](sensor-module/README.md).

---

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [HARDWARE.md](docs/HARDWARE.md) | Platinen, Steckerbelegung, mechanische Daten |
| [SOFTWARE.md](docs/SOFTWARE.md) | Firmware-Aufbau, Build, Codestruktur |
| [INSTALLATION.md](docs/INSTALLATION.md) | Einbau, Verkabelung, Inbetriebnahme |
| [TUNING.md](docs/TUNING.md) | Kennfelder, Kalibrierung, Abstimmung |
| [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Aufbau des Repositories |
| [CHANGELOG.md](CHANGELOG.md) | Versionshistorie |

Externe Quellen: [Speeduino-Wiki](https://wiki.speeduino.com) ·
[Speeduino-Forum](https://speeduino.com/forum) ·
[TunerStudio](http://tunerstudio.com)

---

## Lizenz

Die Firmware im Submodul steht unter GPL v3, wie Speeduino selbst. Hardware
und Dokumentation stehen unter CC BY-SA 4.0. Fremdsoftware liegt nicht im
Repository, sondern wird bei Bedarf aus der jeweiligen Quelle geladen.

## Haftungsausschluss

Ein selbst gebautes Steuergerät greift in Zündung und Kraftstoffzufuhr ein.
Fehler darin führen zu Motorschaden oder zum Ausfall während der Fahrt. Der
Nachbau erfolgt auf eigene Verantwortung, und im Geltungsbereich der StVZO
erlischt mit solchen Eingriffen die Betriebserlaubnis, solange kein Gutachten
vorliegt.
