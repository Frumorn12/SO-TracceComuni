

import math
import multiprocessing
from threading import Condition, Lock, Thread
import time

class DistributoreNumeri:

    def __init__(self,min,max,d=10):
        self.min = min
        self.max = max
        self.numCorrente = min
        self.lock = Lock()
        self.intervallo = d
    '''
        Utilizzato dai macinatori per avere un numero da calcolare
    '''
    def getNextNumber(self):
        with self.lock:
            if self.numCorrente > self.max:
                return -1
            num = self.numCorrente
            self.numCorrente += 1
            return num
        
    """
    Punto 1:
    Si modifichi la logica di funzionamento del DistributoreNumeri in maniera tale da distribuire D numeri da verificare per
    volta. La quantità D, che di default vale 10, deve essere modificabile dinamicamente (e cioè anche durante la fase di calcolo
    dei Macinatori) attraverso il metodo thread safe DistributoreNumeri.setQuantita(d);
    Invece, al posto del metodo DistributoreNumeri.getNextNumber() i Macinatori dovranno usare il metodo
    DistributoreNumeri.getNextInterval() che restituisce un intervallo composto da D numeri da far calcolare
    al Macinatore chiamante. L’intervallo assegnato può essere più piccolo di D nel caso in cui i numeri restanti da testare
    siano di meno.
    Ad esempio, supponiamo che D=20 ed nthread=2.
    Quando si invoca contaPrimiMultiThread(101,175), il distributore di numeri assegnerà ai due Macinatori, mano a
    mano che questi ne fanno richiesta, gli intervalli (101,120), (121,140), (141,160), (161,175).
    La modifica deve essere compatibile con eventuali Macinatori che continuino a usare getNextNumber (e cioè che
    continuano a prelevare un numero per volta)

    """
    def getNextInterval(self):
        with self.lock:
            if self.numCorrente > self.max:
                return -1
            num = self.numCorrente
            self.numCorrente += self.intervallo
            return (num,min(num+self.intervallo-1,self.max)) 



class Barrier:

    def __init__(self,n):

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

'''
    Utilizzabile per testare se un singolo numero è primo
'''
def eprimo(n):
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    for i in range(3,int(math.sqrt(n)+1),2):
        if n % i == 0:
            return False
    return True

'''
    Utilizzabile per conteggiare un singolo intervallo di numeri primi
'''
def contaPrimiSequenziale(min,max):
    totale = 0
    for i in range(min,max+1):
        if eprimo(i):
            totale += 1
    return totale

class Macinatore(Thread):
    def __init__(self,d,b):
        super().__init__()
        self.min = min
        self.max = max
        self.totale = 0
        self.barrier = b
        self.distributore = d

    def getTotale(self):
        return self.totale
    
    def run(self):
        n = self.distributore.getNextNumber()
        quantiNeHoFatto = 0
        while(n != -1):
            
            if eprimo(n):
                self.totale += 1
            quantiNeHoFatto += 1
            n = self.distributore.getNextNumber()
        
        print(f"Il thread {self.getName()} ha finito e ha testato {quantiNeHoFatto} numeri")
        self.barrier.wait()

def contaPrimiMultiThread(min,max):

    nthread = multiprocessing.cpu_count()
    print(f"Trovato {nthread} processori" )
    ciucci = []
        
    b = Barrier(nthread+1)
    d = DistributoreNumeri(min,max)

    for i in range(nthread):
        ciucci.append(Macinatore( d, b ))
        ciucci[i].start()


    b.wait()

    totale = 0
    for i in range(nthread):
        totale += ciucci[i].getTotale()
    return totale



min = 100000
max = 1000000
start = time.time()
nprimi = contaPrimiMultiThread(min,max)
elapsed = time.time() - start
print (f"Primi tra {min} e {max}: {nprimi}")
print (f"Tempo trascorso: {elapsed} secondi")
