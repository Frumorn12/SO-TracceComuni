from threading import Thread,RLock,Condition, current_thread, Lock
from random import random
from time import sleep
#

import random, time



#
# Funzione di stampa sincronizzata
#
plock = RLock()
debug = True
def dprint(s):
    if debug:
        plock.acquire()
        print(s)
        plock.release()

class DatoCondiviso():

    def __init__(self,v):
        self.dato = v
        self.numLettori = 0
        self.ceUnoScrittore = False
        self.lock = RLock()
        self.condition = Condition(self.lock)

    def getDato(self):
        return self.dato
    
    def setDato(self, i):
        self.dato = i


    def acquireReadLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} prova a prendere il lock in lettura")
        while self.ceUnoScrittore:
            dprint(f"Il thread {current_thread().name} voleva leggere ma trova che c'Ã¨ uno scrittore. Dunque aspetta.")
            self.condition.wait()
        self.numLettori += 1
        dprint(f"Il thread {current_thread().name} prende il lock in lettura")
        self.lock.release()

    def releaseReadLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} rilascia il lock in lettura")
        self.numLettori -= 1
        if self.numLettori == 0:
            self.condition.notify()
        self.lock.release()

    def acquireWriteLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} prova a prendere il lock in scrittura")

        while self.numLettori > 0 or self.ceUnoScrittore:
            dprint(f"Il thread {current_thread().name} voleva scrivere, ma trova che ci sono {self.numLettori} lettori e che ceUnoScrittore={self.ceUnoScrittore}. Dunque aspetta.")
            self.condition.wait()
        self.ceUnoScrittore = True
        dprint(f"Il thread {current_thread().name} acquisisce il lock in scrittura")
        self.lock.release()

    def releaseWriteLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} rilascia il lock in scrittura")
        self.ceUnoScrittore = False
        self.condition.notify_all()
        self.lock.release()



class DatoCondivisoSenzaStarvation(DatoCondiviso):
    SOGLIAGIRI = 5

    def __init__(self,v):
        super().__init__(v)
        self.numScrittoriInAttesa = 0
        self.numGiriSenzaScrittori = 0

    def acquireReadLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} prova a prendere il lock in lettura")

        while self.ceUnoScrittore or \
              (self.numScrittoriInAttesa > 0 and self.numGiriSenzaScrittori > self.SOGLIAGIRI):
            dprint(f"Il thread {current_thread().name} trova che {self.numScrittoriInAttesa} scrittori sono in attesa e sono passati {self.numGiriSenzaScrittori} giri senza scrittori. Dunque aspetta")
            self.condition.wait()
        self.numLettori += 1
        # 
        # 		 * Il contatore viene incrementato solo se effettivamente ci sono
        # 		 * scrittori in attesa.
        # 		 
        if self.numScrittoriInAttesa > 0:
            self.numGiriSenzaScrittori += 1
        dprint(f"Il thread {current_thread().name} prende il lock in lettura")
        self.lock.release()

    def releaseReadLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} rilascia il lock in lettura")
        self.numLettori -= 1
        # 
        # 	Nella versione senza starvation, possono esserci anche dei lettori in attesa. 
        #   E' necessario
        #   dunque svegliare tutti.
        # 			 
        if self.numLettori == 0:
            self.condition.notify_all()
        self.lock.release()

    def acquireWriteLock(self):
        self.lock.acquire()
        dprint(f"Il thread {current_thread().name} prova a prendere il lock in scrittura")
 
        self.numScrittoriInAttesa += 1
        while self.numLettori > 0 or self.ceUnoScrittore:
            dprint(f"Il thread {current_thread().name} trova che ci sono {self.numLettori} lettori in attesa e che ceUnoScrittore Ã¨ {self.ceUnoScrittore}. Dunque aspetta")
            self.condition.wait()
        self.ceUnoScrittore = True
        self.numScrittoriInAttesa -= 1
        self.numGiriSenzaScrittori = 0
        dprint(f"Il thread {current_thread().name} prendere il lock in scrittura")
        self.lock.release()

# Resta uguale a DatoCondiviso
#     def releaseWriteLock(self):
#         lock.acquire()
#         ...
#         lock.release()

class Scrittore(Thread):
    
    maxIterations = 1000

    def __init__(self, i, dc):
        super().__init__()
        self.id = i
        self.dc = dc
        self.iterations = 0

    def run(self):
        while self.iterations < self.maxIterations:
            self.dc.acquireWriteLock()
            sleep(random())
            self.dc.setDato(self.id)
            self.dc.releaseWriteLock()
            sleep(random() * 5)
            self.iterations += 1


class Lettore(Thread):
    maxIterations = 100

    def __init__(self, i, dc):
        super().__init__()
        self.id = i
        self.dc = dc
        self.iterations = 0

    def run(self):
        while self.iterations < self.maxIterations:
            self.dc.acquireReadLock()
            sleep(random())
            self.dc.releaseReadLock()
            sleep(random() * 5)
            self.iterations += 1
  
#
#   In questo codice didattico rimangono alcuni difetti:
#   Uno scrittore puÃ² andare in attesa di sÃ¨ stesso se prende il writelock due volte (non rientranza) 
#   o se prende il writelock e poi il readlock (deadlock) 
#   Sapresti correggere questi problemi da solo? (Trovi una soluzione nella traccia di Novembre 2023)


class BlockingQueue:

    def __init__(self,dim):
        self.lock = Lock()
        self.full_condition = Condition(self.lock)
        self.empty_condition = Condition(self.lock)
        self.ins = 0
        self.out = 0
        self.slotPieni = 0
        self.dim = dim
        self.thebuffer = [None] * dim
        
    def put(self,c):
        self.lock.acquire()
        
        while self.slotPieni == len(self.thebuffer):
            self.full_condition.wait()
        
        self.thebuffer[self.ins] = c
        self.ins = (self.ins + 1) % len(self.thebuffer)
        
        self.empty_condition.notifyAll()
        
        self.slotPieni += 1
        self.lock.release()

    def show(self):
        
        self.lock.acquire()
        val = [None] * self.dim;
        
        for i in range(0,self.slotPieni):
            val[(self.out + i) % len(self.thebuffer)] = '*'
        
        for i in range(0,len(self.thebuffer) - self.slotPieni):
            val[(self.ins + i) % len(self.thebuffer)] = '-'
        
        print("In: %d Out: %d C: %d" % (self.ins,self.out,self.slotPieni))
        print("".join(val))
        self.lock.release()


    def get(self): 

        self.lock.acquire()
        try:
            while self.slotPieni == 0:
                self.empty_condition.wait()
    
            returnValue = self.thebuffer[self.out]
            self.out = (self.out + 1) % len(self.thebuffer)
            
            self.full_condition.notifyAll()
            
            self.slotPieni -= 1
            return returnValue
        finally:
            self.lock.release()

'''
In questo esercizio dovrai utilizzare i ReadWriteLock per disciplinare l’accesso a ciascun elemento di un array V di 10
numeri interi, ciascuno dei quali protetto da un proprio ReadWriteLock. Dovrai incapsulare V all’interno di una classe
che chiamerai InteriCombinati.
'''

class InteriCombinati:
    def __init(self):
        self.V = [DatoCondivisoSenzaStarvation(0) for i in range(10)]
    
    def calcola(self,i,j,op):
        try :
            self.V[i].acquireReadLock() # se hai due dati devi fare acquire
            self.V[j].acquireReadLock()
            if op == '+':
                return self.V[i].getDato() + self.V[j].getDato()
            elif op == '-':
                return self.V[i].getDato() - self.V[j].getDato()
            elif op == '*':
                return self.V[i].getDato() * self.V[j].getDato()
            elif op == '/':
                return self.V[i].getDato() / self.V[j].getDato()
            elif op == '%':
                return self.V[i].getDato() % self.V[j].getDato()
        finally:
            self.V[i].releaseReadLock()
            self.V[j].releaseReadLock() 

    def aggiorna(self, i,j,k,op):
        try:
            self.V[i].acquireReadLock()
            self.V[j].acquireReadlock()
            self.V[k].acquireWriteLock()
            if op == '+':
                self.V[k] = self.V[i].getDato() + self.V[j].getDato()
            elif op == '-':
                self.V[k] =  self.V[i].getDato() - self.V[j].getDato()
            elif op == '*':
                self.V[k] =  self.V[i].getDato() * self.V[j].getDato()
            elif op == '/':
                self.V[k] =  self.V[i].getDato() / self.V[j].getDato()
            elif op == '%':
                self.V[k] =  self.V[i].getDato() % self.V[j].getDato()
        finally:
            self.V[i].releaseReadLock()
            self.V[j].releaseReadLock()
            self.V[k].releaseWriteLock()


class Consumer(Thread): 
    
    def __init__(self,buffer):
        self.queue = buffer
        Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(random.random()*2)
            self.queue.get()
            self.queue.show()


class Producer(Thread):

    def __init__(self,buffer):
        self.queue = buffer
        Thread.__init__(self)
        

    def run(self): 
        while True:
            time.sleep(random.random() * 2)
            self.queue.put(self.name)
            self.queue.show()


"""
Successivamente, dovrai implementare una classe Calcolatrice composta da:
-Una istanza IC di InteriCombinati
-Una BlockingQueue B, volta a gestire l’elaborazione di tuple nel formato (i,j,k,op)
-4 Thread Elaboratore, da avviare nel costruttore di Calcolatrice. Il ciclo di vita di un thread Elaboratore
prevede di estrarre ciclicamente una tupla (i,j,k,op) da B e di eseguire l’operazione IC.aggiorna(i,j,k,op).-2 Thread Produttore, da avviare nel costruttore di Calcolatrice. Un Thread produttore inserisce in B una tupla
generata casualmente nel formato (i,j,k,op), dove gli indici i,j,k devono essere compresi tra 0 e 9, mentre op è
costituito da un unico carattere a scelta tra ‘+’ , ‘-’, ‘*’, ‘/’, ‘%’ .
"""

class Cacolatrice():
    def __init__(self):
        self.IC = InteriCombinati() # crea l'array di 10 numeri
        self.B = BlockingQueue(10)  # crea la BlockingQueue 
        # molto utile creare i thread cosi quando si deve eseguire solo una funzioncina
        self.elaboratori = [Thread(target=self.elabora) for _ in range(4)] # crea 4 thread elaboratori che eseguono il metodo elabora  
        self.produttori = [Thread(target=self.produce) for _ in range(2)] 

        for e in self.elaboratori:
            e.start()
        for p in self.produttori:
            p.start() 

    def elabora(self):  
        while True:
            i, j, k, op = self.B.get()
            self.IC.aggiorna(i, j, k, op)


    def produce(self):
        ops = ['+', '-', '*', '/', '%']
        while True:
            i, j, k = random.randint(0, 9), random.randint(0, 9), random.randint(0, 9)
            op = random.choice(ops)
            self.B.put((i, j, k, op))
            

        
#
#  Main
#
if __name__ == "__main__":

    buffer = BlockingQueue(10)

    producers = [Producer(buffer) for x in range(5)]
    consumers = [Consumer(buffer) for x in range(3)]

    for p in producers:
        p.start()

    for c in consumers:
        c.start()

    Cacolatrice()



