# Tuning Guide - Hayabusa ECU

## 🎯 Tuning Overview

### Ziele des Tunings
- **Maximale Performance** bei sicherer Motorlast
- **Optimaler Kraftstoffverbrauch** im Teillastbereich  
- **Zuverlässiger Betrieb** unter allen Bedingungen
- **Emissionsoptimierung** für Straßenzulassung

### Tuning-Philosophie
1. **Sicherheit zuerst** - Konservative Werte bevorzugen
2. **Datenbasiert** - Niemals "blindes" Tuning
3. **Progressiv** - Schrittweise Änderungen
4. **Validiert** - Jede Änderung messen und bestätigen

## 📊 Base Maps & Konfiguration

### Hayabusa Standard Configuration

#### Engine Settings
```ini
[Engine]
displacement = 1340        # cc (Gen 2+)
cylinders = 4
strokeCycles = 4           # 4-stroke
firingOrder = 1243

[Injection]
mode = sequential          # Sequential injection
numberOfInjectors = 4
injectorSize = 318         # cc/min (stock)
openingTime = 1.0          # ms
batteryCorrection = true

[Ignition]  
mode = wastedSpark         # 2 coils, wasted spark
coilChargingTime = 3.0     # ms dwell time
crankingAdvance = 10       # degrees BTDC
```

#### Trigger Configuration
```ini
[Trigger]
pattern = missingTooth
primaryTeeth = 36
missingTeeth = 1
triggerAngle = 0           # BTDC
cam = enabled              # Cam sensor present
camTeeth = 1               # 1 tooth per cycle
```

### VE Table (Volumetric Efficiency)

#### Standard Hayabusa Base Map
```
RPM\MAP   25   40   60   80  100  120  140  160  180  200
  800    45   50   55   60   65   70   75   78   80   82
 1200    47   52   57   62   67   72   77   80   82   84
 1600    49   54   59   64   69   74   79   82   84   86
 2000    51   56   61   66   71   76   81   84   86   88
 2500    53   58   63   68   73   78   83   86   88   90
 3000    55   60   65   70   75   80   85   88   90   92
 4000    57   62   67   72   77   82   87   90   92   94
 5000    59   64   69   74   79   84   89   92   94   96
 6000    61   66   71   76   81   86   91   94   96   98
 7000    63   68   73   78   83   88   93   96   98   99
 8000    64   69   74   79   84   89   94   97   99  100
 9000    65   70   75   80   85   90   95   98  100  101
10000    66   71   76   81   86   91   96   99  101  102
11000    66   71   76   81   86   91   96   99  101  102
```

### Ignition Table (Timing Map)

#### Conservative Base Timing
```
RPM\MAP   25   40   60   80  100  120  140  160  180  200
  800    15   12   10    8    6    4    2    0   -2   -4
 1200    18   15   13   11    9    7    5    3    1   -1
 1600    21   18   16   14   12   10    8    6    4    2
 2000    24   21   19   17   15   13   11    9    7    5
 2500    27   24   22   20   18   16   14   12   10    8
 3000    30   27   25   23   21   19   17   15   13   11
 4000    33   30   28   26   24   22   20   18   16   14
 5000    36   33   31   29   27   25   23   21   19   17
 6000    38   35   33   31   29   27   25   23   21   19
 7000    40   37   35   33   31   29   27   25   23   21
 8000    40   37   35   33   31   29   27   25   23   21
 9000    38   35   33   31   29   27   25   23   21   19
10000    36   33   31   29   27   25   23   21   19   17
11000    34   31   29   27   25   23   21   19   17   15
```

### AFR Target Table

#### Optimal Air/Fuel Ratios
```
RPM\MAP   25   40   60   80  100  120  140  160  180  200
  800   14.7 14.7 14.5 14.0 13.5 13.2 13.0 12.8 12.6 12.4
 1200   14.7 14.7 14.5 14.0 13.5 13.2 13.0 12.8 12.6 12.4
 1600   14.7 14.7 14.5 14.0 13.5 13.2 13.0 12.8 12.6 12.4
 2000   14.7 14.7 14.5 14.0 13.5 13.2 13.0 12.8 12.6 12.4
 2500   14.7 14.5 14.2 13.8 13.4 13.1 12.9 12.7 12.5 12.3
 3000   14.5 14.2 13.9 13.6 13.2 12.9 12.7 12.5 12.3 12.1
 4000   14.2 13.9 13.6 13.3 12.9 12.6 12.4 12.2 12.0 11.8
 5000   14.0 13.7 13.4 13.1 12.7 12.4 12.2 12.0 11.8 11.6
 6000   13.8 13.5 13.2 12.9 12.5 12.2 12.0 11.8 11.6 11.4
 7000   13.6 13.3 13.0 12.7 12.3 12.0 11.8 11.6 11.4 11.2
 8000   13.4 13.1 12.8 12.5 12.1 11.8 11.6 11.4 11.2 11.0
 9000   13.2 12.9 12.6 12.3 11.9 11.6 11.4 11.2 11.0 10.8
10000   13.0 12.7 12.4 12.1 11.7 11.4 11.2 11.0 10.8 10.6
11000   12.8 12.5 12.2 11.9 11.5 11.2 11.0 10.8 10.6 10.4
```

## 🔧 Tuning Process

### Phase 1: Initial Setup & Validation

#### 1.1 Sensor Calibration
```bash
# TPS Calibration
1. Throttle Bodies vollständig geschlossen
2. TunerStudio → Sensor Calibration → TPS
3. "Learn Closed" button
4. Throttle vollständig öffnen
5. "Learn WOT" button
6. Prüfung: Smooth 0-100% transition

# MAP Sensor Check
1. Engine OFF, MAP sollte ~100 kPa zeigen
2. Vacuum pump an MAP line
3. Bei 50 kPa vacuum → MAP ~50 kPa
4. Linearity über gesamten Bereich prüfen

# Temperature Sensors
1. Kaltstart: CLT/IAT ~ambient temperature
2. Warmup: CLT steigt auf 80-90°C
3. Betrieb: Stable CLT, IAT variabel
```

#### 1.2 Fuel System Setup
```bash
# Injector Dead Time Calibration
1. Install wideband O2 sensor
2. Target AFR: 14.7 (stoichiometric)
3. Various RPM steady state (2000-4000)
4. Adjust opening time until AFR stable
5. Typical values: 0.8-1.2ms for stock injectors

# Required Fuel Calculation
Req Fuel = (Displacement × 6.49) ÷ (AFR × Injector Size)
Example: (1340 × 6.49) ÷ (14.7 × 318) = 1.87ms

# Fuel Pump Prime
1. Key ON → Fuel pump 2 seconds
2. Priming pulse: 2-5ms typical
3. Verify fuel pressure: 3.5-4.0 bar
```

### Phase 2: Base Tuning

#### 2.1 Idle Tuning
```bash
# Target Parameters
Target RPM: 1200 ±50 RPM
Target AFR: 14.5-14.7  
Target MAP: 25-35 kPa
Target Advance: 15-18° BTDC

# Procedure
1. Engine fully warmed up
2. All electrical loads OFF
3. Adjust VE table in idle cells (800-1200 RPM, 25-40 kPa)
4. Fine-tune with Idle Control (if equipped)
5. Validate stability over 5+ minutes
```

#### 2.2 Part Throttle Tuning (Cruise)
```bash
# Data Collection Setup
1. Wide-band O2 sensor active
2. TunerStudio data logging: 10Hz
3. Drive steady speeds: 50, 80, 120 km/h
4. Maintain steady throttle for 30+ seconds each
5. Record RPM, MAP, TPS, AFR, timing

# VE Table Adjustment  
1. Target AFR: 14.5-15.0 (lean cruise for economy)
2. Use VE Analyze Live for auto-tuning
3. Manual adjustment: ±2-5% VE changes
4. Revalidate with test drive

# Example Cruise Points
50 km/h: ~3000 RPM, 30 kPa, 15% TPS
80 km/h: ~4500 RPM, 45 kPa, 25% TPS  
120 km/h: ~6500 RPM, 65 kPa, 40% TPS
```

#### 2.3 Wide Open Throttle (WOT) Tuning
```bash
# Safety First!
1. Dyno preferred (safety + repeatability)
2. EGT monitoring essential
3. Knock detection active
4. Conservative start: Rich AFR, retarded timing

# WOT Data Collection
1. 3rd gear pulls: 3000-8000 RPM
2. 4th gear pulls: 4000-9000 RPM  
3. 5th gear: 5000-10000 RPM
4. Monitor: AFR, EGT, knock, power

# Optimization Process
1. Start with AFR 12.0-12.5 (safe rich)
2. Advance timing until knock threshold
3. Back off timing 2-3° (safety margin)
4. Lean AFR gradually while monitoring power
5. Optimal typically: 12.5-13.0 AFR, MBT timing -2°
```

### Phase 3: Advanced Tuning

#### 3.1 Acceleration Enrichment
```bash
# Transient Fuel Requirements
# Sudden throttle opening requires extra fuel

[Accel Enrichment]
Wall Wetting Multiplier: 1.0-1.5 (depends on port injection)
Accel Time: 0.5-2.0 seconds
TPS Threshold: 2-5% change
RPM Threshold: 100-300 RPM change

# Tuning Process
1. Log WOT acceleration runs
2. Monitor AFR during transients  
3. Adjust enrichment until no lean spikes
4. Typical AFR during accel: 12.0-13.5
```

#### 3.2 Deceleration Fuel Cut (DFCO)
```bash
# Fuel Cut on Engine Braking
[Decel Fuel Cut]
Enable RPM: 1500        # Above idle
Resume RPM: 1300        # Below enable  
TPS Threshold: 2%       # Throttle closed
MAP Threshold: 40 kPa   # High vacuum

# Benefits
- Improved fuel economy
- Reduced emissions  
- Engine braking enhancement
- Catalyst protection
```

#### 3.3 Launch Control (Optional)
```bash
# Two-Step Rev Limiter for Drag Racing
[Launch Control]  
Enable: Clutch switch + speed < 5 km/h
Launch RPM: 4000-6000   # Optimal power band
Timing Retard: 10-20°   # Creates backfire/anti-lag
Fuel Cut: Soft (timing only) or Hard (fuel + timing)

# Safety Considerations
- Extreme exhaust temperatures
- Catalyst damage risk
- Transmission shock loads  
- Not for street use
```

### Phase 4: Fine Tuning & Optimization

#### 4.1 Closed Loop Tuning
```bash
# Wideband O2 Feedback
[Closed Loop]
Enable Conditions:
- Engine warmed up (CLT > 70°C)
- Steady state (stable RPM/MAP)
- Cruise load only (MAP < 80 kPa)

Authority: ±10-15%     # Maximum correction
Learning Rate: Slow    # Conservative adaptation
```

#### 4.2 Knock Control
```bash
# Knock Detection & Retard
[Knock Control]
Sensor: Piezo accelerometer on engine block
Frequency Window: 6-8 kHz (Hayabusa specific)
Detection Threshold: Calibrated to false knock rate <1%
Retard Rate: 1-2° per knock event  
Advance Recovery: 0.1-0.5° per second

# Tuning Notes
- Knock sensor location critical
- False knock worse than real knock
- Premium fuel (98+ octane) recommended
```

## 📈 Performance Optimization

### Power Modifications Support

#### Stage 1: Bolt-ons
```bash
# Exhaust System
- Full exhaust system: +5-15 hp
- AFR adjustment: Typically 0.5-1.0 leaner  
- Timing: Usually +2-4° additional advance

# Air Intake
- High-flow air filter: +2-5 hp
- Velocity stacks: +3-8 hp
- Ram air optimization: +5-10 hp (high speed)

# Tuning Changes Required
- VE table: +5-15% in affected cells
- AFR targets: Adjust for optimal power
- Timing: More aggressive possible
```

#### Stage 2: Internal Modifications
```bash
# High Compression Pistons  
- Compression ratio: 12.5:1 → 13.5:1
- Octane requirement: 98+ RON mandatory
- Timing: -2 to -4° base timing
- AFR: Richer for detonation safety

# Camshafts
- Duration: +10-30° over stock
- VE table: Significant changes required
- Idle: Usually rougher, higher RPM
- Power band: Shifted higher

# Port & Polish
- VE improvements: 5-15% throughout  
- Flow matching: All cylinders equal
- AFR distribution: Monitor per-cylinder
```

#### Stage 3: Forced Induction
```bash
# Turbocharger
- Boost pressure: 0.3-1.0 bar (conservative)
- Fuel system: Larger injectors required
- Timing: Significant retard needed
- AFR: Rich for cooling (11.5-12.5)
- Intercooling: Essential for reliability

# Nitrous Oxide
- Wet system preferred (fuel + N2O)
- Progressive controller recommended
- AFR: 11.0-12.0 under spray
- Timing: Retard 2-6° per stage
- Safety: Fuel pressure monitoring
```

### Fuel System Upgrades

#### Injector Sizing
```bash
# Calculation: 80% duty cycle max safe
Required Flow = (HP × BSFC) ÷ (Number of Injectors × 0.8)

Stock Hayabusa (175 hp):
(175 × 0.45) ÷ (4 × 0.8) = 24.6 cc/min per injector
Stock injectors: 318 cc/min → 85% safety margin ✓

Modified (250 hp):
(250 × 0.45) ÷ (4 × 0.8) = 35.2 cc/min per injector  
Required: 440+ cc/min injectors

# Popular Upgrade Injectors
- 440 cc/min: Good for ~300 hp
- 550 cc/min: Good for ~375 hp  
- 750 cc/min: Good for ~500 hp
```

#### Fuel Pump Upgrades
```bash
# Flow Requirements
Stock pump: ~150 LPH (sufficient to ~300 hp)
255 LPH pump: Good for ~500 hp
340 LPH pump: Good for ~700+ hp

# Pressure Requirements
Stock: 3.5 bar (51 psi)
Boosted applications: 4.0+ bar base + boost pressure
High-flow fuel rail: Recommended >400 hp
```

### Dyno Tuning Best Practices

#### Dyno Setup
```bash
# Equipment Required
- Chassis dynamometer (DynoJet preferred)
- Wide-band O2 sensor (AFX, AEM, Innovate)
- EGT monitoring (all cylinders)
- Knock detection system
- High-speed data logging

# Environmental Conditions  
- Ambient temp: 15-25°C optimal
- Humidity: <60% preferred  
- Barometric pressure: Note for corrections
- Cooling fans: Essential for repeatability
```

#### Test Procedure
```bash
# Baseline  
1. Stock tune power run
2. AFR sweep at peak torque RPM
3. Timing sweep at peak torque RPM
4. Document all sensor readings

# Optimization
1. Part throttle: 25%, 50%, 75% openings
2. WOT optimization: Start rich/retarded
3. Incremental changes: 0.5 AFR, 2° timing
4. Validate each change with power run

# Final Validation
1. Heat soak test: 5+ consecutive pulls
2. Street drive test: Real world validation  
3. Data log review: Any anomalies
4. Safety parameter verification
```

### Data Analysis

#### Key Performance Indicators
```bash
# Power Metrics
Peak HP: Location in RPM band
Peak Torque: Should occur 1000-2000 below peak HP
Power Band: RPM range within 90% of peak
HP/L: Specific output (target: 130-180 hp/L)

# Efficiency Metrics  
BSFC: Brake Specific Fuel Consumption (0.45-0.55 typical)
VE Peak: Maximum volumetric efficiency (90-110%)
Thermal Efficiency: Overall engine efficiency

# Reliability Metrics
AFR Consistency: ±0.2 across cylinders
EGT Balance: ±50°C across cylinders  
Knock Events: Zero tolerance on pump gas
```

#### Troubleshooting Common Issues

##### Poor Idle Quality
```bash
Symptoms: Rough idle, stalling, surging

Causes & Solutions:
1. VE table too rich/lean at idle
   → Adjust VE in idle cells (±5-15%)

2. Ignition timing incorrect  
   → Target 15-18° BTDC at idle
   
3. Vacuum leaks
   → Check MAP readings, smoke test
   
4. IAC valve issues (if equipped)
   → Clean valve, check control signals
```

##### Flat Spots / Hesitation
```bash
Symptoms: Power loss during acceleration

Causes & Solutions:
1. Lean spots in VE table
   → Increase VE in affected cells
   
2. Acceleration enrichment insufficient
   → Increase AE multiplier/time
   
3. Ignition timing too advanced (knock)
   → Retard timing in problem areas
   
4. Fuel pressure drop
   → Check pump, filter, pressure regulator
```

##### High-RPM Power Loss  
```bash
Symptoms: Power drops off before rev limiter

Causes & Solutions:  
1. Fuel starvation
   → Larger injectors/pump needed
   
2. Ignition breakdown
   → Check coils, plugs, plug gaps
   
3. Breathing restrictions
   → Flow test intake/exhaust
   
4. VE table inaccuracy
   → Dyno tune high-RPM cells
```

## 📋 Tuning Checklist

### Pre-Tuning Requirements ✓
- [ ] Engine mechanically sound
- [ ] All sensors calibrated  
- [ ] Base maps loaded
- [ ] Wide-band O2 installed
- [ ] Data logging configured
- [ ] Safety systems functional

### Initial Tuning ✓
- [ ] Idle quality acceptable
- [ ] Part throttle AFR targets met
- [ ] WOT AFR safe (not lean)
- [ ] No knock events detected
- [ ] Smooth acceleration/deceleration
- [ ] Engine protection limits set

### Advanced Tuning ✓  
- [ ] Closed loop operation stable
- [ ] Acceleration enrichment optimized
- [ ] Deceleration fuel cut functional
- [ ] Launch control tested (if used)
- [ ] Cold start enrichment adequate
- [ ] Heat soak performance maintained

### Final Validation ✓
- [ ] Dyno power run completed
- [ ] Street drive test successful  
- [ ] Long-term reliability demonstrated
- [ ] Backup tune files created
- [ ] Documentation updated

---

**⚠️ IMPORTANT SAFETY NOTES**
- Never tune without proper AFR monitoring
- Start conservative, optimize gradually
- Professional dyno tuning recommended for WOT
- Always maintain safety margins for reliability

**Letzte Aktualisierung**: Dezember 2025  
**Version**: 2.0  
**Status**: ✅ Production Ready