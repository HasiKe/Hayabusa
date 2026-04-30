# Turbo-Umbau Planung - Hayabusa Gen 1

**Stand:** 26.02.2026  
**Änderung:** Turbo von GT2860RS auf GT3071R geändert (mehr Potenzial, bessere Langzeitoption)  
**Ziel:** 230-250 PS mit Serienmotor (keine internen Mods zunächst)  
**Phase:** Selbstbau (kein Komplett-Kit)

---

## Entscheidungen

### Turbo
- **Modell:** ~~Garrett GT2860RS~~ → **Garrett GT3071R** (Update 26.02.2026)
- **Grund:** Mehr Potenzial oben raum (350-400 PS limit), guter Kompromiss aus Ansprechverhalten und Leistungspitze
- **Alternative:** GT3076R (noch mehr Luft für 400+ PS, etwas träger)
- **Wastegate:** Intern (im Turbo integriert) - spart Platz
  - **Wichtig:** GT3071R mit IWG (Internal Wastegate) bestellen!
- **Specs GT3071R (IWG Version):**
  - Compressor: 71mm inducer, 0.70 A/R compressor housing
  - Turbine: 60mm exducer, .82 A/R turbine housing (passt gut zur Hayabusa-Drehzahl)
  - Wastegate: **Intern (IWG)** – integriert im Turbinengehäuse
  - Limit: ~350-400 PS (viel Headroom für spätere Upgrades)

### Positionierung
- **Lage:** Unter dem Motor / vor dem Motor
- **Krümmer:** Direkt vom Motor in den Turbo
- **Position:** Zwischen Motor und Kühler (wo das Abgasregelventil war)
- **Hinweis:** Hitzeabschirmung zum Kühler notwendig!

### Ladeluftkühler (Intercooler)
- **Typ:** Luft-Wasser Kühler
- **Integration:** In die Airbox eingebaut
- **Status:** Bereits geplant/fast fertig
- **Fehlt noch:** Wasserkühler für den Kreislauf

### Blow-off Ventil
- **Größe:** 25mm Anschluss (reicht für 250 PS)
- **Empfehlung:** Turbosmart Kompact Serie
- **Kosten:** ~150-200€
- **Ladedruck:** Ausgelegt für 0.3-0.5 Bar
- **Position:** Zwischen Turbo und Ladeluftkühler
- **Varianten:**
  - Offen = laut, Luft raus (einfacher)
  - Geschlossen/Recirculating = leiser, Luft zurück (sauberer)

### Ölversorgung
- **Öl-Feed:** Vom Motor zum Turbo
- **Öl-Rücklauf:** Direkt in Ölwanne (geht bei dieser Höhe)
- **Wichtig:** Ölfilter direkt vor dem Turbo!
- **Alternative:** Scavenger Pumpe falls Rücklauf nicht funktioniert

### ECU
- **System:** Speeduino (bereits vorhanden)
- **Status:** Muss noch getestet werden
- **Anpassungen nötig:**
  - Ladedruck-regelung über Wastegate
  - Zündzeitpunkt retardieren (Klapperschutz)
  - AFR anpassen (11.5-12.5 unter Last)
  - Einspritzdüsen anpassen

---

## Noch benötigte Teile

### Sofort
- [ ] Garrett GT3071R Turbo (0.70 A/R compressor, .82 A/R turbine)
- [ ] Krümmer (selbst bauen oder kaufen)
- [ ] Blow-off Ventil (25mm, z.B. Turbosmart Kompact)
- [ ] Ölleitungen (Feed + Return)
- [ ] Ölfilter (vor Turbo)
- [ ] Hitzeabschirmung (zum Kühler)

### Später (wenn Turbo/Krümmer stehen)
- [ ] Ladeluftschläuche (Maße abhängig vom Setup)
- [ ] Schellen
- [ ] Wasserkühler für Ladeluft-Kreislauf
- [ ] Boost-Manometer (optional)
- [ ] Boost-Controller (manuell oder über ECU)

### Upgrade (falls Motor später geöffnet wird)
- [ ] Kolben 9.5:1 (Wossner) - für mehr Boost
- [ ] Pleuel (Wossner/Carrillo) - ab 300 PS nötig
- [ ] Ventilfedern 65lbs - für höhere Drehzahl
- [ ] Größere Einspritzdüsen (440cc+) - für 300+ PS

---

## Technische Details

### Ladedruck
- **Ziel:** 0.3-0.5 Bar (für Serienmotor sicher)
- **Leistung:** ~230-250 PS
- **Regelung:** Über internes Wastegate

### Kompression
- **Stock Gen 1:** 11:1
- **Problematisch:** Bei höherem Ladedruck (>0.5 Bar) Klopfen möglich
- **Lösung:** Erstmal nur 0.3-0.5 Bar, später Kolpen tauschen auf 9.5:1

### Kühlung
- **Turbo:** Wasserkühlung empfohlen (bei Position unter Motor)
- **Ladeluft:** Luft-Wasser Kühler in Airbox
- **Motor:** Standard-Kühler + Lüfter

### Tuning
- **AFR unter Last:** 11.5-12.5 (reicher für Kühlung)
- **Zündung:** Retardieren um Klopfen zu vermeiden
- **Sensor:** Wideband Lambda zwingend nötig!

---

## Nächste Schritte
1. Turbo (GT3071R) bestellen
2. Krümmer planen/bauen
3. Ölleitungen routen
4. Blow-off Ventil beschaffen
5. ECU testen und Basismap erstellen
6. Wideband Lambda installieren

## Links & Ressourcen
- Garrett GT2860RS Spezifikationen
- Turbosmart Kompact Ventil
- Hayabusa.org Forum (Turbo Builds)

---

**Notizen:**
- Stock-Einspritzdüsen (318cc) reichen für 250 PS gerade so
- Stock-Kupplung bei 250 PS + Turbo-Drehmoment kritisch
- Stock-Pleuel halten bis ~300 PS, dann Upgrade nötig
