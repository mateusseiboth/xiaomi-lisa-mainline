#!/usr/bin/env python3
"""Decode a Qualcomm CamX sensor module (com.qti.sensormodule.*.bin).

Reads the "QTI Chromatix" Parameter Parser V3 blob from the vendor partition
and prints or exports what a V4L2 driver needs: the init sequence, the
register writes of each mode, the stream configuration of each mode and the
small tables (stream on/off, group hold).

The blobs are vendor property: run this on your own vendor image and do not
redistribute the output.

Layout (see also isyourbrainfoss/fp5-imx800):
  - schema tree of nodes: name[40], 0xffffffff, type, size, id;
    for a node with size > 0, `type` is an offset into the value section
  - value section at header[0xb8], size header[0xbc]
  - a regSetting value is a table of 40-byte entries; each entry carries the
    register address and the address/data widths. The data of entry N is the
    u32 pointed to by the N-th registerData node after the regSetting.

usage: camx_sensormodule.py <sensormodule.bin> [--c-tables]
"""
import argparse
import struct

NAME_LEN = 40
REG_NODES = ("slaveAddr", "registerData", "delayUs")


def parse(path):
    data = open(path, "rb").read()
    voff, vsize = struct.unpack_from("<II", data, 0xB8)
    values = data[voff:voff + vsize]
    nodes = []
    off = 0xD0
    while off + NAME_LEN + 16 <= voff:
        tag = struct.unpack_from("<I", data, off + NAME_LEN)[0]
        if tag == 0xFFFFFFFF and 65 <= data[off] <= 122:
            name = data[off:off + NAME_LEN].split(b"\0")[0].decode("ascii", "replace")
            typ, size, nid = struct.unpack_from("<III", data, off + NAME_LEN + 4)
            nodes.append({"name": name, "type": typ, "size": size, "id": nid})
            off += NAME_LEN + 16
        else:
            off += 4
    return nodes, values


def reg_table(nodes, values, idx):
    """Return [(addr, value, addr_bytes, data_bytes, delay_us)] for a regSetting."""
    node = nodes[idx]
    count = node["size"] // 40
    data_nodes = []
    delay_nodes = []
    for n in nodes[idx + 1:]:
        if n["name"] == "registerData":
            data_nodes.append(n)
        elif n["name"] == "delayUs":
            delay_nodes.append(n)
        elif n["name"] != "slaveAddr":
            break
    base = node["type"]
    # Entries are tagged with schema ids; find the stride-40 start where the
    # addresses look like 16-bit registers.
    for skip in range(0, 40, 4):
        start = base + skip
        addrs = [struct.unpack_from("<I", values, start + k * 40 + 4)[0] for k in range(count)]
        widths = [struct.unpack_from("<I", values, start + k * 40 + 16)[0] for k in range(count)]
        if all(a <= 0xFFFF for a in addrs) and all(w in (1, 2, 4) for w in widths):
            break
    else:
        raise RuntimeError(f"no register table at {base:#x}")
    out = []
    for k in range(count):
        e = start + k * 40
        addr = struct.unpack_from("<I", values, e + 4)[0]
        addr_w = struct.unpack_from("<I", values, e + 16)[0]
        data_w = struct.unpack_from("<I", values, e + 20)[0]
        value = struct.unpack_from("<I", values, data_nodes[k]["type"])[0] if k < len(data_nodes) and data_nodes[k]["size"] else 0
        delay = struct.unpack_from("<I", values, delay_nodes[k]["type"])[0] if k < len(delay_nodes) and delay_nodes[k]["size"] else 0
        out.append((addr, value, addr_w, data_w, delay))
    return out


# The four settings that follow the gain functions carry no name of their own
# in the blob; the schema order gives them.
SETTINGS_AFTER_GAIN = ("streamOn", "streamOff", "groupHoldOn", "groupHoldOff")


def tables(nodes):
    """Classify the regSetting nodes: per-mode tables first, then the rest."""
    result = []
    mode = -1
    after_gain = []
    for i, n in enumerate(nodes):
        if n["name"] == "streamConfiguration" and n["size"]:
            mode += 1
        if n["name"] == "regToRealGain":
            after_gain = list(SETTINGS_AFTER_GAIN)
        if n["name"] != "regSetting":
            continue
        before = next((nodes[j]["name"] for j in range(i - 1, max(i - 12, 0), -1)
                       if nodes[j]["name"] not in REG_NODES + ("regSetting",) and nodes[j]["size"]), "?")
        label = after_gain.pop(0) if after_gain else before
        result.append((i, mode, label))
    return result


def stream_configs(nodes, values):
    out = []
    for n in nodes:
        if n["name"] == "streamConfiguration" and n["size"]:
            u = struct.unpack_from("<%dI" % (n["size"] // 4), values, n["type"])
            streams = [u[k:k + 8] for k in range(0, len(u), 8)]
            out.append([{"dt": s[1], "x": s[2], "y": s[3], "w": s[4], "h": s[5], "bpp": s[6]} for s in streams])
    return out


def c_table(regs, name):
    """Format a register table as a cci_reg_sequence array.

    Writes to 0x0000 (the read-only chip id) are dropped, and a write with a
    delay is followed by a comment, since the delay has to be done by the
    driver between two cci_multi_reg_write() calls.
    """
    lines = [f"static const struct cci_reg_sequence {name}[] = {{"]
    for addr, value, addr_w, data_w, delay in regs:
        if addr == 0x0000:
            continue
        width = {1: 8, 2: 16, 4: 32}[data_w]
        lines.append(f"\t{{ CCI_REG{width}({addr:#06x}), {value:#06x} }},")
        if delay:
            lines.append(f"\t/* driver must wait {delay} us here */")
    lines.append("};")
    return "\n".join(lines)


def c_tables(prefix, tables):
    """Format named register tables; a table that sets the output size
    (0x034c/0x034e) is named after it, as <prefix>_<w>x<h>_mode."""
    out = []
    for name, regs in tables:
        size = {addr: value for addr, value, *_ in regs if addr in (0x034C, 0x034E)}
        if len(size) == 2:
            name = f"{size[0x034C]}x{size[0x034E]}_mode"
        out.append(c_table(regs, f"{prefix}_{name}"))
    return "\n\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("blob")
    ap.add_argument("--c-tables", action="store_true", help="print the tables as C arrays")
    ap.add_argument("--prefix", default="sensor", help="name prefix of the C arrays")
    args = ap.parse_args()
    nodes, values = parse(args.blob)
    name_node = next(n for n in nodes if n["name"] == "sensorName")
    name = values[name_node["type"]:name_node["type"] + name_node["size"]].split(b"\0")[0].decode()
    configs = stream_configs(nodes, values)
    print(f"/* {name}: {len(configs)} modes */")
    for i, cfg in enumerate(configs):
        print(f"/* mode {i}: " + ", ".join(f"dt {s['dt']:#x} {s['w']}x{s['h']}+{s['x']}+{s['y']} {s['bpp']}bpp" for s in cfg) + " */")
    for idx, mode, before in tables(nodes):
        regs = reg_table(nodes, values, idx)
        label = f"mode{mode}" if before in ("streamConfiguration", "activeLinesTransmissionTimeUS") else before
        print(f"/* regSetting {idx}: {label}, {len(regs)} writes */")
        if args.c_tables:
            print(c_tables(args.prefix, [(label, regs)]))


if __name__ == "__main__":
    main()
