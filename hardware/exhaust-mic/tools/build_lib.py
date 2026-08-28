#!/usr/bin/env python3
"""Generate lib/exhaust-mic.kicad_sym.

Only parts that KiCad's stock libraries do not carry. Every pinout here was
taken from the manufacturer datasheet - see the comment above each part.
"""

from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "lib", "exhaust-mic.kicad_sym")

GRID = 2.54
FONT = "(effects (font (size 1.27 1.27)))"

# side -> (pin rotation, unit direction away from the body)
SIDES = {"L": 0, "R": 180, "T": 270, "B": 90}


def sym(name, ref, desc, keywords, datasheet, footprint, pins,
        width=None, height=None, power=False):
    """pins: list of (side, slot, number, name, type)."""
    left = [p for p in pins if p[0] == "L"]
    right = [p for p in pins if p[0] == "R"]
    top = [p for p in pins if p[0] == "T"]
    bottom = [p for p in pins if p[0] == "B"]

    max_slot_v = max([p[1] for p in left + right] or [0])
    max_slot_h = max([p[1] for p in top + bottom] or [0])

    if height is None:
        height = (max_slot_v + 2) * GRID
    if width is None:
        longest = max([len(p[3]) for p in pins] or [4])
        by_name = max(2 * longest * 0.9, 20.32)
        by_top = (max_slot_h + 2) * GRID if top or bottom else 0
        width = max(by_name, by_top, 20.32)
        width = GRID * round(width / GRID)

    hw, hh = width / 2, height / 2
    body = [
        '      (rectangle (start %s %s) (end %s %s)' % (-hw, hh, hw, -hh),
        '        (stroke (width 0.254) (type default))',
        '        (fill (type background))',
        '      )',
    ]

    pin_lines = []
    for side, slot, number, pname, ptype in pins:
        if side == "L":
            x, y = -hw - GRID, hh - slot * GRID
        elif side == "R":
            x, y = hw + GRID, hh - slot * GRID
        elif side == "T":
            x, y = -hw + slot * GRID, hh + GRID
        else:
            x, y = -hw + slot * GRID, -hh - GRID
        rot = SIDES[side]
        pin_lines += [
            f'      (pin {ptype} line (at {fmt(x)} {fmt(y)} {rot}) (length {fmt(GRID)})',
            f'        (name "{pname}" {FONT})',
            f'        (number "{number}" {FONT})',
            '      )',
        ]

    power_tag = " (power)" if power else ""
    out = [
        f'  (symbol "{name}"{power_tag} (pin_names (offset 0.762)) (in_bom yes) (on_board yes)',
        f'    (property "Reference" "{ref}" (at {fmt(-hw)} {fmt(hh + 2.54)} 0)',
        f'      (effects (font (size 1.27 1.27)) (justify left bottom))',
        '    )',
        f'    (property "Value" "{name}" (at {fmt(-hw)} {fmt(-hh - 2.54)} 0)',
        f'      (effects (font (size 1.27 1.27)) (justify left top))',
        '    )',
        f'    (property "Footprint" "{footprint}" (at 0 0 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        f'    (property "Datasheet" "{datasheet}" (at 0 0 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        f'    (property "ki_keywords" "{keywords}" (at 0 0 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        f'    (property "ki_description" "{desc}" (at 0 0 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        f'    (symbol "{name}_0_1"',
    ]
    out += body
    out += ['    )', f'    (symbol "{name}_1_1"']
    out += pin_lines
    out += ['    )', '  )']
    return "\n".join(out)


def fmt(v):
    s = f"{float(v):.4f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


PARTS = []

# --------------------------------------------------------------------------
# Infineon IM73A135V01, datasheet V1.20 2021-07-07, Table 8 pin configuration
# 1 Output+, 2 VDD, 3 Output-, 4 GND, 5 GND
# --------------------------------------------------------------------------
PARTS.append(sym(
    "IM73A135V01", "MK", "XENSIV analog MEMS microphone, differential output, "
    "135 dBSPL AOP, 73 dB(A) SNR, IP57, LGA-5 bottom port",
    "MEMS microphone analog differential high AOP",
    "https://www.infineon.com/dgdl/Infineon-IM73A135-DataSheet-v01_00-EN.pdf",
    "exhaust-mic:Infineon_PG-LLGA-5-1_4x3mm_BottomPort",
    [
        ("L", 1, "2", "VDD", "power_in"),
        ("L", 3, "4", "GND", "power_in"),
        ("L", 4, "5", "GND", "power_in"),
        ("R", 1, "1", "OUT+", "output"),
        ("R", 2, "3", "OUT-", "output"),
    ],
    width=25.4))

# --------------------------------------------------------------------------
# TI PCM1863, SLAS831D, "Pin Functions: PCM1862, PCM1863, PCM1864, PCM1865"
# 30-pin TSSOP (DBT). Software controlled via I2C/SPI.
# --------------------------------------------------------------------------
PARTS.append(sym(
    "PCM1863", "U", "Stereo 24-bit 192 kHz audio ADC, differential inputs, "
    "PGA -12..+32 dB in 0.5 dB steps per channel, I2C/SPI control, 110 dB SNR",
    "audio ADC stereo differential PGA I2S",
    "https://www.ti.com/lit/ds/symlink/pcm1863.pdf",
    "Package_SO:TSSOP-30_4.4x9.7mm_P0.65mm",
    [
        # analog inputs - left
        ("L", 1,  "3",  "VINL1/VIN1P", "input"),
        ("L", 2,  "1",  "VINL2/VIN1M", "input"),
        ("L", 4,  "4",  "VINR1/VIN2P", "input"),
        ("L", 5,  "2",  "VINR2/VIN2M", "input"),
        ("L", 7,  "29", "VINL3/VIN4P", "input"),
        ("L", 8,  "27", "VINL4/VIN4M", "input"),
        ("L", 9,  "30", "VINR3/VIN3P", "input"),
        ("L", 10, "28", "VINR4/VIN3M", "input"),
        ("L", 12, "5",  "MICBIAS", "power_out"),
        ("L", 13, "6",  "VREF", "passive"),
        ("L", 15, "11", "LDO", "power_out"),
        # audio + control - right
        ("R", 1,  "15", "SCKI", "input"),
        ("R", 2,  "16", "LRCK", "bidirectional"),
        ("R", 3,  "17", "BCK", "bidirectional"),
        ("R", 4,  "18", "DOUT", "output"),
        ("R", 6,  "10", "XI", "input"),
        ("R", 7,  "9",  "XO", "output"),
        ("R", 9,  "23", "MOSI/SDA", "bidirectional"),
        ("R", 10, "24", "MC/SCL", "input"),
        ("R", 11, "22", "MISO/GPIO0", "bidirectional"),
        ("R", 12, "25", "MS/AD", "input"),
        ("R", 13, "26", "MD0", "input"),
        ("R", 15, "21", "GPIO1/INTA", "bidirectional"),
        ("R", 16, "20", "GPIO2/INTB", "bidirectional"),
        ("R", 17, "19", "GPIO3/INTC", "bidirectional"),
        # supplies
        ("T", 3,  "8",  "AVDD", "power_in"),
        ("T", 7,  "13", "DVDD", "power_in"),
        ("T", 11, "14", "IOVDD", "power_in"),
        ("B", 3,  "7",  "AGND", "power_in"),
        ("B", 7,  "12", "DGND", "power_in"),
    ],
    width=45.72, height=48.26))

# --------------------------------------------------------------------------
# TI LM5164, SNVSB48, Table 4-1 Pin Functions, DDA 8-pin SO PowerPAD
# 1 GND, 2 VIN, 3 EN/UVLO, 4 RON, 5 FB, 6 PGOOD, 7 BST, 8 SW, EP
# --------------------------------------------------------------------------
PARTS.append(sym(
    "LM5164", "U", "100 V 1 A synchronous buck converter, constant on-time, "
    "10.5 uA standby current, no external catch diode",
    "buck regulator synchronous automotive wide input",
    "https://www.ti.com/lit/ds/symlink/lm5164.pdf",
    "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm",
    [
        ("L", 1, "2", "VIN", "power_in"),
        ("L", 3, "3", "EN/UVLO", "input"),
        ("L", 5, "4", "RON", "input"),
        ("L", 7, "5", "FB", "input"),
        ("R", 1, "8", "SW", "output"),
        ("R", 2, "7", "BST", "passive"),
        ("R", 5, "6", "PGOOD", "open_collector"),
        ("B", 3, "1", "GND", "power_in"),
        ("B", 6, "9", "EP", "passive"),
    ],
    width=27.94))

# --------------------------------------------------------------------------
# TI TPS7A20, SBVS338H, "Pin Functions: X2SON, SOT-23", DBV package
# 1 IN, 2 GND, 3 EN, 4 N/C, 5 OUT
# --------------------------------------------------------------------------
PARTS.append(sym(
    "TPS7A20", "U", "300 mA ultra-low-noise LDO, fixed output, SOT-23-5. "
    "Set the exact version in the Value field, e.g. TPS7A2028 or TPS7A2033",
    "LDO regulator low noise audio",
    "https://www.ti.com/lit/ds/symlink/tps7a20.pdf",
    "Package_TO_SOT_SMD:SOT-23-5",
    [
        ("L", 1, "1", "IN", "power_in"),
        ("L", 3, "3", "EN", "input"),
        ("R", 1, "5", "OUT", "power_out"),
        ("R", 3, "4", "NC", "no_connect"),
        ("B", 3, "2", "GND", "power_in"),
    ],
    width=25.4))

# --------------------------------------------------------------------------
# TI TLV1117LV, SBVS160C, Table 5-1 Pin Functions, DCY SOT-223
# 1 GND, 2 OUT, 3 IN, Tab OUT
# --------------------------------------------------------------------------
PARTS.append(sym(
    "TLV1117LV33", "U", "1 A fixed 3.3 V LDO, 455 mV dropout at 1 A, "
    "VIN 2 to 5.5 V, SOT-223",
    "LDO regulator low dropout 1A",
    "https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf",
    "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
    [
        ("L", 1, "3", "IN", "power_in"),
        ("R", 1, "2", "OUT", "power_out"),
        ("R", 2, "4", "OUT(tab)", "power_out"),
        ("B", 3, "1", "GND", "power_in"),
    ],
    width=25.4))

# --------------------------------------------------------------------------
# Maxim/ADI DS3231SN, 16-pin SO
# 1 32kHz, 2 VCC, 3 INT/SQW, 4 RST, 5..12 NC, 13 GND, 14 VBAT, 15 SDA, 16 SCL
# --------------------------------------------------------------------------
PARTS.append(sym(
    "DS3231SN", "U", "Extremely accurate I2C RTC with integrated TCXO and "
    "crystal, +/-2 ppm, -40 to +85 C, battery backup, SO-16",
    "RTC real time clock TCXO I2C temperature compensated",
    "https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf",
    "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
    [
        ("L", 1, "15", "SDA", "bidirectional"),
        ("L", 2, "16", "SCL", "input"),
        ("L", 4, "4",  "~{RST}", "bidirectional"),
        ("R", 1, "3",  "~{INT}/SQW", "open_collector"),
        ("R", 2, "1",  "32kHz", "open_collector"),
        ("T", 3, "2",  "VCC", "power_in"),
        ("T", 7, "14", "VBAT", "power_in"),
        ("B", 5, "13", "GND", "power_in"),
    ],
    width=30.48))


def power_sym(name: str, desc: str) -> str:
    """A supply rail marker in the same style as KiCad's stock power symbols."""
    return "\n".join([
        f'  (symbol "{name}" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)',
        f'    (property "Reference" "#PWR" (at 0 -3.81 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        f'    (property "Value" "{name}" (at 0 3.556 0)',
        '      (effects (font (size 1.27 1.27)))',
        '    )',
        '    (property "Footprint" "" (at 0 0 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        '    (property "Datasheet" "" (at 0 0 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        f'    (property "ki_keywords" "power-flag" (at 0 0 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        f'    (property "ki_description" "{desc}" (at 0 0 0)',
        '      (effects (font (size 1.27 1.27)) hide)',
        '    )',
        f'    (symbol "{name}_0_1"',
        '      (polyline',
        '        (pts (xy -0.762 1.27) (xy 0 2.54) (xy 0.762 1.27))',
        '        (stroke (width 0) (type default))',
        '        (fill (type none))',
        '      )',
        '    )',
        f'    (symbol "{name}_1_1"',
        '      (pin power_in line (at 0 0 90) (length 0) hide',
        f'        (name "{name}" (effects (font (size 1.27 1.27))))',
        '        (number "1" (effects (font (size 1.27 1.27))))',
        '      )',
        '    )',
        '  )',
    ])


PARTS.append(power_sym("+4V6", "Zwischenspannung aus dem Buck, speist beide LDOs"))
PARTS.append(power_sym("+3V3D", "Digitalschiene: ESP32-S3, microSD, PCM1863 DVDD/IOVDD"))
PARTS.append(power_sym("+3V3A", "Rauscharme Analogschiene: PCM1863 AVDD und Mikrofonkoepfe"))
PARTS.append(power_sym("VBAT12", "Bordnetz nach Sicherung, Verpolschutz und TVS"))


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    body = "\n".join(PARTS)
    text = ('(kicad_symbol_lib (version 20220914) (generator exhaust_mic_build_lib)\n'
            + body + "\n)\n")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {os.path.normpath(OUT)} with {len(PARTS)} symbols")


if __name__ == "__main__":
    main()
