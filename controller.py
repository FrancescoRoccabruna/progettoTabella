
import sys



obedge = vars().get("obedge", None)
params = obedge.share.input.get("args", [None]*2)

tabellaLocale = params[0]

class GestioneAccessi:
    
    tabella = tabellaLocale

    def __init__(self, code, type, path):
            self.type = type
            self.path = path
            self.code = code


    def add(self,ans):
        method = getattr(self, f"{self.type}_add")
        method(ans)


    def find(self):
        method = getattr(self, f"{self.type}_find")
        return method()

    def update(self, ans, pos):
        method = getattr(self, f"{self.type}_update")
        return method(ans, pos)


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