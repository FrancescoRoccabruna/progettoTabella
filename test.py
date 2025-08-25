
import sys
import sqlite3
import os
import json
import uuid


obedge = vars().get("obedge", None)
params = obedge.share.input.get("args", [None]*2)



class JsonFileError(Exception):
    def __init__(self, message, error):
        self.message = message
        self.error = error
        super().__init__(f"{self.message}, modalità: {self.error}")

class FileExtensionError(Exception):
    def __init__(self, message, extension):
        self.message = message
        self.extension = extension
        super().__init(f"{self.message}, estensione: {self.extension}")

class ParametersError(Exception):
    def __init__(self, message, parameter):
        self.message = message
        self.parameter = parameter
        super().__init__(f"{self.message}, modalità: {self.parameter}")


param = params[0]


path = None
kind = None


if ":" in param:
    kind = param.split(":")[0]
    path = param.split(":")[1]

    if kind == "remote":
        raise ParametersError("Parametri errati", path) 

else:
    kind = param


allowedKind = ["sqlite", "json", "remote"]

if kind not in allowedKind:
    raise ParametersError("Modalità di salvataggio errata", kind)



extension = path.split(".")[-1]

allowedExtensionSqlite = ["sqlite", "db"]

if kind == "sqlite" and extension not in allowedExtensionSqlite or kind == "json" and extension != "json":
    raise FileExtensionError("Estensione file errata", extension)



class GestioneAccessi:

    kind = kind
    path = path

    def __init__(self):
        self.macAddr = f'{uuid.getnode():012x}'
        if kind == "json" and not os.path.exists(path):
            dic = {'data' : {self.macAddr : {'TEST' : {'badges' : [] }}}}
            self.json_write(dic)

        elif kind == "sqlite":
            self.con = sqlite3.connect(path)
            self.create_tables()

    def setCode(self, code):
        self.code = code

    def add(self,ans):
        method = getattr(self, f"{GestioneAccessi.kind}_add", None)
        method(ans)

    def json_open(self, mode):
        out = None
        try:
            out = open(self.path, mode, encoding="utf-8")
        except IOError:
            raise JsonFileError("Impossibile accedere al file", mode)
        return out

    def find(self, code):
        method = getattr(self, f"{GestioneAccessi.kind}_find")
        return method(code)
    
    def remove(self, code):
        method = getattr(self, f"{GestioneAccessi.kind}_remove")
        return method(code)

    def update(self, ans, pos):
        method = getattr(self, f"{GestioneAccessi.kind}_update")
        return method(ans, pos)

    def rewrite_all(self, dic):
        method = getattr(self, f"{GestioneAccessi.kind}_rewrite_all")
        return method(dic)

    def sqlite_update_all(self, dic):
        temp = sqlite3.connect(GestioneAccessi.path)
        cur = temp.cursor()

        partialDic = dic['data'][self.macAddr]['TEST']
        #dati = list(dic.items())
        dati = []

        for badge in partialDic['badges']:
            dati.append((badge['code'], badge['id'], badge['dude_id']))

        query = 'INSERT OR REPLACE INTO auth (code, id, dude_id) VALUES (?, ?, ?)'

        cur.executemany(query, dati)
        temp.commit()

        dati = []

        for key, command in partialDic['command'].items():
            dati.append((key, command))

        query = 'INSERT OR REPLACE INTO commands (key, command) VALUES (?, ?)'

        cur.executemany(query, dati)
        temp.commit()
        temp.close()

    def sqlite_rewrite_all(self, dic):
        temp = sqlite3.connect(GestioneAccessi.path)
        cur = temp.cursor()
        cur.execute('DELETE FROM auth')
        temp.commit()
        temp.close()
        self.sqlite_update_all(dic)

    def json_rewrite_all(self, dic):
        file = self.json_open("w")
        json.dump(dic, file, ensure_ascii=False, indent=4)
        file.close()

    def create_tables(self):
        cur = self.con.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            code TEXT PRIMARY KEY,
            id INTEGER,
            dude_id TEXT
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            key TEXT PRIMARY KEY,
            command TEXT
        )
        ''')
        cur.close()

    def sqlite_find(self, code):
        res = False
        cur = self.con.cursor()
        cur.execute("SELECT * FROM badges WHERE code = ?", (code,))
        out = cur.fetchone()
        cur.close()

        if out:
            res = True
        return res

    def json_remove(self, code):
        file = self.json_open("r")
        jsonDic = json.load(file)
        file.close()

        #jsonDic["badges"].remove(badge)
        for badge in jsonDic['data'][self.macAddr]['TEST']['badges']:
            if badge['code'] == code:
                jsonDic['data'][self.macAddr]['TEST']['badges'].remove(badge)
                break
        self.json_write(jsonDic)


    def json_add(self, badge):
        file = self.json_open("r")
        jsonDic = json.load(file)
        file.close()

        if self.json_find(badge['code']):
            self.json_remove(badge['code'])

        jsonDic['data'][self.macAddr]['TEST']['badges'].append(badge)
        self.json_write(jsonDic)


    def json_write(self, dic):
        file = self.json_open("w")
        json.dump(dic, file, ensure_ascii=False, indent=4)
        file.close()
        
    def json_find(self, code):
        #trovato = any('code' in elem for elem in dati['badges'])
        ans = False
        file = self.json_open("r")
        jsonDic = json.load(file)
        file.close()
        for bedge in jsonDic['data'][self.macAddr]['TEST']['badges']:
            if bedge['code'] == code:
                ans = True
                break
        return ans

    def sqlite_add(self, badge):
        cur = self.con.cursor()
        cur.execute("INSERT OR REPLACE INTO badges (code, id, dude_id) VALUES (?, ?, ?)", (badge['code'], badge['id'], badge['dude_id']))
        self.con.commit()

    def sqlite_remove(self, code):
        cur = self.con.cursor()
        cur.execute("DELETE FROM badges WHERE code = ?", (code,))
        self.con.commit()
        cur.close()


def tableOutput(out, ans, obj):
    res = None
    
    if out:
        out = json.loads(out)
        print(out)
        if out['data']['authorized']:
            res = True
            if ans == False:
                obj.add(out['data']['badge'])
        else: 
            res = False
            if ans:
                obj.remove(out['data']['badge']['code'])
            
    elif ans:
        res = True
    return res


out = None
if GestioneAccessi.path != None:
    out = GestioneAccessi()

def manager():
    global out
    return out


def updateTest(action):
    print("start")
    if GestioneAccessi.path != None:
        global out
        dic = {'action' : action}
        ans = obedge.queue.call(send="check", payload=dic,recv="update")
        print(ans)
        if action == "add":
            out.add(ans)
        elif action == "remove":
            out.remove(ans['code'])
        elif action == "rewrite":
            out.rewrite_all(ans)





def adminUpdate(dit):
    print(f"start: {dit}")
    if GestioneAccessi.path != None:
        global out
        out.rewrite_all(dit)

dic = {'action' : "rewrite"}

obedge.queue.call(send="check", payload=dic,recv="update")

obedge.action.system.register(GestioneAccessi)
obedge.action.system.register(manager)
obedge.action.system.register(tableOutput)
obedge.action.system.register(adminUpdate)
obedge.action.system.register(updateTest)