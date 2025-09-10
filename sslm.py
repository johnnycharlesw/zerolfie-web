import ssl as pyssl

contexts=[]
def create_context(verify=True):
    if verify:
        contexts.append(pyssl.create_default_context(cafile="cacert.pem"))
    else:
        contexts.append(pyssl._create_unverified_context(cafile="cacert.pem"))

def get_context(id):
    return contexts[id]