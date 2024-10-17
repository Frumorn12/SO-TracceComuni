import math
import multiprocessing
from threading import Condition, Lock, Thread
import time


class DistributoreNumeri:

    def __init__(self, min_val, max_val, D=10):
        self.min = min_val
        self.max = max_val
        self.numCorrente = min_val
        self.lock = Lock()
        self.D = D

    def getNextNumber(self):
        with self.lock:
            if self.numCorrente > self.max:
                return -1
            num = self.numCorrente
            self.numCorrente += 1
            return num

    def getNextInterval(self):
        with self.lock:
            if self.numCorrente > self.max:
                return -1, -1
            start = self.numCorrente
            end = min(self.numCorrente + self.D - 1, self.max)
            self.numCorrente = end + 1
            return start, end

    def setQuantita(self, d):
        with self.lock:
            self.D = d


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


class Totale:
    def __init__(self):
        self.totale = 0
        self.lock = Lock()

    def incrementa(self, valore):
        with self.lock:
            self.totale += valore

    def getTotale(self):
        with self.lock:
            return self.totale


def eprimo(n):
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n) + 1), 2):
        if n % i == 0:
            return False
    return True


class Macinatore(Thread):
    def __init__(self, distributore, barrier, totale_condiviso):
        super().__init__()
        self.barrier = barrier
        self.distributore = distributore
        self.totale_condiviso = totale_condiviso

    def run(self):
        start, end = self.distributore.getNextInterval()
        quantiNeHoFatto = 0

        while start != -1:
            for n in range(start, end + 1):
                if eprimo(n):
                    # Aggiorna il totale globale quando trova un numero primo
                    self.totale_condiviso.incrementa(1)
                quantiNeHoFatto += 1
            start, end = self.distributore.getNextInterval()

        print(f"Il thread {self.getName()} ha finito e ha testato {quantiNeHoFatto} numeri")
        self.barrier.wait()


def contaPrimiMultiThread(min_val, max_val, D=10):
    nthread = multiprocessing.cpu_count()
    print(f"Trovato {nthread} processori")

    # Totale condiviso tra tutti i Macinatori
    totale_condiviso = Totale()

    barrier = Barrier(nthread + 1)
    distributore = DistributoreNumeri(min_val, max_val, D)

    threads = []
    for i in range(nthread):
        threads.append(Macinatore(distributore, barrier, totale_condiviso))
        threads[i].start()

    barrier.wait()

    # Restituiamo il totale globale aggiornato dai Macinatori
    return totale_condiviso.getTotale()


min_val = 100000
max_val = 1000000
D = 20  # Quantità D iniziale
start = time.time()
nprimi = contaPrimiMultiThread(min_val, max_val, D)
elapsed = time.time() - start
print(f"Primi tra {min_val} e {max_val}: {nprimi}")
print(f"Tempo trascorso: {elapsed} secondi")
