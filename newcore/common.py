import json

class NotFound: pass

def jdumps(o, *a, **k):
    k["ensure_ascii"] = False
    # ~ k["default"]=serialize
    return json.dumps(o, *a, **k)

if __name__=="__main__":
    pass
