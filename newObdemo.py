
import os
import json
import sys



obedge = vars().get("obedge", None)

GestioneAccessi = getattr(obedge.action.custom, "GestioneAccessi")
tableOutput = getattr(obedge.action.custom, "tableOutput")

data = obedge.take()

out = obedge.queue.call(send="chk", payload=data['args'][0],recv="ans")

if GestioneAccessi.tabella == "local":

    obj = GestioneAccessi(data['args'][0]['code'], "/home/ob/esempio1/db.sqlite")

    ans = obj.find()

    out = tableOutput(out, ans, obj)
else:
    print("salvataggio locale non abilitato")

print(f"output: {out}")
