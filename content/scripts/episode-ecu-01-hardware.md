# Episode: ECU Hardware – Warum ich meine eigene baue

**Format:** YouTube Longform
**Länge Ziel:** 10–13 min (~1700–2000 Wörter gesprochen bei ~150 wpm)
**Zielgruppe:** Leute die selbst eine Standalone-ECU planen oder sich für Motorsteuerungen interessieren
**Style-Referenz:** Hoodinformatik – duzen, Denglisch okay, viel Screencast/Whiteboard, wenig Talking-Head, kein Sarkasmus, technisch aber zugänglich
**Cut-Strategie:** Aus diesem Longform werden 3–5 Insta-Reels geschnitten (Marker im Skript: `[REEL-CUT #x]`)

---

## Legende

- `[VO]` – Voiceover, im Off aufgenommen
- `[ON-CAM]` – Du im Bild
- `[SCREEN: X]` – Screencast oder Standbild einblenden
- `[WHITEBOARD: X]` – animierte Zeichnung/Diagramm (Motion Graphics)
- `[B-ROLL: X]` – Nahaufnahme Werkstatt / PCB / Bike
- `[SFX: X]` – Sound Effect
- `[TEXT-OVERLAY: X]` – Bauchbinde/Callout on screen
- `[MUSIC: X]` – Musik-Cue
- `[REEL-CUT #x START/END]` – Marker für Insta-Cut
- `[ASSET-TODO: X]` – Asset das du noch produzieren musst

---

## 0. Cold Open (0:00 – 0:20)

`[REEL-CUT #1 START]`

`[B-ROLL: Close-up Hayabusa-Krümmer, dann Schwenk auf leere ECU-Position im Rahmen]`
`[SFX: Startversuch Motor – kurzes Zucken, dann Stille]`

`[VO]`
> „Wenn du deine Hayabusa turbot, gibt's ein Problem, das dir keiner sagt: die originale ECU spielt nicht mit. Und die coolen Standalones vom Markt? Kosten dich dein halbes Bike. Also hab ich meine eigene gebaut."

`[SCREEN: Hero-Shot der fertigen ECU-Platine, langsame Rotation, Bokeh]`
`[TEXT-OVERLAY: "Teensy 4.1 · 4-Layer · Custom PCB"]`
`[MUSIC: Beat setzt ein – lo-fi elektronisch]`

`[VO]`
> „Heute zeig ich dir das ganze Teil. Jeder Ein- und Ausgang, warum ich's so gemacht hab – und wo ich mich verrannt hab. Los geht's."

`[TEXT-OVERLAY: Titel – "Ich baue meine eigene ECU. Warum? Und wie?"]`

`[REEL-CUT #1 END]`

---

## 1. Warum überhaupt selbst bauen? (0:20 – 2:00)

`[ON-CAM: Kurz am Schreibtisch, ECU in der Hand]`

`[VO]`
> „Kurz zur Einordnung: ich rüste eine Hayabusa auf Turbo um. Ziel: 230 bis 250 PS. Und die Serien-ECU von Suzuki kann genau eins – exakt das fahren, was Suzuki 1999 vorgesehen hat. Zündkennfeld ändern? Nope. Ladedruck-Regelung? Gibt's nicht mal ein Menü für."

`[WHITEBOARD: Kreis "Serien-ECU" mit rot durchgestrichenen Features: Zündmap, Boost, Lambda-Regelung, Datenlogger]`

`[VO]`
> „Klar – ich könnte mir eine Haltech, MoTeC oder ECUMaster kaufen. Kosten drei- bis viertausend Euro, funktionieren top. Aber zwei Punkte, warum ich das nicht mache."

`[TEXT-OVERLAY: „Grund 1: Lernen"]`

`[VO]`
> „Erstens: ich will's verstehen. Nicht nur 'Wert eintippen, Knopf drücken, hoffen dass es läuft.' Ich will wissen, was mein Injektor macht, wenn ich in TunerStudio ein Feld ändere. Und das lernst du nur, wenn du das Ding selbst gelötet und geflasht hast."

`[TEXT-OVERLAY: „Grund 2: Kontrolle"]`

`[VO]`
> „Zweitens: keine Einschränkungen. Wenn ich in zwei Jahren beschließe, ich brauch acht Einspritzdüsen statt vier – kann ich. Wenn ich Anti-Lag will – bau ich rein. Wenn ich morgen einen neuen Sensor teste – Firmware-Update, done. Bei einer Blackbox von der Stange bist du auf das limitiert, was der Hersteller freigibt."

`[ASSET-TODO: KiCad-Screenshot mit erweitertem Injektor-Layout einblenden bei "acht Einspritzdüsen"]`

`[VO]`
> „Und ganz ehrlich: es macht einfach Spaß. Punkt."

`[REEL-CUT #2 START]`

`[B-ROLL: Timelapse SMD-Bestückung unterm Mikroskop, dann Hand hält die Platine ins Licht]`
`[TEXT-OVERLAY: „Warum eine eigene ECU bauen? Kontrolle. Und Spaß."]`

`[REEL-CUT #2 END]`

---

## 2. Was macht eine ECU überhaupt? (2:00 – 3:30)

`[VO]`
> „Bevor wir in die Platine reingehen – kurz das große Bild. Was macht eine ECU eigentlich?"

`[WHITEBOARD: Diagramm animiert aufbauen]`
- Links: Sensoren-Icons (Kurbelwelle, Nockenwelle, MAP, TPS, Lambda, Temperatur)
- Mitte: Box mit „Motorsteuerung"
- Rechts: Aktuator-Icons (Injektor, Zündspule, Leerlaufsteller)

`[VO]`
> „Ganz simpel: links kommen Sensordaten rein. Kurbelwellenwinkel, Drosselklappenstellung, Saugrohrdruck, Temperaturen. Die ECU rechnet – wie viel Sprit, wann Zündung, wann Injektor auf, wann zu. Und schickt das rechts raus an Injektoren und Zündspulen. Zwei Millisekunden Reaktionszeit. 100 mal pro Sekunde. Ohne Aussetzer."

`[SCREEN: Live-Screencast TunerStudio – Datenlogger läuft, RPM zappt hoch]`

`[VO]`
> „Das heißt: deine ECU ist im Prinzip ein Echtzeit-Computer mit Motor als Peripherie. Und wenn du willst, dass sie das mit einem Turbo, einem anderen Kraftstoff und dreifachem Ladedruck macht, brauchst du – überraschend – einen ordentlichen Prozessor."

---

## 3. Der Prozessor: Teensy 4.1 (3:30 – 5:30)

`[SCREEN: Close-up des Teensy 4.1 – rotierend, Beschriftung sichtbar]`
`[TEXT-OVERLAY: „Teensy 4.1 – ARM Cortex-M7 · 600 MHz · 1 MB RAM · 8 MB Flash"]`

`[VO]`
> „Das Herz von meinem Board ist ein Teensy 4.1. Kleiner ARM Cortex-M7 mit 600 Megahertz. Zum Vergleich: die Original-Hayabusa-ECU von 1999 lief mit 32-Bit bei 40 Megahertz. Wir haben also mal eben Faktor 15 mehr Rechenleistung – und das kostet dich 30 Euro."

`[WHITEBOARD: Timeline mit ECU-Prozessoren: Original 1999 → Speeduino ATmega 2010 → Teensy 4.1 heute]`

`[VO]`
> „Kurz zum Kontext: das ganze Projekt basiert auf Speeduino. Speeduino ist ein Open-Source-Firmware-Projekt, ursprünglich für Arduino Mega mit ATmega2560 – 16 Megahertz, 8-Bit. Läuft, aber wird eng, wenn du sequentielle Einspritzung und viele Sensoren gleichzeitig willst."

`[VO]`
> „Der Teensy 4.1 ist quasi der aktuelle Top-Level-Support in der Speeduino-Welt. Native CAN Bus – ich brauch keinen externen Controller. USB Host – ich kann direkt einen Logger anschließen. Ethernet-fähig – ist für später geplant. Plus: er hat genug freie GPIOs, dass ich am Ende noch Reserven habe."

`[ON-CAM kurz]`
> „Kurzer Realtalk: hätte ich auch STM32 nehmen können. Wär billiger. Aber der Teensy hat einen riesen Vorteil – es gibt fertige Speeduino-Ports dafür. Ich baue also nicht die Firmware von Null auf, sondern kann auf einer stabilen Codebasis aufsetzen. Was mir realistisch geschätzt sechs Monate Arbeit spart."

`[SCREEN: GitHub Repo speeduino/speeduino, board_teensy41.cpp öffnen, scrollen]`

---

## 4. Die Basis: Dropbear v2 – aber angepasst (5:30 – 6:30)

`[SCREEN: KiCad Schaltplan-Übersicht ECU.kicad_sch – Reingezoomt auf Hauptseite]`

`[VO]`
> „Mein Board ist kein Dropbear v2 aus der Schublade. Es ist eine Weiterentwicklung – ich hab die Speeduino-Dropbear-Referenz genommen, alles aufgetrennt und neu aufgebaut."

`[WHITEBOARD: Blockdiagramm mit 8 Feldern]`
- Power-Regulator
- Sensor-Eingänge
- Crank & Cam
- Klopfsensor
- Treiber (Injektoren/Zündung)
- Kommunikation (USB/CAN)
- Konnektoren
- Sensor-Modul (extern)

`[VO]`
> „Warum? Weil die Hayabusa ein paar Eigenheiten hat, die die Standard-Speeduino-Boards nicht abbilden. Zum Beispiel: Suzuki-typisch ein 24-1-Triggerrad statt 36-1. Und ich will einen richtigen Klopfsensor mit TPIC8101-Chip – nicht nur einen billigen Piezo-Verstärker."

`[SCREEN: KiCad – auf knock-sensor.kicad_sch wechseln, TPIC8101 markieren]`
`[TEXT-OVERLAY: „TPIC8101 – dedicated Knock-Signal-Prozessor"]`

`[VO]`
> „Vier Layer PCB. 100 mal 80 Millimeter. Automotive-grade Komponenten. Der ganze Kram ist ausgelegt für minus 40 bis plus 85 Grad – weil im Sommer neben dem Turbo-Krümmer wird's warm."

---

## 5. Die Eingänge – jeden einzeln (6:30 – 9:00)

`[SCREEN: KiCad Schematic – Inputs.kicad_sch offen, dann pro Sensor rangezoomt]`

`[VO]`
> „Jetzt gehen wir jeden Ein- und Ausgang durch. Fange mit den Sensoren an."

`[REEL-CUT #3 START]`
`[TEXT-OVERLAY: „Jeder einzelne Sensor – erklärt"]`

### 5.1 TPS – Throttle Position Sensor
`[SCREEN: KiCad Zoom auf A0/TPS-Schaltung]`
> „TPS – die Drosselklappenstellung. Analog-Eingang A0. Kommt als Null-bis-Fünf-Volt-Signal von einem Potentiometer an der Drosselklappe. Simpel. Ein RC-Filter davor gegen Störungen. Fertig."

### 5.2 MAP – Manifold Absolute Pressure
`[SCREEN: KiCad Zoom auf A3/MAP]`
> „MAP – der Saugrohrdruck. Für Turbo-Aufbauten der wichtigste Sensor überhaupt. Ich hab hier bewusst einen 4-bar-Sensor statt dem 2,5-bar-Serienteil verbaut, damit ich später auch positiven Ladedruck bis 2,5 bar messen kann."
`[TEXT-OVERLAY: „4 bar Sensor – für zukünftigen Boost"]`

### 5.3 CLT / IAT – Temperaturen
`[SCREEN: KiCad Zoom auf A1/A2]`
> „Kühlmittel- und Ansauglufttemperatur. Beides NTC-Thermistoren. Bedeutet: Widerstand ändert sich mit Temperatur. Einfacher Spannungsteiler mit Referenzwiderstand, ADC misst die Spannung, Firmware rechnet in Grad um. Zehn Bauteile, kein Hexenwerk."

### 5.4 Lambda / O2
`[SCREEN: KiCad Zoom auf A4]`
> „Lambda-Sonde. Ich fahre eine Wideband, die gibt Null bis Fünf Volt raus – umgerechnet auf AFR-Werte. Wichtig: die Wideband hat ihren eigenen Controller. Ich lese nur das analoge Ausgangssignal. Der teure Controller sitzt extern."

### 5.5 Batteriespannung
`[SCREEN: KiCad Zoom auf A5]`
> „Batteriespannung mess ich für Injektoren-Kompensation. Injektor-Öffnungszeit ändert sich mit Bordspannung – wenn der Anlasser dreht, sackt die Spannung ab, und die Firmware muss die Einspritzung nachregeln. Sonst läuft dir der Motor beim Kaltstart mager."

### 5.6 Klopfsensor
`[SCREEN: KiCad Zoom auf knock-sensor.kicad_sch]`
> „Klopfsensor – aktuell noch WIP. Piezo-Element vom Motorblock, geht in einen TPIC8101. Der Chip filtert schon in Hardware auf die Resonanzfrequenz vom Motor – bei der Hayabusa liegt die zwischen 6 und 8 Kilohertz. Kommt als sauberes Signal beim Teensy an."

### 5.7 Crank & Cam
`[SCREEN: KiCad Zoom auf Crank-and-Cam.kicad_sch]`
> „Und der wichtigste Input überhaupt: Kurbelwelle und Nockenwelle. Ohne die weiß die ECU nicht, wo der Motor gerade steht. Kurbelwellensignal kommt als VR-Signal – variable Reluktanz, Wechselspannung. Muss durch einen Komparator, damit der Teensy es als sauberen Digital-Puls sieht. Genau das macht der MAX9924."

`[TEXT-OVERLAY: „MAX9924 – VR Sensor Interface"]`

`[REEL-CUT #3 END]`

---

## 6. Die Ausgänge (9:00 – 10:30)

`[SCREEN: KiCad Actuators.kicad_sch]`

### 6.1 Injektoren
`[VO]`
> „Vier Low-Side-Treiber für die Injektoren. Bedeutet: Injektor hängt permanent auf 12 Volt, die ECU zieht die Masse durch. Warum Low-Side? Weil ein N-MOSFET billiger, schneller und robuster ist als ein P-MOSFET auf der Plus-Seite. Und weil jede Automotive-ECU das so macht. Wichtig: Flyback-Diode parallel zum Injektor. Sonst grillst du den MOSFET beim Abschalten – der Injektor ist eine Spule, und die will beim Ausschalten unbedingt weiter Strom fließen lassen."

`[WHITEBOARD: Schaltung MOSFET + Injektor + Flyback-Diode – Strompfeile animiert]`

### 6.2 Zündspulen
`[VO]`
> „Zündungsausgänge – vier Stück, jeweils mit IGBT-Treiber. IGBTs statt MOSFETs, weil Zündspulen mit Peak-Strömen von 10 bis 15 Ampere arbeiten und die Schaltvorgänge härter sind. Der IGBT verträgt das langfristig zuverlässiger."

`[TEXT-OVERLAY: „IGBT – für die harten Schaltvorgänge"]`

### 6.3 Weitere Ausgänge
`[VO]`
> „Dazu kommen noch: Leerlaufsteller-Ansteuerung, Kraftstoffpumpe-Relais, Boost-Solenoid für spätere Wastegate-Regelung. Alle über Reserve-GPIOs vom Teensy und einen kleinen Treiber-Baustein."

---

## 7. Was mir auf die Füße gefallen ist (10:30 – 11:30)

`[ON-CAM: Direkt in die Kamera, ehrlich]`

`[VO]`
> „Kurzer Reality Check – nicht alles lief smooth."

`[REEL-CUT #4 START]`
`[TEXT-OVERLAY: „3 Fails, die mich Nerven gekostet haben"]`

`[WHITEBOARD: „Sackgassen" – 3 Fehler animiert einblenden]`

`[VO]`
> „Erstens: erste Version hatte den VR-Sensor-Input direkt am Teensy dran. Ohne Komparator. Klar hat's Signal geliefert – aber zittrig, mit Jitter, RPM-Anzeige hat gezuckt wie ein Wackeldackel. MAX9924 nachgerüstet, Problem weg."

`[VO]`
> „Zweitens: Massefläche im ersten Layout war nicht durchgängig. Analog-Sensoren haben Rauschen gehabt, das ich mir nicht erklären konnte. Vier-Layer-PCB heißt: eine ganze Ebene ist reine Massefläche. Sofort besser."

`[VO]`
> „Drittens – der Klassiker: Polung des Injektor-Steckers vertauscht in KiCad-Symbol. Erste Platine bekommen, gemerkt, geflucht. Zweite Revision musste ich extra bestellen. Kostenpunkt: eine Woche Wartezeit und ein halber Kaffee mehr am Tag."

`[TEXT-OVERLAY: „Lesson: Symbol-Pinout dreimal checken. Immer."]`

`[REEL-CUT #4 END]`

---

## 8. Ausblick + Nächstes Video (11:30 – 12:30)

`[SCREEN: Split-Screen – links KiCad Schematic, rechts VS Code mit Speeduino-Code]`

`[VO]`
> „Das war die Hardware. Aber Hardware ohne Firmware ist nur ein teurer Untersetzer. Im nächsten Video geht's genau darum: wie ich den Speeduino-Fork angepasst hab. Was ich am Trigger-Code umgeschrieben hab, damit das Hayabusa-24-1-Triggerrad läuft. Wie das Ganze in TunerStudio auftaucht. Und warum ich am Ende einen eigenen Branch fahre und nicht den Mainline-Speeduino."

`[REEL-CUT #5 START]`
`[B-ROLL: ECU mit angesteckten Kabeln, LEDs blinken, Teensy USB-Port]`
`[TEXT-OVERLAY: „Nächstes Video: Firmware – wie ich Speeduino umgeschrieben habe"]`
`[REEL-CUT #5 END]`

`[VO]`
> „Bis dahin – wenn dich das Projekt interessiert, alle KiCad-Files, die Firmware, die Tune-Maps – alles auf GitHub. Link in der Beschreibung. Fragen zur Hardware? Kommentare sind offen."

`[SCREEN: End-Screen mit Video-Vorschau nächste Folge + GitHub-Link]`
`[MUSIC: Outro-Beat fadet]`

---

## Shot- und Asset-Liste

### Was du produzieren/besorgen musst

| Asset | Wofür | Priorität |
|-------|-------|-----------|
| Hero-Shot der ECU rotierend (Bokeh, weißer Hintergrund) | Cold Open, Reel #1 | Hoch |
| Timelapse SMD-Bestückung unterm Mikroskop | Reel #2 | Hoch |
| Close-up Teensy 4.1 rotierend | Section 3 | Mittel |
| Live-Screencast TunerStudio Datenlogger | Section 2 | Mittel |
| KiCad-Screenshots pro Sensor (7 Stück) | Section 5 | Hoch |
| KiCad-Screenshot Actuators-Übersicht | Section 6 | Hoch |
| KiCad-Screenshot knock-sensor + TPIC8101 markiert | Section 5.6 | Mittel |
| GitHub-Screencast speeduino/board_teensy41.cpp | Section 3 | Niedrig |
| B-Roll ECU mit blinkenden LEDs + USB | Section 8, Reel #5 | Hoch |
| Whiteboard-Animationen (7 Stück siehe Skript) | Motion Graphics | Hoch |

### Kamera-Setup

- **Cam A:** Sony ZV-E10 II auf Stativ, Frontal-Talking-Head, 4K/50 fps
- **Cam B:** DJI Pocket 3 als B-Roll, handgeführt oder Overhead-Mount, 4K/50 fps
- **Overhead:** Handy oder GoPro über Schreibtisch für KiCad-Screencasts – oder direkter Bildschirm-Grab via OBS
- **Audio:** Rode Wireless Pro Lav für VO getrennt aufnehmen im Zimmer, nicht im Video-Ton
- **Licht:** 2x LED-Panel 5000K, ein Softbox von schräg oben, ein Fill von rechts

### Editing-Notes

- **B-Roll-Ratio anstreben:** 60 % B-Roll/Screencast, 40 % Talking-Head
- **VO nach dem Rohschnitt** aufnehmen – so kannst du Timing der Bilder freier gestalten
- **Whiteboard-Animationen:** in After Effects oder mit Rive/Lottie – halte den Look konsistent (gleiche Font, gleiche Strichfarbe)
- **Sound Design:** dezente „Whoosh"-SFX bei Screen-Transitions, aber sparsam
- **Musik:** ein Track durchgehend im Background, unter -20 dB unter VO
- **Farb-Look:** leicht entsättigt, warmer Tint – nicht überstilisiert. Hoodinformatik-mäßig „echt aber sauber"

---

## Insta-Reel-Cut-Übersicht

| Reel | Aus Skript | Länge Ziel | Hook |
|------|------------|------------|------|
| #1 | Cold Open (0:00–0:20) | 20 s | „Deine Hayabusa turbot? Deine ECU macht nicht mit." |
| #2 | Ende Section 1 (~1:50) | 30 s | „Warum eine eigene ECU bauen? Kontrolle. Und Spaß." |
| #3 | Sensoren-Rundgang komprimiert | 45 s | „Jeder Sensor an einer Standalone-ECU – in 45 Sekunden." |
| #4 | Section 7 (Fails) | 30 s | „3 Fails beim ECU-Bau, die mich Nerven gekostet haben." |
| #5 | Ausblick Section 8 | 15 s | „Nächstes Video: die Firmware." |

Jedes Reel als eigenständige Story bauen – nicht nur reiner Ausschnitt.
