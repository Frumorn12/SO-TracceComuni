from threading import Thread, Lock, Condition
from time import sleep
from random import random, randrange

'''
    Soluzione commentata esercizio sul gioco delle sedie. 
    In questo sorgente potete sperimentare con tre possibili soluzioni: soluzione A senza lock (sbagliata), soluzione B con i lock ma usati male (sbagliata), soluzione C con i lock usati bene (corretta)

    Soluzione A:
        - Fatta creando un array di PostoUnsafe e usando come thread PartecipanteUnsafe

        In questa soluzione non viene usata alcuna forma di locking. Facendo girare il gioco piÃ¹ volte, riscontrerete che a volte tutti i Partecipanti riescono a sedersi, 
        poichÃ¨ qualcuno si siede sulla stessa sedia

    Soluzione B:
        - Fatta creando un array di PostoQuasiSafe e usando come thread PartecipanteUnSafe

        Questa soluzione ha lo stesso problema della soluzione A. 
        Anche se libero() e set() sono, prese singolarmente, thread-safe, queste vengono chiamate in due tempi distinti (PRIMO TEMPO: chiamata a libero; SECONDO TEMPO: chiamata a set() ), acquisendo e rilasciando il lock entrambe le volte. 
        In mezzo ai due tempi, eventuali altri partecipanti avranno la possibilitÃ  di acquisire il lock su self.posti[i] e modificarne lo stato. Noi non vogliamo questo. E' una race condition.


    Soluzione C:
        - Fatta usando un array di PostoSafe e usando come thread PartecipanteSafe

'''

'''
1) -Un “Campionato” è costituito da 5 round del gioco delle sedie. Il partecipante che perde in un round non può partecipare al successivo. Nel
gioco ci sono almeno 6 partecipanti. Scrivi tutto il codice necessario a gestire un intero Campionato e dichiararne il vincitore;


2)-Ogni partita del gioco delle sedie dura T secondi. La durata T della partita deve poter essere scelta prima dell’avvio della partita; ogni
partecipante può cambiare sedia nell’arco della durata della partita (ma è vietato occupare due sedie contemporaneamente). A ogni sedia
corrisponde un punteggio pari al proprio indice: ad esempio la sedia 1 vale 1 punto, la sedia 5 vale 5 punti, ecc. Vince il partecipante che si
siede sulla sedia di punteggio maggiore

3)Le partite sono a squadre di tre partecipanti. La squadra che si ritrova con un componente che non è riuscito a sedersi è quella che perde
complessivamente



'''

class Campionato:
    def __init__(self, partecipanti, posti):
        self.partecipanti = partecipanti
        self.posti = posti

    def iniziaCampionato(self):
        for i in range(0, 5):
            print("Inizia il round %d" % i)
            if i == 0:
                self.initThread()
            if i != 0:
                self.ripristinaPartecipanti()
            while not self.finitoRound():
                sleep(1)

            self.eliminaMorto()
            self.ripristinaPosti() # Ripristina i posti

            print ("Il numero di posti rimasti Ã¨ %d" % len(self.posti)) # Stampa il numero di posti rimasti

            print("Fine del round %d" % i) # Fine del round
        print ("Il vincitore Ã¨ %s" % self.partecipanti[0].getName()) # Stampa il vincitore
        self.partecipanti[0].uccidi() # Uccide il vincitore
    def initThread(self):
        for i in range(0, len(self.partecipanti)):
            self.partecipanti[i].start()

    def ripristinaPosti(self):
        for i in range(0, len(self.posti)):
            self.posti[i].set(False)
        self.posti.pop() # Rimuove l'ultimo posto che non ci serve

    def ripristinaPartecipanti(self):
        for i in range(0, len(self.partecipanti)):
            self.partecipanti[i].reset() # Resetta i partecipanti

    def finitoRound(self):
        for i in range(0, len(self.partecipanti)):
            if partecipanti[i].isMorto():
                return True
        return False




    def eliminaMorto(self):
        for i in range(0, len(self.partecipanti)):
            if self.partecipanti[i].isMorto():
                print ("Il partecipante %s Ã¨ morto" % self.partecipanti[i].getName())
                self.partecipanti.remove(partecipanti[i])
                return # Rimuove il primo morto che trova





class PostoUnsafe:

    def __init__(self):
        self.occupato = False

    def libero(self):
        return not self.occupato

    def set(self, v):
        self.occupato = v


class PostoQuasiSafe(PostoUnsafe):

    def __init__(self):
        super().__init__()
        self.lock = Lock()

    def libero(self):
        '''
        Il blocco "with self.lock" Ã¨ equivalente a circondare tutte le istruzioni in esso contenute con self.lock.acquire() e self.lock.release()
        Notate che questo costrutto Ã¨ molto comodo in presenza di return, poichÃ¨ self.lock.release() verrÃ  eseguita DOPO la return, cosa che normalmente
        non sarebbe possibile (return normalmente Ã¨ l'ultima istruzione di una funzione)
        '''
        with self.lock:
            return super().libero()

    def set(self, v):
        self.lock.acquire()
        super().set(v)
        self.lock.release()


class PostoSafe(PostoQuasiSafe):

    def __init__(self):
        super().__init__()

    def testaEoccupa(self):
        with self.lock:
            if (self.occupato):
                return False
            else:
                self.occupato = True
                return True

    def testa(self):
        with self.lock:
            return self.occupato

    def set(self, v):
        with self.lock:
            self.occupato = v


class Display(Thread):

    def __init__(self, posti):
        super().__init__()
        self.posti = posti

    def run(self):
        while (True):
            sleep(1)
            for i in range(0, len(self.posti)):
                if self.posti[i].testa():
                    print("-", end='', flush=True)
                else:
                    print("o", end='', flush=True)
            print('')

"""
class PartecipanteUnsafe(Thread):

    def __init__(self, posti):
        super().__init__()
        self.posti = posti

    def run(self):
        sleep(randrange(5))
        for i in range(0, len(self.posti)):
            #
            # Errore. Anche se libero() e set() sono, prese singolarmente, thread-safe, queste vengono chiamate in due tempi distinti (PRIMO TEMPO: chiamata a libero; SECONDO TEMPO: chiamata a set() ), acquisendo e rilasciando il lock entrambe le volte.
            # In mezzo ai due tempi, eventuali altri partecipanti avranno la possibilitÃ  di acquisire il lock di self.posti[i] e modificarne lo stato. Noi non vogliamo questo. E' una race condition.
            #
            if self.posti[i].libero():
                self.posti[i].set(True)
                print("Sono il Thread %s. Occupo il posto %d" % (self.getName(), i))
                return

        print("Sono il Thread %s. HO PERSO" % self.getName())
"""

class PartecipanteSafe(Thread):

    def __init__(self, posti):
        super().__init__()
        self.posti = posti
        self.morto = False
        self.seduto = False

    def run(self):
        while True and not self.morto: # Ciclo infinito
            if not self.seduto:
                sleep(randrange(5))
                for i in range(0, len(self.posti)):
                    if self.posti[i].testaEoccupa():
                        print("Sono il Thread %s. Occupo il posto %d" % (self.getName(), i))
                        self.seduto = True
                        break
                if not self.seduto:
                    print("Sono il Thread %s. HO PERSO" % self.getName())
                    self.morto = True
            else:
                sleep(1)

    def isMorto(self):
        return self.morto
    def reset(self):
        self.seduto = False

    def uccidi(self):
        self.morto = True





NSEDIE = 5
posti = [PostoSafe() for i in range(0,NSEDIE)]



partecipanti = []

for t in range(0, NSEDIE + 1):

    t = PartecipanteSafe(posti)
    partecipanti.append(t)
#lg = Display(posti)
#lg.start()
c = Campionato(partecipanti, posti)
c.iniziaCampionato() # Inizia il campionato
