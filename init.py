
import sys
import sqlite3
import os
import json
import uuid
import time

try:
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

    if path:
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
                self.create_tables()

        def con(self):
            return sqlite3.connect(GestioneAccessi.path)

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

        def action(self):
            method = getattr(self, f"{GestioneAccessi.kind}_action")
            return method()
        
        def json_action(self):
            file = self.json_open("r")
            jsonDic = json.load(file)
            action = jsonDic['data'][self.macAddr]['TEST']['command']
            open_door(self.code, action['door'], action['check'])

        def sqlite_action(self):
            con = self.con()
            cur = con.cursor()

            cur.execute("SELECT * FROM commands")
            out = cur.fetchall()
            action = {}

            for t in out:
                action[t[0]] = t[1]
                
            open_door(self.code, action['door'], action['check'])



        def sqlite_update_all(self, dic):
            temp = sqlite3.connect(GestioneAccessi.path)
            cur = temp.cursor()

            partialDic = dic['data'][self.macAddr]['TEST']
            #dati = list(dic.items())
            dati = []

            for badge in partialDic['badges']:
                dati.append((badge['code'], badge['id'], badge['dude_id']))

            query = 'INSERT OR REPLACE INTO badges (code, id, dude_id) VALUES (?, ?, ?)'

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
            # Optionally clear tables only if dic contains data
            partialDic = dic['data'][self.macAddr]['TEST']
            
            if partialDic.get('badges') or partialDic.get('command'):
                temp = sqlite3.connect(GestioneAccessi.path)
                cur = temp.cursor()
                cur.execute('DELETE FROM badges')
                cur.execute('DELETE FROM commands')
                temp.commit()
                temp.close()
                self.sqlite_update_all(dic)
            else:
                # no data, skip rewriting to prevent empty DB
                print("Warning: rewrite called with empty data, skipping DB wipe.")

        def json_rewrite_all(self, dic):
            file = self.json_open("w")
            json.dump(dic, file, ensure_ascii=False, indent=4)
            file.close()

        def create_tables(self):
            con = self.con()
            cur = con.cursor()
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
            con.close()
        
        def sqlite_find(self, code):
            res = False
            con = self.con()
            cur = con.cursor()
            cur.execute("SELECT * FROM badges WHERE code = ?", (code,))
            out = cur.fetchone()
            cur.close()
            con.close()

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
            con = self.con()
            cur = con.cursor()
            cur.execute("INSERT OR REPLACE INTO badges (code, id, dude_id) VALUES (?, ?, ?)", (badge['code'], badge['id'], badge['dude_id']))
            con.commit()
            con.close()

        def sqlite_remove(self, code):
            con = self.con()
            cur = con.cursor()
            cur.execute("DELETE FROM badges WHERE code = ?", (code,))
            con.commit()
            cur.close()
            con.close()


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
                    obj.remove(obj.code)
                
        elif ans:
            res = True
        return res


    out = None
    if GestioneAccessi.path != None:
        out = GestioneAccessi()
        dic = {'kind' : "", 'code' : "", 'rawdata' : "", 'action' : "rewrite"}
        obedge.queue.feed(payload=dic)

    def manager():
        global out
        return out



    def action(action):
        open_door(action['badge']['code'], action['status']['command']['door'], action['status']['command']['check'])


    def updateBadge(dic):
        print("eseguito updateBadge")
        if GestioneAccessi.path != None:
            global out
            if dic['type'] == "add":
                out.add(dic['badge'])
            else:
                out.remove(dic['badge']['code'])
                

    def adminUpdate(dit):
        print("eseguito adminUpdate")
        if GestioneAccessi.path != None:
            global out
            out.rewrite_all(dit)


    def open_door(badge_code, door, check=None, sleep=0.1,maxseconds=5):
        obedge.iono.write(door, 1)

        if check:
            start = time.time()
            checked = False
            while time.time() - start <= maxseconds:
                var = obedge.iono.read(check)

                if var == 1 or var == "1":
                    checked = True
                    break
            obedge.queue.feed(payload = {
                "badge_code" : badge_code,
                "check" : check,
                "checked" : checked
            })
        else: time.sleep(sleep)
        obedge.iono.write(door, 0)



    obedge.action.system.register(GestioneAccessi)
    obedge.action.system.register(manager)
    obedge.action.system.register(tableOutput)
    obedge.action.system.register(adminUpdate)
    obedge.action.system.register(action)

    #scan "5522df0fe19305cd"
except Exception as a:
    print(a)