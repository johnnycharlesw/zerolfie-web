import os
import sys
if os.name=="posix":
    if sys.uname() == "Darwin":
        from prefers_contrast import macos as p_c
    else:
        from prefers_contrast import linux as p_c
else:
    from prefers_contrast import windows as p_c

def is_high_contrast_enabled():
    return p_c.is_high_contrast_enabled()

def update_media_context(ctx):
    ctx['prefers-contrast'] = 'more' if is_high_contrast_enabled() else 'less'

if __name__ == "__main__":
    print("High contrast" if is_high_contrast_enabled() else "Low contrast")