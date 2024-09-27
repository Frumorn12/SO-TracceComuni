"""
Programma:

Abbiamo un ponte ad una sola corsia,
congiunge MARE E MONTAGNA

Gli abitanti del MARE vanno in montagna
Mentre gli abitanti della MONTAGNA vanno al MARE


1. se sul PONTE stanno viaggiando turisti che dal MARE vanno in MONTAGNA, il ponte non può essere attraversato
   nell’altra direzione (e viceversa), ma può essere attraversato in contemporanea da altri turisti che vengono
   dal MARE (e viceversa);
2. si può considerare la capacità del PONTE infinita: un TURISTA che si trova in prossimità del PONTE
   controlla se la direzione di percorrenza è congruente con la propria, se questo accade allora il turista
   si accinge ad attraversalo, altrimenti aspetta, indipendentemente dalla capienza del ponte;

3. i turisti in attesa alle estremità del ponte possono accedere al ponte (una volta che questo sia accessibile)
   in qualsiasi ordine, non necessariamente nell’ordine di arrivo.

Possibili estensioni:
●   Si riscriva la classe PONTE in modo tale da evitare la starvation
    (e.g. impedire che il passaggio continuo di auto provenienti da
    MARE blocchi indefinitamente l’accesso alle
    auto provenienti da MONTAGNA);
●   Si modelli un ponte che consente un numero massimo N di automobili al suo interno
    (il tentativo di ingresso dell’automobile N+1-esima deve bloccare quest’ultima)
●   Si modifichi la classe in maniera tale che l’ordine di ingresso al ponte sia lo stesso dell’ordine di
    arrivo (le automobili devono effettivamente entrare sul ponte nell’ordine temporale in
    cui hanno cercato di prendere il “lock” sul ponte)
●   Si modifichi la classe in maniera tale che l’ordine di uscita dal ponte sia lo stesso
    dell’ordine di ingresso
    (le automobili devono uscire nell’ordine temporale in cui hanno
    precedentemente acquisito il “lock” sul ponte)
"""


from threading import Thread,RLock,Condition
from time import sleep
from random import randint,random


nomiDirezione = ["MARE","MONTAGNA"]


def opposta(direzione_corrente: int) -> int:
    return (direzione_corrente + 1) % 2

class Ponte:
    MARE = 0
    MONTAGNA = 1

    def __init__(self):
        self.direzione_corrente = self.MARE #Variabile che indica la direzione
        self.turisti = 0; #Variabile che indica il numero di turisti sul ponte, serve per il punto 3 delle estensioni

        self.lock = RLock() #Lock per la mutua esclusione
        self.cond = Condition(self.lock)

        # Qui gestiamo con queste variabili la starvation
        self.turisti_in_attesa = [0,0]
        self.turisti_in_attesa_corrente = 0
        self.turisti_numero_dir_corrente = 0
        self.sogliaMax = 3 #Soglia massima di turisti che possono passare in una direzione prima di dare la precedenza all'altra


    def attraversa(self,direzione: int, turista: int):
        with self.lock:
            while (self.direzione_corrente != direzione and self.turisti > 0) or (self.direzione_corrente == direzione and self.turisti_numero_dir_corrente >= self.sogliaMax and self.turisti_in_attesa[opposta(direzione)] > 0):

                self.cond.wait()

            self.turisti_in_attesa[direzione] -= 1

            if self.direzione_corrente != direzione:
                self.direzione_corrente = direzione
                self.turisti_numero_dir_corrente = 0

            self.turisti += 1
            self.turisti_numero_dir_corrente += 1
            print(f"Turista {turista} attraversa il ponte in direzione {nomiDirezione[direzione]}")

    def fine_tragitto(self, turista: int):
        with self.lock:
            self.turisti -= 1
            print(f"Turista {turista} ha finito il tragitto")
            if self.turisti == 0:
                self.cond.notify_all()



class Turista(Thread):
    def __init__(self, ponte,  turista: int):
        super().__init__()
        self.ponte = ponte
        self.direzione = randint(0,1)
        self.turista = turista

    def run(self):
        self.ponte.attraversa(self.direzione, self.turista)
        sleep(random())
        self.ponte.fine_tragitto(self.turista)




def main():
    p = Ponte()
    turisti = [Turista(p,i) for i in range(50)]
    for t in turisti:
        t.start()


main ()