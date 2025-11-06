import sys
import webview

def main():
    # Launch the webview by default, and also when explicitly asked.
    # Ignore unknown args for now, or extend this to print help in the future.
    if len(sys.argv) > 1:
        if sys.argv[1] == "launch-webview-standalone":
            webview.main()
            return
        # Unknown argument: still launch by default to preserve previous behavior.
        # You could print usage here if desired.
    # No args or unrecognized arg: launch by default
    webview.main()

if __name__ == "__main__":
    main()