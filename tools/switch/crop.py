"""Crop and enlarge a region of a screenshot PNG (pure Python, 8-bit RGB PNGs from nxlink_screens.py).

Usage: python crop.py in.png out.png x y w h scale
"""
import struct
import sys
import zlib


def read_png(path):
    data = open(path, "rb").read()
    pos = 8
    idat = b""
    w = h = 0
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            w, h = struct.unpack(">II", body[:8])
        elif tag == b"IDAT":
            idat += body
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * 3
    rows = []
    prev = bytearray(stride)
    i = 0
    for _ in range(h):
        f = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        if f == 1:
            for x in range(3, stride):
                line[x] = (line[x] + line[x - 3]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f != 0:
            raise SystemExit("unsupported filter %d" % f)
        rows.append(line)
        prev = line
    return w, h, rows


def write_png(path, w, h, rows):
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(tag, d):
        c = struct.pack(">I", len(d)) + tag + d
        return c + struct.pack(">I", zlib.crc32(tag + d) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    open(path, "wb").write(png + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def main():
    src, dst = sys.argv[1], sys.argv[2]
    x, y, cw, ch, s = map(int, sys.argv[3:8])
    w, h, rows = read_png(src)
    out = []
    for yy in range(ch):
        r = rows[y + yy]
        line = bytearray()
        for xx in range(cw):
            px = r[(x + xx) * 3:(x + xx) * 3 + 3]
            line += px * s
        for _ in range(s):
            out.append(line)
    write_png(dst, cw * s, ch * s, out)


if __name__ == "__main__":
    main()
