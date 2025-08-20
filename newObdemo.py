
import os
import json
import sys



obedge = vars().get("obedge", None)

tableOutput = getattr(obedge.action.custom, "tableOutput")
manager = getattr(obedge.action.custom, "manager")

data = obedge.take()

out = obedge.queue.call(send="chk", payload=data['args'][0],recv="ans")

obj = manager()

if obj:

    obj.setCode(data['args'][0]['code'])

    ans = obj.find()

    out = tableOutput(out, ans, obj)


obedge.give(out)

