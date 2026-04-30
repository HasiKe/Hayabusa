# Tuning-Guide

## Grundsätze

1. **Sicherheit zuerst** – konservative Werte, Wideband O2 Pflicht
2. **Datenbasiert** – niemals blindes Tuning
3. **Progressiv** – kleine Schritte, eine Änderung pro Test
4. **Validiert** – jede Änderung loggen und prüfen

## Tune-Dateien

Aktuelle Konfigurationen befinden sich in:

```
tune/Busa/CurrentTune.msq       # Aktuelle Tune
tune/Busa/restorePoints/        # Backups
```

**Wichtig**: Vor jeder Änderung Backup erstellen!

## Voraussetzungen

### Hardware
- Wideband O2 Sensor (AFR-Messung)
- Laptop mit TunerStudio
- Optional: EGT-Sensoren für Volllast-Tuning

### Software
- TunerStudio MS
- Verbindung zur ECU hergestellt

## Tuning-Prozess

### 1. Sensor-Kalibrierung

#### TPS
1. `Engine → Sensor Calibration → TPS`
2. Drosselklappe geschlossen → Learn Closed
3. Drosselklappe voll offen → Learn WOT
4. Prüfung: 0-100% ohne Sprünge

#### MAP
- Motor aus: sollte atmosphärischen Druck zeigen (~100 kPa auf Meereshöhe)

#### Temperatursensoren
- Kaltstart: CLT/IAT sollten Umgebungstemperatur zeigen

### 2. Leerlauf-Tuning

**Vorgehen:**
1. Motor vollständig warmfahren
2. Leerlauf-AFR mit Wideband beobachten
3. VE-Tabelle in Leerlauf-Zellen anpassen bis Ziel-AFR erreicht
4. Stabilität prüfen

### 3. Teillast-Tuning (Cruise)

**Datenerfassung:**
- Wideband O2 aktiv
- Konstante Geschwindigkeiten fahren
- Datenlogger mitlaufen lassen

**VE-Anpassung:**
- TunerStudio VE Analyze oder manuell
- Zellen anpassen bis Ziel-AFR erreicht

### 4. Volllast-Tuning (WOT)

**Warnung**: Prüfstand empfohlen!

**Vorgehen:**
1. Mit fettem Gemisch starten (sicher)
2. Timing konservativ halten
3. Schrittweise optimieren
4. Auf Klopfen achten

## TunerStudio Tools

### VE Analyze Live
Automatische VE-Korrektur basierend auf AFR-Abweichung.

### Tooth Logger
Trigger-Signal visualisieren und Sync prüfen.

### Data Logging
Alle Parameter aufzeichnen für Analyse.

## Troubleshooting

### Motor startet nicht
- Trigger-Signal prüfen (Tooth Logger)
- Fuel Pump Relais prüfen
- Required Fuel / Cranking Enrichment prüfen

### Unrunder Leerlauf
- TPS-Kalibrierung prüfen
- Vacuum-Lecks suchen
- VE in Leerlauf-Zellen anpassen

### Klopfen
- Timing reduzieren
- Gemisch anfetten
- Kraftstoffqualität prüfen

## Ressourcen

- [Speeduino Wiki - Tuning](https://wiki.speeduino.com/en/Tuning)
- [TunerStudio Documentation](http://tunerstudio.com/index.php/manuals)

---

**Wichtig**: Dieses Dokument enthält nur allgemeine Tuning-Prinzipien. Spezifische Werte müssen am Fahrzeug ermittelt werden.

**Version**: 2.0
**Stand**: April 2026
