import darkdetect
def is_dark_mode_enabled():
    try:
        return darkdetect.isDark()
    except Exception:
        return False

def update_media_context(ctx):
    ctx['prefers-color-scheme'] = 'dark' if is_dark_mode_enabled() else 'light'

if __name__ == "__main__":
    ctx = {}
    update_media_context(ctx)
    if ctx['prefers-color-scheme'] == "dark":
        print("Dark mode")
    else:
        print("Light mode")