import html as pyhtml

class HTMLElement:
    def __init__(self,tagName:str):
        self.attributes={} # will put attributes here
        self._textContent="" # textContent backend
        self.tagName=tagName
    def getAttribute(self,name:str):
        try:
            return self.attributes[name.lower()]
        except KeyError:
            return None
    def setAttribute(self,name:str,value):
        self.attributes[name.lower()]=value
    def removeAttribute(self,name:str):
        if name in self.attributes:
            del self.attributes[name.lower()]
    @property
    def textContent(self):
        return self._textContent
    @textContent.setter
    def textContent(self,value):
        self._textContent=value

