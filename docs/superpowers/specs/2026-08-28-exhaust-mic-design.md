# Exhaust-Mic — Stereo-Tonaufnahmegerät für Motor- und Auspuffgeräusche

**Datum:** 2026-08-28
**Status:** Design freigegeben, Umsetzung offen
**Ort:** `hardware/exhaust-mic/`

---

## 1. Ziel

Zweikanaliges Audioaufnahmegerät, fest am Motorrad verbaut, das Motor- und Auspuffgeräusche
in hoher Qualität auf microSD schreibt. Aufnahmen müssen sich nachträglich mit extern
gedrehtem Videomaterial synchronisieren lassen.

### Anforderungen

| # | Anforderung | Quelle |
|---|---|---|
| R1 | Zwei unabhängige Mikrofonkanäle | Nutzer |
| R2 | Kanal A nah am Endrohr (bis ~132 dB SPL), Kanal B an Airbox/Motor (~110–120 dB SPL) | Nutzer |
| R3 | Pegel pro Kanal getrennt einstellbar | folgt aus R2 |
| R4 | Zeitstempel zur Synchronisation mit Videoaufnahmen | Nutzer |
| R5 | Versorgung aus 12-V-Bordnetz, fest verbaut | Nutzer |
| R6 | Deutlich günstiger als Teensy-4.1-Ansatz | Nutzer |
| R7 | Optionale CAN-Anbindung an eigene ECU, bestückungsoptional | Nutzer (Annahme) |
| R8 | Mikrofone abnehmbar (Steckverbinder, keine festen Pigtails) | Nutzer (Annahme) |

### Nicht-Ziele

- Echtzeit-DSP, Spektralanalyse auf dem Gerät
- Wiedergabe / Kopfhörerausgang
- Mehr als zwei Kanäle
- Automotive-Qualifizierung (AEC-Q100)

---

## 2. Systemübersicht

```
┌─ Mikrofonkopf A (Endrohr) ────────┐
│ IM73A135V01 → LDO 2.8 V           │      5-adriges geschirmtes
│ OPA2325 Unity-Buffer (2x)         ├──────Twisted-Pair-Kabel────┐
└───────────────────────────────────┘      3V3 / GND / OUT± / SH │
                                                                 │
┌─ Mikrofonkopf B (Airbox) ─────────┐                            │
│ identisch                         ├────────────────────────────┤
└───────────────────────────────────┘                            │
                                                                 ▼
┌─ Hauptplatine (unter Sitzbank) ─────────────────────────────────────────┐
│                                                                          │
│  CMC + Klemmung ─► PCM1863  ──I2S(Master)──►  ESP32-S3-WROOM-1-N8R2     │
│                    24 bit, PGA                 │                         │
│                       ▲                        ├─ microSD (SDMMC 4 bit)  │
│              24,576 MHz XO                     ├─ USB-C (nativ)          │
│                                                ├─ DS3231SN + CR2032      │
│  12 V ─ Schutz ─ Buck 4,2 V ─┬─ LDO 3V3_D ────┤   (I²C + 1 Hz SQW)      │
│                              └─ LDO 3V3_A      ├─ SN65HVD230 (optional)  │
│                                                ├─ Sync-LED + Piezo       │
│                                                └─ Taster REC / MARK      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Korrekturen gegenüber der ersten Auslegung

Nach Auswertung der Originaldatenblätter waren mehrere Annahmen falsch. Die
Korrekturen sind in dieser Spec bereits eingearbeitet.

| # | Annahme vorher | Datenblatt | Konsequenz |
|---|---|---|---|
| K1 | Mikrofon-VDD 3,3 V | **2,3–3,0 V**, typ. 2,75 V | Lokaler 2,8-V-LDO im Mikrofonkopf nötig |
| K2 | Mikrofon treibt Kabel direkt | **Cload ≤ 100 pF**, Rload ≥ 25 kΩ | Buffer im Mikrofonkopf nötig, sonst Kabellänge auf ~1 m begrenzt |
| K3 | ADC-Baustein PCM1861 mit I²C-PGA | **PCM1861 ist pingesteuert** und bietet nur 0 / 12 / 32 dB, für beide Kanäle gemeinsam | Verletzt R3. Wechsel auf **PCM1863** — gleiche Familie, gleiches Gehäuse, Pins 1–18 identisch, I²C/SPI, PGA **−12…+32 dB in 0,5-dB-Schritten je Kanal** |
| K4 | diff. Vollausschlag 2,1 Vrms, SNR 103 dB | **4,2 Vrms**, **SNR 110 dB** (PCM1861/63/65) | Mehr Headroom, ~8 dB besserer Rauschabstand als angenommen |
| K5 | CMRR ~65 dB (Schätzung) | **56 dB** | Schlechter als geschätzt; wird durch niederohmig gepufferte symmetrische Übertragung kompensiert |
| K6 | Mikrofon-AOP 133 dB SPL | **135 dB SPL @ 10 % THD**, 132 dB SPL @ 1 % THD | Auslegung auf 132 dB SPL Vollaussteuerung |
| K8 | PCM1863 hat einen Reset-Pin | Die softwaregesteuerten PCM186x haben **keinen** Reset-Pin; Rücksetzen erfolgt über Register oder Power-Cycle | GPIO17 wird stattdessen als Interrupt-Eingang an GPIO1/INTA (Pin 21) geführt |
| K9 | Abschaltung über `PWR_HOLD` am Buck-Enable | Der ESP32-S3 kommt im Deep-Sleep auf rund 20 µA, der LM5164 auf 10,5 µA | Die Abschaltlogik entfällt ersatzlos. Der Buck läuft dauerhaft mit einer Unterspannungsabschaltung bei 11,5 V, der ESP32 schläft. Spart Bauteile **und** beseitigt die Gefahr, dass sich das Gerät selbst aussperrt |
| K7 | ESP32-S3 kann CAN-FD, Transceiver TCAN1051 | ESP32-S3 hat **TWAI = CAN 2.0B, kein FD**; TCAN1051 braucht 4,5–5,5 V VCC, die Platine führt nur 4,2 V und 3,3 V | Transceiver **SN65HVD230D** (3,3 V, bis 1 Mbit/s), passt zu TWAI |

---

## 4. Mikrofonkopf (2× identisch)

### 4.1 Bauteile

| Ref | Bauteil | Funktion |
|---|---|---|
| MK1 | Infineon **IM73A135V01** | Analog-MEMS, differentiell, LGA-5, Bottom-Port |
| U1 | **TPS7A2028** (SOT-23-5) | 3,3 V → 2,8 V, rauscharm, entkoppelt Mikrofon vom Kabel |
| U2 | **OPA2325** (MSOP-8/SOIC-8) | Dual RRIO, Unity-Gain-Buffer je Ausgangszweig |
| — | 100 nF direkt am MK1-VDD-Pin | Datenblattvorgabe |
| — | 2× 100 Ω Serie in den Kabelzweigen | Stabilität des OPA2325 an kapazitiver Last, HF-Filter |
| — | 2× 47 kΩ, DNP | Reserve-Last, siehe unten |

Der Mikrofonausgang wird **gleichspannungsgekoppelt** an die Buffer-Eingänge geführt.
Das Mikrofon stellt seinen Ausgangs-VCM von 1,3 V selbst, ein externer Bias entfällt.
Die Lastwiderstände aus Figur 11 des Datenblatts sind nicht nötig — die 25 kΩ dort sind
die typische Messlast, die Datenblattwerte selbst gelten unbelastet. Footprints bleiben
als DNP-Reserve bestehen.

### 4.2 Auslegungsbegründung

Das Mikrofon spezifiziert **Cload ≤ 100 pF**. Geschirmtes Twisted-Pair liegt bei
50–100 pF/m Ader gegen Schirm. Ohne Buffer wäre die Kabellänge auf ~1 m begrenzt und
die Ausgangsstufe grenzwertig belastet. Der Buffer entkoppelt vollständig — das
Mikrofon sieht nur noch die ~5 pF Eingangskapazität des OPA2325.

Zusätzlich präsentiert der Buffer dem Kabel eine sehr niedrige Quellimpedanz an beiden
Zweigen. Da beide Zweige identisch getrieben werden, ist die Impedanzsymmetrie
exzellent — eingekoppelte Störungen bleiben Gleichtakt und werden vom PCM1863
unterdrückt, trotz dessen nur 56 dB CMRR.

Der lokale 2,8-V-LDO erfüllt K1 und verbessert gleichzeitig die Versorgungsentkopplung
(Mikrofon-PSRR gleichtakt nur 65 dB).

### 4.3 Kabel und Stecker

- 4 Adern + Gesamtschirm, 2× Twisted Pair: `3V3` / `GND`, `OUT+` / `OUT−`
- Schirm nur hauptplatinenseitig auf GND (kein Brummschleife)
- Steckverbinder: **TE Superseal 1.0, 5-polig** (Pin 5 = Schirm)
- Länge: bis 3 m unkritisch dank Buffer

### 4.4 Mechanik und Temperatur

⚠️ **Betriebstemperatur des Mikrofons: max. 85 °C.** Das ist die harte Grenze des
gesamten Kopfes, nicht der OPA2325 (bis 125 °C).

- Alu-Röhrchen mit Gitter, Kapsel vergossen, Bottom-Port über PCB-Schallloch
- Montage mit Silikon-Schwingungsentkopplung, **kein direkter Kontakt zum Krümmer**
- Hitzeschild zwischen Rohr und Kopf; Mindestabstand experimentell bestimmen
- Schaumwindschutz zwingend — sonst dominiert bei Fahrt Windrauschen alles andere
- IP57 des Mikrofons hilft gegen Spritzwasser, ersetzt aber kein dichtes Gehäuse

---

## 5. Analogpfad und Pegelplan

### 5.1 Pegelrechnung

Mikrofonempfindlichkeit −38 dBV @ 94 dB SPL = **12,6 mV/Pa differentiell**.

| SPL | Schalldruck | Mikrofonausgang (diff.) |
|---|---|---|
| 94 dB | 1,0 Pa | 12,6 mV rms |
| 120 dB | 20,0 Pa | 252 mV rms |
| 132 dB (1 % THD) | 79,6 Pa | **1,003 V rms** |
| 135 dB (10 % THD, AOP) | 112,5 Pa | 1,418 V rms |

PCM1863 differentieller Vollausschlag: **4,2 Vrms** bei 0 dB PGA.

### 5.2 Gain-Einstellung (Software, I²C)

PGA-Bereich −12…+32 dB in 0,5-dB-Schritten, je Kanal getrennt (Register
`PGA_VAL_CH1_L` / `PGA_VAL_CH1_R`).

| Kanal | PGA | Vollausschlag | entspricht SPL |
|---|---|---|---|
| A — Endrohr | **+12,5 dB** | 0,996 Vrms | **132,0 dB SPL** |
| B — Airbox | **+20,0 dB** | 0,420 Vrms | **124,4 dB SPL** |

Beide per I²C zur Laufzeit änderbar. Firmware implementiert zusätzlich eine
Übersteuerungsanzeige und optional automatische Absenkung.

### 5.3 Rauschbudget

A-bewertet, 20 Hz–20 kHz. PCM1863-Rauschmodell aus zwei Datenblattpunkten
(110 dB SNR @ 0 dB PGA, 90 dB SNR @ 32 dB PGA) → PGA-Eigenrauschen 3,33 µV,
ADC-Kern 12,88 µV eingangsbezogen.

| Beitrag | Kanal A (+12,5 dB) | Kanal B (+20 dB) |
|---|---|---|
| Mikrofon (−111 dBV(A)) | 2,82 µV | 2,82 µV |
| OPA2325-Buffer (2 Zweige) | 1,38 µV | 1,38 µV |
| PCM1863 eingangsbezogen | 4,52 µV | 3,57 µV |
| **Summe (RSS)** | **5,50 µV** | **4,75 µV** |
| Dynamikumfang | 105,2 dB | 98,9 dB |
| **Ersatzrauschpegel** | **26,8 dB(A) SPL** | **25,5 dB(A) SPL** |

Zum Vergleich: Eigenrauschen des Mikrofons allein entspricht 21,0 dB(A) SPL. Die
Elektronik addiert also 4,5–6 dB. Da ein laufender Motor bei >70 dB(A) liegt, ist
das ohne Bedeutung.

### 5.4 Eingangsbeschaltung Hauptplatine

Je Kanal, vom Stecker zum ADC:

1. TVS-Diodenarray gegen ESD und Harnischfehler
2. Gleichtaktdrossel (Audio-CMC, ~1 mH)
3. 100 Ω Serie + 33 pF gegen AGND je Zweig — HF-Filter, Eckfrequenz ~48 MHz, audioneutral
4. AC-Kopplung 1 µF (Mikrofon-VCM 1,3 V ≠ PCM1863-VCM)
5. Bias auf PCM1863-VCM

⚠️ **Bekannte Grenzwertverletzung:** PCM1863 hat 20 kΩ Eingangsimpedanz pro Pin, das
Mikrofon fordert Rload ≥ 25 kΩ. Durch den Buffer im Mikrofonkopf ist das entschärft —
der Buffer treibt die 20 kΩ mühelos, das Mikrofon selbst sieht die 47 kΩ Lastwiderstände.

---

## 6. ADC und Taktung

| Parameter | Wert |
|---|---|
| Baustein | **TI PCM1863** (TSSOP-30 DBT oder VQFN-32 RHB) |
| Auflösung | 24 bit |
| Abtastrate | 48 kHz Standard, 96 kHz optional |
| Eingang | 2× differentiell, VINL1±/VINR1± |
| SNR (diff., 0 dB PGA) | 110 dB typ, 97 dB min |
| THD+N (diff., 0 dB PGA) | −93 dB typ |
| Steuerung | I²C, Adresse per Pin 25 (MS/AD); Pin 26 (MD0) low = I²C |
| PGA | −12…+32 dB, 0,5-dB-Schritte, je Kanal getrennt |
| Betriebstemperatur | −40…+125 °C |
| Versorgung | AVDD/DVDD/IOVDD 3,3 V, AVDD-Strom 18 mA |

**Taktkonzept:** PCM1863 arbeitet als **I2S-Master**. Ein externer 24,576-MHz-CMOS-
Oszillator speist SCKI. Damit:

- 48 kHz = 512 × fs ✓
- 96 kHz = 256 × fs ✓

Beide Raten aus einem Oszillator. Der ESP32-S3 ist reiner I2S-Slave-Empfänger und muss
keinen audiogenauen Takt erzeugen — das eliminiert die gesamte Klasse von
MCU-Taktproblemen und macht den Jitter unabhängig vom Prozessorzustand.

---

## 7. MCU

**ESP32-S3-WROOM-1-N8R2** (8 MB Flash, 2 MB Quad-PSRAM, LCSC C2913204).

Begründung für N8R2 statt N8R8/N16R8: die Octal-PSRAM-Varianten belegen GPIO35–37
intern. 2 MB Quad-PSRAM reichen als Schreibpuffer für ~7 s Stereo-Audio bei 48 kHz/24 bit.

Genutzte Peripherie: I2S (Slave-RX), SDMMC-Host (4 bit), I²C, TWAI (CAN), USB-OTG,
UART, ADC1.

### 7.1 Pinbelegung

| Funktion | GPIO | Anmerkung |
|---|---|---|
| SD_CLK / CMD / D0 / D1 / D2 / D3 | 14 / 13 / 12 / 11 / 10 / 9 | SDMMC 4 bit |
| I2S BCK / LRCK / DIN | 5 / 6 / 7 | Slave-RX von PCM1863 |
| I²C SDA / SCL | 8 / 18 | PCM1863 + DS3231 |
| PCM1863 Interrupt (GPIO1/INTA) | 17 | |
| DS3231 1 Hz SQW | 15 | Interrupt, Sample-Latch |
| CAN TX / RX | 4 / 16 | TWAI = CAN 2.0B bis 1 Mbit/s, **kein CAN-FD**; optional bestückt |
| IGN-Sense / U-Batt | 1 / 2 | ADC1_CH0 / CH1 |
| Taster REC / MARK | 21 / 47 | |
| LED REC / ERR | 48 / 38 | |
| Sync-Blitz-LED / Piezo | 39 / 40 | Videosynchronisation |
| PGOOD des Buck-Reglers | 41 | Eingang |
| GPS UART TX / RX / PPS | 35 / 36 / 37 | Header, unbestückt |
| USB D− / D+ | 19 / 20 | fest verdrahtet |
| UART0 TX / RX | 43 / 44 | Konsole, auf Testpads |
| BOOT / RESET | 0 / EN | Taster |

Nicht belegt und bewusst freigehalten: GPIO3, 45, 46 (Strapping-Pins). GPIO26–32 sind
modulintern für den SPI-Flash belegt und nicht herausgeführt.

---

## 8. Zeitbasis und Videosynchronisation

Drei Ebenen, weil eine Wanduhr allein für Frame-Genauigkeit nicht reicht.

### 8.1 RTC

**DS3231SN**, SO-16, TCXO, ±2 ppm (0,17 s/Tag), −40…+85 °C, CR2032-Backup mit
interner Umschaltung.

Verworfen: PCF8563 — unkompensierter Quarz, 20–50 ppm temperaturabhängig. Im
Motorradheck mit −5…+60 °C Schwankung ergäbe das mehrere Sekunden Drift pro Tag.

### 8.2 NTP-Abgleich

Sobald das Fahrzeug im bekannten WLAN oder Hotspot steht, zieht die Firmware die RTC
per NTP nach. Kostet nichts, WiFi ist ohnehin im Modul.

### 8.3 Sample-genaue Zeitzuordnung

Der 1-Hz-Rechteckausgang der DS3231 liegt auf GPIO15 mit Interrupt. Bei jeder
Sekundenflanke wird der laufende I2S-Samplezähler gelatcht:

```
14:30:12 → Sample 66150000
14:30:13 → Sample 66198000
```

Ergebnis: driftfreie Abbildung Wanduhrzeit ↔ Audiosample über die gesamte Aufnahme,
unabhängig von Abtastratenfehlern des Oszillators.

### 8.4 Frame-genauer Marker

Weiße Power-LED (Blitz) plus Piezo-Summer. Bei Aufnahmestart und auf Tastendruck:
kurzer sichtbarer Blitz und hörbarer Piep, im Log mit exakter Samplenummer vermerkt.
Die Kamera nimmt Blitz und/oder Piep auf → im Schnittprogramm framegenau ausrichtbar.

Das ist die einzige Ebene, die tatsächlich Frame-Genauigkeit liefert. RTC und NTP
bringen auf ~100 ms.

### 8.5 Dateiformat

- Dateiname `YYYY-MM-DD_HHMMSS.wav`
- **BWF/BEXT-Chunk** mit `OriginationDate`, `OriginationTime`, `TimeReference`
  (Samples seit Mitternacht). DaVinci Resolve und Premiere lesen das und
  synchronisieren Clips automatisch.
- Sidecar-CSV: Samplenummer ↔ UTC je Sekunde, Marker-Events, CAN-Daten

### 8.6 Offengelassen: GPS

5-poliger Header (UART TX/RX, PPS, 3V3, GND) auf GPIO35–37. Ein u-blox-Modul für ~6 €
diszipliniert die Zeit später auf Mikrosekunden und liefert Geschwindigkeit und
Position dazu. Kostet jetzt nur den Footprint.

---

## 9. Stromversorgung

```
+12V ─ Sicherung 2 A ─ P-FET Verpolschutz ─ TVS SMBJ36A
     └─ LM5164 Buck (100 V Eingang, synchron, 10,5 µA Ruhestrom) ──► 4,6 V
             │
             ├─ Schottky-Verodung mit USB-C VBUS (Programmierung/Download)
             │
             ├─ TLV1117LV33 (SOT-223, 1 A)  ──► +3V3_D  ESP32, SD, PCM1863 DVDD/IOVDD, XO
             └─ TPS7A2033 (rauscharm)       ──► +3V3_A  PCM1863 AVDD, 2× Mikrofonkopf
```

**Warum LM5164 statt LMR36015:** 100 V Eingangsfestigkeit statt 60 V, damit ist der
Load-Dump auch ohne perfekt greifende TVS unkritisch. Ruhestrom 10,5 µA — Voraussetzung
für den Dauerplus-Betrieb.

**Warum 4,6 V Zwischenspannung:** nach den beiden Verodungsdioden bleiben 4,3 V. Der
TLV1117LV33 braucht bei 1 A nur 455 mV Dropout, es bleibt also knapp 1 V Reserve.
Gleichzeitig ist die Verlustleistung mit 1,0 V × 0,5 A = 0,5 W im SOT-223 beherrschbar.

⚠️ **Der LM5164 ist ein COT-Regler und braucht mindestens 20 mV Rippel am
FB-Knoten**, sonst schaltet er in Bursts. Umgesetzt als Type-2 nach Datenblatt
Tabelle 6-1: R7 = 0,1 Ω in Reihe zu den Ausgangskondensatoren, C5 = 100 pF parallel
zum oberen FB-Widerstand. Beide Werte sind am Aufbau zu verifizieren.

Schaltfrequenz nach Datenblattformel: f = V_out × 2500 / R_RON = 4,6 × 2500 / 28,7 kΩ
= **401 kHz**.

**Warum ein Buck plus LDOs statt zweier Bucks:** ein einziger Schaltregler, dessen
Störungen von beiden LDOs weggefiltert werden. Der Analogzweig bekommt einen
rauscharmen LDO mit hoher PSRR.

### 9.1 Strombudget

| Verbraucher | typisch | Spitze |
|---|---|---|
| ESP32-S3 (WiFi aus) | 60 mA | 355 mA (WiFi TX) |
| microSD Schreiben | 40 mA | 100 mA |
| PCM1863 (AVDD + DVDD) | 28 mA | 30 mA |
| Oszillator 24,576 MHz | 15 mA | 20 mA |
| 2× Mikrofonkopf | 3,2 mA | 4 mA |
| SN65HVD230 (optional) | 10 mA | 60 mA |
| **Summe @3,3 V** | **~150 mA** | ~580 mA |
| **Eingangsstrom @12 V** | ~55 mA | ~210 mA |
| Ruhezustand (ESP32 im Deep-Sleep) | ~65 µA | |

### 9.2 Zündungslogik

Das Gerät hängt an **Dauerplus**, `IGN` dient nur als Sense-Eingang.

Der Buck läuft dauerhaft; abgeschaltet wird über den Schlafzustand des ESP32, nicht
über die Versorgung. Das spart die gesamte Halte- und Abschaltlogik und kann das
Gerät nicht aussperren.

1. Zündung aus → IGN fällt → Firmware schließt WAV und CSV sauber
2. ESP32 geht in Deep-Sleep, Weckquelle ist die IGN-Flanke auf GPIO1 (RTC-fähig)
3. Zündung an → IGN steigt → ESP32 wacht auf und nimmt den Betrieb wieder auf

**Unterspannungsabschaltung:** Der UVLO-Teiler R2/R3 (1 M / 150 k) sperrt den Buck
unterhalb von rund 11,5 V. Damit kann das Gerät die Fahrzeugbatterie nicht tiefentladen.

Ruhestrom im Schlaf: LM5164 10,5 µA + ESP32-S3 Deep-Sleep ~20 µA + Spannungsteiler
22 µA + LDOs und RTC ~10 µA ≈ **65 µA**, also rund 1,6 mAh pro Tag.

---

## 10. Schnittstellen und Steckverbinder

| Ref | Typ | Belegung |
|---|---|---|
| J1 | TE Superseal 1.0, 6-polig | +12V, GND, IGN, CANH, CANL, EXT_BTN |
| J2 | TE Superseal 1.0, 5-polig | Mikrofon A: 3V3, GND, OUT+, OUT−, Schirm |
| J3 | TE Superseal 1.0, 5-polig | Mikrofon B: identisch |
| J4 | USB-C, 16-polig | Programmierung, Datendownload |
| J5 | microSD Push-Push | Platinenkante |
| J6 | Stiftleiste 5-polig, 2,54 mm | GPS: TX, RX, PPS, 3V3, GND — unbestückt |
| J7 | Stiftleiste 4-polig, 2,54 mm | I²C-Erweiterung: SDA, SCL, 3V3, GND |
| BT1 | CR2032-Halter | RTC-Backup |

---

## 11. EMV und Umgebung

| Risiko | Maßnahme |
|---|---|
| Zündspulen-Transienten auf Mikrofonkabel | Symmetrische Übertragung, niederohmig gepuffert, Gesamtschirm, Gleichtaktdrossel, TVS |
| PCM1863-CMRR nur 56 dB | Wird durch obige Maßnahmen aufgefangen. Rückfalloption: INA1650-Empfänger (90 dB CMRR) in Rev. B, ~+5 € inkl. 5-V-Schiene |
| Load-Dump am Bordnetz | 60-V-Buck, TVS SMBJ36A, Verpolschutz-P-FET |
| **WiFi-Sender neben 5-µV-Analogpfad** | Funk in Firmware hart abgeschaltet während Aufnahme. Antenne an gegenüberliegender Platinenkante, durchgehende Massefläche, Analogteil auf eigener AGND-Insel |
| Vibration | Gummi-entkoppelte Gehäusemontage, keine schweren Bauteile ohne Klebung |
| Hitze am Mikrofonkopf A | Hitzeschild, Abstandshalter, 85-°C-Grenze des Mikrofons einhalten |
| Feuchtigkeit | Gehäuse IP65+, gedichtete Steckverbinder, Mikrofonkapsel selbst IP57 |

**Layout:** 4 Lagen. Signal/AGND-Insel unter Analogteil und PCM1863, sternförmig am
ADC mit DGND verbunden. Schaltregler räumlich getrennt, Schleifenfläche minimal.

---

## 12. Firmware-Anforderungen

Nur Anforderungen, keine Implementierung — diese folgt in einem eigenen Plan.

| # | Anforderung |
|---|---|
| F1 | I2S-Slave-RX per DMA, doppelt gepuffert, in PSRAM-Ringpuffer |
| F2 | Schreiben nach SD mit vorallokierter Datei; WAV-Header beim Schließen gepatcht — Stromausfall kostet maximal einen Block |
| F3 | BWF/BEXT-Chunk mit RTC-Zeit beim Dateianlegen |
| F4 | 1-Hz-SQW-Interrupt latcht Samplezähler, Ausgabe in Sidecar-CSV |
| F5 | PCM1863-Konfiguration per I²C: PGA je Kanal, differentieller Eingangsmodus (VIN1P/M und VIN2P/M), Master-Mode, Abtastrate |
| F6 | Übersteuerungserkennung mit LED-Anzeige, optional automatische Gain-Absenkung |
| F7 | Zündungs-Zustandsautomat inklusive sauberem Herunterfahren und `PWR_HOLD`-Freigabe |
| F8 | Sync-Marker: LED-Blitz plus Piezo, Samplenummer protokolliert |
| F9 | WiFi ausschließlich außerhalb der Aufnahme; NTP-Abgleich der RTC |
| F10 | CAN-Empfang über TWAI, Frames mit Samplenummer in Sidecar-CSV (nur bei bestücktem SN65HVD230) |
| F11 | Download über USB-MSC oder WiFi |

---

## 13. Kostenschätzung

⚠️ Schätzwerte, Einzelstückpreise, noch nicht bei Distributoren verifiziert.

| Position | € |
|---|---|
| ESP32-S3-WROOM-1-N8R2 | 4,00 |
| PCM1863 | 5,00 |
| Oszillator 24,576 MHz | 0,80 |
| DS3231SN + CR2032-Halter | 2,50 |
| LMR36015 + Induktivität + Passive | 3,50 |
| 2× LDO | 1,50 |
| Schutzbeschaltung (P-FET, TVS, Sicherung) | 1,50 |
| SN65HVD230D (optional) | 1,20 |
| microSD-Sockel, USB-C, ESD | 1,80 |
| Sync-LED, Piezo, Taster, LEDs | 1,50 |
| Passive, CMC, Stecker J1–J3 | 9,00 |
| Leiterplatte 4 Lagen (5 Stück) | 2,50 |
| **Hauptplatine gesamt** | **~35** |
| 2× Mikrofonkopf (Mikrofon 2,50 + LDO + OPA2325 + Passive + PCB) | ~12 |
| Kabel, Alu-Röhrchen, Windschutz, Gehäuse | ~30 |
| **Gesamt** | **~77** |

Referenz Teensy-4.1-Variante: ~110 €.

---

## 14. Offene Punkte und Risiken

| # | Punkt | Umgang |
|---|---|---|
| O1 | PCM1863-Preis und Verfügbarkeit nicht verifiziert | Vor Bestellung bei LCSC/Mouser/DigiKey prüfen. PCM1863 ist teurer und schlechter verfügbar als PCM1861 |
| O2 | Lokale KiCad-Installation ist 7.0.11, die übrigen Repo-Dateien sind KiCad-10-Format | Schaltplan wird im KiCad-7-Format (20230121) erzeugt, damit er lokal per `kicad-cli` prüfbar ist. KiCad 10 öffnet und migriert ihn beim ersten Speichern |
| O7 | Werte für R7 (Rippel) und C5 (Feedforward) sind gerechnet, nicht gemessen | Am ersten Aufbau Schaltverhalten des LM5164 am Oszilloskop prüfen |
| O3 | CMRR 56 dB in realer Zündumgebung unerprobt | Nach Aufbau messen. Rückfall: INA1650 in Rev. B |
| O4 | Zulässige Einbauposition Mikrofon A bezüglich 85 °C | Vor Endmontage mit Thermoelement ausmessen |
| O5 | Kein Symbol/Footprint für IM73A135V01, PCM1863, LMR36015, LDOs im Repo | Projektlokale Bibliothek `lib/exhaust-mic.kicad_sym`. ESP32-S3-WROOM-1, DS3231M, OPA2325, SN65HVD230, Micro-SD und USB-C kommen aus den KiCad-Standardbibliotheken |
| O6 | 96-kHz-Betrieb erhöht SD-Durchsatz auf 576 kB/s | Unkritisch für SDMMC 4 bit, aber verifizieren |

---

## 15. Verifikationsplan

| Stufe | Prüfung |
|---|---|
| Schaltplan | `kicad-cli sch export netlist` — Parsebarkeit und Netzliste; manuelle Netzlistendurchsicht gegen diese Spec |
| Schaltplan | PDF-Plot, visuelle Prüfung aller Blätter |
| Schaltplan | Pinbelegung ESP32-S3 gegen Abschnitt 7.1 abgleichen; Strapping-Pins prüfen |
| Bestückung | Spannungen aller Schienen vor Einsetzen des Moduls |
| Inbetriebnahme | I²C-Scan findet PCM1863 und DS3231 |
| Audio | Sinus über Kalibrator, Pegelplan gegen Abschnitt 5.2 verifizieren |
| Audio | Rauschmessung bei abgeschlossenem Eingang, Vergleich mit Abschnitt 5.3 |
| EMV | Aufnahme bei laufendem Motor, Zündticken im Spektrum suchen |
| Zeit | Sync-Marker gegen Videoaufnahme prüfen, Restversatz messen |

---

## 16. Umsetzungsreihenfolge

1. Projektlokale Symbol- und Footprintbibliothek
2. Schaltplan Mikrofonkopf (klein, validiert Bibliothek und Vorgehen)
3. Hauptplatine, hierarchisch: Power → Analog → ADC → MCU → I/O
4. Netzliste und PDF verifizieren
5. BOM mit echten Distributorpreisen
6. PCB-Layout (eigener Plan)
7. Firmware (eigener Plan)
