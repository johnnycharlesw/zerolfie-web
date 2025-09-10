import dns.resolver as resolv
import ipaddress
def dns_lookup(domain):
    try:
        try:
            if ipaddress.ip_address(domain):
                return {
                    "domain":domain,
                    "ip":domain
                }
        except ValueError:
            pass
        if domain=="localhost":
            return {
                "domain":domain,
                "ip":"127.0.0.1"
            }
        answers = resolv.resolve(domain, 'A')
        for rdata in answers:
            return {
                "domain":domain,
                "ip":rdata
            }
    except resolv.NoAnswer:
        print(f"No answer for {domain}")
    except resolv.NXDOMAIN:
        print(f"Domain {domain} does not exist")
    except resolv.Timeout:
        print(f"Timeout while resolving {domain}")
    except resolv.NoNameservers:
        print(f"No nameservers available for {domain}")
    except Exception as e:
        print(f"An error occurred: {e}")
