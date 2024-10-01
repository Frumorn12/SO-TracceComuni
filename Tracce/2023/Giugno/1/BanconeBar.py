import threading
import random
import time
import string


#
#   BANCONE DEL BAR
#
#   Questo codice simula il workflow tipico dell'arrivo dei clienti in un bar
#   e la loro gestione da parte del barista.
#
#   Il bancone del bar Ã¨ rappresentato da un vettore di liste, dove ogni lista
#   rappresenta una "colonna" del bancone e cioÃ¨ un certo numero di clienti che si accodano sulla stessa fila
#   Ogni colonna puÃ² contenere al massimo
#   un numero di elementi pari al numero di "righe" del bancone.
#
#   I clienti che arrivano al bar vengono inseriti in una delle colonne del bancone
#   tra quelle che hanno meno elementi. Se ci sono piÃ¹ colonne con lo stesso
#   numero minimo di elementi, viene scelta una di queste a caso. Se il bancone Ã¨ pieno,
#   la procedura di inserimento viene messa in attesa.
#
#   Il barista, quando Ã¨ libero, prende un cliente a caso che trova sulla fila 0
#   e lo serve.  Se non ci sono clienti, la procedura di estrazione viene posta in attesa.
#
#  Ad esempio, lo stato del bancone in un certo momento potrebbe essere:
#
#   OOOOO
#   OO-OO
#   OO--O
#   -O--O
#
#  dove O indica che c'Ã¨ un cliente e - indica che la posizione corrispondente Ã¨ vuota. Il barista
#  serve prima i clienti sulla prima riga, scegliendo a caso tra quelli che trova.
#
#  I clienti in arrivo preferiscono accodarsi sulle colonne che hanno meno elementi.
#

class BanconeBar:
    def __init__(self, righe, colonne):
        self.righe = righe
        self.colonne = colonne
        self.bancone = [[] for _ in range(colonne)]
        self.lock = threading.RLock()
        self.ceElemento = threading.Condition(self.lock)
        self.cePostoLibero = threading.Condition(self.lock)


    def __cisonoElementi(self):
        for c in range(self.colonne):
            if len(self.bancone[c]) > 0:
                return True
        return False

    def __tuttoPieno(self):
        for c in range(self.colonne):
            if len(self.bancone[c]) < self.righe:
                return False
        return True

    def __getIndiciFilaPiuCorta(self):
        minimo = len(self.bancone[0])
        for i in range(1, self.colonne):
            if len(self.bancone[i]) < minimo:
                minimo = len(self.bancone[i])
        return [i for i in range(self.colonne) if len(self.bancone[i]) == minimo]

    def get(self):
        with self.lock:
            while not self.__cisonoElementi():
                self.ceElemento.wait()


            indici_non_nulli = [i for i in range(self.colonne) if len(self.bancone[i]) > 0] # indici non nulli della prima riga del bancone

            count = sum(1 for i in indici_non_nulli if "*" in self.bancone[i][0])

            tuttiAnonimi = all("*" in self.bancone[i][0] for i in indici_non_nulli)

            if not (count == len(indici_non_nulli) - 1):
                while True:
                    indice_scelto = random.choice(indici_non_nulli)
                    if not ("*" in self.bancone[indice_scelto][0]) or tuttiAnonimi:
                        elemento = self.bancone[indice_scelto].pop(0)
                        self.cePostoLibero.notify_all()
                        return elemento



    def put(self, elemento):
        with self.lock:
            while self.__tuttoPieno():
                self.cePostoLibero.wait()


            randint = random.randint(1, 10)
            if randint == 1:
                self.bancone[random.choice(self.__getIndiciFilaPiuCorta())].append(elemento+"*")
                self.ceElemento.notify_all()
                return




            self.bancone[random.choice(self.__getIndiciFilaPiuCorta())].append(elemento)
            self.ceElemento.notify_all()

    def print_bancone(self):
        with self.lock:
            for r in range(self.righe):
                for c in range(self.colonne):
                    toPrint = self.bancone[c][r] if len(self.bancone[c]) >= r + 1 else '-'
                    print(toPrint, end='')
                print()

    def miglioraPosizione(self, r, c):
        with self.lock:
            if self.colonne == 1:
                return

            if len(self.bancone[c]) <= r:
                return


            if c - 1 >= 0 and len(self.bancone[c - 1]) + 1 < len(self.bancone[c]):
                self.bancone[c - 1].append(self.bancone[c].pop(r))

            if c + 1 < self.colonne and len(self.bancone[c + 1]) + 1 < len(self.bancone[c]):
                self.bancone[c + 1].append(self.bancone[c].pop(r))


    def checkIfElementoIsInBancone(self, E):
        with self.lock:
            for c in range(self.colonne):
                for r in range(len(self.bancone[c])):
                    if E in self.bancone[c][r]:
                        return True
            return False # non ho trovato l'elemento E nel bancone del bar (E non è più in coda) quindi ritorno False
    def attendiServizio(self, E):
        with self.lock:
            if not self.checkIfElementoIsInBancone(E):
                return False

            while True:
                # se nella riga 0 c'`e e ok altrimenti sto in wait
                if self.checkIfElementoIsInBancone(E):
                    self.cePostoLibero.wait() # aspetto che il barista serva il cliente E
                else:
                    return True








def prendi_elementi(bancone):
    while True:
        elemento = bancone.get()
        print("Elemento prelevato:", elemento)
        time.sleep(1)  # Simula un tempo di elaborazione


def inserisci_elementi(bancone):
    while True:
        elemento = random.choice(string.ascii_uppercase)
        bancone.put(elemento)
        print("Elemento inserito:", elemento)
        time.sleep(0.5)  # Simula un tempo di elaborazione


def stampa_bancone(bancone):
    while True:
        bancone.print_bancone()
        time.sleep(1)


bancone = BanconeBar(7, 5)

#
# Un modo diverso per creare i thread senza dovere dichiarare una classe a parte,
# consiste nel passare come target una funzione che si vuole eseguire al posto del metodo run
#
thread_barista = threading.Thread(target=prendi_elementi, args=(bancone,))
thread_barista.start()

thread_creaClienti = threading.Thread(target=inserisci_elementi, args=(bancone,))
thread_creaClienti.start()

thread_stampab = threading.Thread(target=stampa_bancone, args=(bancone,))
thread_stampab.start()
