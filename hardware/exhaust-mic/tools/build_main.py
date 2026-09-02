#!/usr/bin/env python3
"""Generate the exhaust-mic main board schematic.

Root sheet plus five child sheets. Cross-sheet connectivity is by global
label, so the sheets carry no hierarchical pins.

Reference: docs/specs/2026-08-28-exhaust-mic-design.md
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kigen import SymbolLib, Schematic  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.normpath(os.path.join(HERE, ".."))
LOCAL_LIB = os.path.join(PROJ_DIR, "lib", "exhaust-mic.kicad_sym")

PROJECT = "exhaust-mic"
REV = "A"
DATE = "2026-08-28"
COMPANY = "Hayabusa / exhaust-mic"

R0603 = "Resistor_SMD:R_0603_1608Metric"
R0805 = "Resistor_SMD:R_0805_2012Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
SOD123 = "Diode_SMD:D_SOD-123"
SMB = "Diode_SMD:D_SMB"


def new_lib() -> SymbolLib:
    lib = SymbolLib()
    lib.add_stock("Device", "Connector", "Connector_Generic", "power", "Diode",
                  "Switch", "RF_Module", "Interface_CAN_LIN", "Oscillator",
                  "Amplifier_Operational")
    lib.add_file("exhaust-mic", LOCAL_LIB)
    return lib


def sheet(lib, filename, title, root_uuid):
    sch = Schematic(lib, PROJECT, filename, title=title, rev=REV, date=DATE,
                    company=COMPANY, paper="A3")
    from kigen import uuid_for
    sch.parent_path = "/" + root_uuid + "/" + uuid_for(PROJECT, filename)
    return sch


def cap_to_gnd(sch, ref, value, x, y, node_x, node_y, fp=C0603, junction=True):
    """Drop a bypass cap from a horizontal rail down to a ground symbol."""
    c = sch.part("Device:C", ref, value, x, y, footprint=fp)
    top = c.pin("1")
    sch.wire(node_x, node_y, x, node_y)
    sch.wire(x, node_y, top[0], top[1])
    sch.power("GND", *c.pin("2"))
    if junction:
        sch.junction(node_x, node_y)
    return c


# ==========================================================================
# 01 - Versorgung
# ==========================================================================

def build_power(lib, root_uuid) -> Schematic:
    s = sheet(lib, "01-power.kicad_sch",
              "Exhaust-Mic - Versorgung, Schutzbeschaltung, Zuendungserkennung",
              root_uuid)

    s.text("Bordnetzeingang und Schutz", 30, 30, 2.2)
    s.text("Dauerplus. IGN ist reiner Sense-Eingang - der ESP32 geht bei Zuendung aus", 30, 36)
    s.text("in Deep-Sleep (ca. 20 uA) statt die Versorgung abzuschalten. Standby gesamt", 30, 40)
    s.text("rund 90 uA, das haelt die Fahrzeugbatterie problemlos aus.", 30, 44)

    # ---- Harness-Steckverbinder -------------------------------------
    j1 = s.part("Connector_Generic:Conn_01x06", "J1", "XH-6pol_Power_CAN",
                40, 70,
                footprint="Connector_JST:JST_XH_S6B-XH-A_1x06_P2.50mm_Horizontal",
                fields={"MPN": "S6B-XH-A(LF)(SN)"})
    s.stub(j1, "1", "V12_IN", 12.7)
    # Kein eigenes Label: Pin 2 liegt direkt auf GND. Der fruehere Name
    # GND_CHASSIS suggerierte eine Trennung, die es nicht gibt - auf dem
    # Motorrad ist der Rahmen der Minuspol.
    s.wire(*j1.pin("2"), j1.pin("2")[0] - 12.7, j1.pin("2")[1])
    s.stub(j1, "3", "IGN_IN", 12.7, glob=True, shape="input")
    s.stub(j1, "4", "CANH", 12.7, glob=True, shape="bidirectional")
    s.stub(j1, "5", "CANL", 12.7, glob=True, shape="bidirectional")
    s.stub(j1, "6", "EXT_BTN", 12.7, glob=True, shape="input")
    gx, gy = j1.pin("2")
    s.wire(gx - 12.7, gy, gx - 20.32, gy)
    s.wire(gx - 20.32, gy, gx - 20.32, gy + 7.62)
    s.power("GND", gx - 20.32, gy + 7.62)

    # ---- Sicherung, Verpolschutz, TVS -------------------------------
    rail = 62.0
    s.label("V12_IN", 62, rail, 0)
    s.wire(62, rail, 72, rail)
    f1 = s.part("Device:Fuse", "F1", "2A_traege", 76.2, rail, 90,
                footprint="Fuse:Fuse_1206_3216Metric",
                fields={"MPN": "0453002.MR"})
    s.wire(72, rail, *f1.pin("1"))

    q1 = s.part("Device:Q_PMOS_GSD", "Q1", "ZXMP6A17E6", 104.14, rail + 7.62, 0,
                footprint=SOT23,
                fields={"MPN": "ZXMP6A17E6TA",
                        "Hinweis": "Drain am Bordnetz, Source zur Last"})
    # Drain am Eingang, Source zur Last. Beide Pins liegen auf derselben
    # x-Achse, deshalb bekommt die Lastseite eine eigene Schiene weiter unten -
    # sonst wuerde der Transistor schlicht ueberbrueckt.
    dx, dy = q1.pin("3")
    s.wire(f1.pin("2")[0], rail, dx, rail)
    s.wire(dx, rail, dx, dy)
    sx, sy = q1.pin("2")
    out_rail = sy
    s.wire(sx, sy, 137.16, out_rail)

    # Gate: 10k nach GND, Zener begrenzt Vgs bei Load-Dump
    ggx, ggy = q1.pin("1")
    gate_x = ggx - 12.7
    s.wire(ggx, ggy, gate_x, ggy)
    r1 = s.part("Device:R", "R1", "10k", gate_x, ggy + 12.7, footprint=R0603)
    s.wire(gate_x, ggy, *r1.pin("1"))
    s.power("GND", *r1.pin("2"))
    # Kathode auf die Source-Seite, also direkt an VBAT12
    d1 = s.part("Device:D_Zener", "D1", "BZX84C15", gate_x - 15.24, ggy - 7.62,
                270, footprint=SOT23, fields={"MPN": "BZX84C15LT1G"})
    s.power("VBAT12", *d1.pin("1"))
    ax_, ay_ = d1.pin("2")
    s.wire(ax_, ay_, ax_, ggy)
    s.wire(ax_, ggy, gate_x, ggy)
    s.text("D1 begrenzt Vgs auf 15 V - ohne sie zerstoert ein Load-Dump", 66, 92)
    s.text("mit 40 V das Gate (Vgs max +/-20 V).", 66, 96)

    d2 = s.part("Device:D_TVS", "D2", "SMBJ36A", 137.16, out_rail + 12.7, 270,
                footprint=SMB, fields={"MPN": "SMBJ36A-13-F",
                                       "Hinweis": "unidirektional, Kathode nach +12V"})
    s.wire(137.16, out_rail, *d2.pin("1"))
    s.power("GND", *d2.pin("2"))
    s.wire(137.16, out_rail, 165.1, out_rail)
    s.power("VBAT12", 165.1, out_rail - 7.62)
    s.wire(165.1, out_rail, 165.1, out_rail - 7.62)

    # ERC braucht je Netz eine Quelle. Bordnetz, Masse und USB kommen ueber
    # Steckverbinderpins herein, die als "passiv" gelten.
    s.text("Speiseflags fuer ERC", 250, 118, 2.0)
    for i, (rail, xx) in enumerate((("VBAT12", 250.0), ("GND", 275.0),
                                    ("USB_VBUS", 300.0), ("+4V6", 325.0))):
        fl = s.part("power:PWR_FLAG", f"#FLG{i:04d}", "PWR_FLAG", xx, 132.0,
                    in_bom=False)
        s.wire(xx, 132.0, xx, 138.0)
        if rail == "USB_VBUS":
            s.glabel("USB_VBUS", xx, 138.0, 270, "input")
        else:
            s.power(rail, xx, 138.0)

    # ---- Buck ---------------------------------------------------------
    s.text("Abwaertswandler 12 V -> 4,6 V", 30, 118, 2.2)
    s.text("LM5164: 100 V Eingang, synchron, 10,5 uA Ruhestrom. Fsw = Vout*2500/Rron", 30, 124)
    s.text("= 4,6*2500/28,7k = 401 kHz. R7 und C5 erzeugen die vom COT-Regler", 30, 128)
    s.text("geforderten 20 mV Rippel am FB-Knoten (Type-2, Datenblatt Tabelle 6-1).", 30, 132)

    vin_y = 150.0
    s.power("VBAT12", 40, vin_y - 7.62)
    s.wire(40, vin_y - 7.62, 40, vin_y)
    s.wire(40, vin_y, 88.9, vin_y)
    cap_to_gnd(s, "C1", "2u2/100V", 48.26, vin_y + 12.7, 40, vin_y, C0805)
    cap_to_gnd(s, "C2", "2u2/100V", 60.96, vin_y + 12.7, 48.26, vin_y, C0805)
    cap_to_gnd(s, "C3", "100n/100V", 73.66, vin_y + 12.7, 60.96, vin_y, C0603)

    u1 = s.part("exhaust-mic:LM5164", "U1", "LM5164DDA", 116.84, vin_y + 8.89,
                footprint="Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm",
                fields={"MPN": "LM5164DDAR",
                        "Datasheet": "https://www.ti.com/lit/ds/symlink/lm5164.pdf"})
    px, py = u1.pin("2")                     # VIN
    s.wire(88.9, vin_y, 88.9, py)
    s.wire(88.9, py, px, py)
    s.junction(73.66, vin_y)

    # GND und EP
    for pin in ("1", "9"):
        gx, gy = u1.pin(pin)
        s.wire(gx, gy, gx, gy + 6.35)
        s.power("GND", gx, gy + 6.35)

    # UVLO-Teiler: Abschaltung unter ca. 11,5 V schuetzt die Batterie.
    # Jeder der drei linken Pins bekommt eine eigene x-Spalte, sonst laufen
    # die Abzweige uebereinander.
    ex, ey = u1.pin("3")
    uvlo_x = ex - 20.32
    s.wire(ex, ey, uvlo_x, ey)
    r2 = s.part("Device:R", "R2", "1M", uvlo_x, ey - 15.24, footprint=R0603)
    s.wire(uvlo_x, ey, *r2.pin("2"))
    s.power("VBAT12", *r2.pin("1"))
    r3 = s.part("Device:R", "R3", "150k", uvlo_x, ey + 15.24, footprint=R0603)
    s.wire(uvlo_x, ey, *r3.pin("1"))
    s.power("GND", *r3.pin("2"))
    s.text("UVLO 11,5 V", uvlo_x - 26, ey - 1)

    # RON - eigene Spalte, kurz vor der UVLO-Spalte
    rx, ry = u1.pin("4")
    ron_x = rx - 6.35
    s.wire(rx, ry, ron_x, ry)
    r4 = s.part("Device:R", "R4", "28k7", ron_x, ry + 15.24, footprint=R0603)
    s.wire(ron_x, ry, *r4.pin("1"))
    s.power("GND", *r4.pin("2"))

    # BST
    bx, by = u1.pin("7")
    c4 = s.part("Device:C", "C4", "2n2/50V", bx + 15.24, by, 90, footprint=C0603)
    s.wire(bx, by, *c4.pin("1"))

    # SW -> Drossel
    swx, swy = u1.pin("8")
    s.wire(swx, swy, swx + 7.62, swy)
    s.wire(swx + 7.62, swy, swx + 7.62, swy - 12.7)
    sw_y = swy - 12.7
    s.wire(c4.pin("2")[0], by, c4.pin("2")[0] + 7.62, by)
    s.wire(c4.pin("2")[0] + 7.62, by, c4.pin("2")[0] + 7.62, sw_y)
    s.junction(swx + 7.62, sw_y)
    s.wire(swx + 7.62, sw_y, 175.26, sw_y)

    l1 = s.part("Device:L", "L1", "22u/1A2", 179.07, sw_y, 90,
                footprint="Inductor_SMD:L_Bourns_SRN6045TA",
                fields={"MPN": "SRN6045TA-220M"})
    out_y = sw_y
    s.wire(l1.pin("2")[0], out_y, 200.66, out_y)

    # Ausgangskapazitaet mit Rippel-Widerstand
    c6 = s.part("Device:C", "C6", "22u/25V", 200.66, out_y + 12.7, footprint=C1210)
    s.wire(200.66, out_y, *c6.pin("1"))
    s.junction(200.66, out_y)
    c7 = s.part("Device:C", "C7", "22u/25V", 213.36, out_y + 12.7, footprint=C1210)
    s.wire(200.66, out_y, 213.36, out_y)
    s.wire(213.36, out_y, *c7.pin("1"))
    s.junction(213.36, out_y)
    s.wire(c6.pin("2")[0], c6.pin("2")[1], c7.pin("2")[0], c7.pin("2")[1])
    r7 = s.part("Device:R", "R7", "0R1", 207.01, out_y + 25.4, footprint=R0805,
                fields={"Hinweis": "Rippelerzeugung Type-2, ggf. am Aufbau nachziehen"})
    s.wire(207.01, c6.pin("2")[1], *r7.pin("1"))
    s.power("GND", *r7.pin("2"))

    cap_to_gnd(s, "C8", "100n", 226.06, out_y + 12.7, 213.36, out_y, C0603)

    # FB-Teiler mit Feedforward. Der Abgriff faellt zuerst nach unten und
    # kreuzt damit weder die UVLO- noch die RON-Spalte.
    fx, fy = u1.pin("5")
    fb_col = fx - 2.54
    fb_y = 178.0
    s.wire(fx, fy, fb_col, fy)
    s.wire(fb_col, fy, fb_col, fb_y)

    r6 = s.part("Device:R", "R6", "12k0", fb_col, fb_y + 12.7, footprint=R0603)
    s.wire(fb_col, fb_y, *r6.pin("1"))
    s.power("GND", *r6.pin("2"))

    r5 = s.part("Device:R", "R5", "34k0", fb_col + 20.32, fb_y, 90, footprint=R0603)
    s.wire(fb_col, fb_y, *r5.pin("1"))
    c5 = s.part("Device:C", "C5", "100p", fb_col + 20.32, fb_y - 15.24, 90,
                footprint=C0603)
    s.wire(r5.pin("1")[0], fb_y, r5.pin("1")[0], c5.pin("1")[1])
    s.wire(r5.pin("1")[0], c5.pin("1")[1], *c5.pin("1"))
    s.wire(r5.pin("2")[0], fb_y, r5.pin("2")[0], c5.pin("2")[1])
    s.wire(r5.pin("2")[0], c5.pin("2")[1], *c5.pin("2"))

    tap_x = 246.38
    s.wire(r5.pin("2")[0], fb_y, tap_x, fb_y)
    s.wire(tap_x, fb_y, tap_x, out_y)
    s.wire(226.06, out_y, tap_x, out_y)
    s.text("C5 koppelt den Ausgangsrippel auf FB - ohne ihn", fb_col + 34, fb_y - 22)
    s.text("schwingt der COT-Regler in Bursts.", fb_col + 34, fb_y - 18)

    # PGOOD
    pgx, pgy = u1.pin("6")
    s.wire(pgx, pgy, pgx + 7.62, pgy)
    s.glabel("PGOOD", pgx + 7.62, pgy, 180, "output")

    # ---- Verodern mit USB, dann die beiden LDOs ------------------------
    s.text("Schienenaufteilung", 30, 248, 2.2)
    s.text("D3 und D4 verodern Bordnetz und USB, ohne dass eine Quelle in die andere", 30, 254)
    s.text("zurueckspeist. Digital und Analog bekommen getrennte Regler; der TPS7A2033", 30, 258)
    s.text("ist der rauscharme fuer PCM1863-AVDD und die beiden Mikrofonkoepfe.", 30, 262)

    ldo_y = 212.0
    d3 = s.part("Device:D_Schottky", "D3", "PMEG3020", 55.88, ldo_y, 180,
                footprint=SOD123, fields={"MPN": "PMEG3020EP-115"})
    feed_y = 200.0
    s.wire(258.06, out_y, 258.06, feed_y)
    s.wire(258.06, feed_y, 45.72, feed_y)
    s.wire(45.72, feed_y, 45.72, ldo_y)
    s.wire(tap_x, out_y, 258.06, out_y)
    s.wire(45.72, ldo_y, *d3.pin("2"))

    node46 = 88.9
    s.wire(d3.pin("1")[0], ldo_y, node46, ldo_y)

    d4 = s.part("Device:D_Schottky", "D4", "PMEG3020", 55.88, ldo_y + 17.78, 180,
                footprint=SOD123, fields={"MPN": "PMEG3020EP-115"})
    s.glabel("USB_VBUS", 40, ldo_y + 17.78, 0, "input")
    s.wire(40, ldo_y + 17.78, *d4.pin("2"))
    s.wire(d4.pin("1")[0], ldo_y + 17.78, node46, ldo_y + 17.78)
    s.wire(node46, ldo_y + 17.78, node46, ldo_y)
    s.junction(node46, ldo_y)

    cap_to_gnd(s, "C9", "1u/16V", 101.6, ldo_y + 12.7, node46, ldo_y, C0603)
    s.wire(101.6, ldo_y, 114.3, ldo_y)
    s.power("+4V6", 114.3, ldo_y - 7.62)
    s.wire(114.3, ldo_y, 114.3, ldo_y - 7.62)
    s.junction(101.6, ldo_y)

    # Digital-LDO
    u2 = s.part("exhaust-mic:TLV1117LV33", "U2", "TLV1117LV33", 165.1, ldo_y,
                footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
                fields={"MPN": "TLV1117LV33DCYR",
                        "Datasheet": "https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf"})
    ix, iy = u2.pin("3")
    s.power("+4V6", ix - 10.16, iy - 7.62)
    s.wire(ix - 10.16, iy - 7.62, ix - 10.16, iy)
    s.wire(ix - 10.16, iy, ix, iy)
    cap_to_gnd(s, "C10", "1u/16V", ix - 20.32, iy + 12.7, ix - 10.16, iy, C0603)
    gx, gy = u2.pin("1")
    s.wire(gx, gy, gx, gy + 6.35)
    s.power("GND", gx, gy + 6.35)
    # Pin 2 fuehrt zugleich die Kuehlfahne, ein separater Fahnen-Pin
    # entfaellt (siehe Symbol).
    ox, oy = u2.pin("2")
    s.wire(ox, oy, ox + 12.7, oy)
    cap_to_gnd(s, "C11", "22u/10V", ox + 25.4, oy + 12.7, ox + 12.7, oy, C1210)
    cap_to_gnd(s, "C12", "100n", ox + 38.1, oy + 12.7, ox + 25.4, oy, C0603)
    s.wire(ox + 38.1, oy, ox + 50.8, oy)
    s.power("+3V3D", ox + 50.8, oy - 7.62)
    s.wire(ox + 50.8, oy, ox + 50.8, oy - 7.62)

    # Analog-LDO
    u3 = s.part("exhaust-mic:TPS7A20", "U3", "TPS7A2033", 290.0, ldo_y + 3.81,
                footprint="Package_TO_SOT_SMD:SOT-23-5",
                fields={"MPN": "TPS7A2033PDBVR",
                        "Datasheet": "https://www.ti.com/lit/ds/symlink/tps7a20.pdf"})
    ix, iy = u3.pin("1")
    s.power("+4V6", ix - 15.24, iy - 7.62)
    s.wire(ix - 15.24, iy - 7.62, ix - 15.24, iy)
    s.wire(ix - 15.24, iy, ix, iy)
    ex, ey = u3.pin("3")
    s.wire(ix - 15.24, iy, ix - 15.24, ey)
    s.wire(ix - 15.24, ey, ex, ey)
    s.junction(ix - 15.24, iy)
    cap_to_gnd(s, "C13", "1u/16V", ix - 27.94, iy + 12.7, ix - 15.24, iy, C0603)
    gx, gy = u3.pin("2")
    s.wire(gx, gy, gx, gy + 6.35)
    s.power("GND", gx, gy + 6.35)
    s.noconn(*u3.pin("4"))
    ox, oy = u3.pin("5")
    s.wire(ox, oy, ox + 10.16, oy)
    cap_to_gnd(s, "C14", "1u/16V", ox + 10.16, oy + 12.7, ox + 10.16, oy, C0603,
               junction=False)
    cap_to_gnd(s, "C15", "10u/10V", ox + 22.86, oy + 12.7, ox + 10.16, oy, C0805)
    s.wire(ox + 22.86, oy, ox + 35.56, oy)
    s.power("+3V3A", ox + 35.56, oy - 7.62)
    s.wire(ox + 35.56, oy, ox + 35.56, oy - 7.62)

    # ---- Zuendungserkennung und Batteriemessung ------------------------
    s.text("Zuendung und Batteriespannung", 290, 30, 2.2)
    s.text("IGN treibt einen RTC-faehigen Pin, damit der ESP32 aus dem", 300, 36)
    s.text("Deep-Sleep aufwacht. D5/D6 klemmen den Load-Dump auf 3,3 V.", 300, 40)

    for (name, rtop, rbot, ref_r1, ref_r2, ref_c, ref_d, yv, src) in [
            ("IGN_SENSE", "100k", "47k", "R9", "R10", "C16", "D5", 60.0, "IGN_IN"),
            ("VBAT_SENSE", "470k", "68k", "R11", "R12", "C17", "D6", 95.0, None)]:
        if src:
            s.glabel(src, 300, yv, 0, "input")
            s.wire(300, yv, 312.42, yv)
        else:
            s.power("VBAT12", 312.42, yv - 7.62)
            s.wire(312.42, yv - 7.62, 312.42, yv)
        ra = s.part("Device:R", ref_r1, rtop, 316.23, yv, 90, footprint=R0603)
        s.wire(312.42, yv, *ra.pin("1"))
        mid = 330.2
        s.wire(ra.pin("2")[0], yv, mid, yv)
        rb = s.part("Device:R", ref_r2, rbot, mid, yv + 12.7, footprint=R0603)
        s.wire(mid, yv, *rb.pin("1"))
        s.power("GND", *rb.pin("2"))
        s.junction(mid, yv)
        cc = s.part("Device:C", ref_c, "100n", mid + 12.7, yv + 12.7, footprint=C0603)
        s.wire(mid, yv, mid + 12.7, yv)
        s.wire(mid + 12.7, yv, *cc.pin("1"))
        s.power("GND", *cc.pin("2"))
        s.junction(mid + 12.7, yv)
        dz = s.part("Device:D_Zener", ref_d, "BZX84C3V3", mid + 25.4, yv + 12.7,
                    270, footprint=SOT23)
        s.wire(mid + 12.7, yv, mid + 25.4, yv)
        s.wire(mid + 25.4, yv, *dz.pin("1"))
        s.power("GND", *dz.pin("2"))
        s.wire(mid + 25.4, yv, mid + 40.64, yv)
        s.glabel(name, mid + 40.64, yv, 180, "output")

    return s


# ==========================================================================
# 02 - Analoge Eingangsstufe
# ==========================================================================

def build_analog(lib, root_uuid) -> Schematic:
    s = sheet(lib, "02-analog.kicad_sch",
              "Exhaust-Mic - Mikrofoneingaenge, EMV-Filter, ADC-Ankopplung",
              root_uuid)

    s.text("Mikrofoneingaenge", 25, 22, 2.2)
    s.text("Beide Kanaele identisch. Die Mikrofonkoepfe treiben symmetrisch und", 25, 28)
    s.text("niederohmig, Stoerungen bleiben dadurch Gleichtakt. Die Gleichtaktdrossel", 25, 32)
    s.text("unterdrueckt den Rest, bevor der PCM1863 mit seinen nur 56 dB CMRR uebernimmt.", 25, 36)
    s.text("Die Koppelkondensatoren sind Pflicht - die ADC-Eingaenge stellen ihren", 25, 40)
    s.text("Arbeitspunkt selbst auf AVDD/2 ein (Datenblatt Abschnitt 9.3.1).", 25, 44)

    channels = [("A", "Endrohr", 75.0, "J2", "FB2", "C20", "L2", ("D10", "D11"),
                 ("R20", "R21"), ("C21", "C22"), ("C23", "C24")),
                ("B", "Airbox", 200.0, "J3", "FB3", "C25", "L3", ("D12", "D13"),
                 ("R22", "R23"), ("C26", "C27"), ("C28", "C29"))]

    for (ch, where, y0, jref, fbref, cbulk, lref, dref, rref, cshunt,
         ccoup) in channels:
        s.text(f"Kanal {ch} - {where}", 25, y0 - 18, 2.0)

        # ---------------- Steckverbinder ----------------
        j = s.part("Connector_Generic:Conn_01x05", jref,
                   f"XH-5pol_Mic{ch}", 45, y0, 180,
                   footprint="Connector_JST:JST_XH_S5B-XH-A_1x05_P2.50mm_Horizontal",
                   fields={"MPN": "S5B-XH-A(LF)(SN)"})
        p1, p2 = j.pin("1"), j.pin("2")
        p5 = j.pin("5")

        # Schirm nach oben, Kabelmasse nach oben aussen, Versorgung nach unten.
        # Jeder Abzweig biegt an eigener x-Position ab, damit sich die
        # Steigleitungen nicht mit den Signalabgriffen schneiden.
        s.wire(p5[0], p5[1], p5[0] + 7.62, p5[1])
        s.wire(p5[0] + 7.62, p5[1], p5[0] + 7.62, p5[1] - 10.16)
        s.power("GND", p5[0] + 7.62, p5[1] - 10.16)

        s.stub(j, "4", f"{ch}_N_RAW", 15.24)
        s.stub(j, "3", f"{ch}_P_RAW", 22.86)

        s.wire(p2[0], p2[1], p2[0] + 30.48, p2[1])
        s.wire(p2[0] + 30.48, p2[1], p2[0] + 30.48, p2[1] - 22.86)
        s.power("GND", p2[0] + 30.48, p2[1] - 22.86)

        rail_y = p1[1] + 20.32
        s.wire(p1[0], p1[1], p1[0] + 38.1, p1[1])
        s.wire(p1[0] + 38.1, p1[1], p1[0] + 38.1, rail_y)
        fb = s.part("Device:FerriteBead", fbref, "600R@100MHz",
                    p1[0] + 45.72, rail_y, 90, footprint=R0603)
        s.wire(p1[0] + 38.1, rail_y, *fb.pin("1"))
        s.wire(fb.pin("2")[0], rail_y, p1[0] + 60.96, rail_y)
        cb = s.part("Device:C", cbulk, "10u/10V", p1[0] + 60.96, rail_y + 12.7,
                    footprint=C0805)
        s.wire(p1[0] + 60.96, rail_y, *cb.pin("1"))
        s.power("GND", *cb.pin("2"))
        s.wire(p1[0] + 60.96, rail_y, p1[0] + 71.12, rail_y)
        s.power("+3V3A", p1[0] + 71.12, rail_y)
        s.text("Versorgung fuer den Mikrofonkopf", p1[0] + 30, rail_y + 22)

        # ---------------- Gleichtaktdrossel mit Klemmung ----------------
        cmc = s.part("Device:L_Ferrite_Coupled", lref, "1mH_CMC", 140, y0 + 7.62,
                     footprint="Inductor_SMD:L_CommonMode_Wuerth_WE-SL2",
                     fields={"MPN": "744232222"})
        in_p, in_n = cmc.pin("1"), cmc.pin("3")

        s.label(f"{ch}_P_RAW", in_p[0] - 22.86, in_p[1], 0)
        s.wire(in_p[0] - 22.86, in_p[1], in_p[0], in_p[1])
        s.label(f"{ch}_N_RAW", in_n[0] - 22.86, in_n[1], 0)
        s.wire(in_n[0] - 22.86, in_n[1], in_n[0], in_n[1])

        # P-Klemmung nach oben, N-Klemmung nach unten - so beruehren sich
        # die beiden Zweige nirgends.
        tap = in_p[0] - 10.16
        dp = s.part("Device:D_TVS", dref[0], "PESD3V3L1BA", tap, in_p[1] - 14.0,
                    90, footprint=SOD123)
        s.wire(tap, in_p[1], *dp.pin("1"))
        s.power("GND", *dp.pin("2"))
        dn = s.part("Device:D_TVS", dref[1], "PESD3V3L1BA", tap, in_n[1] + 14.0,
                    270, footprint=SOD123)
        s.wire(tap, in_n[1], *dn.pin("1"))
        s.power("GND", *dn.pin("2"))

        # ---------------- Filter und Ankopplung ----------------
        out_p, out_n = cmc.pin("2"), cmc.pin("4")
        p_y, n_y = y0 - 7.62, y0 + 27.94
        s.route(out_p, (out_p[0] + 7.62, out_p[1]), (out_p[0] + 7.62, p_y),
                (162.0 - 3.81, p_y))
        s.route(out_n, (out_n[0] + 15.24, out_n[1]), (out_n[0] + 15.24, n_y),
                (162.0 - 3.81, n_y))

        for (yy, rr, cs, cc, up, netname) in (
                (p_y, rref[0], cshunt[0], ccoup[0], True, f"ADC_{ch}_P"),
                (n_y, rref[1], cshunt[1], ccoup[1], False, f"ADC_{ch}_N")):
            r = s.part("Device:R", rr, "100R", 162.0, yy, 90, footprint=R0603)
            node = 180.34
            s.wire(r.pin("2")[0], yy, node, yy)
            shunt = s.part("Device:C", cs, "33p", node,
                           yy - 14.0 if up else yy + 14.0, footprint=C0603)
            near, far = (shunt.pin("2"), shunt.pin("1")) if up else \
                        (shunt.pin("1"), shunt.pin("2"))
            s.wire(node, yy, *near)
            s.power("GND", *far)
            ccp = s.part("Device:C", cc, "1u/16V", 198.12, yy, 90, footprint=C0603)
            s.wire(node, yy, *ccp.pin("1"))
            s.wire(ccp.pin("2")[0], yy, 220.98, yy)
            s.glabel(netname, 220.98, yy, 180, "output")

    s.text("100 Ohm in Serie mit 33 pF ergibt rund 48 MHz Grenzfrequenz - das hoert man", 25, 262)
    s.text("nicht, haelt aber HF vom ADC-Eingang fern. Der 1-uF-Koppelkondensator bildet", 25, 266)
    s.text("mit den 20 kOhm Eingangswiderstand des PCM1863 einen 8-Hz-Hochpass.", 25, 270)
    return s


# ==========================================================================
# 03 - ADC
# ==========================================================================

def build_adc(lib, root_uuid) -> Schematic:
    s = sheet(lib, "03-adc.kicad_sch",
              "Exhaust-Mic - Stereo-ADC PCM1863 und Audiotakt", root_uuid)

    s.text("Stereo-ADC", 25, 26, 2.2)
    s.text("PCM1863 arbeitet als I2S-Master: der 24,576-MHz-Oszillator geht auf SCKI,", 25, 32)
    s.text("der ADC erzeugt BCK und LRCK selbst. Der ESP32 ist reiner Slave-Empfaenger", 25, 36)
    s.text("und muss keinen audiogenauen Takt bereitstellen.", 25, 40)
    s.text("512 x fs = 24,576 MHz -> 48 kHz;  256 x fs -> 96 kHz. Beides aus einem Quarz.", 25, 44)

    u5 = s.part("exhaust-mic:PCM1863", "U5", "PCM1863DBT", 190.5, 150,
                footprint="exhaust-mic:TSSOP-30_4.4x7.8mm_P0.5mm",
                fields={"MPN": "PCM1863DBTR",
                        "Datasheet": "https://www.ti.com/lit/ds/symlink/pcm1863.pdf"})

    # Analogeingaenge
    for pin, net in (("3", "ADC_A_P"), ("1", "ADC_A_N"),
                     ("4", "ADC_B_P"), ("2", "ADC_B_N")):
        s.stub(u5, pin, net, 22.86, glob=True, shape="input")

    # Unbenutzte Analogeingaenge bleiben offen (Datenblatt: "Do not connect")
    for pin in ("29", "27", "30", "28"):
        px, py = u5.pin(pin)
        s.noconn(px, py)
    s.text("Datenblatt: unbenutzte Analogeingaenge NICHT beschalten.", 60, 200)

    # MICBIAS bleibt offen (Datenblatt: darf unbeschaltet bleiben).
    # VREF liegt zwei Rasterschritte ueber dem LDO-Pin, deshalb greift der
    # VREF-Zweig weiter links ab als die LDO-Zweige.
    s.noconn(*u5.pin("5"))
    vx, vy = u5.pin("6")
    s.wire(vx, vy, vx - 40.64, vy)
    c30 = s.part("Device:C", "C30", "1u/16V", vx - 40.64, vy + 12.7, footprint=C0603)
    s.wire(vx - 40.64, vy, *c30.pin("1"))
    s.power("GND", *c30.pin("2"))
    s.text("C30 an VREF, 1 uF laut Datenblatt", vx - 40.64, vy - 4)

    lx, ly = u5.pin("11")
    s.wire(lx, ly, lx - 27.94, ly)
    c31 = s.part("Device:C", "C31", "100n", lx - 15.24, ly + 12.7, footprint=C0603)
    s.wire(lx - 15.24, ly, *c31.pin("1"))
    s.power("GND", *c31.pin("2"))
    c32 = s.part("Device:C", "C32", "10u/10V", lx - 27.94, ly + 12.7, footprint=C0805)
    s.wire(lx - 27.94, ly, *c32.pin("1"))
    s.power("GND", *c32.pin("2"))

    # Massepins
    for pin, xoff in (("7", -6.35), ("12", 6.35)):
        gx, gy = u5.pin(pin)
        s.wire(gx, gy, gx, gy + 7.62)
        s.power("GND", gx, gy + 7.62)

    # AVDD ueber Ferrit von der rauscharmen Analogschiene
    ax, ay = u5.pin("8")
    node_y = ay - 10.16
    s.wire(ax, ay, ax, node_y)
    fb4 = s.part("Device:FerriteBead", "FB4", "600R@100MHz", ax, node_y - 7.62,
                 footprint=R0603)
    s.wire(ax, node_y, *fb4.pin("2"))
    s.wire(ax, fb4.pin("1")[1], ax, fb4.pin("1")[1] - 7.62)
    s.power("+3V3A", ax, fb4.pin("1")[1] - 7.62)
    # AVDD wird nur ueber den Ferrit gespeist, der als passiv gilt.
    # Das Flag haengt links an derselben Leitung wie C33/C34; nach rechts
    # laege es im Bausteinkoerper und wuerde fremde Pins kreuzen.
    s.part("power:PWR_FLAG", "#FLG0100", "PWR_FLAG", ax - 53.34,
           node_y - 7.62, in_bom=False)
    s.wire(ax - 53.34, node_y - 7.62, ax - 53.34, node_y)
    s.wire(ax - 53.34, node_y, ax - 38.1, node_y)
    for ref, val, dx, fp in (("C33", "10u/10V", -22.86, C0805),
                             ("C34", "100n", -38.1, C0603)):
        c = s.part("Device:C", ref, val, ax + dx, node_y + 8.89, footprint=fp)
        s.wire(ax, node_y, ax + dx, node_y)
        s.wire(ax + dx, node_y, *c.pin("1"))
        s.power("GND", *c.pin("2"))
    s.text("AVDD haengt hinter FB4 an der rauscharmen Schiene.", ax - 60, node_y - 20)

    # DVDD und IOVDD liegen auf derselben Schiene, also ein gemeinsamer Zweig
    dvx, dvy = u5.pin("13")
    iox, ioy = u5.pin("14")
    bus_y = dvy - 15.24
    s.wire(dvx, dvy, dvx, bus_y)
    s.wire(iox, ioy, iox, bus_y)
    s.wire(dvx, bus_y, iox + 20.32, bus_y)
    s.power("+3V3D", iox + 20.32, bus_y - 7.62)
    s.wire(iox + 20.32, bus_y, iox + 20.32, bus_y - 7.62)
    for ref, val, cx_, fp in (("C35", "10u/10V", dvx + 3.81, C0805),
                              ("C36", "100n", iox + 6.35, C0603)):
        c = s.part("Device:C", ref, val, cx_, bus_y - 8.89, footprint=fp)
        s.wire(cx_, bus_y, *c.pin("2"))
        s.power("GND", *c.pin("1"))

    # Audio-Interface zum ESP32
    for pin, net, shape in (("16", "I2S_LRCK", "output"), ("17", "I2S_BCK", "output"),
                            ("18", "I2S_DOUT", "output")):
        s.stub(u5, pin, net, 22.86, glob=True, shape=shape)

    # Steuerbus
    for pin, net in (("23", "I2C_SDA"), ("24", "I2C_SCL")):
        s.stub(u5, pin, net, 22.86, glob=True, shape="bidirectional")
    s.stub(u5, "21", "PCM_INT", 22.86, glob=True, shape="output")

    # MD0 low = I2C, MS/AD low = Basisadresse
    for pin, note, off in (("26", "MD0 low = I2C-Modus", 10.16),
                           ("25", "AD low = Basisadresse", 17.78)):
        px, py = u5.pin(pin)
        s.wire(px, py, px + off, py)
        s.power("GND", px + off, py)
        s.text(note, px + off + 5.08, py + 1.5)

    for pin in ("22", "20", "19", "9", "10"):
        s.noconn(*u5.pin(pin))
    s.text("XI/XO bleiben offen: XI vertraegt nur 1,8 V, der Takt kommt", 240, 96)
    s.text("ueber SCKI mit 3,3 V CMOS.", 240, 100)

    # Oszillator
    s.text("Audiotakt", 25, 232, 2.2)
    y1 = s.part("Oscillator:XO53", "Y1", "24.576MHz", 60, 258,
                footprint="Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm",
                fields={"MPN": "ASE-24.576MHZ-ET"})
    ex, ey = y1.pin("1")
    s.wire(ex, ey, ex - 10.16, ey)
    s.wire(ex - 10.16, ey, ex - 10.16, ey - 10.16)
    s.power("+3V3D", ex - 10.16, ey - 10.16)
    vx, vy = y1.pin("4")
    s.wire(vx, vy, vx, vy - 7.62)
    s.power("+3V3D", vx, vy - 7.62)
    gx, gy = y1.pin("2")
    s.wire(gx, gy, gx, gy + 7.62)
    s.power("GND", gx, gy + 7.62)
    c37 = s.part("Device:C", "C37", "100n", vx + 17.78, vy - 7.62 + 8.89,
                 footprint=C0603)
    s.wire(vx, vy - 7.62, vx + 17.78, vy - 7.62)
    s.wire(vx + 17.78, vy - 7.62, *c37.pin("1"))
    s.power("GND", *c37.pin("2"))

    ox, oy = y1.pin("3")
    s.wire(ox, oy, ox + 7.62, oy)
    r24 = s.part("Device:R", "R24", "33R", ox + 11.43, oy, 90, footprint=R0603)
    s.wire(ox + 7.62, oy, *r24.pin("1"))
    s.wire(r24.pin("2")[0], oy, ox + 27.94, oy)
    s.label("MCLK", ox + 27.94, oy, 0)
    s.text("R24 daempft die Taktflanke - weniger Ueberschwingen und weniger", 25, 275)
    s.text("Einstrahlung in den daneben liegenden Analogteil.", 25, 279)

    scx, scy = u5.pin("15")
    s.wire(scx, scy, scx + 15.24, scy)
    s.label("MCLK", scx + 15.24, scy, 180)

    return s


# ==========================================================================
# 04 - MCU, USB, microSD
# ==========================================================================

def build_mcu(lib, root_uuid) -> Schematic:
    s = sheet(lib, "04-mcu.kicad_sch",
              "Exhaust-Mic - ESP32-S3, USB-C und microSD", root_uuid)

    s.text("Mikrocontroller", 25, 24, 2.2)
    s.text("ESP32-S3-WROOM-1-N8R2: 8 MB Flash, 2 MB Quad-PSRAM. Bewusst nicht die", 25, 30)
    s.text("R8-Variante - deren Octal-PSRAM belegt GPIO35...37, die hier fuer GPS", 25, 34)
    s.text("gebraucht werden. 2 MB reichen fuer rund 7 s Schreibpuffer.", 25, 38)
    s.text("WLAN muss waehrend der Aufnahme per Firmware aus bleiben.", 25, 42)

    u6 = s.part("RF_Module:ESP32-S3-WROOM-1", "U6", "ESP32-S3-WROOM-1-N8R2",
                165, 145, footprint="RF_Module:ESP32-S3-WROOM-1",
                fields={"MPN": "ESP32-S3-WROOM-1-N8R2", "LCSC": "C2913204"})

    # Versorgung. Die Abblockkondensatoren haengen in einer Reihe oberhalb
    # des Moduls, damit sie den Reset- und Bootpfaden nicht in die Quere kommen.
    vx, vy = u6.pin("3V3")
    rail_y = vy - 22.86
    s.wire(vx, vy, vx, rail_y)
    s.power("+3V3D", vx, rail_y - 7.62)
    s.wire(vx, rail_y, vx, rail_y - 7.62)
    for ref, val, dx, fp in [("C40", "22u/10V", -17.78, C1210),
                             ("C41", "10u/10V", -35.56, C0805),
                             ("C42", "100n", -53.34, C0603),
                             ("C43", "100n", -71.12, C0603)]:
        s.wire(vx, rail_y, vx + dx, rail_y)
        c = s.part("Device:C", ref, val, vx + dx, rail_y + 8.89, footprint=fp)
        s.wire(vx + dx, rail_y, *c.pin("1"))
        s.power("GND", *c.pin("2"))

    for pin in ("1", "40", "41"):
        gx, gy = u6.pin(pin)
        s.wire(gx, gy, gx, gy + 6.35)
        s.power("GND", gx, gy + 6.35)

    # EN mit Reset-Taster. Alle Abzweige fallen nach unten, jeder auf
    # eigener Spalte.
    ex, ey = u6.pin("EN")
    s.wire(ex, ey, ex - 45.72, ey)
    r30 = s.part("Device:R", "R30", "10k", ex - 5.08, ey - 12.7, footprint=R0603)
    s.wire(ex - 5.08, ey, *r30.pin("2"))
    s.power("+3V3D", *r30.pin("1"))
    c44 = s.part("Device:C", "C44", "1u/16V", ex - 20.32, ey + 12.7, footprint=C0603)
    s.wire(ex - 20.32, ey, *c44.pin("1"))
    s.power("GND", *c44.pin("2"))
    sw1 = s.part("Switch:SW_Push", "SW1", "RESET", ex - 50.8, ey + 15.24, 180,
                 footprint="Button_Switch_SMD:SW_SPST_TL3342")
    s.wire(ex - 45.72, ey, ex - 45.72, sw1.pin("1")[1])
    s.wire(ex - 45.72, sw1.pin("1")[1], *sw1.pin("1"))
    s.power("GND", *sw1.pin("2"))

    # IO0 mit Boot-Taster, tiefer gelegt damit nichts den EN-Zweig kreuzt
    bx, by = u6.pin("IO0")
    boot_y = by + 55.88
    s.wire(bx, by, bx - 10.16, by)
    s.wire(bx - 10.16, by, bx - 10.16, boot_y)
    s.wire(bx - 10.16, boot_y, bx - 40.64, boot_y)
    r31 = s.part("Device:R", "R31", "10k", bx - 25.4, boot_y - 12.7, footprint=R0603)
    s.wire(bx - 25.4, boot_y, *r31.pin("2"))
    s.power("+3V3D", *r31.pin("1"))
    sw2 = s.part("Switch:SW_Push", "SW2", "BOOT", bx - 45.72, boot_y, 180,
                 footprint="Button_Switch_SMD:SW_SPST_TL3342")
    s.wire(bx - 40.64, boot_y, *sw2.pin("1"))
    s.power("GND", *sw2.pin("2"))

    # Signalzuordnung, siehe Spec Abschnitt 7.1
    io_map = [
        ("IO5", "I2S_BCK", "input"), ("IO6", "I2S_LRCK", "input"),
        ("IO7", "I2S_DOUT", "input"),
        ("IO8", "I2C_SDA", "bidirectional"), ("IO18", "I2C_SCL", "output"),
        ("IO15", "RTC_SQW", "input"), ("IO17", "PCM_INT", "input"),
        ("IO4", "CAN_TX", "output"), ("IO16", "CAN_RX", "input"),
        ("IO1", "IGN_SENSE", "input"), ("IO2", "VBAT_SENSE", "input"),
        ("IO21", "BTN_REC", "input"), ("IO47", "BTN_MARK", "input"),
        ("IO48", "LED_REC", "output"), ("IO38", "LED_ERR", "output"),
        ("IO39", "LED_SYNC", "output"), ("IO40", "BUZZ", "output"),
        ("IO41", "PGOOD", "input"),
        ("IO35", "GPS_TX", "output"), ("IO36", "GPS_RX", "input"),
        ("IO37", "GPS_PPS", "input"),
        ("IO14", "SD_CLK", "output"), ("IO13", "SD_CMD", "bidirectional"),
        ("IO12", "SD_D0", "bidirectional"), ("IO11", "SD_D1", "bidirectional"),
        ("IO10", "SD_D2", "bidirectional"), ("IO9", "SD_D3", "bidirectional"),
        ("IO19", "USB_DM", "bidirectional"), ("IO20", "USB_DP", "bidirectional"),
        ("TXD0", "UART0_TX", "output"), ("RXD0", "UART0_RX", "input"),
    ]
    for name, net, shape in io_map:
        s.stub(u6, name, net, 19.05, glob=True, shape=shape)

    # Strapping-Pins und Reserve bleiben offen
    for name in ("IO3", "IO45", "IO46", "IO42"):
        s.noconn(*u6.pin(name))
    s.text("IO3/IO45/IO46 sind Strapping-Pins und bleiben frei.", 25, 250)
    s.text("IO42 ist Reserve.", 25, 254)

    # ---- USB-C -------------------------------------------------------
    s.text("USB-C", 300, 24, 2.2)
    s.text("Nativer USB des S3: Flashen, Konsole und Download der Aufnahmen.", 300, 30)

    j4 = s.part("Connector:USB_C_Receptacle_USB2.0_16P", "J4", "USB-C", 330, 80,
                footprint="Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11")
    # Im Symbol liegen A1/B1/A12/B12 und A4/B4/A9/B9 jeweils auf demselben
    # Punkt - ein Anschluss je Gruppe genuegt.
    gx, gy = j4.pin("A1")
    s.wire(gx, gy, gx, gy + 5.08)
    s.power("GND", gx, gy + 5.08)
    sx, sy = j4.pin("S1")
    s.wire(sx, sy, sx, sy + 5.08)
    s.power("GND", sx, sy + 5.08)
    s.stub(j4, "A4", "USB_VBUS", 15.24, glob=True, shape="output")
    for pin in ("A6", "B6"):
        s.stub(j4, pin, "USB_DP", 20.32, glob=True, shape="bidirectional")
    for pin in ("A7", "B7"):
        s.stub(j4, pin, "USB_DM", 20.32, glob=True, shape="bidirectional")
    for pin in ("A8", "B8"):
        s.noconn(*j4.pin(pin))

    # CC1 liegt ueber CC2, also biegt CC1 weiter rechts ab - so kreuzt keine
    # Steigleitung den Abzweig der anderen.
    for pin, ref, off in (("A5", "R34", 27.94), ("B5", "R35", 12.7)):
        cx, cy = j4.pin(pin)
        s.wire(cx, cy, cx + off, cy)
        r = s.part("Device:R", ref, "5k1", cx + off, cy + 20.32, footprint=R0603)
        s.wire(cx + off, cy, *r.pin("1"))
        s.power("GND", *r.pin("2"))

    # ---- microSD -----------------------------------------------------
    s.text("microSD", 300, 150, 2.2)
    s.text("SDMMC 4 bit. 48 kHz/24 bit stereo sind 288 kB/s - reichlich Reserve.", 300, 156)

    # Det2 statt Det1: nur dessen Nummerierung passt zum DM3D-SF. Bei Det1
    # heisst Pin 10 SHIELD, liegt im Footprint aber auf einem Kontakt des
    # Kartenschalters - der Metallrahmen (Pad 11) bliebe unverbunden.
    j5 = s.part("Connector:Micro_SD_Card_Det2", "J5", "microSD_PushPush", 340, 200,
                footprint="Connector_Card:microSD_HC_Hirose_DM3D-SF")
    sd_map = [("CLK", "SD_CLK"), ("CMD", "SD_CMD"), ("DAT0", "SD_D0"),
              ("DAT1", "SD_D1"), ("DAT2", "SD_D2"), ("DAT3/CD", "SD_D3")]
    for name, net in sd_map:
        s.stub(j5, name, net, 17.78, glob=True, shape="bidirectional")
    # Alle Pins liegen auf derselben Kante. Versorgung und Masse bekommen
    # darum kurze Stichleitungen mit Symbol direkt am Ende, statt an den
    # Datenleitungen entlangzulaufen.
    # Kartenerkennung wird nicht ausgewertet, beide Schalterkontakte auf Masse.
    for pin, off in (("VSS", 8.89), ("DET_A", 8.89), ("DET_B", 12.7),
                     ("SHIELD", -8.89)):
        gx, gy = j5.pin(pin)
        s.wire(gx, gy, gx - off, gy)
        s.power("GND", gx - off, gy)
    vx, vy = j5.pin("VDD")
    s.wire(vx, vy, vx - 8.89, vy)
    s.power("+3V3D", vx - 8.89, vy)
    for ref, val, cx_, fp in (("C45", "10u/10V", 305.0, C0805),
                              ("C46", "100n", 322.0, C0603)):
        c = s.part("Device:C", ref, val, cx_, 240.0, footprint=fp)
        s.power("+3V3D", *c.pin("1"))
        s.power("GND", *c.pin("2"))
    s.text("Stuetzkondensatoren der Karte", 300, 232)
    s.text("Pull-ups sitzen auf Blatt 05 zusammen mit den I2C-Pull-ups.", 300, 252)
    return s


# ==========================================================================
# 05 - RTC, CAN, Bedienung
# ==========================================================================

def build_io(lib, root_uuid) -> Schematic:
    s = sheet(lib, "05-io.kicad_sch",
              "Exhaust-Mic - Echtzeituhr, CAN, Bedienung und Videosynchronisation",
              root_uuid)

    # ---- RTC ----------------------------------------------------------
    s.text("Echtzeituhr", 25, 24, 2.2)
    s.text("DS3231SN mit integriertem TCXO: +/-2 ppm ueber -40...+85 C. Das ist die", 25, 30)
    s.text("Voraussetzung fuer brauchbare Zeitstempel im Motorradheck.", 25, 34)
    s.text("Der 1-Hz-Ausgang SQW rastet in der Firmware den Samplezaehler ein und", 25, 38)
    s.text("liefert damit eine driftfreie Zuordnung Uhrzeit zu Audiosample.", 25, 42)

    u7 = s.part("exhaust-mic:DS3231SN", "U7", "DS3231SN", 105, 90,
                footprint="Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
                fields={"MPN": "DS3231SN#"})
    vx, vy = u7.pin("2")
    s.wire(vx, vy, vx, vy - 10.16)
    s.power("+3V3D", vx, vy - 10.16)
    c50 = s.part("Device:C", "C50", "100n", vx + 15.24, vy - 4.0, footprint=C0603)
    s.wire(vx, vy - 10.16, vx + 15.24, vy - 10.16)
    s.wire(vx + 15.24, vy - 10.16, *c50.pin("1"))
    s.power("GND", *c50.pin("2"))
    s.junction(vx, vy - 10.16)

    gx, gy = u7.pin("13")
    s.wire(gx, gy, gx, gy + 7.62)
    s.power("GND", gx, gy + 7.62)

    bx, by = u7.pin("14")
    s.wire(bx, by, bx, by - 12.7)
    s.wire(bx, by - 12.7, bx + 33.02, by - 12.7)
    bt1 = s.part("Device:Battery_Cell", "BT1", "CR1220", bx + 33.02, by - 4.0,
                 footprint="Battery:BatteryHolder_Keystone_3000_1x12mm",
                 fields={"MPN": "Keystone 3000"})
    s.wire(bx + 33.02, by - 12.7, *bt1.pin("1"))
    s.power("GND", *bt1.pin("2"))
    flg = s.part("power:PWR_FLAG", "#FLG0101", "PWR_FLAG", bx + 33.02,
                 by - 25.4, in_bom=False)
    s.wire(bx + 33.02, by - 25.4, bx + 33.02, by - 12.7)
    c51 = s.part("Device:C", "C51", "100n", bx + 17.78, by - 4.0, footprint=C0603)
    s.wire(bx + 17.78, by - 12.7, *c51.pin("1"))
    s.power("GND", *c51.pin("2"))
    s.junction(bx + 17.78, by - 12.7)

    s.stub(u7, "15", "I2C_SDA", 20.32, glob=True, shape="bidirectional")
    s.stub(u7, "16", "I2C_SCL", 20.32, glob=True, shape="input")
    s.stub(u7, "3", "RTC_SQW", 20.32, glob=True, shape="output")
    s.noconn(*u7.pin("1"))
    s.noconn(*u7.pin("4"))

    # I2C- und SQW-Pull-ups
    s.text("Bus-Pull-ups", 25, 130, 2.0)
    for i, (ref, net, val) in enumerate([("R40", "I2C_SDA", "4k7"),
                                         ("R41", "I2C_SCL", "4k7"),
                                         ("R42", "RTC_SQW", "10k")]):
        x = 40 + i * 25.4
        r = s.part("Device:R", ref, val, x, 152, footprint=R0603)
        s.wire(x, r.pin("1")[1], x, r.pin("1")[1] - 7.62)
        s.power("+3V3D", x, r.pin("1")[1] - 7.62)
        s.wire(x, r.pin("2")[1], x, r.pin("2")[1] + 6.35)
        s.glabel(net, x, r.pin("2")[1] + 6.35, 270, "bidirectional")

    # SD-Pull-ups
    s.text("microSD-Pull-ups", 140, 130, 2.0)
    for i, (ref, net) in enumerate([("R43", "SD_CMD"), ("R44", "SD_D0"),
                                    ("R45", "SD_D1"), ("R46", "SD_D2"),
                                    ("R47", "SD_D3")]):
        x = 150 + i * 20.32
        r = s.part("Device:R", ref, "10k", x, 152, footprint=R0603)
        s.wire(x, r.pin("1")[1], x, r.pin("1")[1] - 7.62)
        s.power("+3V3D", x, r.pin("1")[1] - 7.62)
        s.wire(x, r.pin("2")[1], x, r.pin("2")[1] + 6.35)
        s.glabel(net, x, r.pin("2")[1] + 6.35, 270, "bidirectional")

    # ---- CAN ----------------------------------------------------------
    s.text("CAN - bestueckungsoptional", 275, 24, 2.2)
    s.text("Der ESP32-S3 hat TWAI, also klassisches CAN 2.0B bis 1 Mbit/s und", 275, 30)
    s.text("kein CAN-FD. Passend dazu ein 3,3-V-Transceiver - ein TCAN1051", 275, 34)
    s.text("waere hier falsch, der braucht 5 V.", 275, 38)

    u8 = s.part("Interface_CAN_LIN:SN65HVD230", "U8", "SN65HVD230D", 320, 70,
                footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
                fields={"MPN": "SN65HVD230DR", "Bestueckung": "optional"})
    vx, vy = u8.pin("3")
    s.wire(vx, vy, vx, vy - 10.16)
    s.power("+3V3D", vx, vy - 10.16)
    c52 = s.part("Device:C", "C52", "100n", vx + 15.24, vy - 4.0, footprint=C0603)
    s.wire(vx, vy - 10.16, vx + 15.24, vy - 10.16)
    s.wire(vx + 15.24, vy - 10.16, *c52.pin("1"))
    s.power("GND", *c52.pin("2"))
    s.junction(vx, vy - 10.16)
    gx, gy = u8.pin("2")
    s.wire(gx, gy, gx, gy + 7.62)
    s.power("GND", gx, gy + 7.62)
    s.stub(u8, "1", "CAN_TX", 17.78, glob=True, shape="input")
    s.stub(u8, "4", "CAN_RX", 17.78, glob=True, shape="output")
    s.noconn(*u8.pin("5"))
    rsx, rsy = u8.pin("8")
    s.wire(rsx, rsy, rsx - 10.16, rsy)
    r48 = s.part("Device:R", "R48", "10k", rsx - 10.16, rsy + 14.0, footprint=R0603)
    s.wire(rsx - 10.16, rsy, *r48.pin("1"))
    s.power("GND", *r48.pin("2"))
    s.text("R48 setzt die Flankensteilheit; 0R = maximale Bitrate.", rsx - 60, rsy + 20)

    # Terminierung, per Jumper zuschaltbar
    for pin, net, yv in (("7", "CANH", 60.0), ("6", "CANL", 80.0)):
        px, py = u8.pin(pin)
        s.wire(px, py, px + 20.32, py)
        s.glabel(net, px + 20.32, py, 180, "bidirectional")
    r49 = s.part("Device:R", "R49", "120R", 300, 130, 90, footprint=R0805,
                 fields={"Bestueckung": "nur wenn Endknoten"}, dnp=True)
    s.stub(r49, "1", "CANH", 12.7, glob=True, shape="bidirectional")
    s.stub(r49, "2", "CANL", 12.7, glob=True, shape="bidirectional")
    s.text("R49 nur bestuecken, wenn dieses Geraet am Busende sitzt.", 275, 142)

    # ---- Bedienung und Videosynchronisation ---------------------------
    s.text("Bedienung und Videosynchronisation", 25, 190, 2.2)
    s.text("LED_SYNC und der Piezo markieren den Aufnahmestart sichtbar und hoerbar.", 25, 196)
    s.text("Die Kamera nimmt Blitz oder Piep mit auf, danach laesst sich der Clip im", 25, 200)
    s.text("Schnittprogramm framegenau ausrichten - das schafft keine Uhr allein.", 25, 204)

    for i, (ref, net) in enumerate([("SW3", "BTN_REC"), ("SW4", "BTN_MARK")]):
        x = 45 + i * 45.72
        sw = s.part("Switch:SW_Push", ref, "REC" if i == 0 else "MARK", x, 228,
                    footprint="Button_Switch_SMD:SW_SPST_TL3342")
        p1 = sw.pin("1")
        s.wire(p1[0], p1[1], p1[0], p1[1] - 7.62)
        s.glabel(net, p1[0], p1[1] - 7.62, 90, "output")
        s.power("GND", *sw.pin("2"))
    s.text("Interne Pull-ups des ESP32 genuegen; entprellt wird in Software.", 25, 246)
    s.text("EXT_BTN vom Harness liegt parallel zu SW4.", 25, 250)
    ext = s.part("Device:R", "R50", "1k", 140, 228, footprint=R0603)
    s.stub(ext, "1", "EXT_BTN", 10.16, glob=True, shape="input")
    s.stub(ext, "2", "BTN_MARK", 10.16, glob=True, shape="output")

    for i, (ref, net, colour, rref, rval) in enumerate([
            ("D20", "LED_REC", "gruen", "R51", "1k"),
            ("D21", "LED_ERR", "rot", "R52", "1k")]):
        x = 195 + i * 30.48
        # Anode oben an 3V3, Kathode ueber den Vorwiderstand auf den GPIO
        d = s.part("Device:LED", ref, colour, x, 228, 90,
                   footprint="LED_SMD:LED_0603_1608Metric")
        s.wire(*d.pin("2"), x, d.pin("2")[1] - 7.62)
        s.power("+3V3D", x, d.pin("2")[1] - 7.62)
        r = s.part("Device:R", rref, rval, x, 244, footprint=R0603)
        s.wire(*d.pin("1"), *r.pin("1"))
        s.wire(*r.pin("2"), x, r.pin("2")[1] + 6.35)
        s.glabel(net, x, r.pin("2")[1] + 6.35, 270, "input")

    # Sync-Blitz mit FET, damit genug Strom fliesst
    dx = 275.0
    d22 = s.part("Device:LED", "D22", "weiss_Sync", dx, 200, 90,
                 footprint="LED_SMD:LED_0805_2012Metric")
    s.wire(*d22.pin("2"), dx, d22.pin("2")[1] - 7.62)
    s.power("+4V6", dx, d22.pin("2")[1] - 7.62)
    r53 = s.part("Device:R", "R53", "18R", dx, 216, footprint=R0805)
    s.wire(*d22.pin("1"), *r53.pin("1"))
    q3 = s.part("Device:Q_NMOS_GSD", "Q3", "2N7002", dx + 5.08, 236, 0,
                footprint=SOT23)
    s.wire(*r53.pin("2"), dx, q3.pin("3")[1])
    s.wire(dx, q3.pin("3")[1], *q3.pin("3"))
    s.power("GND", *q3.pin("2"))
    ggx, ggy = q3.pin("1")
    s.wire(ggx, ggy, ggx - 12.7, ggy)
    s.glabel("LED_SYNC", ggx - 12.7, ggy, 0, "input")
    r54 = s.part("Device:R", "R54", "100k", ggx - 12.7, ggy + 14.0, footprint=R0603)
    s.wire(ggx - 12.7, ggy, *r54.pin("1"))
    s.power("GND", *r54.pin("2"))
    s.junction(ggx - 12.7, ggy)

    # Piezo
    bx = 345.0
    # SMD statt Durchsteckausfuehrung: fuer den 12,5-mm-Piezo mit
    # Drahtanschluessen gibt es auf dieser Platine keinen Platz mehr, an
    # dem seine Pins nicht auf der Gegenseite auf Pads treffen.
    bz = s.part("Device:Buzzer", "LS1", "Piezo_SMD", bx, 200,
                footprint="Buzzer_Beeper:Buzzer_Murata_PKMCS0909E",
                fields={"MPN": "PKMCS0909E4000-R1"})
    p1x, p1y = bz.pin("1")
    s.wire(p1x, p1y, p1x - 10.16, p1y)
    s.wire(p1x - 10.16, p1y, p1x - 10.16, p1y - 10.16)
    s.power("+3V3D", p1x - 10.16, p1y - 10.16)
    q4 = s.part("Device:Q_NMOS_GSD", "Q4", "2N7002", bx - 15.24, 236, 0,
                footprint=SOT23)
    p2x, p2y = bz.pin("2")
    s.wire(p2x, p2y, p2x - 5.08, p2y)
    s.wire(p2x - 5.08, p2y, p2x - 5.08, q4.pin("3")[1])
    s.wire(p2x - 5.08, q4.pin("3")[1], *q4.pin("3"))
    s.power("GND", *q4.pin("2"))
    ggx, ggy = q4.pin("1")
    s.wire(ggx, ggy, ggx - 12.7, ggy)
    s.glabel("BUZZ", ggx - 12.7, ggy, 0, "input")
    r55 = s.part("Device:R", "R55", "100k", ggx - 12.7, ggy + 14.0, footprint=R0603)
    s.wire(ggx - 12.7, ggy, *r55.pin("1"))
    s.power("GND", *r55.pin("2"))
    s.junction(ggx - 12.7, ggy)

    # ---- Erweiterungsstecker ------------------------------------------
    s.text("Erweiterung", 25, 262, 2.0)
    # Pin 1 ist die Versorgung und Pin n die Masse, damit beide nach oben bzw.
    # unten herausgefuehrt werden koennen ohne die Signalabgriffe zu kreuzen.
    j6 = s.part("Connector_Generic:Conn_01x05", "J6", "GPS_unbestueckt", 60, 278,
                footprint="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
                dnp=True)
    for pin, net in (("2", "GPS_TX"), ("3", "GPS_RX"), ("4", "GPS_PPS")):
        s.stub(j6, pin, net, 22.86, glob=True, shape="bidirectional")
    px, py = j6.pin("1")
    s.wire(px, py, px - 8.89, py)
    s.wire(px - 8.89, py, px - 8.89, py - 7.62)
    s.power("+3V3D", px - 8.89, py - 7.62)
    px, py = j6.pin("5")
    s.wire(px, py, px - 8.89, py)
    s.wire(px - 8.89, py, px - 8.89, py + 6.35)
    s.power("GND", px - 8.89, py + 6.35)
    s.text("J6: 1=3V3  2=TX  3=RX  4=PPS  5=GND", 30, 292)

    j7 = s.part("Connector_Generic:Conn_01x04", "J7", "I2C_Erweiterung", 175, 278,
                footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")
    for pin, net in (("2", "I2C_SDA"), ("3", "I2C_SCL")):
        s.stub(j7, pin, net, 22.86, glob=True, shape="bidirectional")
    px, py = j7.pin("1")
    s.wire(px, py, px - 8.89, py)
    s.wire(px - 8.89, py, px - 8.89, py - 7.62)
    s.power("+3V3D", px - 8.89, py - 7.62)
    px, py = j7.pin("4")
    s.wire(px, py, px - 8.89, py)
    s.wire(px - 8.89, py, px - 8.89, py + 6.35)
    s.power("GND", px - 8.89, py + 6.35)
    s.text("J7: 1=3V3  2=SDA  3=SCL  4=GND", 145, 292)

    # UART0 auf Testpunkte
    for i, net in enumerate(("UART0_TX", "UART0_RX")):
        tp = s.part("Connector_Generic:Conn_01x01", f"TP{i+1}", net, 250 + i * 25.4,
                    278, footprint="TestPoint:TestPoint_Pad_D1.5mm")
        s.stub(tp, "1", net, 12.7, glob=True, shape="bidirectional")

    return s


# ==========================================================================
# Wurzelblatt
# ==========================================================================

def build_root(lib, root_uuid) -> Schematic:
    s = Schematic(lib, PROJECT, "exhaust-mic.kicad_sch",
                  title="Exhaust-Mic - Stereo-Tonaufnahme Motor und Auspuff",
                  rev=REV, date=DATE, company=COMPANY, paper="A3")
    s.uuid = root_uuid

    s.text("Exhaust-Mic", 30, 40, 4.0)
    s.text("Zweikanalige Tonaufnahme von Motor- und Auspuffgeraeuschen.", 30, 52, 2.0)
    s.text("Zwei Mikrofonkoepfe IM73A135V01 (135 dBSPL AOP) an einem PCM1863,", 30, 60)
    s.text("aufgezeichnet von einem ESP32-S3 auf microSD.", 30, 65)
    s.text("Der Mikrofonkopf ist ein eigenes Projekt: mic-head/mic-head.kicad_sch", 30, 73)
    s.text("Auslegung, Rauschbudget und Pegelplan:", 30, 81)
    s.text("docs/specs/2026-08-28-exhaust-mic-design.md", 30, 86)

    sheets = [
        ("Versorgung", "01-power.kicad_sch", 30, 110, "2"),
        ("Analogeingang", "02-analog.kicad_sch", 130, 110, "3"),
        ("ADC", "03-adc.kicad_sch", 230, 110, "4"),
        ("MCU", "04-mcu.kicad_sch", 30, 175, "5"),
        ("IO", "05-io.kicad_sch", 130, 175, "6"),
    ]
    for name, fn, x, y, page in sheets:
        s.sheet(name, fn, x, y, 76.2, 45.72, page)

    s.text("Kennwerte", 250, 175, 2.0)
    s.text("Kanal A  Endrohr   PGA +12,5 dB   Vollaussteuerung 132,0 dB SPL", 250, 183)
    s.text("Kanal B  Airbox    PGA +20,0 dB   Vollaussteuerung 124,4 dB SPL", 250, 188)
    s.text("Rauschteppich 26,8 bzw. 25,5 dB(A) SPL", 250, 193)
    s.text("Abtastung 48 kHz / 24 bit, optional 96 kHz", 250, 198)
    s.text("Versorgung 12 V Bordnetz, Standby rund 90 uA", 250, 203)

    return s


# ==========================================================================


def load_sourcing() -> dict:
    """tools/parts.json einlesen, falls vorhanden."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parts.json")
    if not os.path.exists(path):
        return {}
    import json
    return json.load(open(path, encoding="utf-8"))


def main():
    from kigen import uuid_for
    lib = new_lib()
    root_uuid = uuid_for(PROJECT, "exhaust-mic.kicad_sch")

    built = [build_root(lib, root_uuid),
             build_power(lib, root_uuid),
             build_analog(lib, root_uuid),
             build_adc(lib, root_uuid),
             build_mcu(lib, root_uuid),
             build_io(lib, root_uuid)]

    quellen = load_sourcing()
    if quellen:
        n = sum(sh.apply_sourcing(quellen) for sh in built)
        print(f"Beschaffungsdaten auf {n} Bauteile angewandt")

    problems = []
    for s in built:
        problems += s.check()
        print("wrote", os.path.basename(s.write(PROJ_DIR)))
    if problems:
        print("\nWARNUNGEN:")
        for p in problems:
            print("  " + p)

    tbl = os.path.join(PROJ_DIR, "sym-lib-table")
    with open(tbl, "w", encoding="utf-8") as fh:
        fh.write("(sym_lib_table\n"
                 '  (lib (name "exhaust-mic")(type "KiCad")'
                 '(uri "${KIPRJMOD}/lib/exhaust-mic.kicad_sym")'
                 '(options "")(descr "Projektsymbole exhaust-mic"))\n)\n')
    print("wrote sym-lib-table")


if __name__ == "__main__":
    main()
