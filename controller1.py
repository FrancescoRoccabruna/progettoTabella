
import sys
import sqlite3



obedge = vars().get("obedge", None)
params = obedge.share.input.get("args", [None]*2)

tabellaLocale = params[0]

type = params[1]


class GestioneAccessi:

    tabella = tabellaLocale
    type = type

    def __init__(self, code, path):
            self.path = path
            self.code = code

    def add(self,ans):
        method = getattr(self, f"{GestioneAccessi.type}_add", None)
        method(ans)


    def find(self):
        try:
            method = getattr(self, f"{GestioneAccessi.type}_find")
            return method()
        except AttributeError:
            print("type non valido")
            sys.exit()
            
    def update(self, ans, pos):
        method = getattr(self, f"{GestioneAccessi.type}_update", None)
        return method(ans, pos)



    def create_table(self):
        cur = self.con.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS auth (
            code TEXT PRIMARY KEY,
            permesso TEXT
        )
        ''')


    def sqlite_find(self):
        self.con = sqlite3.connect(self.path)
        cur = self.con.cursor()
        self.create_table()
        cur.execute(f"SELECT * FROM auth WHERE code = '{self.code}'")
        res = cur.fetchone()
        return res


    def text_update(self, ans, pos):
        with open(self.path, "r") as file:
            lines = file.readlines()
            lines[pos] = f"{self.code}/{ans}\n"
        with open(self.path, "w") as file:
            file.writelines(lines)

    def text_find(self):
        ans = None
        try:
            with open(self.path, "r") as file:
                righe = file.readlines()
                for i, riga in enumerate(righe):
                    if riga.split("/")[0] == self.code:
                        ans = [i, riga.split("/")[-1].strip()]
                        break
                return ans
        except IOError:
            print("Il file non è editabile")
            sys.exit()

    def text_add(self, ans):
        with open(self.path, "a") as file:
            file.write(self.code+"/"+ans+"\n")

    def sqlite_add(self, ans):
        cur = self.con.cursor()
        #cur.execute(f"INSERT INTO auth VALUES '{self.code}', '{ans}' ")
        cur.execute("INSERT INTO auth (code, permesso) VALUES (?, ?)", (self.code, ans))
        self.con.commit()

    def sqlite_update(self, ans, pos):
        cur = self.con.cursor()
        cur.execute(f"UPDATE auth SET permesso = '{ans}' WHERE code = '{self.code}'")
        self.con.commit()

def tableOutput(out, ans, obj):
    if out:
        if ans == None:
            obj.add(out)
        elif ans[1] != out:
            obj.update(out, ans[0])
    elif out == None and ans:
        out = ans[1]
    return out


obedge.action.system.register(GestioneAccessi)
obedge.action.system.register(tableOutput)

