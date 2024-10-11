from threading import Thread, Lock, Condition
from os import system
import random
import time
import string  # Per generare stringhe casuali

# Dimensione della griglia
dimensione_griglia = 25

dX = {"nord": 0, "sud": 0, "est": 1, "ovest": -1}
dY = {"nord": -1, "sud": 1, "est": 0, "ovest": 0}


debug = False

class PlayerData:

    def __init__(self, id, game, lettera):
        self.id = id
        self.game = game
        self.lock = Lock()
        self.x = random.randint(0, game.dim - 1)
        self.y = random.randint(0, game.dim - 1)
        self.vivo = True
        self.lettera = lettera

    def muovi(self, direzione):
        with self.lock:
            nuovo_x = self.x + dX[direzione]
            nuovo_y = self.y + dY[direzione]

            # Verifica se il nuovo punto è all'interno della griglia e non contiene un '*'
            if 0 <= nuovo_x < self.game.dim and 0 <= nuovo_y < self.game.dim and self.game.griglia[nuovo_x][nuovo_y] != '*':

                # Verifica se c'è un altro giocatore in quella posizione
                giocatore_b = self.game.trova_giocatore_in_posizione(nuovo_x, nuovo_y)
                if giocatore_b is not None:
                    # Elimina l'altro giocatore
                    giocatore_b.vivo = False
                    self.game.dprint(f"Giocatore {self.id} ha eliminato Giocatore {giocatore_b.id}", True)
                    self.game.griglia[giocatore_b.x][giocatore_b.y] = '*'  # Segna la posizione come 'morta'

                # Sposta il giocatore nella nuova posizione
                self.x = nuovo_x
                self.y = nuovo_y
                self.game.dprint(f"Giocatore {self.id} si è mosso in posizione ({self.x}, {self.y})")
            else:
                # Vedo se * è dentro la griglia
                if 0 <= nuovo_x < self.game.dim and 0 <= nuovo_y < self.game.dim:
                    self.game.dprint(f"Giocatore {self.id} ha cercato di muoversi su '*', movimento negato.")
                else:
                    return False
            return self.vivo


class Giocatore(Thread):
    def __init__(self, id, game):
        super().__init__()
        self.id = id
        self.game = game

    def run(self):
        while self.compie_azione() and self.game.inGioco():  # Punto 3
            time.sleep(2)

    def compie_azione(self):
        if not self.game.datiGiocatori[self.id].vivo:  # Controlla se il giocatore è vivo
            return False
        direzione = random.choice(list(dX.keys()))
        return self.game.muovi(self.id, direzione)


class GridGame:
    maxStampe = 5

    def __init__(self, dim, nplayers, durata_max=None):
        self.durata_max = durata_max  # Durata massima della partita
        self.inizo = time.time()
        self.dim = dim
        self.codaStampeLock = Lock()
        self.codaStampe = []
        self.nplayers = nplayers
        self.alfabeto = list(string.ascii_uppercase + string.ascii_lowercase)  # Genero l'alfabeto
        self.datiGiocatori = [PlayerData(i, self, self.alfabeto[i]) for i in range(nplayers)]
        self.griglia = [[None for _ in range(dim)] for _ in range(dim)]  # Griglia di gioco

        # Avvia i thread dei giocatori
        self.threadGiocatori = [Giocatore(i, self) for i in range(nplayers)]
        for t in self.threadGiocatori:
            t.start()


        self.restringiMappa = RestringiMappa(self, 5)
        self.restringiMappa.start()  # Punto 6
        self.stampaMappa = StampaMappa(self)
        self.stampaMappa.start()

    def inGioco(self):

        if self.checkOnlyOnePlayerLive(): return False # Punto 5
        if self.durata_max is not None :
            return time.time() - self.inizo < self.durata_max
        else:
            return True

    def trova_giocatore_in_posizione(self, x, y):
        for giocatore in self.datiGiocatori:
            if giocatore.vivo and giocatore.x == x and giocatore.y == y:
                return giocatore
        return None

    #
    # Metodo per muovere uno specifico giocatore in una direzione specificata
    #
    def muovi(self, player, direzione):
        return self.datiGiocatori[player].muovi(direzione)

    #
    # Metodo per prendere il lock su tutti i PlayerData e poter stampare la mappa senza race condition
    #
    def lockAllPlayers(self):
        for player in self.datiGiocatori:
            player.lock.acquire()

    #
    # Metodo per rilasciare il lock su tutti i PlayerData
    #
    def unlockAllPlayers(self):
        for player in self.datiGiocatori:
            player.lock.release()

    #
    #  Metodo per inviare messaggi di debug che vengono stampati dal thread visualizzatore nell'ordine in cui arrivano
    #  Da notare che le stampe più vecchie vengono via via rimosse quando la coda delle stampe supera il valore massimo impostato
    #
    def dprint(self, string, priorita=False):

        with self.codaStampeLock:
            if priorita:
                print(f"'\x1b[31m' DEBUG: {string} ")  # Stampa il messaggio di debug
                return
            self.codaStampe.append(string)
            if len(self.codaStampe) > self.maxStampe:
                self.codaStampe.pop(0)

    def printCodaStampe(self):
        with self.codaStampeLock:
            for p in self.codaStampe:
                print('\x1b[30m' + p)

    def checkOnlyOnePlayerLive(self):
        count = 0
        for p in self.datiGiocatori:
            if p.vivo:
                count += 1
        return count == 1

    def restringi_mappa(self):
        """Restringe la mappa eliminando i bordi e uccidendo i giocatori fuori dalla nuova area."""
        self.lockAllPlayers()
        # Riduci i bordi della griglia
        if self.dim > 2:  # Assicura che ci sia una griglia riducibile
            self.dprint(f"Restringo la mappa. Nuove dimensioni: {self.dim - 2}x{self.dim - 2}", True)
            # Controlla se qualche giocatore è sui bordi e uccidilo
            for giocatore in self.datiGiocatori:
                if giocatore.vivo and (
                        giocatore.x == 0 or giocatore.x == self.dim - 1 or giocatore.y == 0 or giocatore.y == self.dim - 1):
                    giocatore.vivo = False
                    self.dprint(f"Giocatore {giocatore.id} è stato eliminato durante il restringimento", True)

            # Aggiorna le dimensioni della griglia
            self.dim -= 2

        self.unlockAllPlayers()


#
# Thread per la stampa periodica della mappa
#
class StampaMappa(Thread):

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.griglia = [[None for _ in range(game.dim)] for _ in range(game.dim)]

    def run(self):
        iterazioni = 0
        while self.game.inGioco():  # Punto 3
            system('clear')
            print ('\x1b[30m')
            self.game.lockAllPlayers()
            for p in self.game.datiGiocatori:
                if p.vivo:
                    # Solo giocatori vivi

                    # Checko se x e y sono all'interno della griglia
                    if 0 <= p.x < self.game.dim and 0 <= p.y < self.game.dim:
                        self.griglia[p.x][p.y] = p.lettera
                else:
                    # Checko se x e y sono all'interno della griglia
                    if 0 <= p.x < self.game.dim and 0 <= p.y < self.game.dim:
                        self.griglia[p.x][p.y] = '*'
            for riga in self.griglia:
                print("".join([c if c is not None else "." for c in riga]))
            self.griglia = [[None for _ in range(self.game.dim)] for _ in range(self.game.dim)]
            self.game.unlockAllPlayers()
            iterazioni += 1
            print(f"ITER: {iterazioni}")
            self.game.printCodaStampe()
            time.sleep(1)
        self.game.dprint("Il gioco è terminato", True)



class RestringiMappa(Thread):
    def __init__(self, game, intervallo):
        super().__init__()
        self.game = game
        self.intervallo = intervallo

    def run(self):
        while self.game.inGioco():
            time.sleep(self.intervallo)
            self.game.restringi_mappa()


if __name__ == "__main__":
    # Crea una partita su una griglia di lato 25 con 10 giocatori
    the_game = GridGame(dimensione_griglia, 10)
