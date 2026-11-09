"""Extract the debug screenshots that the deko3d renderer sends over nxlink into PNG files.

Usage: python nxlink_screens.py live.log [out_dir]
"""
import base64
import os
import struct
import sys
import zlib


def write_png(path, w, h, rgb):
    raw = b"".join(b"\x00" + rgb[y * w * 3:(y + 1) * w * 3] for y in range(h))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    log = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(log), "shots")
    os.makedirs(out, exist_ok=True)
    text = open(log, "r", encoding="latin-1").read()
    n = 0
    pos = 0
    while True:
        start = text.find("[screenshot ", pos)
        if start < 0:
            break
        eol = text.find("\n", start)
        end = text.find("[/screenshot]", eol)
        if eol < 0 or end < 0:
            break
        w, h = map(int, text[start + 12:text.find("]", start)].split())
        # Other threads' log lines ("[time] [level] ...\n") can land in the middle of the base64:
        # cut every segment at its first '[' and keep only base64 characters.
        b64 = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")
        parts = []
        for seg in text[eol + 1:end].split("\n"):
            seg = seg.split("[", 1)[0]
            parts.append("".join(ch for ch in seg if ch in b64))
        data = "".join(parts)
        data = data[:len(data) - len(data) % 4]
        rgb = base64.b64decode(data + "=" * (-len(data) % 4))
        if len(rgb) < w * h * 3:
            print("shot %d: %d of %d bytes (padded)" % (n + 1, len(rgb), w * h * 3))
            rgb = rgb + bytes(w * h * 3 - len(rgb))
        n += 1
        write_png(os.path.join(out, "shot_%03d.png" % n), w, h, rgb[:w * h * 3])
        pos = end
    print(n, "screenshots ->", out)


if __name__ == "__main__":
    main()
