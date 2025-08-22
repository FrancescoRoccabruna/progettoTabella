import json

obedge = vars().get("obedge", None)

tableOutput = getattr(obedge.action.custom, "tableOutput")
manager = getattr(obedge.action.custom, "manager")

try:

    data = obedge.take()

    res = obedge.queue.call(send="check", payload=data['args'][0],recv="answer")

    obj = manager()

    if obj:

        obj.setCode(data['args'][0]['code'])
        ans = obj.find(obj.code)
        print(ans)
        out = tableOutput(res, ans, obj)
        print(out)

    obedge.give(out)

except Exception as a:
    print(a)

