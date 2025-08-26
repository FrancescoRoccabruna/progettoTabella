import json

obedge = vars().get("obedge", None)

tableOutput = getattr(obedge.action.custom, "tableOutput")
manager = getattr(obedge.action.custom, "manager")
action = getattr(obedge.action.custom, "action")

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
    elif res:
        out = json.loads(res)['data']['authorized']

    #obedge.give(out)

    if out and res:
        res = json.loads(res)
        action(res["data"]["status"]['command'])
    elif out:
        obj.action()

    
    
    #elif out:
     #   db_action()


except Exception as a:
    print(a)


# ./test.sh sqlite:prova.sqlite FTDI_FT232R


