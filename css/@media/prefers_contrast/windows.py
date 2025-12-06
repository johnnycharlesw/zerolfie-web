import ctypes

def is_high_contrast_enabled():
    user32 = ctypes.windll.user32
    high_contrast = ctypes.c_int()
    user32.SystemParametersInfoW(0x0042, 0, ctypes.byref(high_contrast), 0)
    return high_contrast.value != 0
