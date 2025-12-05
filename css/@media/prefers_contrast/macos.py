import subprocess

def is_high_contrast_enabled():
    script = """
    tell application "System Events"
        return (UI elements contrast is greater than normal)
    end tell
    """
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip() == 'true'
