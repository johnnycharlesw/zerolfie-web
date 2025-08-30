import STPyV8 as v8js

def init():
    with v8js.JSContext() as ctxt:
      upcase = ctxt.eval("""
        ( (lowerString) => {
            return lowerString.toUpperCase();
        })
    """)
    print(upcase("hello world!"))