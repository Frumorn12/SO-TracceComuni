import threading
import random
from asyncio import sleep

"""
Punto 1.

Come primo punto, modifica ogni VasettoDiMiele in maniera da ottimizzare l’uso delle condition e non risvegliare
inutilmente più thread del necessario. In particolare, rimuovi la condition esistente e introduci una
condition_aumento, da usare quando si aspetta che il vasetto aumenti il suo contenuto e una
condition_diminuzione, da usare quando si aspetta che il vasetto diminuisca il suo contenuto. Puoi anche
ottimizzare il codice a tua scelta introducendo più di due condition, se lo ritieni opportuno.

FATTO


Punto 2

Avrai notato che è molto difficile che le mamme orse riescano a rabboccare un vasetto di miele, poiché è necessario che un
vasetto di miele sia completamente vuoto. Per risolvere il problema, fai in modo che quando almeno una mamma orsa è
bloccata all’interno del metodo riempi, nessun papà orso possa aggiungere del miele. Inoltre, quando una mamma orsa
invoca il metodo riempi, ma il vaso è già pieno fino all’orlo, bisogna uscire immediatamente anziché aspettare.
N.B : Non dobbiamo preoccuparci del deadlock. 

Punto 3

Implementa una funzione totaleMiele() che stampa a video la quantità di miele attualmente presente in tutti i
vasetti, e la quantità che è stata finora mangiata da qualcuno. Bonus: osserva che potrebbero esserci delle quantità di
miele temporaneamente fuori dai vasetti, poiché nelle mani di un papà orso nell’intervallo di tempo tra prendi() e
aggiungi(). Puoi fare in modo che totaleMiele() tenga conto anche di queste quantità?

"""


class VasettoDiMiele:
    def __init__(self, indice, capacita):  # Costruttore

        # Capacita max del vasetto
        self.capacita = capacita

        # Miele attuale nel vasetto
        self.miele = capacita

        # Indice del vasetto (per identificarlo)
        self.indice = indice

        # Lock per la sincronizzazione
        self.lock = threading.RLock()

        # Condition per l'attesa bloccante

        #self.condition = threading.Condition(self.lock)
        self.condition_aumento = threading.Condition(self.lock)
        self.condition_diminuzione = threading.Condition(self.lock)

        # PUNTO 2
        self.mamma_orsa_bloccata = False  # Se la mamma orsa è bloccata

        # PUNTO 3
        self.miele_preso = 0  # Miele preso
        self.miele_papa_orso = 0  # Miele preso dai papa orsi

    #
    # Si sblocca solo quando il vasetto Ã¨ totalmente vuoto
    #


    def mieleAggiuntoPapaOrso(self, quantita):
        with self.lock:
            self.miele_papa_orso -= quantita
            print(f"Orso {threading.current_thread().name} ha aggiunto {quantita} unitÃ  di miele al vasetto {self.indice}")


    # Riempie il vasetto
    def riempi(self):
        with self.lock:  # Acquisisce il lock
            # Puoi riempire il vasetto soltanto se è vuoto

            if self.miele == self.capacita:  # Se il vasetto è pieno
                print(f"Il vasetto {self.indice} Ã¨ giÃ  pieno, non posso riempirlo")  # Stampa il messaggio
                return  # Esce dalla funzione

            while self.miele > 0:  # Se il vasetto non è vuoto
                print(
                    f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, aspetto che si svuoti completamente")  # Stampa il messaggio
                self.mamma_orsa_bloccata = True  # La mamma orsa è bloccata
                print(f"La mamma orsa Ã¨ bloccata")
                self.condition_diminuzione.wait()  # Attende che il vasetto si svuoti completamente

            self.mamma_orsa_bloccata = False  # La mamma orsa non è bloccata

            # Appena il vasetto è vuoto, lo riempie di nuovo fino alla sua capacita
            self.miele = self.capacita

            # Notifica tutti i thread in attesa che aspettano di prendere il miele
            self.condition_aumento.notify_all()
            print(f"{threading.current_thread().name} ha rabboccato il vasetto {self.indice}")

    #
    # Preleva del miele dal vasetto
    #

    def prendi(self, quantita):
        with self.lock:
            # Se la quantita di miele richiesta è maggiore di quella presente nel vasetto
            while self.miele < quantita:  # Se la quantita di miele richiesta è maggiore di quella presente nel vasetto
                print(  # Stampa il messaggio
                    f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, non Ã¨ possibile prendere {quantita}. Aspetto che il vasetto venga riempito")
                self.condition_aumento.wait()  # Attende che il vasetto venga riemp
            self.miele -= quantita  # Sottrae la quantita di miele richiesta dal vasetto
            self.miele_preso += quantita  # Aggiunge la quantita di miele preso
            print(
                f"Orsetto {threading.current_thread().name} ha preso {quantita} unitÃ  di miele dal vasetto {self.indice}")  #
            self.condition_diminuzione.notify_all()

    def aggiungi(self, quantita):
        with self.lock:  # Acquisisce il lock
            while self.miele + quantita > self.capacita or self.mamma_orsa_bloccata:  # Se la quantita di miele richiesta è maggiore di quella presente nel vasetto
                print(
                    f"Il vasetto {self.indice} ha {self.miele} unitÃ  di miele, aggiungerne {quantita} supererebbe la capacitÃ  massima di {self.capacita}")

                if self.mamma_orsa_bloccata:
                    print(f"La mamma orsa Ã¨ bloccata, papa orso non puÃ² aggiungere miele")  # Stampa il messaggio
                self.condition_diminuzione.wait()  # Attende che il vasetto venga riempito
            self.miele += quantita  # Aggiunge la quantita di miele richiesta al vasetto
            self.miele_papa_orso += quantita  # Aggiunge la quantita di miele preso dai papa orsi
            print(
                f"Orso {threading.current_thread().name} ha aggiunto {quantita} unitÃ  di miele al vasetto {self.indice}")
            self.condition_aumento.notify_all()  # Notifica tutti i thread in attesa che aspettano di prendere il miele

    def totaleMiele(self):
        with self.lock:


            print(f"Vasetto {self.indice} ha {self.miele} unitÃ  di miele")
            print(f"Vasetto {self.indice} ha {self.miele_preso} unitÃ  di miele preso")
            if self.miele_papa_orso > 0:
                print(f"Vasetto {self.indice} ha {self.miele_papa_orso} unitÃ  di miele preso dai papa orsi")

            # QUI DOVREI STAMPARE L"instanza


class OrsettoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):  # Costruttore
        threading.Thread.__init__(self)  # Inizializza il thread
        self.name = name  # Nome dell'orsetto
        self.vasettiMiele = vasettiMiele  # Vasetti di miele

    def run(self):
        while True:
            vasetto_indice = random.randint(0, len(self.vasettiMiele) - 1)  # Sceglie un vasetto a caso
            quantita = random.randint(1, self.vasettiMiele[
                vasetto_indice].capacita)  # Sceglie una quantita di miele a caso
            self.vasettiMiele[vasetto_indice].prendi(quantita)  # Prende la quantita di miele dal vasetto


class PapaOrsoThread(threading.Thread):
    def __init__(self, name, vasettiMiele):
        threading.Thread.__init__(self)  # Inizializza il thread
        self.name = name  # Nome dell'orsetto
        self.vasettiMiele = vasettiMiele  # Vasetti di miele

    def run(self):
        while True:
            vasetto_indice1 = random.randint(0, len(self.vasettiMiele) - 1)  # Sceglie un vasetto a caso
            vasetto_indice2 = random.randint(0, len(self.vasettiMiele) - 1)  # Sceglie un altro vasetto a caso
            while vasetto_indice1 == vasetto_indice2:  # Se i due vasetti scelti sono uguali
                vasetto_indice2 = random.randint(0, len(self.vasettiMiele) - 1)  # Sceglie un altro vasetto a caso
            quantita = random.randint(1, self.vasettiMiele[
                vasetto_indice1].capacita)  # Sceglie una quantita di miele a caso


            self.vasettiMiele[vasetto_indice1].prendi(quantita)  # Prende la quantita di miele dal vasetto

            self.vasettiMiele[vasetto_indice2].aggiungi(quantita)  # Aggiunge la quantita di miele al vasetto


            self.vasettiMiele[vasetto_indice1].mieleAggiuntoPapaOrso(quantita)
            print(
                f"Papa orso {self.name} ha spostato {quantita} grammi dal vasetto {vasetto_indice1} al vasetto {vasetto_indice2}")  # Stampa il messaggio


class MammaOrsoThread(threading.Thread):  # Classe MammaOrsoThread
    def __init__(self, name, vasettiMiele):  # Costruttore
        threading.Thread.__init__(self)  # Inizializza il thread
        self.name = name  # Nome dell'orsetto
        self.vasettiMiele = vasettiMiele  # Vasetti di miele

    def run(self):  # Metodo run
        while True:  # Ciclo infinito
            vasetto_indice = random.randint(0, len(self.vasettiMiele) - 1)  # Sceglie un vasetto a caso
            self.vasettiMiele[vasetto_indice].riempi()  # Riempie il vasetto
            print(f"Mamma orso {self.name} ha riempito il vasetto {vasetto_indice}")  # Stampa il messaggio


class Display(threading.Thread):
    def __init__(self, vasetti):
        threading.Thread.__init__(self)
        self.vasetti = vasetti

    def run(self):
        while True:
            sleep(50)
            for vasetto in self.vasetti:
                vasetto.totaleMiele()
            print("")


if __name__ == '__main__':
    num_vasetti = 5  # Numero di vasetti
    vasetti = [VasettoDiMiele(i, 50 + 50 * i) for i in range(num_vasetti)]  # Crea i vasetti di miele

    orsetti = [OrsettoThread(f"Winnie-{i}", vasetti) for i in range(5)]  # Crea gli orsetti
    mamme_orse = [MammaOrsoThread(f"Mamma-{i}", vasetti) for i in range(2)]  # Crea le mammine
    papa_orso = [PapaOrsoThread(f"Babbo-{i}", vasetti) for i in range(3)]  # Crea i papa orsi

    for orsetto in orsetti:
        orsetto.start()

    for orsa in mamme_orse:
        orsa.start()

    for orso in papa_orso:
        orso.start()

    display = Display(vasetti)
    display.start()
