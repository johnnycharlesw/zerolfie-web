import subprocess

def is_high_contrast_enabled():
    result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'], capture_output=True, text=True)
    return result.stdout.strip() == "'prefer-dark'"
