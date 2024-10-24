import math
from threading import Condition, Lock, Thread
import time

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

class ExtendedBarrier(Barrier):

    # Incrementa threadArrivati di uno ed esce
    def finito(self):
        with self.lock:
            self.threadArrivati += 1
            if self.threadArrivati == self.soglia:
                self.condition.notifyAll()

    # Aspetta che threadArrivati raggiunga la soglia, senza incrementare
    def aspettaEbasta(self):
        with self.lock:
            while self.threadArrivati < self.soglia:
                self.condition.wait()

    # Fattorizza wait utilizzando finito e aspettaEbasta
    def wait(self):
        self.finito()       # Incrementa threadArrivati
        self.aspettaEbasta() # Aspetta che tutti i thread arrivino



class DoppiaBarriera:

    def __init__(self, n0, n1):
        self.soglia0 = n0  # Soglia per S0
        self.soglia1 = n1  # Soglia per S1
        self.threadArrivati0 = 0  # Thread arrivati per S0
        self.threadArrivati1 = 0  # Thread arrivati per S1
        self.lock = Lock()
        self.condition = Condition(self.lock)

    # Incrementa threadArrivati su numSoglia (0 o 1)
    def finito(self, numSoglia):
        with self.lock:
            if numSoglia == 0:
                self.threadArrivati0 += 1
                if self.threadArrivati0 == self.soglia0:
                    self.condition.notifyAll()
            elif numSoglia == 1:
                self.threadArrivati1 += 1
                if self.threadArrivati1 == self.soglia1:
                    self.condition.notifyAll()

    # Aspetta che threadArrivati su numSoglia raggiunga la soglia (0 o 1)
    def aspettaEbasta(self, numSoglia):
        with self.lock:
            if numSoglia == 0:
                while self.threadArrivati0 < self.soglia0:
                    self.condition.wait()
            elif numSoglia == 1:
                while self.threadArrivati1 < self.soglia1:
                    self.condition.wait()

    # Incrementa e aspetta per numSoglia (0 o 1)
    def wait(self, numSoglia):
        self.finito(numSoglia)  # Incrementa il numero di thread arrivati
        self.aspettaEbasta(numSoglia)  # Attende che si raggiunga la soglia

    # Incrementa di uno entrambe le soglie e aspetta che entrambe le soglie siano raggiunte
    def waitAll(self):
        with self.lock:
            self.threadArrivati0 += 1
            self.threadArrivati1 += 1
            if self.threadArrivati0 == self.soglia0 and self.threadArrivati1 == self.soglia1:
                self.condition.notifyAll()

            while self.threadArrivati0 < self.soglia0 or self.threadArrivati1 < self.soglia1:
                self.condition.wait()


# Esempio di utilizzo della classe ExtendedBarrier
def thread_funzione(barriera, id):
    print(f"Thread {id} in attesa...")
    barriera.wait()
    print(f"Thread {id} ha superato la barriera!")

def thread_finito(barriera, id):
    print(f"Thread {id} finito!")
    barriera.finito()

def thread_aspetta(barriera, id):
    print(f"Thread {id} aspetta solo...")
    barriera.aspettaEbasta()
    print(f"Thread {id} ha finito di aspettare!")

# Esecuzione di esempio
if __name__ == "__main__":
    num_thread = 5
    barriera = ExtendedBarrier(num_thread)

    # Creiamo thread che chiamano wait, finito, e aspettaEbasta
    threads = [Thread(target=thread_funzione, args=(barriera, i)) for i in range(3)]
    threads += [Thread(target=thread_finito, args=(barriera, i)) for i in range(3, 4)]
    threads += [Thread(target=thread_aspetta, args=(barriera, i)) for i in range(4, 5)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("Tutti i thread hanno terminato!")
