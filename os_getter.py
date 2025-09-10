import platform

# Get the operating system name
os_name = platform.system()
print(f"Operating System: {os_name}")

if os_name=="Windows":
    ua_os_name="Windows NT"
else:
    ua_os_name=os_name
print(f"User-Agent OS Name: {ua_os_name}")
# Get the operating system version
os_version = platform.version()
print(f"OS Version: {os_version}")
ua_os_version=""
ua_os_version_parts=os_version.split(".")
if len(ua_os_version_parts)>=2:
    ua_os_version=".".join(ua_os_version_parts[:2])
print(f"User-Agent OS Version: {ua_os_version}")
# Get detailed information about the operating system
os_info = platform.platform()
print(f"Detailed OS Info: {os_info}")

ua=f"Mozilla/5.0 ({ua_os_name} {ua_os_version}) Python/{platform.python_version()} {platform.python_implementation()}/{platform.python_version()} ZerolfieWeb/0.0.1"
print(f"User-Agent: {ua}")