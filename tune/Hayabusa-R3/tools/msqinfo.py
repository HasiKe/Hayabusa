import sys, re, xml.etree.ElementTree as ET
KEYS = """TrigPattern numTeeth missingTeeth TrigAng TrigEdge trigPatternSec TrigEdgeSec TrigSpeed FixAng CrankAng TrigFilter SkipCycles useResync trigTeeth
nCylinders engineType twoStroke nInjectors injLayout injType inj4CylPairing pinLayout algorithm multiplyMAP mapSample baroCorr stoich reqFuel divider alternate injOpen dutyLim
sparkMode IgInv useDwellLim useDwellMap dwellErrCorrect sparkDur dwellrun dwellcrank dwellLim
mapMin mapMax tpsMin tpsMax useExtBaro baroPin baroMin baroMax egoType egoAlgorithm
SoftRevLim SoftLimRetard hardRevLim hardCutType knock_mode
fanPin fuelPumpPin tachoPin boostPin idleUpPin launchPin vssPin flexPin resetControlPin ignBypassPin wmiEnabledPin airConCompPin fanEnable iacAlgorithm iacStepperInv
launchEnabled flexEnabled vssMode vss_mode canBMWCluster canVAGCluster
egoType egoCount egoTemp egoRPM egoTPSMax egoLimit egoKP egoKI egoKD ego_sdelay
dfcoEnabled dfcoRPM dfcoHyster dfcoTPSThresh dfcoMinCLT dfcoDelay
aeMode taeThresh taeMinChange aeTime aeApplyMode
crankingPct asePct aseCount useOpenLoop primePulse
oddfire perToothIgn resetControl resetControlPin
nCylinders engineType
""".split()
def load(fn):
    t = ET.parse(fn).getroot()
    ns = {'m': t.tag.split('}')[0].strip('{')} if '}' in t.tag else {}
    def q(x): return ('m:'+x) if ns else x
    vi = t.find(q('versionInfo'), ns)
    bib = t.find(q('bibliography'), ns)
    consts = {}
    for p in t.findall(q('page'), ns):
        for c in p.findall(q('constant'), ns):
            consts[c.get('name')] = (c.text or '').strip(), c.get('cols'), c.get('rows'), c.get('digits'), c.get('units'), p.get('number')
    return vi.attrib if vi is not None else {}, bib.attrib if bib is not None else {}, consts
if __name__ == '__main__':
    for fn in sys.argv[1:]:
        vi, bib, c = load(fn)
        print("="*100); print(fn); print("versionInfo:", vi); print("bib:", bib); print("n constants:", len(c))
        for k in KEYS:
            if k in c:
                v = c[k]
                s = v[0] if len(v[0]) < 90 else v[0][:90]+'...'
                print(f"  {k:18s} = {s}  [{v[4]}] p{v[5]}")
