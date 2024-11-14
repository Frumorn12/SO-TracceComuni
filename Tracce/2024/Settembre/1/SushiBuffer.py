from threading import RLock, Condition, Thread
from time import sleep
import random

debug = True

plock = RLock()

def sprint(s):
    pass

def dprint(s):
    pass

class RunningSushiBuffer:

    def __init__(self, dim):
        self.theBuffer = [None] * dim
        self.zeroPosition = 0
        self.dim = dim
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.verso = 1
        # Lista per tracciare le posizioni riservate ai cuochi
        self.posizioni_riservate = []

    def __getRealPosition(self, i: int):
        return (i + self.zeroPosition) % self.dim

    def aggiungi_posizione_riservata(self, pos: int):
        with self.lock:
            if pos < 0 or pos >= self.dim:
                raise ValueError("Posizione non valida")
            if pos not in self.posizioni_riservate:
                self.posizioni_riservate.append(pos)

    def rimuovi_posizione_riservata(self, pos: int):
        with self.lock:
            if pos in self.posizioni_riservate:
                self.posizioni_riservate.remove(pos)

    def get(self, pos: int):
        with self.lock:
            if pos in self.posizioni_riservate:
                raise ValueError("Posizione riservata ai cuochi, operazione get non consentita")
            if pos <= 0 or pos >= self.dim:
                raise ValueError("Posizione non valida per una operazione di get")
            while self.theBuffer[self.__getRealPosition(pos)] == None:
                self.condition.wait()
            palluzza = self.theBuffer[self.__getRealPosition(pos)]
            self.theBuffer[self.__getRealPosition(pos)] = None
            return palluzza

    def put(self, t):
        with self.lock:
            while self.theBuffer[self.__getRealPosition(0)] != None:
                self.condition.wait()
            self.theBuffer[self.__getRealPosition(0)] = t

    def shift(self, j=1):
        with self.lock:
            self.zeroPosition = (self.zeroPosition + j * self.verso) % self.dim
            self.condition.notify_all()

    def __checkFreePositions(self, n):
        for i in range(0, n):
            if self.theBuffer[self.__getRealPosition(i)] != None:
                return False
        return True

    def putList(self, L):
        with self.lock:
            while (not self.__checkFreePositions(len(L))):
                self.condition.wait()
            for elem in L:
                self.put(elem)
                self.shift()

    def __rawPut(self, T, i):
        self.theBuffer[self.__getRealPosition(i)] = T

    def __attendi_shift(self, t, i):
        while self.theBuffer[self.__getRealPosition(i)] == t:
            self.condition.wait()

    def getList(self, N, t, i):
        with self.lock:
            if i in self.posizioni_riservate:
                raise ValueError("Posizione riservata ai cuochi, operazione getList non consentita")
            retList = []
            elemDaPrendere = N
            while elemDaPrendere > 0:
                T = self.get(i)
                if T != t:
                    retList.append(T)
                    elemDaPrendere -= 1
                else:
                    self.__rawPut(T, i)
                    self.__attendi_shift(t, i)
            return retList

    def cambiaverso(self):
        with self.lock:
            self.verso = -self.verso
            self.condition.notify_all()

class NastroRotante(Thread):

    def __init__(self, d: RunningSushiBuffer):
        super().__init__()
        self.iterazioni = 10000
        self.d = d

    def run(self):
        while (self.iterazioni > 0):
            sleep(0.1)
            self.iterazioni -= 1
            self.d.shift()

class Cuoco(Thread):
    piatti = ["*", ";", "^", "%", "!", "@"]

    def __init__(self, nastro_A: RunningSushiBuffer, nastro_B: RunningSushiBuffer):
        super().__init__()
        self.iterazioni = 1000
        self.nastro_A = nastro_A
        self.nastro_B = nastro_B

    def run(self):
        while (self.iterazioni > 0):
            sleep(0.5 * random.random())
            self.iterazioni -= 1
            randPiatto = random.choice(self.piatti)
            self.nastro_A.put(randPiatto)  # Metti sul nastro A
            self.nastro_B.put(randPiatto)  # Metti sul nastro B
            dprint(f"Il cuoco {self.ident} ha cucinato un ottimo <{randPiatto}> su entrambi i nastri")

class Cliente(Thread):

    def __init__(self, nastro_A: RunningSushiBuffer, nastro_B: RunningSushiBuffer, pos: int):
        super().__init__()
        self.quantitaCheVoglioMangiare = random.randint(1, 20)
        self.nastro_A = nastro_A
        self.nastro_B = nastro_B
        self.pos = pos

    def run(self):
        while (self.quantitaCheVoglioMangiare > 0):
            sleep(5 * random.random())
            self.quantitaCheVoglioMangiare -= 1
            try:
                if random.choice([True, False]):
                    cibo = self.nastro_A.get(self.pos)
                else:
                    cibo = self.nastro_B.get(self.pos)
                dprint(f"Il cliente {self.ident} mangia con gusto del <{cibo}>")
            except ValueError:
                dprint(f"Il cliente {self.ident} non può prendere cibo dalla posizione riservata")
        dprint(f"Il cliente {self.ident} ha la pancia piena e va via")

class GruppoClienti(Thread):

    def __init__(self, nastro_A: RunningSushiBuffer, nastro_B: RunningSushiBuffer, pos: int, numClienti: int):
        super().__init__()
        self.numClienti = numClienti
        self.quantitaCheVogliamoMangiare = random.randint(1, 20)
        self.cosaCheNonVogliamoMangiare = random.choice(Cuoco.piatti)
        self.nastro_A = nastro_A
        self.nastro_B = nastro_B
        self.pos = pos

    def run(self):
        while (self.quantitaCheVogliamoMangiare > 0):
            sleep(5 * random.random())
            self.quantitaCheVogliamoMangiare -= self.numClienti
            dprint(f"Il gruppo clienti {self.ident} aspetta cibo")
            dprint(
                f"Il gruppo clienti {self.ident} mangia con gusto dei <{self.nastro_A.getList(self.numClienti, self.cosaCheNonVogliamoMangiare, self.pos)}>")

class Monitor (Thread):
    def __init__(self, d: RunningSushiBuffer):
        super().__init__()
        self.d = d

    def run(self):
        while True:
            sleep(2)

            with plock:
                print("\nStato attuale del buffer:")
                print(f"Direzione attuale: {'orario' if self.d.verso == 1 else 'antiorario'}")
                for i in range(0, self.d.dim):
                    print(f"{i} -> {self.d.theBuffer[i]}")

                print("\n")
                self.d.cambiaverso()

size = 20
nastro_A = RunningSushiBuffer(size)
nastro_B = RunningSushiBuffer(size)

NastroRotante(nastro_A).start()
NastroRotante(nastro_B).start()

Monitor(nastro_A).start()
Monitor(nastro_B).start()

for i in range(0, 2):
    Cuoco(nastro_A, nastro_B).start()

for i in range(1, 10):
    Cliente(nastro_A, nastro_B, i).start()

for i in range(10, 20):
    GruppoClienti(nastro_A, nastro_B, i, random.randint(2, 5)).start()
