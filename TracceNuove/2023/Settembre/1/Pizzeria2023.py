
from queue import Queue
from random import randint
from threading import Condition, RLock, Thread
import time

"""
Traccia:

ESERCIZIO 1 - PROGRAMMAZIONE MULTITHREADED
(Punteggio minimo richiesto 18/30. Pesa per ⅔ del voto finale)
Per questa prova di esame, dovrai progettare la classe Ristorante che combina una istanza di Pizzeria con una istanza di
classe Sala e con altri elementi che ora ti descriverò. Una Sala è composta da N tavoli da 10 posti ciascuno. Ciascun posto
può essere vuoto oppure essere occupato da una pizza. La Sala comunica con la pizzeria sostituendo ai Clienti, delle istanze
di thread Cameriere.
Il Cameriere è un nuovo tipo di thread che dovrai progettare appositamente. Così come avviene nel codice esistente di
Cliente, un Cameriere genera un ordine casualmente, lo affida ai pizzaioli usando il metodo putOrdine per poi prelevare
le pizze con il metodo getPizze.
Ci sono tuttavia delle differenze rispetto ai clienti:
-ogni ordine ora dovrà indicare un tavolo designato T, scelto tra quelli completamente sgombri, e appartenente alla Sala; T
rappresenta il tavolo dove il cameriere dovrà depositare le pizze appena sfornate;
-gli ordini non possono superare la quantità di dieci pizze totali;
-quando l’ordine è pronto, il cameriere sistema le pizze sul tavolo T, ma poichè può trasportare al massimo due pizze per
volta, è costretto a fare più viaggi. Sarà tuo compito modificare il codice per fare in modo che si possano prelevare da uno
specifico ordine contenuto nel buffer delle pizze 2 elementi alla volta al massimo; inoltre, tra un viaggio e l’altro dovrai
introdurre del tempo di attesa che simula il tempo che ci vuole ad andare dalla Pizzeria alla Sala e viceversa.
Una sala è inoltre dotata di una o più istanze di thread Sparecchiatore. Uno sparecchiatore toglie periodicamente le pizze
dai tavoli della Sala, ma dovrai assicurarti che una pizza appena depositata da un Cameriere non sia rimossa prima di 3
secondi dal momento in cui è stata poggiata sul tavolo.
Questo è tutto. Come sempre, è tuo specifico compito decidere cosa fare per tutti i dettagli che non sono stati
espressamente definiti

"""


pizze = { "margherita" : "(.)", 
          "capricciosa" : "(*)", 
          "diavola" : "(@)",
          "ananas" : "(,)"}


class Ristorante:
    def __init__(self):
        print ("Inizializzazione del ristorante") 
        self.pizzeria = Pizzeria()
        self.sala = Sala()
        self.camerieri = []
        self.pizzaioli = [] 
        self.sparecchiatori = []
        self.clienti = []

        for i in range(0, 3):
            cameriere = Cameriere("Giovanni_" + str(i), self.pizzeria, self.sala)
            self.camerieri.append(cameriere)
            cameriere.start()

        for i in range(0, 2):
            sparecchiatore = Sparecchiatore("Pasquale_" + str(i), self.sala) 
            self.sparecchiatori.append(sparecchiatore)
            sparecchiatore.start() 
        
        for i in range (0, 2):
            pizzaiolo = Pizzaiolo("Totonno_" + str(i), self.pizzeria)
            self.pizzaioli.append(pizzaiolo)
            pizzaiolo.start()

        for i in range(0, 20):
            cliente = Cliente("Ciro_" + str(i), self.pizzeria)
            self.clienti.append(cliente)
            cliente.start() 


class Sparecchiatore(Thread):
    def __init__(self, name, sala):
        super().__init__()
        self.name = name
        self.sala = sala

    def run(self):
        while True:
            tavolo = randint(0, 9)
            print(f"Lo sparecchiatore {self.name} sparecchia il tavolo {tavolo}")
            if self.sala.sparecchiaTuttoIlTavolo(tavolo):
                print(f"Lo sparecchiatore {self.name} ha sparecchiato il tavolo {tavolo}")
            else :
                print(f"Lo sparecchiatore {self.name} non ha sparecchiato il tavolo {tavolo}, aspetta 3 secondi") 
            time.sleep(1) 


class Cameriere(Thread): 
    def __init__(self, name, pizzeria, sala):
        super().__init__()
        self.name = name
        self.pizzeria = pizzeria
        self.sala = sala

    def run(self):
        while True:
            numeroPizze = 1 + randint(0, 7)
            tipiPizza = list(pizze.keys())
            codicePizza = tipiPizza[randint(0, len(tipiPizza) - 1)]
            tavolo = randint(0, 9)
            print(f"Il cameriere {self.name} ha preso l'ordine per il tavolo {tavolo} e ha ordinato {numeroPizze} pizze di tipo {codicePizza}")
            ordine = self.pizzeria.putOrdine(codicePizza, numeroPizze)
            print(f"Il cameriere {self .name} aspetta le pizze con codice d'ordine numero {ordine.codiceOrdine}")
            time.sleep(randint(0, numeroPizze))
            pizzeconcatenate = self.pizzeria.getPizzeCameriere(ordine)
            pizze = pizzeconcatenate.split(" ") 
            print(f"Il cameriere {self.name} ha preso le pizze con codice d'ordine numero {ordine.codiceOrdine}")
            print(f"Il cameriere {self.name} ora depositera 2 alla volta le pizze sul tavolo  {tavolo}")
            for i in range(0, len(pizze), 2):
                self.sala.pizzaSulTavolo(pizze[i], tavolo)
                if i+1 < len(pizze):
                    self.sala.pizzaSulTavolo(pizze[i+1], tavolo)
                print(f"Il cameriere {self.name} ha depositato le pizze sul tavolo {tavolo}, ora aspetta di andare a prendere le altre")  
                time.sleep(1) 
            
            print (f"Il cameriere {self.name} ha depositato tutte le pizze sul tavolo {tavolo}") 


class Sala:
    def __init__(self):
        self.tavoli = []
        for i in range(0, 10):
            self.tavoli.append(Tavolo())

    def  pizzaSulTavolo(self, nomePizza, tavolo):
        return self.tavoli[tavolo].pizzaSulTavolo(nomePizza) 

    def sparecchiaTuttoIlTavolo(self, tavolo): 
        return self.tavoli[tavolo].sparecchiaTuttoIlTavolo() 
        

class Tavolo: 
    def __init__(self):
        # pizze sono un array di 10 booleani
        self.pizze = [False] * 10
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.tempoUltimaPizzaInserita = 0 

    def pizzaSulTavolo(self, nomePizza):
        with self.lock:
            for i in range(0, 10):
                if self.pizze[i] == False:
                    self.pizze[i] = nomePizza 
                    self.tempoUltimaPizzaInserita = time.time() 
                    return i
                
            return -1 
    def sparecchiaTuttoIlTavolo(self):
        with self.lock:
            if time.time() - self.tempoUltimaPizzaInserita > 3: 
                for i in range(0, 10):
                    self.pizze[i] = False
                return True 
            else :
                print("Non posso sparecchiare, aspetta 3 secondi")
                return False     
             

class Ordine:
    nextCodiceOrdine = 0
    def __init__(self,tipoPizza,quantita):
        self.tipoPizza = tipoPizza
        self.quantita = quantita
        self.codiceOrdine = Ordine.nextCodiceOrdine
        self.pizzePronte = ""

        Ordine.nextCodiceOrdine += 1

    def prepara(self):
        for i in range(self.quantita):
            self.pizzePronte += pizze[self.tipoPizza]+" " 

class BlockingSet(set):

    def __init__(self, size = 10):
        super().__init__()
        self.size = size
        self.lock = RLock()
        self.condition = Condition(self.lock)

    def add(self,T):
        with self.lock:
            while len(self) == self.size:
                self.condition.wait()
            self.condition.notify_all()
            return super().add(T)

    def remove(self,T):
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

    def putOrdine(self,codicePizza,quantita):
        ordine = Ordine(codicePizza,quantita)
        self.BO.put(ordine)
        return ordine

    def getPizzeCameriere(self,ordine):
        return self.BP.remove(ordine) 
        

    def getPizze(self,ordine):
        self.BP.remove(ordine)

    def putPizze(self,ordine):
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
            time.sleep(randint(1,3))

class Cliente(Thread):
    def __init__(self, name, pizzeria):
        super().__init__()
        self.name = name
        self.pizzeria = pizzeria

    def run(self):
        while True:
                numeroPizze = 1 + randint(0,7)
                tipiPizza = list(pizze.keys())
                codicePizza = tipiPizza[randint(0,len(tipiPizza)-1)]

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


Ristorante() 
