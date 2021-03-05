import json

class NotFound: pass

def jdumps(o, *a, **k):
    k["ensure_ascii"] = False
    # ~ k["default"]=serialize
    return json.dumps(o, *a, **k)


def decodeBytes(b:bytes) -> str:
    assert type(b)==bytes
    try:
        x=b.decode()
    except:
        try:
            x= b.decode("cp1252")
        except:
            x= str(b)
    assert type(x)==str
    return x

if __name__=="__main__":
    pass
