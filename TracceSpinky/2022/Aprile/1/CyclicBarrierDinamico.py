import math
import multiprocessing
from threading import Condition, Lock, Thread
import time

class DistributoreNumeri:
    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.numCorrente = min
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
                self.condition.notifyAll()
            while self.threadArrivati < self.soglia:
                self.condition.wait()

def eprimo(n):
    if n <= 3:
        return n > 1
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

class Totale:
    def __init__(self):
        self.totale = 0
        self.lock = Lock()

    def incrementa(self, valore=1):
        with self.lock:
            self.totale += valore

    def getTotale(self):
        with self.lock:
            return self.totale

class Macinatore(Thread):
    def __init__(self, distributore, barrier, totale):
        super().__init__()
        self.distributore = distributore
        self.barrier = barrier
        self.totale = totale

    def run(self):
        quantiNeHoFatto = 0
        intervallo = self.distributore.getNextInterval()
        while intervallo != -1:
            inizio, fine = intervallo
            for n in range(inizio, fine + 1):
                if eprimo(n):
                    self.totale.incrementa()
                quantiNeHoFatto += 1
            intervallo = self.distributore.getNextInterval()

        print(f"Il thread {self.getName()} ha finito e ha testato {quantiNeHoFatto} numeri")
        self.barrier.wait()

def contaPrimiMultiThread(min, max):
    nthread = multiprocessing.cpu_count()
    print(f"Trovato {nthread} processori")

    barrier = Barrier(nthread + 1)
    distributore = DistributoreNumeri(min, max)
    totaleCondiviso = Totale()

    macinatori = []
    for _ in range(nthread):
        m = Macinatore(distributore, barrier, totaleCondiviso)
        m.start()
        macinatori.append(m)

    barrier.wait()
    return totaleCondiviso.getTotale()

# Esecuzione
min = 100000
max = 1000000

start = time.time()
nprimi = contaPrimiMultiThread(min, max)
elapsed = time.time() - start

print(f"Primi tra {min} e {max}: {nprimi}")
print(f"Tempo trascorso: {elapsed:.2f} secondi")
