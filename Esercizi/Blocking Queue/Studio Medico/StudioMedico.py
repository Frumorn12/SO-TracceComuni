"""
Programma:

Abbiamo uno studio medico. Esso [ fornito di una sala di attesa presso la quale devono
attendere il proprio turno i pazienti. I pazienti all'arrivo occupano un posto nella sala di
attesa ed attende il proprio turno. L'ordine di "servizio" sara di tipo FIFO.
Il paziente puo recarsi allo studio medico sia per effettuare una visita, ma anche
per richiedere il rilascio di una ricetta medica

Il medico chiamera il paziente uno alla volta per la visita, sempre in ordine FIFO. Inoltre
visitera solo i pazienti che devono effettuare una visita, mentre i pazienti che devono
ricevere una ricetta medica verranno serviti dalla segretaria.

Il paziente servito dalla ricetta medica, una volta servito, lascia lo studio medico.
Il paziente servito dalla visita, una volta servito, si rimettera in attesa per ricevere a sua volta
una ricetta medica, pero in tal caso il paziente acquisisce una PRIORITA rispetto agli altri pazienti che aspettano
la ricetta.

Quindi ricapitolando:
    - Studio medico composto:
        - Sala d'attesa
        - Medico
        - Segretaria
    - Pazienti:
        - Possono richiedere visita o ricetta
        - Possono essere serviti dal medico o dalla segretaria
        - Possono avere priorita se hanno gia effettuato la visita

Implentazione:
    Allora farei cosi:
    Abbiamo una sala di attesa con 3 code:
    - Pazienti in attesa per la visita medica
    - Pazienti in attesa per la ricetta medica
    - Pazienti in attesa per la visita medica con priorita

    Il medico chiamera i pazienti in ordine FIFO dalla coda dei pazienti in attesa per la visita medica
    Se un paziente ha gia effettuato la visita, allora andra nella coda dei pazienti in attesa per la ricetta medica con priorita

    La segretaria chiamera i pazienti in ordine FIFO dalla coda dei pazienti in priorita per la ricetta medica, altrimenti dalla coda dei pazienti in attesa per la ricetta medica

    Se tutte le code sono vuote, il medico e la segretaria aspetteranno che un paziente arrivi in sala d'attesa per servirlo.

"""


from threading import RLock, Condition, Thread
import time
import random
from queue import Queue


class SalaAttesa:
    def __init__(self):
        self.salaVisite = Queue()
        self.salaPriorita = Queue()
        self.salaRicette = Queue()
        self.lock = RLock()
        self.codeVuote = Condition(self.lock)

    def aggiungiPazienteVisite(self, paziente):
        self.salaVisite.put(paziente)
        paziente.ricetta.creaRicetta()
    def aggiungiPazienteRicette(self, paziente):
        self.salaRicette.put(paziente)
        self.lock.acquire()
        self.codeVuote.notify_all()
        self.lock.release()

    def aggiungiPazientePriorita(self, paziente):
        self.salaPriorita.put(paziente)
        self.lock.acquire()
        self.codeVuote.notify_all()
        self.lock.release()

    def chiamataMedico(self):
        return self.salaVisite.get()

    def chiamataSegretaria(self):
        self.lock.acquire()
        try:
            while self.salaPriorita.empty() and self.salaRicette.empty():
                self.codeVuote.wait()
            if not self.salaPriorita.empty():
                return self.salaPriorita.get()
            else:
                return self.salaRicette.get()

        finally:
            self.lock.release()



class Medico(Thread):
    def __init__(self, sala):
        super().__init__()
        self.sala = sala

    def run(self):
        while True:
            paziente = self.sala.chiamataMedico()
            print(f"Il medico sta visitando {paziente.nome}")
            time.sleep(random.randint(1, 3))
            print(f"Il medico ha finito di visitare {paziente.nome}")
            self.sala.aggiungiPazienteRicette(paziente)




class Segretaria(Thread):
    def __init__(self, sala):
        super().__init__()
        self.sala = sala

    def run(self):
        while True:
            paziente = self.sala.chiamataSegretaria()
            print(f"La segretaria sta servendo {paziente.nome}")
            time.sleep(random.randint(1, 3))
            print(f"La segretaria ha finito di servire {paziente.nome}")
            paziente.finisciVisita()




class Ricetta:
    def __init__(self):
        self.ricetta = None

    def creaRicetta(self):
        self.ricetta = True

    def prendiRicetta(self):
        return self.ricetta

    def finisciVisita(self):
        self.ricetta = None
class Paziente:
    def __init__(self, sala, nome):
        self.nome = nome
        self.ricetta = Ricetta()
        self.sala = sala

    def creaRicetta(self):
        sleepTime = random.randint(1, 3)
        time.sleep(sleepTime)
        print(f"{self.nome} ha richiesto la ricetta medica ed `e stato messo in attesa")
        self.sala.aggiungiPazientePriorita(self)

    def finisciVisita(self):
        print(f"{self.nome} ha finito la visita e la ricetta medica, quindi puo uscire dalla sala d'attesa")


def main():
    sala = SalaAttesa()
    medico = Medico(sala)
    segretaria = Segretaria(sala)
    medico.start()
    segretaria.start()
    for i in range(20):
        paziente = Paziente(sala, f"Paziente {i}")

        randint = random.randint(0, 1)
        if randint == 0:
            print(f"{paziente.nome} ha richiesto la visita medica")
            sala.aggiungiPazienteVisite(paziente)
        else:
            print(f"{paziente.nome} ha richiesto la ricetta medica")
            sala.aggiungiPazienteRicette(paziente)
        time.sleep(random.randint(1, 3))

main()





