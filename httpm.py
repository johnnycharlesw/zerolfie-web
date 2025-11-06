import http.client as pyhttp
import os_getter
from urllib.parse import urlparse
import dnsm
import sslm
from typing import Optional, Tuple, List

connections: List = []
connections_metadata: List[dict] = []
# Tracks the last successfully requested URL to help resolve relative paths
_last_url: Optional[str] = None

def connect_to_server_via_domain(https_enabled: bool = True, port: int = 443, domain: str = 'localhost', blocksize: int = 8192):
    dns_lookup = dnsm.dns_lookup(domain)
    ip = dns_lookup["ip"]
    return connect_to_server(https_enabled=https_enabled, port=port, ip=ip, domain=domain, blocksize=blocksize)


def connect_to_server(https_enabled: bool = True, port: int = 443, ip: str = "127.0.0.1", domain: Optional[str] = None, blocksize: int = 8192):
    # disable_ssl is kept to signal that SSL should be avoided when scanning among many HTTP connections
    disable_ssl = False
    if https_enabled:
        if ip == "127.0.0.1":
            disable_ssl = True
        # Use domain for SSL certificate validation, fall back to IP if no domain
        hostname = domain if domain else ip
        connections.append(pyhttp.HTTPSConnection(host=hostname, port=port, blocksize=blocksize))
    else:
        if port == 443:
            port = 80
        # Use domain as host for proper Host header on HTTP/1.1
        hostname = domain if domain else ip
        connections.append(pyhttp.HTTPConnection(host=hostname, port=port))

    connections_metadata.append({
        "ip": ip,
        "domain": domain,
        "port": port,
        "https_enabled": https_enabled,
        "disable_ssl": disable_ssl
    })


def _request(url: str, method: str, connection_id: int):
    if connection_id is None:
        print("Invalid connection ID")
        return None

    headers = {
        "User-Agent": os_getter.ua
    }
    # Extract path from URL for the request (fragments must NOT be sent)
    parsed_url = urlparse(url)
    path = parsed_url.path or '/'
    if parsed_url.query:
        path += '?' + parsed_url.query

    connections[connection_id].request(method=method, url=path, headers=headers)
    response = connections[connection_id].getresponse()
    response_dict = {
        "status": response.status,
        "reason": response.reason,
        "headers": response.getheaders(),  # list of (name, value)
        "content": response.read()
    }
    return response_dict


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


def _guess_mime_type(path: str) -> str:
    lower = path.lower()
    if lower.endswith('.css'):
        return 'text/css; charset=utf-8'
    if lower.endswith('.js'):
        return 'application/javascript; charset=utf-8'
    if lower.endswith('.html') or lower.endswith('.htm'):
        return 'text/html; charset=utf-8'
    if lower.endswith('.svg'):
        return 'image/svg+xml'
    if lower.endswith('.png'):
        return 'image/png'
    if lower.endswith('.jpg') or lower.endswith('.jpeg'):
        return 'image/jpeg'
    if lower.endswith('.gif'):
        return 'image/gif'
    if lower.endswith('.webp'):
        return 'image/webp'
    if lower.endswith('.ico'):
        return 'image/x-icon'
    return 'application/octet-stream'


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


def _is_relative_or_path(url_str: str) -> bool:
    p = urlparse(url_str)
    return (not p.scheme) and (not p.netloc)


def _serve_local_asset_from_html_dir(asset_path: str):
    # Normalize and prevent path traversal
    safe_path = asset_path.lstrip("/\\")
    file_path = f"html/{safe_path}"
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return {
            "status": 200,
            "reason": "OK",
            "headers": [("ZerolfieWeb-Internal-Asset", "True"), ("Content-Type", _guess_mime_type(file_path))],
            "content": data
        }
    except FileNotFoundError:
        body = b"<h1>404 Not Found</h1>\n<p>Local asset not found.</p>\n"
        return {
            "status": 404,
            "reason": "Not Found",
            "headers": [("ZerolfieWeb-Internal-Asset", "True"), ("Content-Type", "text/html; charset=utf-8")],
            "content": body
        }


def request(url: str = "http://localhost/index.php/Main_Page", port: Optional[int] = 443, method: str = "GET"):
    global _last_url
    url_parsed = urlparse(url)

    # If URL is relative (no scheme/netloc), decide how to serve it
    if _is_relative_or_path(url):
        # If last URL was an about: page, serve from html/ directory
        if _last_url and (_last_url.startswith("about:") or urlparse(_last_url).scheme == "about"):
            resp = _serve_local_asset_from_html_dir(url)
            return resp
        # Otherwise, if last URL is a network URL, resolve relative by joining paths
        if _last_url:
            base = urlparse(_last_url)
            if base.scheme in ("http", "https") and base.hostname:
                # Build absolute URL against base
                # Ensure path join without introducing //
                base_path = base.path if base.path else "/"
                if not base_path.endswith("/"):
                    base_path = base_path.rsplit("/", 1)[0] + "/"
                abs_path = base_path + url.lstrip("/")
                absolute_url = f"{base.scheme}://{base.netloc}{abs_path}"
                return request(absolute_url, port=None, method=method)
        # Fallback: try serving from html/ as a best effort for bare paths
        return _serve_local_asset_from_html_dir(url)

    # Handle about: URLs immediately
    if url_parsed.scheme == "about" or url.startswith("about:"):
        resp = _about_url_request(url=url, method=method)
        _last_url = url
        return resp

    # Determine host and port robustly
    domain = url_parsed.hostname or ""
    derived_port = url_parsed.port

    # Determine protocol based on scheme first
    https_enabled = True if url_parsed.scheme == "https" else False

    # Default ports by scheme if missing
    if derived_port is None:
        derived_port = 443 if https_enabled else 80

    # If explicit port param is provided and not None, respect it; otherwise use derived
    if port is None:
        port = derived_port

    # Find an existing connection or create a new one
    ip_result = dnsm.dns_lookup(domain)
    ip = ip_result["ip"]

    correct_connection_id: Optional[int] = None
    for idx, meta in enumerate(connections_metadata):
        if meta.get("ip") == ip and meta.get("port") == port and meta.get("domain") == domain and meta.get("https_enabled") == https_enabled:
            correct_connection_id = idx
            break

    if correct_connection_id is None:
        connect_to_server_via_domain(domain=domain, https_enabled=https_enabled, port=port)
        correct_connection_id = len(connections) - 1

    resp = _request(url=url, method=method, connection_id=correct_connection_id)
    _last_url = url
    return resp


def repl():
    while True:
        try:
            prompt = input(">>>")
            result = eval(prompt)
            if result is not None:
                print(result)
        except KeyboardInterrupt:
            cleanup_connections()


def cleanup_connections():
    for connection in connections:
        connection.close()
    # Ensure we clear the global metadata list rather than rebinding a local variable
    connections_metadata.clear()
    print("Cleaned up")


if __name__ == "__main__":
    repl()