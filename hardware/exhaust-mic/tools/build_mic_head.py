#!/usr/bin/env python3
"""Generate the mic-head schematic (mic-head/mic-head.kicad_sch).

Two identical boards are built from this: channel A at the exhaust tip and
channel B at the airbox. See docs/specs/2026-08-28-exhaust-mic-design.md
section 4.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kigen import SymbolLib, Schematic  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.normpath(os.path.join(HERE, "..", "mic-head"))
LOCAL_LIB = os.path.normpath(os.path.join(HERE, "..", "lib", "exhaust-mic.kicad_sym"))

PROJECT = "mic-head"
REV = "A"
DATE = "2026-08-28"
COMPANY = "Hayabusa / exhaust-mic"

FP_R = "Resistor_SMD:R_0603_1608Metric"
FP_C = "Capacitor_SMD:C_0603_1608Metric"
FP_C1210 = "Capacitor_SMD:C_0805_2012Metric"


def build() -> Schematic:
    lib = SymbolLib()
    lib.add_stock("Device", "Connector_Generic", "power", "Amplifier_Operational")
    lib.add_file("exhaust-mic", LOCAL_LIB)

    sch = Schematic(lib, PROJECT, "mic-head.kicad_sch",
                    title="Exhaust-Mic - Mikrofonkopf (2x bestueckt: Kanal A und B)",
                    rev=REV, date=DATE, company=COMPANY, paper="A3")

    # ------------------------------------------------------------------
    # Steckverbinder zum Hauptboard
    # ------------------------------------------------------------------
    sch.text("Steckverbinder zum Hauptboard", 330, 40, 2.0)
    sch.text("Kabel direkt einloeten, Pads zweireihig versetzt. 2x Twisted Pair + Schirm.", 330, 45)
    sch.text("Keine Zugentlastung auf der Platine - Kabel vergiessen oder im Roehrchen klemmen.", 330, 41)
    sch.text("Schirm liegt beidseitig auf Masse, siehe Hinweis unten rechts.", 330, 49)

    j1 = sch.part("Connector_Generic:Conn_01x05", "J1", "Loetpads_Kabel_5x",
                  340, 75,
                  footprint="exhaust-mic:SolderWire-0.1sqmm_1x05_2reihig_P2.6mm",
                  fields={"MPN": "-"})
    sch.stub(j1, "1", "VIN_3V3", 15.24, glob=True, shape="input")
    sch.stub(j1, "2", "GND_CBL", 15.24)
    sch.stub(j1, "3", "OUT_P", 15.24, glob=True, shape="output")
    sch.stub(j1, "4", "OUT_N", 15.24, glob=True, shape="output")
    sch.stub(j1, "5", "SHIELD", 15.24, glob=True, shape="passive")

    # Kabelmasse direkt auf GND
    x, y = j1.pin("2")
    sch.wire(x - 7.62, y, x - 12.7, y)
    sch.wire(x - 12.7, y, x - 12.7, y + 7.62)
    sch.power("GND", x - 12.7, y + 7.62)

    # ------------------------------------------------------------------
    # Versorgung: 3V3 vom Kabel -> Ferrit -> LDO -> 2V8
    # ------------------------------------------------------------------
    sch.text("Versorgung", 40, 40, 2.0)
    sch.text("Mikrofon-VDD ist auf 2,3...3,0 V begrenzt (Datenblatt Tabelle 6),", 40, 45)
    sch.text("darum lokaler 2,8-V-LDO. Versorgt auch den Buffer - eine saubere Schiene.", 40, 49)

    lab_y = 65.0
    sch.glabel("VIN_3V3", 40, lab_y, 0, "input")
    sch.wire(40, lab_y, 50.8, lab_y)

    fb1 = sch.part("Device:FerriteBead", "FB1", "600R@100MHz", 54.61, lab_y, 90,
                   footprint=FP_R)
    sch.wire(50.8, lab_y, *fb1.pin("1"))

    n_in = 68.58                       # LDO-Eingangsknoten
    sch.wire(fb1.pin("2")[0], lab_y, n_in, lab_y)

    c1 = sch.part("Device:C", "C1", "10u/16V", n_in, lab_y + 12.7,
                  footprint=FP_C1210)
    sch.wire(n_in, lab_y, *c1.pin("1"))
    sch.power("GND", *c1.pin("2"))
    sch.junction(n_in, lab_y)

    u1 = sch.part("exhaust-mic:TPS7A20", "U1", "TPS7A2028", 96.52, lab_y + 3.81,
                  footprint="Package_TO_SOT_SMD:SOT-23-5",
                  fields={"MPN": "TPS7A2028PDBVR",
                          "Datasheet": "https://www.ti.com/lit/ds/symlink/tps7a20.pdf"})
    # IN
    ix, iy = u1.pin("1")
    sch.wire(n_in, lab_y, n_in, iy)
    sch.wire(n_in, iy, ix, iy)
    sch.junction(n_in, lab_y)
    # EN fest auf IN - Regler laeuft immer mit
    ex, ey = u1.pin("3")
    sch.wire(n_in, iy, n_in, ey)
    sch.wire(n_in, ey, ex, ey)
    sch.junction(n_in, iy)
    # GND
    gx, gy = u1.pin("2")
    sch.wire(gx, gy, gx, gy + 5.08)
    sch.power("GND", gx, gy + 5.08)
    # NC
    sch.noconn(*u1.pin("4"))

    n_out = 127.0                      # 2V8-Knoten
    ox, oy = u1.pin("5")
    sch.wire(ox, oy, n_out, oy)
    sch.wire(n_out, oy, n_out, lab_y)

    c3 = sch.part("Device:C", "C3", "1u/16V", n_out, lab_y + 12.7, footprint=FP_C)
    sch.wire(n_out, lab_y, *c3.pin("1"))
    sch.power("GND", *c3.pin("2"))
    sch.junction(n_out, lab_y)

    c4 = sch.part("Device:C", "C4", "10u/16V", n_out + 15.24, lab_y + 12.7,
                  footprint=FP_C1210)
    sch.wire(n_out, lab_y, n_out + 15.24, lab_y)
    sch.wire(n_out + 15.24, lab_y, *c4.pin("1"))
    sch.power("GND", *c4.pin("2"))
    sch.junction(n_out + 15.24, lab_y)

    sch.wire(n_out + 15.24, lab_y, n_out + 30.48, lab_y)
    sch.wire(n_out + 30.48, lab_y, n_out + 30.48, lab_y - 7.62)
    sch.power("+2V8", n_out + 30.48, lab_y - 7.62)

    # ------------------------------------------------------------------
    # Mikrofon
    # ------------------------------------------------------------------
    sch.text("Mikrofonkapsel", 40, 125, 2.0)
    sch.text("Bottom-Port: Schallloch in der Leiterplatte unter der Kapsel.", 40, 130)
    sch.text("C5 laut Datenblatt so dicht wie moeglich an Pin 2.", 40, 134)

    mk1 = sch.part("exhaust-mic:IM73A135V01", "MK1", "IM73A135V01", 76.2, 160,
                   footprint="exhaust-mic:Infineon_PG-LLGA-5-1",
                   fields={"MPN": "IM73A135V01XTSA1"})
    vx, vy = mk1.pin("2")
    sch.wire(vx, vy, vx - 10.16, vy)
    sch.wire(vx - 10.16, vy, vx - 10.16, vy - 7.62)
    sch.power("+2V8", vx - 10.16, vy - 7.62)

    c5 = sch.part("Device:C", "C5", "100n", vx - 20.32, vy + 7.62, footprint=FP_C)
    sch.wire(vx - 10.16, vy, vx - 20.32, vy)
    sch.wire(vx - 20.32, vy, *c5.pin("1"))
    sch.power("GND", *c5.pin("2"))
    sch.junction(vx - 10.16, vy)

    g4 = mk1.pin("4")
    g5 = mk1.pin("5")
    grail = g4[0] - 5.08
    sch.wire(g4[0], g4[1], grail, g4[1])
    sch.wire(g5[0], g5[1], grail, g5[1])
    sch.wire(grail, g4[1], grail, g5[1] + 5.08)
    sch.junction(grail, g5[1])
    sch.power("GND", grail, g5[1] + 5.08)

    sch.stub(mk1, "1", "MIC_P", 7.62)
    sch.stub(mk1, "3", "MIC_N", 7.62)

    # Reserve-Last differentiell, unbestueckt
    r3 = sch.part("Device:R", "R3", "47k", 76.2, 200, footprint=FP_R, dnp=True)
    sch.stub(r3, "1", "MIC_P", 5.08)
    sch.stub(r3, "2", "MIC_N", 5.08)
    sch.text("R3 unbestueckt: Reserve-Last, falls doch noetig.", 88.9, 200)

    # ------------------------------------------------------------------
    # Buffer
    # ------------------------------------------------------------------
    sch.text("Impedanzwandler", 175, 125, 2.0)
    sch.text("Das Mikrofon darf laut Datenblatt nur 100 pF treiben. Der Buffer", 175, 130)
    sch.text("entkoppelt es vom Kabel und macht die Kabellaenge unkritisch.", 175, 134)

    for unit, (yc, src, dst) in enumerate(
            [(155.0, "MIC_P", "BUF_P"), (185.0, "MIC_N", "BUF_N")], start=1):
        u = sch.part("Amplifier_Operational:OPA2325", "U2", "OPA2325", 213.36, yc,
                     unit=unit, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
                     fields={"MPN": "OPA2325AIDR"})
        plus = "3" if unit == 1 else "5"
        minus = "2" if unit == 1 else "6"
        out = "1" if unit == 1 else "7"
        px, py = u.pin(plus)
        sch.wire(px, py, px - 7.62, py)
        sch.label(src, px - 7.62, py, 180)
        ox, oy = u.pin(out)
        mx, my = u.pin(minus)
        sch.route((ox, oy), (ox + 5.08, oy), (ox + 5.08, oy + 12.7),
                  (mx - 5.08, oy + 12.7), (mx - 5.08, my), (mx, my))
        sch.wire(ox + 5.08, oy, ox + 12.7, oy)
        sch.junction(ox + 5.08, oy)
        sch.label(dst, ox + 12.7, oy, 0)

    upwr = sch.part("Amplifier_Operational:OPA2325", "U2", "OPA2325", 269.24, 160,
                    unit=3, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
    vp = upwr.pin("8")
    sch.wire(vp[0], vp[1], vp[0], vp[1] - 5.08)
    sch.power("+2V8", vp[0], vp[1] - 5.08)
    vn = upwr.pin("4")
    sch.wire(vn[0], vn[1], vn[0], vn[1] + 5.08)
    sch.power("GND", vn[0], vn[1] + 5.08)

    c6 = sch.part("Device:C", "C6", "100n", 287.02, 152.4, footprint=FP_C)
    sch.wire(vp[0], vp[1] - 5.08, 287.02, vp[1] - 5.08)
    sch.wire(287.02, vp[1] - 5.08, *c6.pin("1"))
    sch.power("GND", *c6.pin("2"))
    sch.junction(vp[0], vp[1] - 5.08)

    c7 = sch.part("Device:C", "C7", "1u/16V", 302.26, 152.4, footprint=FP_C)
    sch.wire(287.02, vp[1] - 5.08, 302.26, vp[1] - 5.08)
    sch.wire(302.26, vp[1] - 5.08, *c7.pin("1"))
    sch.power("GND", *c7.pin("2"))
    sch.junction(287.02, vp[1] - 5.08)

    # ------------------------------------------------------------------
    # Serienwiderstaende zum Kabel
    # ------------------------------------------------------------------
    sch.text("Serienwiderstaende: Stabilitaet des OPA2325 an kapazitiver Last", 330, 125)
    sch.text("und HF-Filter zusammen mit der Kabelkapazitaet.", 330, 129)

    r1 = sch.part("Device:R", "R1", "100R", 342.9, 155, 90, footprint=FP_R)
    sch.stub(r1, "1", "BUF_P", 5.08)
    sch.stub(r1, "2", "OUT_P", 5.08, glob=True, shape="output")

    r2 = sch.part("Device:R", "R2", "100R", 342.9, 185, 90, footprint=FP_R)
    sch.stub(r2, "1", "BUF_N", 5.08)
    sch.stub(r2, "2", "OUT_N", 5.08, glob=True, shape="output")

    # ------------------------------------------------------------------
    # Schirmanbindung
    # ------------------------------------------------------------------
    # Frueher stand hier ein 0R als abschaltbare Bruecke zwischen Schirm und
    # Masse, unbestueckt. Das war wirkungslos: Kabelmasse und Schirm liegen
    # ohnehin auf demselben Knoten, und ein unbestuecktes Bauteil trennt in
    # der Netzliste nichts - KiCad fuehrt DNP-Teile weiterhin als Verbindung.
    # Die Kupferflaeche waere also in jedem Fall durchgaengig gewesen.
    sch.text("Schirm und Kabelmasse liegen hier auf einem Knoten und sind", 330, 212)
    sch.text("damit beidseitig geerdet - so wirkt der Schirm auch bei hohen", 330, 216)
    sch.text("Frequenzen. Gleichtaktanteile faengt die Drossel auf der", 330, 220)
    sch.text("Hauptplatine ab, nicht die Schirmfuehrung.", 330, 224)

    return sch



def load_sourcing() -> dict:
    """tools/parts.json einlesen, falls vorhanden."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parts.json")
    if not os.path.exists(path):
        return {}
    import json
    return json.load(open(path, encoding="utf-8"))


def write_project() -> None:
    os.makedirs(PROJ_DIR, exist_ok=True)
    sch = build()
    quellen = load_sourcing()
    if quellen:
        print(f"Beschaffungsdaten auf {sch.apply_sourcing(quellen)} Bauteile angewandt")
    path = sch.write(PROJ_DIR)
    print("wrote", path)

    pro = os.path.join(PROJ_DIR, PROJECT + ".kicad_pro")
    if not os.path.exists(pro):
        with open(pro, "w", encoding="utf-8") as fh:
            fh.write('{\n  "board": {},\n  "meta": {"filename": "%s.kicad_pro", '
                     '"version": 1},\n  "sheets": [],\n  "text_variables": {}\n}\n'
                     % PROJECT)
        print("wrote", pro)

    tbl = os.path.join(PROJ_DIR, "sym-lib-table")
    with open(tbl, "w", encoding="utf-8") as fh:
        fh.write("(sym_lib_table\n"
                 '  (lib (name "exhaust-mic")(type "KiCad")'
                 '(uri "${KIPRJMOD}/../lib/exhaust-mic.kicad_sym")'
                 '(options "")(descr "Projektsymbole exhaust-mic"))\n)\n')
    print("wrote", tbl)


if __name__ == "__main__":
    write_project()
