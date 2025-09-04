import json

try:
    obedge = vars().get("obedge", None)

    tableOutput = getattr(obedge.action.custom, "tableOutput")
    manager = getattr(obedge.action.custom, "manager")
    action = getattr(obedge.action.custom, "action")

    obj = manager()
    data = obedge.take()

    call = obedge.queue.call(send="check", payload=data['args'][0],recv="answer")

    if obj:
        obj.setCode(data['args'][0]['code'])
        ans = obj.find(obj.code)
        out = tableOutput(call, ans, obj)
    elif call:
        out = json.loads(call)['data']['authorized']
    if out and call:
        call = json.loads(call)
        action(call["data"])
    elif out:
        obj.action()

except Exception as a:
    print(a)





