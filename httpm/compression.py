import gzip
import brotli

def decompress(recieved_bytes, algorithm):
    if algorithm == "gzip":
        return gzip.decompress(recieved_bytes)
    elif algorithm == "identity":
        return recieved_bytes
    elif algorithm == "deflate":
        try:
            # For real Apache/NGINX/LightTPD
            return zlib.decompress(recieved_bytes)
        except zlib.error:
            # For cheap knockoffs of Apahce/NGINX/LightTPD that do not properly send zlib streams
            return zlib.decompress(recieved_bytes, -zlib.MAX_WBITS)
    elif algorithm == "br":
        return brotli.decompress(recieved_bytes)

