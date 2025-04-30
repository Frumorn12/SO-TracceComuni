import threading
import random
from time import sleep  
lock = threading.RLock()
miele = []
class VasettoDiMiele:
    def __init__(self, indice, capacita):
        self.capacita = capacita
        self.miele = capacita # Inizialmente la quantità di miele è uguale alla capacità
        self.indice = indice # Identificativo del vasetto 
        self.lock = threading.RLock()
        self.condition_aumento = threading.Condition(self.lock)
        self.condition_diminuzione = threading.Condition(self.lock)
        self.waitMamma = False

    #
    # Si sblocca solo quando il vasetto Ã¨ totalmente vuoto
    #
    def riempi(self):
        with self.lock:
            if self.miele == self.capacita:
                print(f"Il vasetto {self.indice} Ã¨ giÃ  pieno, non posso riempirlo")
                return

            while self.miele > 0:
                print(f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, aspetto che si svuoti completamente")
                self.waitMamma = True
                self.condition_aumento.wait()
                
            self.miele = self.capacita
            self.condition_aumento.notify_all() # Notifica gli altri thread che potrebbero essere in attesa di riempire il vasetto
            self.waitMamma = False
            lock.acquire()
            miele[ self.indice] = self.miele
            lock.release()
            print(f"{threading.current_thread().name} ha rabboccato il vasetto {self.indice}")

    #
    # Preleva del miele dal vasetto
    #
    def prendi(self, quantita):
        with self.lock:
            while self.miele < quantita: # Se non c'Ã¨ abbastanza miele, aspetta
                print(f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, non Ã¨ possibile prendere {quantita}. Aspetto che il vasetto venga riempito")
                self.condition_diminuzione.wait()
            self.miele -= quantita
            print(f"Orsetto {threading.current_thread().name} ha preso {quantita} unitÃ  di miele dal vasetto {self.indice}")
            lock.acquire()
            miele[ self.indice] = self.miele
            lock.release()
            self.condition_diminuzione.notify_all() # Notifica gli altri thread che potrebbero essere in attesa di prelevare miele
    
    def aggiungi(self, quantita): 
        with self.lock:
            while self.miele + quantita > self.capacita or self.waitMamma: 
                print(f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, aggiungerne {quantita} supererebbe la capacitÃ  massima di {self.capacita}")
                self.condition_aumento.wait()
            self.miele += quantita
            print(f"Orso {threading.current_thread().name} ha aggiunto {quantita} unitÃ  di miele al vasetto {self.indice}")
            lock.acquire()
            miele[ self.indice] = self.miele
            lock.release()
            self.condition_aumento.notify_all() # Notifica gli altri thread che potrebbero essere in attesa di aggiungere miele 
            

class OrsettoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def run(self):
        while True:
            vasetto_indice = random.randint(0, len(self.vasettiMiele)-1)
            quantita = random.randint(1,self.vasettiMiele[vasetto_indice].capacita)
            self.vasettiMiele[vasetto_indice].prendi(quantita)

class PapaOrsoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def run(self):
        while True:
            vasetto_indice1 = random.randint(0, len(self.vasettiMiele)-1)
            vasetto_indice2 = random.randint(0, len(self.vasettiMiele)-1)
            while vasetto_indice1 == vasetto_indice2:
                vasetto_indice2 = random.randint(0, len(self.vasettiMiele)-1)
            quantita = random.randint(1, self.vasettiMiele[vasetto_indice1].capacita)
            self.vasettiMiele[vasetto_indice1].prendi(quantita)
            self.vasettiMiele[vasetto_indice2].aggiungi(quantita)
            print(f"Papa orso {self.name} ha spostato {quantita} grammi dal vasetto {vasetto_indice1} al vasetto {vasetto_indice2}")

'''
Punto 3
'''          
class DisplayThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
       

    def run(self):  
        while True:
            sleep(5)   
            lock.acquire()
            somma = 0
            for i in range(len(miele)):
                somma += miele[i] 
            lock.release()

            print(f"Il totale del miele Ã¨ {somma} grammi")

class MammaOrsoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)
        self.name = name
        self.vasettiMiele = vasettiMiele

    def run(self):
        while True:
            vasetto_indice = random.randint(0, len(self.vasettiMiele)-1)
            self.vasettiMiele[vasetto_indice].riempi()
            print(f"Mamma orso {self.name} ha riempito il vasetto {vasetto_indice}")


if __name__ == '__main__':
    num_vasetti = 5
    
    vasetti = [VasettoDiMiele(i,50+50*i) for i in range(num_vasetti)]

    orsetti = [OrsettoThread(f"Winnie-{i}", vasetti) for i in range(5)]
    mamme_orse = [MammaOrsoThread(f"Mamma-{i}",vasetti) for i in range(2)]
    papa_orso = [PapaOrsoThread(f"Babbo-{i}", vasetti) for i in range(3)]

    # nella lista globale miele ci sono i vasetti di miele. vado ad aggiuhngere 0 alla lista per ogni vasetto

    for i in range(num_vasetti):
        miele.append(0)
                
    for orsetto in orsetti:
        orsetto.start()
 
    for orsa in mamme_orse:
        orsa.start()

    for orso in papa_orso:
        orso.start()

    display = DisplayThread("Display")  
    display.start()
        
    
