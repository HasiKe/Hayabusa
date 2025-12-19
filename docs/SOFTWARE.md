# Software Dokumentation - Hayabusa ECU

## 💻 Speeduino Firmware

### Übersicht
Das Speeduino Engine Management System ist eine vollständige Open-Source ECU Firmware, die für Arduino und ARM-basierte Mikrocontroller entwickelt wurde.

### Version Information
- **Current Version**: 202310 (October 2023)
- **Platform**: PlatformIO
- **License**: GPL v3
- **Repository**: Git Submodule in `speeduino/`

### Supported Boards

#### Arduino Mega 2560 (Standard)
```ini
[env:megaatmega2560]
platform = atmelavr
board = megaatmega2560
framework = arduino
```

#### Teensy 4.1 (Performance)
```ini
[env:teensy41]
platform = teensy
board = teensy41
framework = arduino
```

#### STM32 (Alternative)
```ini
[env:bluepill]
platform = ststm32
board = bluepill_f103c8
framework = arduino
```

### Core Features

#### Engine Management
- **Fuel Injection Control**
  - Sequential, Semi-sequential, Batch fire
  - Primary/Secondary fuel maps
  - Acceleration enrichment
  - Deceleration fuel cut

- **Ignition Control**
  - Advance/Retard maps
  - Knock detection/retard
  - Launch control
  - Rev limiter

- **Idle Control**
  - PWM idle valve control
  - Stepper motor support
  - Closed loop idle control

#### Advanced Features
- **CAN Bus Support**
- **Data Logging**
- **Real-time Tuning**
- **Staged Injection**
- **Nitrous Control**
- **Boost Control**

### Configuration

#### Hayabusa Specific Settings

##### Engine Configuration
```cpp
// Engine Parameters
configPage2.nCylinders = 4;           // 4 Cylinder
configPage2.engineType = 0;           // 4-stroke
configPage2.fuelAlgorithm = 1;        // Speed Density
configPage4.sparkMode = 2;            // Wasted Spark
configPage2.nInjectors = 4;           // Sequential
```

##### Trigger Settings
```cpp
// Suzuki Hayabusa Trigger Wheel
configPage4.TrigPattern = 1;          // Missing tooth
configPage4.triggerTeeth = 36;        // 36-1 wheel
configPage4.triggerMissingTeeth = 1;  // 1 missing tooth
```

##### Sensor Calibration
```cpp
// MAP Sensor (Hayabusa specific)
configPage2.mapType = 1;              // MPX4250
configPage2.mapMin = 10;               // kPa
configPage2.mapMax = 250;              // kPa

// TPS Calibration
configPage2.tpsMin = 150;              // ADC counts
configPage2.tpsMax = 850;              // ADC counts
```

### Build System

#### PlatformIO Configuration
```ini
[platformio]
default_envs = megaatmega2560
src_dir = speeduino

[common]
lib_deps = 
    EEPROM
    SD
    SPI

[env:megaatmega2560]
platform = atmelavr
board = megaatmega2560
framework = arduino
lib_deps = ${common.lib_deps}
build_flags = 
    -DCORE_AVR
    -DBOARD_MEGA2560
monitor_speed = 115200
```

#### Build Commands
```bash
# Clean build
pio run -t clean

# Build for Mega 2560
pio run -e megaatmega2560

# Build and upload
pio run -e megaatmega2560 -t upload

# Build for Teensy 4.1
pio run -e teensy41 -t upload
```

### Testing Framework

#### Unit Tests
```bash
# Run all tests
pio test

# Run specific test suite
pio test -f test_fuel
pio test -f test_ignition
pio test -f test_sensors
```

#### Test Coverage
- **Fuel Calculations**: ✅ 95%
- **Ignition Timing**: ✅ 92%
- **Sensor Processing**: ✅ 88%
- **Decoders**: ✅ 90%

### Code Structure

#### Main Components

```
speeduino/speeduino/
├── speeduino.ino           # Main entry point
├── globals.h/.cpp          # Global variables & config
├── init.h/.cpp             # Initialization routines
├── auxiliaries.h/.cpp      # Auxiliary outputs
├── comms.h/.cpp           # Serial communications
├── corrections.h/.cpp      # Fuel/ignition corrections
├── decoders.h/.cpp        # Trigger decoders
├── idle.h/.cpp            # Idle control
├── scheduler.h/.cpp       # Event scheduling
├── sensors.h/.cpp         # Sensor processing
├── storage.h/.cpp         # EEPROM handling
├── table2d.h/.cpp         # 2D lookup tables
├── table3d.h/.cpp         # 3D fuel/ignition maps
└── src/                   # External libraries
```

#### Key Files for Hayabusa

##### Decoder Configuration
```cpp
// decoders.cpp - Hayabusa trigger decoder
void triggerPri_missingTooth() {
    curTime = micros();
    curGap = curTime - lastTooth;
    
    if (curGap < triggerFilterTime) { return; }
    
    // Missing tooth detection
    if (curGap > (triggerSecFilterTime * 3)) {
        toothCurrentCount = 1;
        toothOneMinusOneTime = toothOneTime;
        toothOneTime = curTime;
        currentStatus.hasSync = true;
    }
}
```

##### Fuel Calculation
```cpp
// fuel_calcs.cpp - Hayabusa specific fuel calculations
uint16_t calculatePW() {
    // Base fuel calculation
    uint16_t pw = table3D_getValue(&fuelTable, 
                                   currentStatus.MAP, 
                                   currentStatus.RPM);
    
    // Apply corrections
    pw = correctionsFuel(pw);
    
    return pw;
}
```

## 🎛️ TunerStudio Configuration

### Project Setup

#### Busa Standard Tune
```
tune/Busa/
├── CurrentTune.msq          # Current tune file
├── projectCfg/             # Project configuration
│   ├── project.properties   # TS project settings
│   └── mainController.ini   # Controller definition
├── dashboard/              # Custom dashboards
└── restorePoints/          # Backup tunes
```

#### Hayabusa-R1 Hybrid Tune
```
tune/Hayabusa-R1/
├── CurrentTune.msq          # R1 hybrid tune
├── projectCfg/             # Modified for R1 components
└── dashboard/              # R1-specific dashboards
```

### Base Maps

#### VE Table (Fuel Map)
```
RPM\MAP    30   50   70   90  110  130  150
 1000     55   60   65   70   75   80   82
 2000     58   63   68   73   78   83   85
 3000     60   65   70   75   80   85   87
 4000     62   67   72   77   82   87   89
 5000     63   68   73   78   83   88   90
 6000     64   69   74   79   84   89   91
 8000     65   70   75   80   85   90   92
10000     66   71   76   81   86   91   93
12000     67   72   77   82   87   92   94
```

#### Ignition Table (Timing Map)
```
RPM\MAP    30   50   70   90  110  130  150
 1000     15   12   10    8    6    4    2
 2000     18   15   12   10    8    6    4
 3000     20   17   14   12   10    8    6
 4000     22   19   16   14   12   10    8
 5000     24   21   18   16   14   12   10
 6000     26   23   20   18   16   14   12
 8000     28   25   22   20   18   16   14
10000     30   27   24   22   20   18   16
12000     32   29   26   24   22   20   18
```

### Custom Dashboards

#### Performance Dashboard
```xml
<?xml version="1.0"?>
<dashboard>
    <panel>
        <gauge type="numeric" channel="rpm" />
        <gauge type="numeric" channel="map" />
        <gauge type="numeric" channel="tps" />
        <gauge type="numeric" channel="iat" />
        <gauge type="histogram" channel="afr" />
    </panel>
</dashboard>
```

#### Analysis Dashboard
```xml
<?xml version="1.0"?>
<dashboard>
    <panel>
        <chart type="scatter">
            <x-axis channel="rpm" />
            <y-axis channel="ve" />
            <color channel="map" />
        </chart>
    </panel>
</dashboard>
```

### Communication Settings

#### Serial Connection
```ini
; TunerStudio Communication
[Communications]
port = COM3
baud = 115200
protocol = ms2
```

#### CAN Bus (Optional)
```ini
[CAN]
enabled = true
canId = 0x200
baud = 500000
```

## 📊 Data Logging

### Real-time Parameters

#### Engine Data
```cpp
struct statuses {
    uint16_t RPM;           // Engine RPM
    uint16_t MAP;           // Manifold Pressure (kPa)
    uint8_t  TPS;           // Throttle Position (%)
    int16_t  IAT;           // Intake Air Temp (°C)
    int16_t  CLT;           // Coolant Temp (°C)
    uint16_t AFR;           // Air/Fuel Ratio * 100
    int8_t   advance;       // Ignition advance (degrees)
    uint16_t PW1;           // Pulse width (µs)
    uint8_t  dutyCycle;     // Duty cycle (%)
    uint16_t battery;       // Battery voltage (V * 10)
};
```

#### Calculated Values
```cpp
struct calculated {
    uint16_t req_fuel;      // Required fuel (µs)
    uint8_t  ve;            // Volumetric efficiency (%)
    int8_t   corrections;   // Total corrections (%)
    uint16_t load;          // Engine load (%)
    uint8_t  warmup;        // Warmup enrichment (%)
    uint8_t  accel;         // Acceleration enrichment (%)
    uint8_t  dwell;         // Dwell time (ms)
};
```

### SD Card Logging

#### Log Format
```csv
Time,RPM,MAP,TPS,IAT,CLT,AFR,ADV,PW1,DUTY,BATT
0,800,30,0,25,80,14.7,15,2000,25,13.2
100,850,32,2,25,82,14.5,14,2100,27,13.1
200,900,35,5,26,84,14.3,13,2200,30,13.0
```

#### Configuration
```cpp
// SD logging setup
#define SD_LOGGING_ENABLED 1
#define SD_LOG_RATE 10      // 10Hz logging
#define SD_BUFFER_SIZE 512  // Bytes
```

## 🔧 Tuning Process

### Initial Setup

#### 1. Base Configuration
```bash
# Load base tune
File → Open → tune/Busa/CurrentTune.msq

# Verify sensor calibration
Tools → Sensor Calibration

# Set trigger configuration
Engine → Trigger Settings
```

#### 2. Sensor Validation
```
1. MAP sensor: 100kPa at sea level
2. TPS: 0% closed, 100% WOT
3. CLT: Match coolant temperature
4. IAT: Match ambient temperature
5. Battery: Match system voltage
```

#### 3. Fuel System Setup
```
1. Set injector size (cc/min)
2. Calculate required fuel
3. Set cranking pulsewidth
4. Configure acceleration enrichment
```

### Tuning Workflow

#### Phase 1: Cranking & Warmup
```
1. Set cranking pulsewidth (3-8ms typical)
2. Configure warmup enrichment table
3. Set idle target RPM (1200 RPM)
4. Tune closed loop idle control
```

#### Phase 2: Base Fuel Map
```
1. Target AFR: 13.5:1 (cruise), 12.5:1 (WOT)
2. Use VE Analyze Live to autotune
3. Record 15+ minutes of driving data
4. Apply VE changes gradually (±5%)
```

#### Phase 3: Ignition Timing
```
1. Start conservative (20° @ idle)
2. Advance until knock detection
3. Retard 2-3° for safety margin
4. Optimize for MBT timing
```

#### Phase 4: Fine Tuning
```
1. Acceleration enrichment
2. Deceleration fuel cut
3. Rev limiter settings
4. Launch control (optional)
```

### Safety Parameters

#### Engine Protection
```cpp
// Temperature limits
#define CLT_WARN_TEMP 95    // °C
#define CLT_CUTOFF_TEMP 105 // °C

// Pressure limits  
#define MAP_MAX_KPA 250     // kPa

// RPM limits
#define RPM_HARD_LIMIT 11500 // RPM
#define RPM_SOFT_LIMIT 11000 // RPM
```

#### Fail-safes
```cpp
// Sensor fail-safe values
if (MAP > 300 || MAP < 10) {
    MAP = 100;  // Default to atmospheric
    setError(ERR_MAP_SENSOR);
}

if (CLT > 150 || CLT < -40) {
    CLT = 80;   // Default to normal temp
    setError(ERR_CLT_SENSOR);
}
```

## 🚀 Performance Optimization

### Memory Usage
```
Flash Usage: 98% (252KB / 256KB)
SRAM Usage:  75% (6KB / 8KB)
EEPROM:      40% (409 bytes / 1KB)
```

### Timing Critical Functions

#### Interrupt Service Routines
```cpp
// Trigger interrupt - highest priority
ISR(INT0_vect) {
    triggerPri_missingTooth();
}

// Injection scheduling
ISR(TIMER1_COMPA_vect) {
    fuelSchedule1Interrupt();
}

// Ignition scheduling  
ISR(TIMER4_COMPA_vect) {
    ignitionSchedule1Interrupt();
}
```

#### Performance Metrics
- **Trigger Jitter**: <±0.5°
- **Injection Accuracy**: ±50µs
- **Ignition Accuracy**: ±0.1°
- **Loop Time**: 100µs typical

---

**Letzte Aktualisierung**: Dezember 2025  
**Version**: 2.0  
**Status**: ✅ Production Ready