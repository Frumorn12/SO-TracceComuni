import math
import multiprocessing
from threading import Condition, Lock, Thread
import time

class DistributoreNumeri:

    def __init__(self, min_val, max_val):
        self.min = min_val
        self.max = max_val
        self.numCorrente = min_val
        self.quantita = 10
        self.lock = Lock()

    def getNextNumber(self):
        with self.lock:
            if self.numCorrente > self.max:
                return -1
            num = self.numCorrente
            self.numCorrente += 1
            return num

    def setQuantita(self, d):
        with self.lock:
            self.quantita = d

    def getNextInterval(self):
        with self.lock:
            if self.numCorrente > self.max:
                return -1
            inizio = self.numCorrente
            fine = min(self.max, self.numCorrente + self.quantita - 1)
            self.numCorrente = fine + 1
            return (inizio, fine)


class Barrier:

    def __init__(self, n):
        self.soglia = n
        self.threadArrivati = 0
        self.lock = Lock()
        self.condition = Condition(self.lock)

    def wait(self):
        with self.lock:
            self.threadArrivati += 1
            if self.threadArrivati == self.soglia:
                self.condition.notify_all()
            while self.threadArrivati < self.soglia:
                self.condition.wait()


class TotaleCondiviso:
    def __init__(self):
        self.totale = 0
        self.lock = Lock()

    def incrementa(self, n=1):
        with self.lock:
            self.totale += n

    def getTotale(self):
        with self.lock:
            return self.totale


Totale = TotaleCondiviso()

def eprimo(n):
    if n <= 3:
        return n > 1
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def contaPrimiSequenziale(min_val, max_val):
    totale = 0
    for i in range(min_val, max_val + 1):
        if eprimo(i):
            totale += 1
    return totale


class Macinatore(Thread):
    def __init__(self, d, b):
        super().__init__()
        self.distributore = d
        self.barrier = b

    def getTotale(self):
        return Totale.getTotale()

    def run(self):
        intervallo = self.distributore.getNextInterval()
        quantiNeHoFatto = 0

        while intervallo != -1:
            inizio, fine = intervallo
            for n in range(inizio, fine + 1):
                if eprimo(n):
                    Totale.incrementa()
                quantiNeHoFatto += 1
            intervallo = self.distributore.getNextInterval()

        print(f"Il thread {self.name} ma ha finito e ha testato {quantiNeHoFatto} numeri")
        self.barrier.wait()

class Macinatore2(Thread):
    def __init__(self, d, b):
        super().__init__()
        self.distributore = d
        self.barrier = b

    def run(self):
        intervallo = self.distributore.getNextInterval()
        quantiNeHoFatto = 0 
        while intervallo != -1:
            inizio, fine = intervallo
            for n in range(inizio, fine + 1):
                if eprimo(n):
                    Totale.incrementa()
                quantiNeHoFatto += 1 
            intervallo = self.distributore.getNextInterval()

        print(f"Il thread {self.name} con intervallo ma ha finito e ha testato {quantiNeHoFatto}" )
        self.barrier.wait() 

def contaPrimiMultiThread(min_val, max_val, intervallo_dinamico=10):
    nthread = multiprocessing.cpu_count()
    print(f"Trovato {nthread} processori")
    ciucci = []

    b = Barrier(nthread + 1)
    d = DistributoreNumeri(min_val, max_val)
    d.setQuantita(intervallo_dinamico)

    global Totale
    Totale = TotaleCondiviso()

    for i in range(nthread):
        if i % 2 == 0:
            ciucci.append(Macinatore(d, b))
        else:
            
            ciucci.append(Macinatore2(d, b)) 
        ciucci[i].start()

    b.wait()

    return Totale.getTotale()


if __name__ == "__main__":
    min_val = 1
    max_val = 10000000
    start = time.time()
    nprimi = contaPrimiMultiThread(min_val, max_val, intervallo_dinamico=20)
    elapsed = time.time() - start

    print(f"Primi tra {min_val} e {max_val}: {nprimi}")
    print(f"Tempo trascorso: {elapsed:.4f} secondi")
