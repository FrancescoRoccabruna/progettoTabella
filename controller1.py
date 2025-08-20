
import sys
import sqlite3
import os


obedge = vars().get("obedge", None)
params = obedge.share.input.get("args", [None]*2)



class TextFileError(Exception):
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


allowedKind = ["sqlite", "text", "remote"]

if kind not in allowedKind:
    raise ParametersError("Modalità di salvataggio errata", kind)



extension = path.split(".")[-1]

allowedExtensionSqlite = ["sqlite", "db"]

if kind == "sqlite" and extension not in allowedExtensionSqlite or kind == "text" and extension != "txt":
    raise FileExtensionError("Estensione file errata", extension)



class GestioneAccessi:

    kind = kind
    path = path

    def __init__(self):
        if kind == "text" and not os.path.exists(path):
            self.text_open("x")
        elif kind == "sqlite":
            self.con = sqlite3.connect(path)
            self.create_table()

    def setCode(self, code):
        self.code = code

    def add(self,ans):
        method = getattr(self, f"{GestioneAccessi.kind}_add", None)
        method(ans)

    def text_open(self, mode):
        out = None
        try:
            out = open(self.path, mode)
        except IOError:
            raise TextFileError("Impossibile accedere al file", mode)
        return out

    def find(self):
        method = getattr(self, f"{GestioneAccessi.kind}_find")
        return method()

    def update(self, ans, pos):
        method = getattr(self, f"{GestioneAccessi.kind}_update")
        return method(ans, pos)

    def update_all(self, dic):
        method = getattr(self, f"{GestioneAccessi.kind}_update_all")
        return method(dic)

    def rewrite_all(self, dic):
        method = getattr(self, f"{GestioneAccessi.kind}_rewrite_all")
        return method(dic)


    def text_update_all(self, dic):
        file = self.text_open("r")
        local = {}
        for riga in file:
            if "/" in riga:
                local[riga.split("/")[0].strip()] = riga.split("/")[-1].strip()
        file.close()

        out = {**local, **dic}
        
        self.text_rewrite_all(out)

    def sqlite_update_all(self, dic):
        temp = sqlite3.connect(GestioneAccessi.path)
        cur = temp.cursor()
        dati = list(dic.items())
        query = 'INSERT OR REPLACE INTO auth (code, permesso) VALUES (?, ?)'

        cur.executemany(query, dati)
        print("beccato!")
        temp.commit()
        temp.close()

    def sqlite_rewrite_all(self, dic):
        temp = sqlite3.connect(GestioneAccessi.path)
        cur = temp.cursor()
        cur.execute('DELETE FROM auth')
        temp.commit()
        temp.close()
        self.sqlite_update_all(dic)

    def text_rewrite_all(self, dic):
        file = self.text_open("w")
        for codice, auth in dic.items():
            file.write(f"{codice}/{auth}\n")
        file.close()


    def create_table(self):
        cur = self.con.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS auth (
            code TEXT PRIMARY KEY,
            permesso TEXT
        )
        ''')
        cur.close()

    def sqlite_find(self):
        cur = self.con.cursor()
        cur.execute(f"SELECT * FROM auth WHERE code = '{self.code}'")
        res = cur.fetchone()
        cur.close()
        return res


    def text_update(self, ans, pos):
        file = self.text_open("r")
        lines = file.readlines()
        lines[pos] = f"{self.code}/{ans}\n"
        file.close()

        file = self.text_open("w")
        file.writelines(lines)
        file.close()
        
    def text_find(self):
        ans = None
        file = self.text_open("r")
        righe = file.readlines()
        for i, riga in enumerate(righe):
            if riga.split("/")[0] == self.code:
                ans = [i, riga.split("/")[-1].strip()]
                break
        file.close()
        return ans

    def text_add(self, ans):
        file = self.text_open("a")
        file.write(self.code+"/"+ans+"\n")
        file.close()


    def sqlite_add(self, ans):
        cur = self.con.cursor()
        cur.execute("INSERT INTO auth (code, permesso) VALUES (?, ?)", (self.code, ans))
        self.con.commit()

    def sqlite_update(self, ans, pos):
        cur = self.con.cursor()
        cur.execute(f"UPDATE auth SET permesso = '{ans}' WHERE code = '{self.code}'")
        self.con.commit()
        cur.close()
def tableOutput(val, ans, obj):
    out = val
    if out:
        if ans == None:
            obj.add(out)
        elif ans[1] != out:
            obj.update(out, ans[0])
    elif out == None and ans:
        out = ans[1]
    return out

out = None
if GestioneAccessi.path != None:
    out = GestioneAccessi()

def manager():
    global out
    return out

def adminUpdate(dic, method="update"):
    if GestioneAccessi.path != None:
        global out
        if method == "update":
            out.update_all(dic)
        elif method == "rewrite":
            out.rewrite_all(dic)

obedge.action.system.register(GestioneAccessi)
obedge.action.system.register(manager)
obedge.action.system.register(tableOutput)
obedge.action.system.register(adminUpdate)
