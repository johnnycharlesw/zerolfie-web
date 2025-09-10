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
    return connect_to_server(https_enabled=https_enabled,port=port,ip=ip,blocksize=blocksize)

def connect_to_server(https_enabled: bool=True,port: int=443,ip: str="127.0.0.1",blocksize: int=8192):
    id=len(connections)
    disable_ssl=False
    if https_enabled:
        if ip=="127.0.0.1":
            disable_ssl=True
        connections.append(pyhttp.HTTPSConnection(host=ip,port=port,blocksize=blocksize))
        
    else:
        if port==443:
            port=80
        connections.append(pyhttp.HTTPConnection(host=ip,port=port))

    connections_metadata.append({
        "ip":ip,
        "port":port,
        "disable_ssl":disable_ssl
    })
    print(id)



def _request(url,method,connection_id):
    if connection_id==None:
        print("Invalid connection ID")
        return
    headers={
        "User-Agent": os_getter.ua
    }
    connections[connection_id].request(method=method,url=url,headers=headers)
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
        
    ip=dnsm.dns_lookup(domain)
    id=0
    for connection_metadata in connections_metadata:
        if len(connections)==0:
            connect_to_server_via_domain(domain=domain,https_enabled=https_enabled)
        if connection_metadata["ip"]==ip and connection_metadata["port"]==port:
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