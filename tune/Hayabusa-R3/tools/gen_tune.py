#!/usr/bin/env python3
"""Generate the TunerStudio project (CurrentTune.msq + projectCfg/mainController.ini) for the
Gen1 Hayabusa ECU R3 (Speeduino fork, board 57) from
  (a) the fork's TunerStudio ini            speeduino/reference/speeduino.ini
  (b) the stock ECU maps                    tune/setup/maps.ods (sheets VE_org and IGN_org)
  (c) an older TunerStudio-written tune     tools/base_tune_Busa_2026-02-02.msq (format skeleton and
      fallback for inert settings; its values are not trusted for anything that acts on the engine)
Every value is validated against the ini (option lists, ranges, resolution).

    python3 tools/gen_tune.py                         # writes tune/Hayabusa-R3/CurrentTune.msq
    python3 tools/gen_tune.py OUT.msq '{"inj_cc_min": 276}'   # override parameters as JSON
"""
import sys, re, math, datetime, json, os
from xml.sax.saxutils import escape as xesc
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
from iniparse import parse_ini
from msqinfo import load as load_msq
from stockmaps import stock_maps, bilinear, interp1

INI = os.path.join(REPO, "speeduino", "reference", "speeduino.ini")
OLD = os.path.join(HERE, "base_tune_Busa_2026-02-02.msq")
ODS = os.path.join(REPO, "tune", "setup", "maps.ods")
SETTINGS = ["pressure_bar", "mcu_teensy", "enablehardware_test", "CELSIUS", "resetcontrol_standard", "AFR", "HAYABUSA_MULTIMAP"]
DEFINES = set(SETTINGS)

# ---------------------------------------------------------------- parameters
P = dict(
    displacement_cc=1299, ncyl=4, stoich=14.7,
    inj_cc_min=257.0,           # 24.5 lb/hr @ 3 bar (MPS Racing) - conservative (rich) assumption
    ve_peak=120.0,              # stock TPS map max (205) is scaled to this VE%
    ign_source="IGN_org",       # sheet with the stock ignition map
    ign_retard_deg=3.0, ign_retard_load_from=25.0, ign_retard_rpm_from=2000,   # safety margin for 12:1 compression (stock map is for 11:1)
    idle_ve=40, idle_ve_load_max=4.0, idle_ve_rpm_max=2000,   # flatten the untrustworthy stock 0..4 % TPS cells at idle rpm (stock ECU used the IAP map there)
    fix_timing_first_start=10,   # first start with fixed timing so the trigger angle can be verified with a strobe
    first_start=True,           # True: Wasted COP + Semi-Sequential (cam phase independent). False: Sequential/Sequential
    trig_ang=350, trig_edge="RISING", trig_edge_sec="RISING", trig_filter="Weak", use_resync="Yes",
    dwell_run=1.6, dwell_crank=2.5, dwell_lim=4, spark_dur=1.0,
    adc_full_scale_v=3.3/0.625,  # R3 analog front end: 12k/20k divider -> ADC full scale = 5.28 V at the sensor
    map_sensor="Suzuki IAP 18590-81A00",   # or "MPX4250AP"
    soft_rev=5500, hard_rev=6000,   # commissioning limits; stock limiter is 10900. Raise only with the wideband watching WOT
    fuel_rpm=[800,1200,1600,2000,2400,2800,3400,4000,4800,5600,6400,7200,8000,9200,10400,12000],
    load_bins=[0,2,4,6,8,10,13,16,20,25,30,40,50,60,75,100],
    ign_rpm=[800,1200,1600,2000,2400,2800,3200,3600,4000,4800,5600,6400,7200,8400,10000,12000],
)
if len(sys.argv) > 2:
    P.update(json.loads(sys.argv[2]))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "CurrentTune.msq")

# ---------------------------------------------------------------- derived values
def req_fuel_ms(p):
    # fuel per cylinder per cycle at 100 % VE, 20 C, 101.325 kPa, AFR = stoich, fuel density 0.745 g/cc
    air_g = p['displacement_cc'] / p['ncyl'] * 1.204e-3
    fuel_cc = air_g / p['stoich'] / 0.745
    return fuel_cc / (p['inj_cc_min'] / 60.0) * 1000.0

def mpx4250_kpa(v):  # Vout = Vs*(0.004*P - 0.04), Vs = 5 V  ->  P = 50*V + 10
    return 50.0 * v + 10.0
def suzuki_iap_kpa(v):  # Suzuki 18590-81A00: 3.6 V at 100 kPa, bands 2.4-2.9 V at 70-76 kPa ... -> linear fit P = 25*V + 10 (derived, verify on the bike)
    return 25.0 * v + 10.0
MAP_FN = {"MPX4250AP": mpx4250_kpa, "Suzuki IAP 18590-81A00": suzuki_iap_kpa}
if P['map_sensor'] not in MAP_FN: raise SystemExit("unknown MAP sensor")
MAP_MIN, MAP_MAX = round(MAP_FN[P['map_sensor']](0.0)), round(MAP_FN[P['map_sensor']](P['adc_full_scale_v']))

REQ_FUEL = round(req_fuel_ms(P), 1)

# ---------------------------------------------------------------- stock maps
maps = stock_maps(ODS)
tps_axis, ve_rpm, ve_grid = maps['tps']
ign_axis, ign_rpm_axis, ign_grid = maps['ign']
stock_max = max(map(max, ve_grid))
ve_scale = P['ve_peak'] / stock_max

def ve_table():
    rows = []
    for l in P['load_bins']:
        row = []
        for r in P['fuel_rpm']:
            v = bilinear(tps_axis, ve_rpm, ve_grid, l, r) * ve_scale
            if P['idle_ve'] and l <= P['idle_ve_load_max'] and r <= P['idle_ve_rpm_max']: v = P['idle_ve']
            row.append(round(v))
        rows.append(row)
    return rows

def ign_table():
    rows = []
    for l in P['load_bins']:
        row = []
        for r in P['ign_rpm']:
            v = bilinear(ign_axis, ign_rpm_axis, ign_grid, l, r)
            if l >= P['ign_retard_load_from'] and r >= P['ign_retard_rpm_from']: v -= P['ign_retard_deg']
            row.append(round(v))
        rows.append(row)
    return rows

def afr_table():
    anchors = [(0,14.2),(8,14.5),(15,14.7),(35,14.7),(50,13.8),(70,13.2),(100,12.8)]
    xs=[a for a,_ in anchors]; ys=[b for _,b in anchors]
    return [[round(interp1(xs, ys, l), 1) for r in P['fuel_rpm']] for l in P['load_bins']]

VE, IGN, AFR = ve_table(), ign_table(), afr_table()
LAMBDA = [[round(a / P['stoich'], 3) for a in row] for row in AFR]

# ---------------------------------------------------------------- explicit settings
first = P['first_start']
E = {
  # engine constants (page 1 in TS numbering = page 0 in msq)
  'nCylinders': "4", 'engineType': "Even fire", 'twoStroke': "Four-stroke", 'nInjectors': "4",
  'injLayout': "Semi-Sequential" if first else "Sequential", 'injType': "Port", 'inj4CylPairing': "1+3 & 2+4",
  'pinLayout': "Gen1 Hayabusa ECU R3", 'algorithm': "TPS", 'ignAlgorithm': "TPS",
  'multiplyMAP': "Off", 'mapSample': "Cycle Average", 'baroCorr': "Off", 'incorporateAFR': "No", 'includeAFR': "No",
  'stoich': P['stoich'], 'reqFuel': REQ_FUEL, 'divider': 2 if first else 4, 'alternate': "Alternating",
  'injOpen': 1.0, 'dutyLim': 85,
  'tpsMin': 53, 'tpsMax': 208, 'mapMin': MAP_MIN, 'mapMax': MAP_MAX, 'baroMin': MAP_MIN, 'baroMax': MAP_MAX,
  'useExtBaro': "No", 'baroPin': "A1",
  'perToothIgn': "Yes", 'fixAngEnable': "On" if (first and P['fix_timing_first_start']) else "Off", 'FixAng': P['fix_timing_first_start'] if first else 0, 'CrankAng': 5, 'ignCranklock': "Off",
  'tpsflood': 90.0, 'crankRPM': 500, 'primingDelay': 0.5, 'knock_pin': "A13", 'fanSP': 98, 'fanHyster': 5,
  # trigger
  'TrigPattern': "Dual Wheel", 'numTeeth': 8, 'missingTeeth': 0, 'TrigAng': P['trig_ang'],
  'TrigEdge': P['trig_edge'], 'TrigEdgeSec': P['trig_edge_sec'], 'trigPatternSec': "Single tooth cam",
  'TrigSpeed': "Crank Speed", 'TrigFilter': P['trig_filter'], 'SkipCycles': 3, 'useResync': P['use_resync'],
  # spark
  'sparkMode': "Wasted COP" if first else "Sequential", 'IgInv': "Going Low",
  'useDwellLim': "On", 'dwellLim': P['dwell_lim'], 'dwellcrank': P['dwell_crank'], 'dwellrun': P['dwell_run'],
  'sparkDur': P['spark_dur'], 'dwellErrCorrect': "On", 'useDwellMap': "No",
  # rev limits / protection
  'SoftRevLim': P['soft_rev'], 'SoftLimRetard': 10, 'SoftLimMax': 1.5, 'SoftLimitMode': "Fixed",
  'hardRevLim': P['hard_rev'], 'hardCutType': "Full", 'engineProtectType': "Both",
  # fuel corrections
  'aeMode': "TPS", 'taeThresh': 50, 'taeMinChange': 3.0, 'aeTime': 250, 'aeApplyMode': "PW Multiplier",
  'aeColdPct': 120, 'aeColdTaperMin': 0, 'aeColdTaperMax': 60, 'aeTaperMin': 3000, 'aeTaperMax': 8000, 'decelAmount': 100,
  'aseTaperTime': 1.0, 'fpPrime': 3,
  'dfcoEnabled': "Off", 'dfcoRPM': 2500, 'dfcoHyster': 250, 'dfcoTPSThresh': 2.0, 'dfcoMinCLT': 60, 'dfcoDelay': 1.0,
  # EGO (LC-2 read only, no correction yet)
  'egoType': "Wide Band", 'egoAlgorithm': "No correction", 'ego_sdelay': 30, 'egoTemp': 60, 'egoRPM': 1500,
  'egoTPSMax': 70.0, 'egoLimit': 15, 'egoKP': 80, 'egoKI': 60, 'egoKD': 50, 'egoCount': 4,
  # idle / fan / misc off
  'iacAlgorithm': "None", 'idleAdvEnabled': "Off", 'fanEnable': "Off", 'boostEnabled': "Off",   'flexEnabled': "Off", 'launchEnable': "No", 'vssMode': "Off", 'knock_mode': "Off", 'wmiEnabled': "Off", 'n2o_enable': "Off", 'vvtEnabled': "Off",
  'stagingEnabled': "Off", 'fuel2Mode': "Off", 'spark2Mode': "Off", 'fuelTrimEnabled': "No", 'resetControl': "Disabled",
  'enable_secondarySerial': "Disable", 'enable_intcan': "Disable", 'rtc_mode': "Off", 'onboard_log_file_style': "Disabled",
  'idleUpEnabled': "Off", 'airConEnable': "Off", 'oilPressureEnable': "Off", 'oilPressureProtEnbl': "Off", 'fuelPressureEnable': "Off",
  'tachoPin': "Board Default", 'tachoDiv': "Normal", 'tachoDuration': 3, 'useTachoSweep': "Off",
  'fuelPumpPin': "Board Default", 'fanPin': "Board Default", 'boostPin': "Board Default", 'launchPin': "Board Default",
  'vssPin': "Board Default", 'idleUpPin': "Board Default", 'resetControlPin': "Board Default", 'wmiEnabledPin': "Board Default",
  'batVoltCorrect': 0.0,
  # tables
  'rpmBins': P['fuel_rpm'], 'fuelLoadBins': P['load_bins'], 'veTable': VE,
  'rpmBins2': P['ign_rpm'], 'mapBins1': P['load_bins'], 'advTable1': IGN,
  'rpmBinsAFR': P['fuel_rpm'], 'loadBinsAFR': P['load_bins'], 'afrTable': AFR, 'lambdaTable': LAMBDA,
  'ego_min_lambda': 10.0/P['stoich'], 'ego_max_lambda': 18.0/P['stoich'], 'afrProtectDeviationLambda': 1.5/P['stoich'],
  # map set 2 (Speeduino secondary tables), 3 and 4: identical copies for now
  'fuelRPM2Bins': P['fuel_rpm'], 'fuelLoad2Bins': P['load_bins'], 'veTable2': VE,
  'rpmBins3': P['ign_rpm'], 'mapBins2': P['load_bins'], 'advTable2': IGN,
  'fuelRPM3Bins': P['fuel_rpm'], 'fuelLoad3Bins': P['load_bins'], 'veTable3': VE,
  'ignRPM3Bins': P['ign_rpm'], 'ignLoad3Bins': P['load_bins'], 'advTable3': IGN,
  'fuelRPM4Bins': P['fuel_rpm'], 'fuelLoad4Bins': P['load_bins'], 'veTable4': VE,
  'ignRPM4Bins': P['ign_rpm'], 'ignLoad4Bins': P['load_bins'], 'advTable4': IGN,
  # curves
  'wueBins': [-40,-30,-20,-10,0,10,20,40,60,80], 'wueRates': [160,152,145,138,130,123,116,108,102,100],
  'aseBins': [-40,0,20,60], 'asePct': [30,25,20,10], 'aseCount': [8,6,5,3],
  'primeBins': [-40,0,30,80], 'primePulse': [6.0,4.0,3.0,2.0],
  'crankingEnrichBins': [-40,0,30,80], 'crankingEnrichValues': [300,220,160,120],
  'injAng': [355,355,355,355], 'injAngRPM': [500,2000,4500,6500],
  'taeBins': [0,60,150,400], 'taeRates': [10,25,45,70],
  'maeBins': [0,50,100,200], 'maeRates': [0,0,0,0],
  'brvBins': [6.0,8.0,10.0,12.0,14.0,20.0], 'injBatRates': [250,200,150,120,100,100], 'dwellRates': [240,200,150,130,100,100],
  'airDenBins': [-40,-30,-20,0,20,40,60,80,100], 'airDenRates': [126,121,116,107,100,94,88,83,79],
  'iatRetBins': [20,40,60,70,80,100], 'iatRetRates': [0,0,0,2,4,6],
  'cltAdvBins': [0,10,30,45,60,80], 'cltAdvValues': [0,0,0,0,0,0],
  'idleAdvBins': [-500,-300,-100,100,300,500], 'idleAdvValues': [0,0,0,0,0,0],
  'baroFuelBins': [70,80,90,95,100,105,110,120], 'baroFuelValues': [100]*8,
  'rpmBinsBoost': [500,1500,2500,3500,4500,5500,6500,7500], 'tpsBinsBoost': [0,10,20,30,40,60,80,100], 'boostTable': [[0]*8 for _ in range(8)],
  'boostRPM3Bins': [500,1500,2500,3500,4500,5500,6500,7500], 'boostLoad3Bins': [0,10,20,30,40,60,80,100], 'boostTable3': [[0]*8 for _ in range(8)],
  'boostRPM4Bins': [500,1500,2500,3500,4500,5500,6500,7500], 'boostLoad4Bins': [0,10,20,30,40,60,80,100], 'boostTable4': [[0]*8 for _ in range(8)],
  'rpmBinsDwell': [1000,3000,5000,7000], 'loadBinsDwell': [10,30,60,100], 'dwellTable': [[P['dwell_run']]*4 for _ in range(4)],
}

E.update({
  'launchEnable': "No", 'engineProtectMaxRPM': 3000, 'ego_min_afr': 10.0, 'ego_max_afr': 18.0,
  'boostFreq': 30, 'vvtFreq': 30, 'fanFreq': 30, 'lnchSoftLim': 3000, 'lnchHardLim': 3000, 'flatSSoftWin': 1000, 'flatSArm': 1500,
  'n2o_stage1_minRPM': 3000, 'n2o_stage1_maxRPM': 5000, 'n2o_stage2_minRPM': 3000, 'n2o_stage2_maxRPM': 5000,
  'afrProtectDeviation': 1.5, 'boostCutEnabled': "Off", 'boostLimit': 200, 'fuel2Algorithm': "TPS", 'spark2Algorithm': "TPS", 'CTPSEnabled': "Off",
  'vvtTable': [[0]*8 for _ in range(8)], 'rpmBinsVVT': [500,1500,2500,3500,4500,5500,6500,7500], 'loadBinsVVT': [0,10,20,30,40,60,80,100],
  'vvt2Table': [[0]*8 for _ in range(8)], 'rpmBinsVVT2': [500,1500,2500,3500,4500,5500,6500,7500], 'loadBinsVVT2': [0,10,20,30,40,60,80,100],
  'stagingTable': [[0]*8 for _ in range(8)], 'rpmBinsStaging': [500,1500,2500,3500,4500,5500,6500,7500], 'loadBinsStaging': [0,10,20,30,40,60,80,100],
  'wmiTable': [[0]*8 for _ in range(8)], 'rpmBinsWMI': [500,1500,2500,3500,4500,5500,6500,7500], 'mapBinsWMI': [100,120,140,160,180,200,220,240],
  'boostTableDutyLookup': [[0]*8 for _ in range(8)], 'rpmBinsDutyLookup': [500,1500,2500,3500,4500,5500,6500,7500], 'loadBinsDutyLookup': [0,10,20,30,40,60,80,100],
  'rotarySplitValues': [0]*8, 'rotarySplitBins': [0,10,20,30,40,60,80,100],
  'flexBoostBins': [0,20,40,60,80,100], 'flexBoostAdj': [0]*6, 'flexFuelBins': [0,20,40,60,80,100], 'flexFuelAdj': [100]*6,
  'flexAdvBins': [0,20,40,60,80,100], 'flexAdvAdj': [0]*6,
  'knock_window_rpms': [1000,2000,3000,4000,5000,6000], 'knock_window_angle': [0]*6, 'knock_window_dur': [40]*6,
  'oilPressureProtMins': [0.5,1.0,1.5,2.0], 'oilPressureProtRPM': [1000,3000,5000,7000],
  'wmiAdvBins': [100,120,140,160,180,200], 'wmiAdvAdj': [0]*6,
  'fuelTempBins': [-40,0,20,40,60,80], 'fuelTempValues': [100]*6,
  'coolantProtRPM': [10000]*6, 'coolantProtTemp': [-40,-20,0,20,40,60],
  'rollingProtRPMDelta': [-300,-200,-100,-50], 'rollingProtCutPercent': [50,75,90,100],
  'PWMFanDuty': [0]*4, 'fanPWMBins': [-40,0,40,80],
  'iacCLValues': [1500,1400,1300,1250,1200,1150,1100,1100,1100,1100], 'iacOLStepVal': [0]*10, 'iacOLPWMVal': [0]*10,
  'iacBins': [-40,-30,-20,-10,0,20,40,60,80,100], 'iacCrankSteps': [0]*4, 'iacCrankDuty': [0]*4, 'iacCrankBins': [-40,0,40,80],
  'outputPin': [0]*8, 'outputDelay': [0]*8, 'firstDataIn': [0]*8, 'secondDataIn': [0]*8, 'outputTimeLimit': [0]*8,
  'firstTarget': [0]*8, 'secondTarget': [0]*8, 'candID': [0]*8, 'canoutput_param_group': [0]*8,
})
for i in range(8): E[f'outputPin{i}'] = "Disabled"
for i in range(1, 9):
    E[f'fuelTrim{i}Table'] = [[0]*6 for _ in range(6)]
    E[f'fuelTrim{i}rpmBins'] = [500,2000,3500,5000,6500,8000]
    E[f'fuelTrim{i}loadBins'] = [0,20,40,60,80,100]

E['ignTrim1'] = E['ignTrim2'] = E['ignTrim3'] = E['ignTrim4'] = E['ignTrim5'] = E['ignTrim6'] = E['ignTrim7'] = E['ignTrim8'] = 0

# ---------------------------------------------------------------- ini + old msq
ini = parse_ini(INI, DEFINES)
consts, pages, order = ini['consts'], ini['pages'], ini['order']
defaults = {}
for raw in open(INI, encoding='latin-1'):
    m = re.match(r'\s*defaultValue\s*=\s*(\w+)\s*,\s*(.*?)\s*(;.*)?$', raw)
    if m: defaults[m.group(1)] = m.group(2).strip()
old_vi, old_bib, old_c = load_msq(OLD)
old_text = open(OLD, encoding='latin-1').read()

errors, report = [], {'explicit': [], 'default': [], 'old': [], 'zero': []}

def shape(c):
    s = c.get('shape', '') or ''
    m = re.findall(r'\d+', s)
    if not m: return None
    return [int(x) for x in m]

def fmt(v, digits):
    d = max(1, int(digits or 0))
    s = f"{float(v):.{d}f}"
    if d > 1:
        s = s.rstrip('0')
        if s.endswith('.'): s += '0'
    return s

def scal(c):
    sc = c.get('scale', '1'); tr = c.get('translate', '0')
    try: return float(sc), float(tr)
    except ValueError:
        # expression like {fuelLoadRes} -> TPS load: 0.5 % resolution
        if 'stoich' in sc: return 0.1 / P['stoich'], 0.0
        return (0.5 if 'LoadRes' in sc else 1.0), 0.0

warnings = []
def check_scalar(c, v):
    """Return the value snapped to the ini's raw resolution; range errors only for explicit settings."""
    n = c['name']; explicit = n in E
    lo, hi = c.get('lo', ''), c.get('hi', '')
    v = float(v)
    try:
        if lo not in ('', None) and v < float(lo) - 1e-9:
            (errors if explicit else warnings).append(f"{n}: {v} < lo {lo}"); v = float(lo) if not explicit else v
        if hi not in ('', None) and v > float(hi) + 1e-9:
            (errors if explicit else warnings).append(f"{n}: {v} > hi {hi}"); v = float(hi) if not explicit else v
    except ValueError: pass
    sc, tr = scal(c)
    raw = (v - tr) / sc
    if abs(raw - round(raw)) > 1e-6:
        warnings.append(f"{n}: {v} snapped to {round(raw) * sc + tr:.4g} (raw {round(raw)}, scale {sc:.4g})")
        v = round(raw) * sc + tr
    return v

def units_of(c):
    u = c.get('units', '')
    if u.startswith('{'):
        if 'algorithmUnits' in u: return "% TPS"      # algorithm, ignAlgorithm, fuel2Algorithm, spark2Algorithm are all TPS in this tune
        if 'boostTableLabels' in u: return "Duty Cycle %"
        m = re.search(r'name="%s"[^>]*units="([^"]*)"' % re.escape(c['name']), old_text)
        return m.group(1) if m else ""
    return u

def value_for(c):
    n = c['name']
    if n in E:
        report['explicit'].append(n); return E[n], 'explicit'
    if n in defaults:
        report['default'].append(n); return defaults[n], 'default'
    if n in old_c:
        report['old'].append(n); return old_c[n][0], 'old'
    report['zero'].append(n); return None, 'zero'

def render(c, v):
    n, kind = c['name'], c['kind']
    if kind == 'bits':
        opts = c['options']
        if not opts:  # unused bit fields without an option list: keep the old tune's raw text
            raw = old_c.get(n, ('"0"',))[0]
            return f'<constant name="{n}">{raw}</constant>'
        if isinstance(v, str) and v.strip().startswith('"'): v = v.strip().strip('"')
        if v is None: v = opts[0]
        def by_index(i):
            if i < len(opts): return opts[i]
            warnings.append(f"{n}: default index {i} out of range, using old tune value")
            return old_c[n][0].strip('"') if n in old_c else opts[0]
        if isinstance(v, (int, float)) and not isinstance(v, bool):  # index from defaultValue
            v = by_index(int(v))
        elif isinstance(v, str) and v.isdigit() and v not in opts:
            v = by_index(int(v))
        if v not in opts:
            if n in E: errors.append(f"{n}: option {v!r} not in {opts[:6]}...")
            else: warnings.append(f"{n}: option {v!r} not in ini list (ini typo?), kept as text")
        elif v == 'INVALID':
            if n in E: errors.append(f"{n}: INVALID chosen")
            else: warnings.append(f"{n}: option index 0 is INVALID (= none) -> constant omitted like TunerStudio does")
            return ''
        return f'<constant name="{n}">"{xesc(v)}"</constant>'
    if kind == 'string':
        return f'<constant name="{n}">"{v or ""}"</constant>'
    digits = c.get('digits', '0')
    try: int(digits)
    except: digits = '1' if ('DecimalRes' in str(digits) and 'vvt' not in c['name'].lower()) else '0'
    u = units_of(c)
    if kind == 'scalar':
        if v is None: v = 0
        if isinstance(v, str): v = float(v.split()[0])
        v = check_scalar(c, v)
        ua = f' units="{xesc(u)}"' if u else ''
        return f'<constant digits="{int(digits)}" name="{n}"{ua}>{fmt(v, digits)}</constant>'
    # array
    sh = shape(c)
    if sh is None: errors.append(f"{n}: no shape"); return ''
    if len(sh) == 1: rows, cols = sh[0], 1
    else: rows, cols = sh[0], sh[1]   # ini writes [16x16] as rows x cols
    total = rows * cols
    if v is None: flat = [0.0] * total
    elif isinstance(v, str): flat = [float(x) for x in v.split()]
    elif isinstance(v[0], list): flat = [float(x) for row in v for x in row]
    else: flat = [float(x) for x in v]
    if len(flat) != total: errors.append(f"{n}: has {len(flat)} values, expected {total}"); flat = (flat + [0.0]*total)[:total]
    flat = [check_scalar(c, x) for x in flat]
    if n.lower().endswith('bins') and cols == 1 and any(b < a for a, b in zip(flat, flat[1:])):
        errors.append(f"{n}: bins not monotonic {flat}")
    lines = []
    for r in range(rows):
        lines.append("         " + " ".join(fmt(x, digits) for x in flat[r*cols:(r+1)*cols]) + " ")
    body = "\n".join(lines)
    ua = f' units="{xesc(u)}"' if u else ''
    return f'<constant cols="{cols}" digits="{int(digits)}" name="{n}" rows="{rows}"{ua}>\n{body}\n      </constant>'

# ---------------------------------------------------------------- emit
unknown = [n for n in E if n not in consts]
if unknown: errors.append(f"explicit settings not in ini: {unknown}")

out = []
out.append('<?xml version="1.0" encoding="ISO-8859-1"?>')
out.append('<msq xmlns="http://www.msefi.com/:msq">')
now = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y").replace("  ", " ")
out.append(f'<bibliography author="tools/gen_tune.py (Hayabusa ECU R3 base tune)" tuneComment="" writeDate="{now}"/>')
out.append(f'<versionInfo fileFormat="5.0" firmwareInfo="Speeduino+2025.04-dev" nPages="{ini["npages"]}" signature="speeduino 202504-dev"/>')
# pcVariables block copied from the old tune
m = re.search(r'<page>\n(.*?)</page>\n', old_text, re.S)
out.append('<page>'); out.append(m.group(1).rstrip('\n')); out.append('</page>')
sizes = ini['pagesizes']
for pg in sorted(pages):
    out.append(f'<page number="{pg-1}" size="{sizes[pg-1]}">')
    for c in pages[pg]:
        v, src = value_for(c)
        r = render(c, v)
        if r: out.append(r)
    out.append('</page>')
out.append('<settings Comment="These setting are only used if this msq is opened without a project.">')
for s in SETTINGS: out.append(f'<setting name="{s}" value="{s}"/>')
out.append('</settings>')
out.append('<userComments Comment="These are user comments that can be related to a particular setting or dialog."/>')
out.append('</msq>')

os.makedirs(os.path.dirname(os.path.abspath(OUT)) or '.', exist_ok=True)
open(OUT, 'w', encoding='latin-1').write("\n".join(out) + "\n")

import shutil
proj = os.path.join(os.path.dirname(os.path.abspath(OUT)), "projectCfg"); os.makedirs(proj, exist_ok=True)
shutil.copyfile(INI, os.path.join(proj, "mainController.ini"))
print(f"written {OUT} (+ projectCfg/mainController.ini from {INI})")
print(f"reqFuel = {REQ_FUEL} ms  (inj {P['inj_cc_min']} cc/min)   VE scale {ve_scale:.3f} (stock max {stock_max:g} -> {P['ve_peak']})")
print(f"MAP cal: mapMin {MAP_MIN} kPa, mapMax {MAP_MAX} kPa (ADC full scale {P['adc_full_scale_v']:.2f} V at sensor)")
print(f"constants: explicit {len(report['explicit'])}, ini default {len(report['default'])}, from old tune {len(report['old'])}, zero {len(report['zero'])}")
print("from old tune:", " ".join(n for n in report['old'] if not n.startswith('unused') and not n.startswith('Unused')))
print("zero:", " ".join(n for n in report['zero'] if not n.lower().startswith('unused')))
print(f"warnings ({len(warnings)}):"); [print("  ", w) for w in warnings]
if errors:
    print("\nERRORS:"); [print("  ", e) for e in errors]; sys.exit(1)
print("validation: OK")
