import html as htmlescaper

class HTMLElement:
    def __init__(self,tagName:str):
        self.attributes={} # will put attributes here
        self._textContent="" # textContent backend
        self.tagName=tagName
        self.childNodes=[]
    def getAttribute(self,name:str):
        try:
            return self.attributes[name.lower()]
        except KeyError:
            return None
    def setAttribute(self,name:str,value):
        self.attributes[name.lower()]=value
    def removeAttribute(self,name:str):
        key = name.lower()
        if key in self.attributes:
            del self.attributes[key]
    @property
    def textContent(self):
        return self._textContent
    @textContent.setter
    def textContent(self,value):
        self._textContent=value

    def appendChild(self,child):
        self.children.append(child)

    @property
    def children(self):
        toReturn=[]
        for childNode in self.childNodes:
            if isinstance(childNode,HTMLElement):
                toReturn.append(childNode)