#!/usr/bin/python3

from threading import RLock, Condition, Thread
from time import sleep
from random import randint

'''
MATERIALE PER LA PROVA SULLA PROGRAMMAZIONE MULTI-THREADED 

Il codice fornito implementa un piccolo sistema di gestione di una sala bowling. Una sala da bowling contiene un certo numero di piste P 
e un certo numero N di palle da bowling. Per poter giocare, una squadra composta da M giocatori necessita di avere a disposizione una pista 
e una palla da bowling per ciascun giocatore (dunque devono essere disponibili M palle da bowling).
Ogni pista puÃ² essere assegnata a una certa squadra, ammesso che sia disponibile un numero di palle da bowling pari al numero di giocatori per la data squadra. 
Ad esempio, se le palle a disposizione sono 10, e in un certo momento una squadra di 6 giocatori occupa la pista n.1, 
una eventuale squadra di 5 giocatori non potrÃ  usufruire della pista n.2, pur essendo questa libera, poichÃ© le restanti 4 palle non sono sufficienti. 

La classe Sala contiene questi metodi:

richiedi_pista(self, id_squadra, num_giocatori: int, modalita_gentile=False) -> int

Il primo metodo consente di richiedere una pista e una dotazione di palle da bowling specificando un certo numero di giocatori. 
Se la quantitÃ  di palle richiesta non Ã¨ disponibile, oppure non ci sono piste libere, la squadra viene messa in attesa. Viene restituito il codice della pista che Ã¨ stata assegnata.
Per come funziona il metodo quando modalita_gentile Ã¨ True, leggi la descrizione del metodo richiedi_pista_gentilmente.

libera_pista(self, num_pista: int, num_giocatori: int) 

Il secondo metodo prevede la liberazione di una pista precedentemente occupata e la restituzione delle palle da bowling non piÃ¹ utilizzate. 

richiedi_pista_gentilmente(self, id_squadra, num_giocatori)

Questo metodo invoca richiedi_pista con la modalita_gentile impostata a True.
Questo metodo si mette in attesa finchÃ© non sono disponibili 'num_giocatori' palle da bowling e una pista, proprio come il
metodo richiedi_pista standard. Tuttavia, quando si Ã¨ in modalitÃ  gentile interviene un meccanismo diverso di gestione
della turnazione tra squadre.
PiÃ¹ in dettaglio, quando arriva il turno per una squadra S, ma contemporaneamente non Ã¨ subito disponibile il
numero di palle da bowling richiesto per la squadra S, allora il thread chiamante si rimette subito in stato di wait, ma retrocedendo di quattro
posti nella lista di attesa. Qualora i thread in attesa subito dopo S siano meno di 4, allora S si metterÃ  in coda.

A corredo trovi anche il codice di una classe Squadra che simula il comportamento casuale di una squadra attraverso un thread. 
La soluzione fornita elimina i potenziali problemi di starvation accodando le richieste delle squadre secondo l'ordine di arrivo.
'''
# esercizio pre esame
# usare una barrier per regolare il punto 3
# due squadre possono condividere la pista ma solo insieme
# e finisco insieme 
class Sala:
    
    def __init__(self, num_piste, num_palle):
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.num_piste = num_piste

        """
        TIPO ABBIAMO QUATTRO PISTE
        0  1  2  3
        F  F  F  F 

        0  1  2  3  -> Numero Piste
        -1 -1 -1 -1 -> queste variabili ci dicono se la pista è occupata o meno
        
        leggenda:
        -1 = pista libera
        0 = pista occupata da condiviso
        1 = pista occupata da condiviso piena
        2 = pista occupata da non condiviso


        
        
        """
        self.piste = [-1] * num_piste
        
        self.palle_disponibili = num_palle
        self.id_squadra_prioritaria = -1  
        
        self.prossimo_id = 1
        self.lista_attesa = []

    def richiedi_pista(self, id_squadra, num_giocatori, modalita_gentile=False, modalita_tamarra=False, condivisione = False): 
        with self.lock:
            if modalita_tamarra:
                while (self.id_squadra_prioritaria != -1):
                    self.condition.wait() 
                print(f"SQUADRA TAMARRA {id_squadra} si infila davanti a tutti!")
                self.lista_attesa.insert(0, id_squadra)
            else:
                self.lista_attesa.append(id_squadra)
            count = 0             
            
            # Per uscire da questo while devono verificarsi tre condizioni:
            # 1) Deve esserci una pista libera
            # 2) Deve esserci un numero sufficiente di palle per la squadra
            # 3) Deve essere il turno della squadra, ossia id_squadra deve essere il primo elemento della lista_attesa
            while (pista:=self._cerca_pista(condivisione) == False or #:= è un operatore che assegna in maniera dinamica il
                   self.palle_disponibili < num_giocatori or 
                   id_squadra != self.lista_attesa[0] ): 
                
                #
                # Sono in blocco per via delle poche palle disponibili e sono in modalitÃ  gentile, quindi...
                #     
                if modalita_gentile and id_squadra == self.lista_attesa[0] and pista!=-1:
                    self.lista_attesa.pop(0)
                    #
                    # Siccome mi sto levando dalla cima della lista di attesa, do la possibilitÃ  alla prossima squadra di giocare 
                    #
                    self.condition.notify_all()
                    print(f"La squadra {id_squadra} con {num_giocatori} giocatori rimanda il suo turno")
                    if len(self.lista_attesa) >= 4:
                        self.lista_attesa.insert(3, id_squadra)
                    else:
                        self.lista_attesa.append(id_squadra)
                print(f"La squadra {id_squadra} con {num_giocatori} giocatori deve attendere il suo turno")
                count += 1 
                if count == 4 and self.id_squadra_prioritaria == -1 and not modalita_tamarra and not modalita_gentile:   
                    # mi tolgo dalla posizione in cui ero e mi metto primo
                    self.lista_attesa.remove(id_squadra)
                    self.lista_attesa.insert(0, id_squadra) 
                    self.id_squadra_prioritaria = id_squadra 
                self.condition.wait()
                
            self.lista_attesa.pop(0)
            if self.id_squadra_prioritaria == id_squadra:
                self.id_squadra_prioritaria = -1 
            # Essendosi modificata la lista di attesa, notifico per dare la possibilitÃ  alla prossima squadra di provare a giocare
            self.condition.notify_all()
            self.palle_disponibili -= num_giocatori
            pista = self._cerca_pista()
            if (condivisione):
                self.piste[pista] += 1
            else:
                self.piste[pista] = 2 
            print(f"La squadra {id_squadra} ottiene la pista {pista} con {num_giocatori} giocatori")
            return pista

    def richiedi_pista_gentilmente(self, id_squadra, num_giocatori):
        return self.richiedi_pista(id_squadra, num_giocatori, True)

    def libera_pista(self, num_pista, num_giocatori, condivisione = False):
        # La pista viene liberata e le palle restituite
        with self.lock:
            self.palle_disponibili += num_giocatori
            if condivisione:
                self.piste[num_pista] -= 1
            else:
                self.piste[num_pista] = -1 
            # Si sono liberate delle risorse, notifico per dare la possibilitÃ  di usare le risorse liberate a chi Ã¨ in attesa
            self.condition.notify_all()

    def print_stato_piste(self): 
        with self.lock:
            print(f"Stato piste: {self.piste}")
            print(f"Palle disponibili: {self.palle_disponibili}")
            print(f"Lista attesa: {self.lista_attesa}")
            print(f"ID squadra prioritaria: {self.id_squadra_prioritaria}") 

    # Metodo privato usato per individuare la prima pista libera
    def _cerca_pista(self, condivisione = False):
        if condivisione:
            for i in range(len(self.piste)):
                if (self.piste[i] == -1 or self.piste[i] == 1):
                    return i
                 
        for i in range(len(self.piste)):
            if not self.piste[i]:
                return i
        return False

class Display(Thread):
    def __init__(self, sala):
        super(Display, self).__init__()
        self.sala = sala

    def run(self):
        while True:
            sleep(2)
            self.sala.print_stato_piste()



class Squadra(Thread):

    def __init__(self, id_squadra, sala):
        super(Squadra, self).__init__()
        self.sala = sala
        self.id_squadra = id_squadra

    def run(self):
        while True:
            # La squadra fa altro prima di chiedere una pista
            sleep(randint(0,6))
            # Prova a chiedere una pista
            num_giocatori = randint(2,15)
            print(f"La squadra {self.id_squadra} chiede una pista per {num_giocatori} giocatori.")
            pista = self.sala.richiedi_pista_gentilmente(self.id_squadra, num_giocatori)
            print(f"La squadra {self.id_squadra} gioca sulla pista {pista}.")
            # Simula il tempo di gioco
            sleep(randint(1,4))
            self.sala.libera_pista(pista, num_giocatori)
            print(f"La squadra {self.id_squadra} lascia la pista {pista}.")
            

if __name__ == '__main__':
    # Crea una sala con 4 piste e 20 palle
    sala = Sala(4, 40)
    for i in range(10):
        Squadra(i, sala).start()