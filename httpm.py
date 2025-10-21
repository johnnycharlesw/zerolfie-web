import http.client as pyhttp
import os_getter
from urllib.parse import urlparse
import dnsm
import sslm
connections=[]
connections_metadata=[]
def connect_to_server_via_domain(https_enabled=True,port=443,domain='localhost',blocksize=8192):
    dns_lookup=dnsm.dns_lookup(domain)
    ip=dns_lookup["ip"]
    return connect_to_server(https_enabled=https_enabled,port=port,ip=ip,domain=domain,blocksize=blocksize)

def connect_to_server(https_enabled: bool=True,port: int=443,ip: str="127.0.0.1",domain: str=None,blocksize: int=8192):
    id=len(connections)
    disable_ssl=False
    if https_enabled:
        if ip=="127.0.0.1":
            disable_ssl=True
        # Use domain for SSL certificate validation, fall back to IP if no domain
        hostname = domain if domain else ip
        connections.append(pyhttp.HTTPSConnection(host=hostname,port=port,blocksize=blocksize))
        
    else:
        if port==443:
            port=80
        # Use domain as host for proper Host header on HTTP/1.1
        hostname = domain if domain else ip
        connections.append(pyhttp.HTTPConnection(host=hostname,port=port))

    connections_metadata.append({
        "ip":ip,
        "domain":domain,
        "port":port,
        "disable_ssl":disable_ssl
    })
    


def _request(url,method,connection_id):
    if connection_id==None:
        print("Invalid connection ID")
        return
    headers={
        "User-Agent": os_getter.ua
    }
    # Extract path from URL for the request
    parsed_url = urlparse(url)
    path = parsed_url.path or '/'
    if parsed_url.query:
        path += '?' + parsed_url.query
    if parsed_url.fragment:
        path += '#' + parsed_url.fragment
    
    connections[connection_id].request(method=method,url=path,headers=headers)
    response=connections[connection_id].getresponse()
    response_dict={
        "status":response.status,
        "reason":response.reason,
        "headers":response.getheaders(),
        "content":response.read()
    }
    return response_dict

def request(url="http://localhost/index.php/Main_Page",port=443,method="GET"):
    correct_connection_id=None
    url_parsed=urlparse(url)
    netloc=url_parsed.netloc
    domain=""
    is_parsing_domain=True
    port_str=""
    for char in netloc:
        if char != ":":
            if is_parsing_domain:
                domain+=char
            else:
                port_str+=char
        else:
            is_parsing_domain=False
    
    if not port_str=="":
        port=int(port_str)
    
    https_enabled=True
    if port==None:
        if url_parsed.scheme=="https":
            port=443
        elif url_parsed.scheme=="http":
            port=80
            https_enabled=False
        
    ip_result = dnsm.dns_lookup(domain)
    ip = ip_result["ip"]
    id=0
    for connection_metadata in connections_metadata:
        if len(connections)==0:
            connect_to_server_via_domain(domain=domain,https_enabled=https_enabled)
        if connection_metadata["ip"]==ip and connection_metadata["port"]==port and connection_metadata.get("domain")==domain:
            correct_connection_id=id
        else:
            try:
                connection=connections[id+1]
            except IndexError:
                connect_to_server_via_domain(domain=domain,https_enabled=https_enabled)
            id+=1
            continue   
    if correct_connection_id==None:
        correct_connection_id=len(connections)
        connect_to_server_via_domain(domain=domain,https_enabled=https_enabled)

    return _request(url=url,method=method,connection_id=correct_connection_id)

        

def repl():
    while True:
        try:
            prompt=input(">>>")
            result=eval(prompt)
            if not result==None:
                print(result)
        except KeyboardInterrupt:
            cleanup_connections()
            
def cleanup_connections():
    for connection in connections:
        connection.close()
    connections_metadata=[]
    print("Cleaned up")
    exit()

if __name__=="__main__":
    repl()