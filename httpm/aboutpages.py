def _about_url_request(url: str, method: str):
    key = _parse_about_key(url)
    # Special-case about:blank -> serve html/blank.html
    if key in ("blank", ""):
        file_path = "html/blank.html"
        try:
            with open(file_path, "rb") as fd:
                content = fd.read()
            return {
                "status": 200,
                "reason": "OK",
                "headers": [("ZerolfieWeb-Internal-WebPage", "True"), ("Content-Type", _guess_mime_type(file_path))],
                "content": content
            }
        except FileNotFoundError:
            # Fallback to truly empty if the file is missing
            return {
                "status": 200,
                "reason": "OK",
                "headers": [("ZerolfieWeb-Internal-WebPage", "True"), ("Content-Type", "text/html; charset=utf-8")],
                "content": b""
            }
    file_path = f"html/{key}.html"
    try:
        with open(file_path, "rb") as fd:
            content = fd.read()
            return {
                "status": 200,
                "reason": "OK",
                "headers": [("ZerolfieWeb-Internal-WebPage", "True"), ("Content-Type", _guess_mime_type(file_path))],
                "content": content
            }
    except FileNotFoundError:
        not_found = (
            b"<h1>404 Not Found</h1>\n"
            b"<p>The about: URL you requested could not be found.</p>\n"
        )
        return {
            "status": 404,
            "reason": "Not Found",
            "headers": [("ZerolfieWeb-Internal-WebPage", "True"), ("Content-Type", "text/html; charset=utf-8")],
            "content": not_found
        }

def _parse_about_key(url: str) -> str:
    # Accept forms like 'about:mozilla' or full URLs parsed earlier
    if url.startswith("about:"):
        return url.split(":", 1)[1]
    parsed = urlparse(url)
    # Some about URIs might put the key in path
    key = parsed.path.lstrip("/")
    if not key:
        key = parsed.netloc
    return key