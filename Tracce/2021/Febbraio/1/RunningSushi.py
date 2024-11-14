from threading import Lock, RLock, Condition, Thread
from time import sleep
from random import random, randint


"""


"""

debug = True

# Stampa sincronizzata
plock = Lock()
def sprint(s):
    with plock:
        print(s)

# Stampa solo in debug mode
def dprint(s):
    with plock:
        if debug:
            print(s)

class RunningSushiBuffer:

    def __init__(self, dim):
        self.theBuffer = [None] * dim
        self.zeroPosition = 0
        self.dim = dim
        self.lock = RLock()
        self.condition_put = Condition(self.lock) # Condition per put()
        self.condition_get = Condition(self.lock) # Condition per get()

    def _getRealPosition(self, i):
        return (i + self.zeroPosition) % self.dim

    def get(self, pos):
        with self.lock:
            while self.theBuffer[self._getRealPosition(pos)] is None:
                self.condition.wait()
            palluzza = self.theBuffer[self._getRealPosition(pos)]
            self.theBuffer[self._getRealPosition(pos)] = None
            return palluzza

    def put(self, t):
        with self.lock:
            while self.theBuffer[self._getRealPosition(0)] is not None:
                self.condition.wait()
            self.theBuffer[self._getRealPosition(0)] = t

    def putList(self, L):
        with self.lock:
            # Attende fino a che non ci siano abbastanza posizioni consecutive libere a partire dalla posizione 0
            while not all(self.theBuffer[self._getRealPosition(i)] is None for i in range(len(L))):
                self.condition.wait()
            # Inserisce ogni elemento della lista e fa uno shift dopo ciascun inserimento
            for item in L:
                self.theBuffer[self._getRealPosition(0)] = item
                self.shift()
            self.condition_get.notifyAll()

    def getList(self, N, t, i):

        with self.lock:
            collected_items = []
            while len(collected_items) < N:
                item = self.theBuffer[self._getRealPosition(i)]
                if item is None or item == t:
                    # Attende se non ci sono elementi disponibili o se l'elemento è da ignorare
                    self.condition.wait()
                else:
                    # Raccoglie l'elemento e lo rimuove dal buffer
                    collected_items.append(item)
                    self.theBuffer[self._getRealPosition(i)] = None
            self.condition_put.notifyAll()
            return collected_items

    def shift(self, j=1):
        with self.lock:
            # Uso zeroPosition per spostare la posizione 0 solo virtualmente
            self.zeroPosition = (self.zeroPosition + j) % self.dim
            # Sveglia un thread in attesa su put() o get()
            self.condition.notifyAll()



class NastroRotante(Thread):

    def __init__(self, d):
        super().__init__()
        self.iterazioni = 10000
        self.d = d

    def run(self):
        while self.iterazioni > 0:
            sleep(0.1)
            self.iterazioni -= 1
            self.d.shift()

class Cuoco(Thread):

    piatti = ["*", ";", "^", "%"]

    def __init__(self, d):
        super().__init__()
        self.iterazioni = 1000
        self.d = d

    def run(self):
        while self.iterazioni > 0:
            sleep(0.5 * random())
            self.iterazioni -= 1
            randPiatto = randint(0, len(self.piatti) - 1)
            self.d.put(self.piatti[randPiatto])
            print(f"Il cuoco {self.ident} ha cucinato <{self.piatti[randPiatto]}>")
        print(f"Il cuoco {self.ident} ha finito il suo turno e va via")

class Cliente(Thread):

    def __init__(self, d, pos):
        super().__init__()
        self.coseCheVoglioMangiare = randint(1, 20)
        self.d = d
        self.pos = pos

    def run(self):
        while self.coseCheVoglioMangiare > 0:
            sleep(5 * random())
            self.coseCheVoglioMangiare -= 1
            print(f"Il cliente {self.ident} aspetta cibo")
            print(f"Il cliente {self.ident} mangia <{self.d.get(self.pos)}>")
        print(f"Il cliente {self.ident} ha la pancia piena e va via")

size = 20
D = RunningSushiBuffer(size)
NastroRotante(D).start()
for i in range(0, 2):
    Cuoco(D).start()
for i in range(1, size):
    Cliente(D, i).start()
