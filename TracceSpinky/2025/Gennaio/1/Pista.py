import random
import time
from threading import *

# Lunghezza pista
K = 100
# Posizione del traguardo
T = 98

# Direzioni
sinistra = 0
destra = 1
alto = 2
basso = 3

spostamenti = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def lettera(num_giocatore):
    return chr(ord('A') + num_giocatore) if num_giocatore >= 0 else "Nessuno"


class Pista:
    def __init__(self, numGiocatori):
        self.pista = [[' ' for _ in range(K + 1)] for _ in range(6)]
        self.fillpista(self.pista[0], '#')
        self.fillpista(self.pista[5], '#')
        for i in range(1, 5):
            self.pista[i][T] = '|'
        self.giocatore_di_turno = -1
        self.mosseDisponibili = 0
        self.numGiocatori = numGiocatori
        self.posizioneX = [0] * numGiocatori
        self.posizioneY = [0] * numGiocatori
        self.lock = Lock()
        self.condition_wait_turno = Condition(self.lock)
        self.prossimo_turno = 0
        self.arrivi = []

        for i in range(numGiocatori):
            self.posizioneX[i] = i // 2
            self.posizioneY[i] = 2 + i % 2
            self.pista[self.posizioneY[i]][self.posizioneX[i]] = lettera(i)

        self.cars = [Automobile(i, self) for i in range(PLAYERS)]
        for car in self.cars:
            car.start()

    def fillpista(self, l, c):
        for i in range(K):
            l[i] = c

    def leggi(self, dir):
        with self.lock:
            if self.giocatore_di_turno < 0:
                return None, 0
            (dx, dy) = spostamenti[dir]
            X = self.posizioneX[self.giocatore_di_turno] + dx
            Y = self.posizioneY[self.giocatore_di_turno] + dy
            dist = 0
            while 0 <= Y < 6 and 0 <= X <= K and self.pista[Y][X] == ' ':
                dist += 1
                X += dx
                Y += dy
            return self.pista[Y][X] if 0 <= Y < 6 and 0 <= X <= K else '#', dist

    def prendi_e_lancia_dado(self, g):
        with self.lock:
            while self.giocatore_di_turno != -1 or g != self.prossimo_turno:
                self.condition_wait_turno.wait()
            self.giocatore_di_turno = g
            self.mosseDisponibili = random.randint(1, 3)
            self.visualizza()
            return self.mosseDisponibili

    def muovi(self, dir):
        with self.lock:
            self.mosseDisponibili -= 1
            (dx, dy) = spostamenti[dir]
            X = self.posizioneX[self.giocatore_di_turno]
            Y = self.posizioneY[self.giocatore_di_turno]

            if self.pista[Y + dy][X + dx] != ' ':
                if self.pista[Y + dy][X + dx] == '|':
                    if self.giocatore_di_turno not in self.arrivi:
                        self.arrivi.append(self.giocatore_di_turno)
                self.mosseDisponibili = 0
            else:
                self.pista[Y + dy][X + dx] = self.pista[Y][X]
                # Tenta di lasciare un ostacolo dietro
                if 0 <= X - dx <= K and 0 <= Y - dy < 6 and self.pista[Y - dy][X - dx] == ' ':
                    if random.random() < 0.5:
                        self.pista[Y - dy][X - dx] = '.'
                    else:
                        self.pista[Y][X] = ' '
                else:
                    self.pista[Y][X] = ' '
                self.posizioneX[self.giocatore_di_turno] = X + dx
                self.posizioneY[self.giocatore_di_turno] = Y + dy

            if self.mosseDisponibili == 0:
                self.prossimo_turno = (self.giocatore_di_turno + 1) % self.numGiocatori
                self.giocatore_di_turno = -1
                self.condition_wait_turno.notify_all()
                self.visualizza()
                return False
            return True

    def get_vincitore(self):
        with self.lock:
            return self.arrivi[0] if self.arrivi else -1

    def visualizza(self):
        with self.lock:
            print("\033[H\033[J")
            for i in range(6):
                print(''.join(self.pista[i]))
            if self.arrivi:
                print(f"Vincitore provvisorio: {lettera(self.arrivi[0])}")


class Automobile(Thread):
    def __init__(self, n, p):
        super().__init__()
        self.nt = n
        self.p = p

    def pensa(self):
        c, dist = self.p.leggi(destra)
        if c == '|' or dist > 0:
            return destra
        c, dist = self.p.leggi(alto)
        if dist > 0:
            return alto
        c, dist = self.p.leggi(basso)
        if dist > 0:
            return basso
        return -1

    def run(self):
        while len(self.p.arrivi) < self.p.numGiocatori:
            if penalizzatore.è_bloccato(self.nt):
                time.sleep(0.1)
                continue
            mosse = self.p.prendi_e_lancia_dado(self.nt)
            while True:
                direzione = self.pensa()
                if direzione == -1 or not self.p.muovi(direzione):
                    break
            time.sleep(1)


class Penalizzatore(Thread):
    def __init__(self, p):
        super().__init__()
        self.p = p
        self.bloccati = set()
        self.lock_blocco = Lock()

    def run(self):
        while len(self.p.arrivi) < self.p.numGiocatori:
            time.sleep(5)
            with self.lock_blocco:
                g = random.randint(0, self.p.numGiocatori - 1)
                print(f"\n🚫 Auto {lettera(g)} penalizzata per 3 secondi")
                self.bloccati.add(g)
            time.sleep(3)
            with self.lock_blocco:
                self.bloccati.discard(g)

    def è_bloccato(self, g):
        with self.lock_blocco:
            return g in self.bloccati


# Main
PLAYERS = 6
print("Starting Game...")
p = Pista(PLAYERS)
penalizzatore = Penalizzatore(p)
penalizzatore.start()

for car in p.cars:
    car.join()

print("\n ORDINE D'ARRIVO:")
for pos, g in enumerate(p.arrivi):
    print(f"{pos+1}° - {lettera(g)}")