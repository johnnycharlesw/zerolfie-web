hex_digits = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F"
]

def clamp(value, lo=0, hi=255):
    return max(lo, min(hi, value))

def parse_rgb_channel(token: str) -> int:
    token = token.strip().lower()

    if token.endswith("%"):
        try:
            pct = float(token[:-1])
        except ValueError:
            return 0
        return clamp(round(pct * 255 / 100))
    else:
        try:
            return clamp(int(token))
        except ValueError:
            return 0

def rgba(r,g,b,a):
    r_parsed = parse_rgb_channel(str(r))
    g_parsed=parse_rgb_channel(str(g))
    b_parsed=parse_rgb_channel(str(b))

def rgb(r,g,b):
    return rgba(r,g,b,255)
