from threading import Thread, RLock, Condition, get_ident
from time import sleep
from random import random, randint


class PivotBlockingQueue:
    def __init__(self, dim):
        self.dim = dim
        self.buffer = []
        self.criterio = True
        self.pivotNumber = 1  # Numero di pivot da rimuovere
        self.lock = RLock()
        self.condNewElement = Condition(self.lock)

    def take(self) -> int:
        with self.lock:
            while len(self.buffer) < self.pivotNumber + 1:
                self.condNewElement.wait()

            for _ in range(self.pivotNumber):
                self.__removePivot__()

            return self.buffer.pop(0)

    def doubleTake(self) -> tuple:
        with self.lock:
            while len(self.buffer) < self.pivotNumber + 2:
                self.condNewElement.wait()

            for _ in range(self.pivotNumber):
                self.__removePivot__()

            first_element = self.buffer.pop(0)
            second_element = self.buffer.pop(0)

            return first_element, second_element

    def put(self, v: int):
        with self.lock:
            if len(self.buffer) == self.dim:
                self.__removePivot__()
            self.buffer.append(v)
            if len(self.buffer) >= self.pivotNumber + 1:
                self.condNewElement.notify()

    def setCriterioPivot(self, minMax: bool):
        with self.lock:
            self.criterio = minMax

    def setPivotNumber(self, n: int):
        with self.lock:
            if 1 <= n <= self.dim - 1:
                self.pivotNumber = n
            else:
                raise ValueError("Il numero di pivot deve essere compreso tra 1 e N-1.")

    def waitFor(self, n: int):
        with self.lock:
            # Attende finché la somma degli elementi della coda non supera n
            while sum(self.buffer) <= n:
                self.condNewElement.wait()
            # Uscita automatica quando la somma supera n

    def __migliore__(self, a: int, b: int) -> bool:
        return a < b if self.criterio else a > b

    def __removePivot__(self):
        pivot = self.buffer[0]
        pivotMultipli = False
        for i in range(1, len(self.buffer)):
            if self.__migliore__(self.buffer[i], pivot):
                pivot = self.buffer[i]
                pivotMultipli = False
            elif self.buffer[i] == pivot:
                pivotMultipli = True

        self.buffer.remove(pivot) if not pivotMultipli else self.buffer.pop()


'''
    Thread di test
'''


class Operator(Thread):
    def __init__(self, c):
        super().__init__()
        self.coda = c

    def run(self):
        for i in range(1000):
            sleep(random())
            self.coda.put(randint(-100, 100))
            self.coda.put(randint(-100, 100))
            sleep(random())
            if len(self.coda.buffer) >= 4:
                print(f"Il thread TID={get_ident()} ha estratto la coppia {self.coda.doubleTake()}")
            else:
                print(f"Il thread TID={get_ident()} ha estratto il valore {self.coda.take()}")
            # Esempio di attesa con waitFor
            self.coda.waitFor(50)
            print(f"Il thread TID={get_ident()} ha atteso che la somma degli elementi superasse 50")


if __name__ == '__main__':
    coda = PivotBlockingQueue(10)
    coda.setPivotNumber(2)  # Imposta il numero di pivot a 2
    operatori = [Operator(coda) for i in range(50)]
    for o in operatori:
        o.start()
