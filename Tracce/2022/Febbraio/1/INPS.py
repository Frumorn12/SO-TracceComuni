import random, time, os
from threading import Thread, Condition, RLock, get_ident
from queue import Queue


#
# Una sede sarÃ  formata da tanti Uffici
#
class Ufficio:
    def __init__(self, l):
        Thread.__init__(self)
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.lettera = l
        self.ticketDaRilasciare = 0
        self.ticketDaServire = 0

    #
    # Fornisce un ticket formattato abbinando correttamente lettera e numero
    #
    def formatTicket(self, lettera, numero):
        return "%s%03d" % (lettera, numero)

    #
    # Restituisce quanti ticket in attesa ci sono in questo ufficio
    #
    def getTicketInAttesa(self):
        with self.lock:
            return self.ticketDaRilasciare - self.ticketDaServire

    #
    # Invocato da un utente  quando deve prendere un numerino
    #
    def prendiProssimoTicket(self):
        with self.lock:
            #
            # self.ticketDaRilasciare e self.ticketDaServire stanno per diventare diversi e cioÃ¨ ci sono utenti da smaltire
            #
            if (self.ticketDaRilasciare <= self.ticketDaServire):
                self.condition.notify_all()
            self.ticketDaRilasciare += 1

            return self.formatTicket(self.lettera, self.ticketDaRilasciare)

    #
    # Invocato da un impiegato quando deve chiamare la prossima persona
    #
    def chiamaProssimoTicket(self):
        with self.lock:
            #
            # Non ci sono ticket in attesa da elaborare. Attendo
            #
            while (self.ticketDaRilasciare <= self.ticketDaServire):
                self.condition.wait()

            self.ticketDaServire += 1

            return self.formatTicket(self.lettera, self.ticketDaServire)


class Sede:

    def __init__(self, n):
        self.n = n
        #
        # Gestiremo gli n uffici con un dizionario. Esempio: per selezionare l'ufficio "C" si usa self.uffici["C"]
        #
        self.uffici = {}
        for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:n]:
            self.uffici[l] = Ufficio(l)
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.ultimiTicket = []
        self.historyTicket = []
        self.update = False
        self.setPrintAttese = False

    #
    # Preleva ticket da rispettivo ufficio. N.B. si usa il lock del rispettivo ufficio
    #
    def prendiTicket(self, uff):
        return self.uffici[uff].prendiProssimoTicket()

    #
    # Chiama ticket del rispettivo ufficio. N.B. si usa il lock del rispettivo ufficio e poi si aggiorna l'elenco degli ultimi ticket con il lock di SEDE
    #
    def chiamaTicket(self, uff):
        ticket = self.uffici[uff].chiamaProssimoTicket()
        with self.lock:
            self.condition.notifyAll()
            self.update = True

            # Limitiamo la lista ultimiTicket alla dimensione attuale, se necessario
            if len(self.ultimiTicket) >= self.currentSize:
                self.historyTicket.append(self.ultimiTicket.pop())

            self.ultimiTicket.insert(0, ticket)

    def waitForTicket(self, ticket):
        with self.lock:
            if (ticket in self.historyTicket):
                return False    # Se il ticket Ã¨ stato giÃ  chiamato, ritorno False
            while (ticket not in self.ultimiTicket):
                self.condition.wait()
            return True # Se il ticket Ã¨ stato chiamato, ritorno True

    def waitForTickets(self, L):
        with self.lock:
            # Verifica se uno dei ticket è già stato chiamato e non è più disponibile
            if all(ticket in self.historyTicket for ticket in L):
                return False  # Tutti i ticket sono stati chiamati in passato

            # Attendere finché almeno uno dei ticket non viene chiamato
            while not any(ticket in self.ultimiTicket for ticket in L):
                self.condition.wait()
                # Controllare di nuovo se sono ormai tutti in historyTicket (non più validi)
                if all(ticket in self.historyTicket for ticket in L):
                    return False

            return True  # Almeno uno dei ticket è stato trovato

    #
    # Serve a segnalare al display di stampare il riepilogo
    #
    def printAttese(self):
        with self.lock:
            self.setPrintAttese = True

    #
    #  Stampa gli ultimi numeri chiamati
    #
    def printUltimi(self):
        with self.lock:
            while not self.update:
                self.condition.wait()
            self.update = False
            # os.system('clear')
            #
            # Se qualcuno lo ha chiesto, stampo l'elenco degli utenti in coda per ogni ufficio
            #
            if (self.setPrintAttese):
                for u in self.uffici:
                    print("%s : %d" % (self.uffici[u].lettera, self.uffici[u].getTicketInAttesa()))
                self.setPrintAttese = False
            for t in self.ultimiTicket:
                print(t)
            print("=" * 10)

    def incDecSizeUltimi(self, n: int):
        with self.lock:
            # Caso di incremento della dimensione della lista
            if n > 0:
                self.ultimiTicket = self.ultimiTicket[:n] + self.ultimiTicket

            # Caso di decremento della dimensione della lista
            elif n < 0:
                if abs(n) >= len(self.ultimiTicket):
                    # Ignora l'operazione se n è negativo e supera la lunghezza attuale della lista
                    return
                else:
                    # Rimuovi gli ultimi ticket dalla lista per ridurre la dimensione
                    self.ultimiTicket = self.ultimiTicket[:n]


class Utente(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        self.n = len(sede.uffici)

    def run(self):
        while True:
            ticket = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
            print(
                f"Sono l'utente {get_ident()} e mi faccio un giro prima di mettermi ad aspettare il mio ticket {ticket}")
            time.sleep(random.randint(1, 3))
            print(f"Sono l'utente {get_ident()}, ho preso un caffÃ¨ e adesso aspetto il mio ticket: {ticket}")
            self.sede.waitForTicket(str(ticket))


class Impiegato(Thread):
    def __init__(self, sede, lettera):
        Thread.__init__(self)
        self.sede = sede
        self.ufficio = lettera

    def run(self):
        while True:
            self.sede.chiamaTicket(self.ufficio)
            #
            # Simula un certo tempo in cui l'impiegato serve l'utente appena chiamato
            #
            time.sleep(random.randint(1, 4))
            #
            # Notifica di voler stampare il riepilogo attese
            #
            if random.randint(0, 5) >= 4:
                self.sede.printAttese()


class UtenteFurbetto(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        self.n = len(sede.uffici)

    def run(self):
        while True:
            # Prendere 3 ticket da 3 uffici diversi
            ticket1 = self.sede.prendiTicket("B")
            ticket2 = self.sede.prendiTicket("F")
            ticket3 = self.sede.prendiTicket("D")
            tickets = [ticket1, ticket2, ticket3]
            print(f"Sono l'utente furbetto {get_ident()} e ho preso i ticket: {tickets}")
            time.sleep(random.randint(1, 3))
            print(
                f"Sono l'utente furbetto {get_ident()}, ho preso un caffè e aspetto che uno dei miei ticket venga chiamato: {tickets}")

            # Aspetta che uno qualsiasi dei ticket venga chiamato
            result = self.sede.waitForTickets(tickets)
            if result:
                print(f"Uno dei miei ticket {tickets} è stato chiamato!")
            else:
                print(f"Nessuno dei miei ticket {tickets} è più valido, sono stati chiamati troppo tempo fa.")


class Display(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede

    def run(self):
        while True:
            self.sede.printUltimi()


class TestThread(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede

    def run(self):
        while True:
            # Aumenta o diminuisci la dimensione della lista ultimiTicket in modo casuale
            increment = random.choice([-2, -1, 1, 2])
            self.sede.incDecSizeUltimi(increment)
            print(f"Dimensione lista ultimiTicket modificata di {increment}")
            time.sleep(2)



sede = Sede(6)

display = Display(sede)
display.start()

utenti = [Utente(sede) for p in range(10)]
impiegato = [Impiegato(sede, i) for i in "ABCDEF"]

furbetto = UtenteFurbetto(sede) # Un utente furbetto

test = TestThread(sede)

for p in utenti:
    p.start()

for i in impiegato:
    i.start()

furbetto.start()
test.start()