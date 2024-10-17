from queue import Queue
from random import randint
from threading import Condition, RLock, Thread
import time

pizze = {"margherita": "(.)",
         "capricciosa": "(*)",
         "diavola": "(@)",
         "ananas": "(,)"}


class Tavolo:
    def __init__(self):
        self.posti = [False for i in range(10)] # False = libero, True = occupato
        self.tempo_per_sparecchiare = [-1 for i in range(10)]  # -1 = libero, 0 = occupato
        self.pizze = ["" for i in range(10)]
        self.lock = RLock()

    def occupa(self, pizza):
        with self.lock:
            for i in range(10):
                if not self.posti[i]:
                    self.posti[i] = True
                    self.tempo_per_sparecchiare[i] = time.time()  # tempo di occupazione, dopo 3 secondi puo essere sparecchiato
                    self.pizze[i] = pizza # pizza occupata
                    return i
            return -1

    def sparecchia(self, i):
        with self.lock:
            for i in range(10):
                if self.posti[i]:
                    if time.time() - self.tempo_per_sparechhiare[i] > 3:
                        self.posti[i] = False
                        self.tempo_per_sparecchiare[i] = -1
                        print ("Il posto %d con la pizza %c e stato sparecchiato" % (i, self.pizze[i])) # pizza occupata
                        self.pizze[i] = ""
                        return i
                    else :
                        print ("Il posto %d non puo essere sparecchiato" % i)


class Sala:
    def __init__(self, num_tavoli):
        self.tavoli = [Tavolo() for i in range(num_tavoli)]
        self.lock = RLock()






class Ristorante:
    def __init__(self, pizzeria, sala):
        self.pizzeria = pizzeria
        self.sala = sala




class Ordine:
    nextCodiceOrdine = 0

    def __init__(self, tipoPizza, quantita):
        self.tipoPizza = tipoPizza
        self.quantita = quantita
        self.codiceOrdine = Ordine.nextCodiceOrdine
        self.pizzePronte = ""
        Ordine.nextCodiceOrdine += 1

    def prepara(self):
        for i in range(self.quantita):
            self.pizzePronte += pizze[self.tipoPizza]


class BlockingSet(set):

    def __init__(self, size=10):
        super().__init__()
        self.size = size
        self.lock = RLock()
        self.condition = Condition(self.lock)

    def add(self, T):
        with self.lock:
            while len(self) == self.size:
                self.condition.wait()
            self.condition.notify_all()
            return super().add(T)

    def remove(self, T):
        with self.lock:
            while not T in self:
                self.condition.wait()
            super().remove(T)
            self.condition.notify_all()
            return True


class Pizzeria:

    def __init__(self):
        self.BO = Queue(10)
        self.BP = BlockingSet()

    def getOrdine(self):
        return self.BO.get()

    def putOrdine(self, codicePizza, quantita):
        ordine = Ordine(codicePizza, quantita)
        self.BO.put(ordine)
        return ordine

    def getPizze(self, ordine):
        self.BP.remove(ordine)

    def putPizze(self, ordine):
        self.BP.add(ordine)


class Pizzaiolo(Thread):

    def __init__(self, name, pizzeria):
        super().__init__()
        self.name = name
        self.pizzeria = pizzeria

    def run(self):
        while True:
            ordine = self.pizzeria.getOrdine()
            tempoDiPreparazione = ordine.quantita
            time.sleep(tempoDiPreparazione)
            ordine.prepara()
            self.pizzeria.putPizze(ordine)
            #
            #  Sigaretta...
            #
            time.sleep(randint(1, 3))

"""
class Cliente(Thread):
    def __init__(self, name, pizzeria):
        super().__init__()
        self.name = name
        self.pizzeria = pizzeria

    def run(self):
        while True:
            numeroPizze = 1 + randint(0, 7)
            tipiPizza = list(pizze.keys())
            codicePizza = tipiPizza[randint(0, len(tipiPizza) - 1)]

            print(f"Il cliente {self.name} entra in pizzeria e prova ad ordinare delle pizze")
            ordine = self.pizzeria.putOrdine(codicePizza, numeroPizze)
            print(f"Il cliente {self.name} aspetta le pizze con codice d'ordine numero {ordine.codiceOrdine}")

            time.sleep(randint(0, numeroPizze))

            self.pizzeria.getPizze(ordine)

            print(f"Il cliente {self.name} ha preso le pizze con codice d'ordine numero {ordine.codiceOrdine}")
            print(ordine.pizzePronte)
            #
            # Prima o poi mi tornerÃ  fame
            #
            time.sleep(randint(0, numeroPizze))
"""

def main():
    NUMP = 3
    NUMC = 20
    p = []
    c = []
    pizzeria = Pizzeria()

    for i in range(0, NUMP):
        pizzaiolo = Pizzaiolo("Totonno_" + str(i), pizzeria)
        p.append(pizzaiolo)
        pizzaiolo.start()
    """
    for i in range(0, NUMC):
        cliente = Cliente("Ciro_" + str(i), pizzeria)
        c.append(cliente)
        cliente.start()
    """

if __name__ == '__main__':
    main()

