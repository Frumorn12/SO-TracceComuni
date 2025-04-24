import random, time, os
from threading import Thread,Condition,RLock, get_ident
from queue import Queue

#
# Una sede sarÃ  formata da tanti Uffici
#
class Ufficio: # Ufficio 
    def __init__(self,l): # lettera 
        Thread.__init__(self) # 
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.lettera = l
        self.ticketDaRilasciare = 0
        self.ticketDaServire = 0

    #
    # Fornisce un ticket formattato abbinando correttamente lettera e numero
    #
    def formatTicket(self,lettera,numero):
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
            self.ticketDaRilasciare+=1
            
            return self.formatTicket(self.lettera, self.ticketDaRilasciare)

    #
    # Invocato da un impiegato quando deve chiamare la prossima persona
    #
    def chiamaProssimoTicket(self):
        with self.lock:
            #
            # Non ci sono ticket in attesa da elaborare. Attendo
            #
            while(self.ticketDaRilasciare <= self.ticketDaServire):
                self.condition.wait()

            self.ticketDaServire+=1
            
            return self.formatTicket(self.lettera, self.ticketDaServire)
                
 
class Sede:

    def __init__(self,n):
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
        self.sizeUltimiTicket = 5
        self.ticketChiamati = [] 
        self.update = False
        self.setPrintAttese = False

    #
    # Preleva ticket da rispettivo ufficio. N.B. si usa il lock del rispettivo ufficio
    #
    def prendiTicket(self,uff):
        return self.uffici[uff].prendiProssimoTicket()

    #
    # Chiama ticket del rispettivo ufficio. N.B. si usa il lock del rispettivo ufficio e poi si aggiorna l'elenco degli ultimi ticket con il lock di SEDE
    #
    def chiamaTicket(self,uff):
        ticket = self.uffici[uff].chiamaProssimoTicket()
        with self.lock:
            self.condition.notifyAll()
            #
            # Questo aggiornamento serve a far capire al display che ci sono novitÃ  da stampare a video
            #
            self.update = True
            if(len(self.ultimiTicket) >= self.sizeUltimiTicket):
                self.ticketChiamati.append(self.ultimiTicket.pop())
                
            self.ultimiTicket.insert(0,ticket)
            

    def waitForTicket(self,ticket):
        with self.lock:
            while(ticket not in self.ultimiTicket):
                self.condition.wait()

    def waitForTicketSafe(self,ticket):
        with self.lock:
            if ticket in self.ultimiTicket:
                return False
            
            while (ticket not in self.ultimiTicket):
                self.condition.wait()
            return True 
        
    def waitForTickets(self,list):
        with self.lock:
            count = 0
            for ticket in list:
                if ticket in self.ultimiTicket:
                    count += 1
            if count == len(list):
                return False
            
            oneTicket = False

            while (not oneTicket):
                for ticket in list:
                    if ticket in self.ultimiTicket:
                        oneTicket = True
                        break
                if not oneTicket:
                    self.condition.wait() 

            return True


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
            #os.system('clear')
            #
            # Se qualcuno lo ha chiesto, stampo l'elenco degli utenti in coda per ogni ufficio
            #
            if (self.setPrintAttese):
                for u in self.uffici:
                    print("%s : %d" % (self.uffici[u].lettera, self.uffici[u].getTicketInAttesa()))
                self.setPrintAttese = False
            for t in self.ultimiTicket:
                print(t)
            print ("="*10)
    def incDecSizeUltimi(self, n):
        with self.lock:
            if (n < 0 and -n >= len(self.ultimiTicket)):
                return 
            
            if (n > 0):
                self.sizeUltimiTicket += n
            else:
                self.sizeUltimiTicket -= n 
            



class Utente(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        self.n = len(sede.uffici)

    def run(self):
        while True:
            ticket = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
            print(f"Sono l'utente {get_ident()} e mi faccio un giro prima di mettermi ad aspettare il mio ticket {ticket}")
            time.sleep(random.randint(1,3))
            print(f"Sono l'utente {get_ident()}, ho preso un caffÃ¨ e adesso aspetto il mio ticket: {ticket}") 
            self.sede.waitForTicket(str(ticket))

class UtenteFurbetto(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        self.n = len(sede.uffici)
    
    def run(self):
        while True:
            ticket = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
            ticket2 = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
            ticket3 = self.sede.prendiTicket(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[0:self.n]))
            lista = [ticket, ticket2, ticket3] 
            print(f"Sono l'utente {get_ident()} e mi faccio un giro prima di mettermi ad aspettare il mio ticket {ticket}")
            time.sleep(random.randint(1,3))
            print(f"Sono l'utente {get_ident()}, ho preso un caffÃ¨ e adesso aspetto il mio ticket: {ticket}")
            self.sede.waitForTickets(lista) 



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
            time.sleep(random.randint(1,4))
            #
            # Notifica di voler stampare il riepilogo attese 
            #
            if random.randint(0,5) >= 4:
                self.sede.printAttese()





class Display(Thread):
    def __init__(self, sede):
        Thread.__init__(self)
        self.sede = sede
        

    def run(self):
        while True:
            self.sede.printUltimi()
            





sede = Sede(6)

display = Display(sede)
display.start()


utenti = [Utente(sede) for p in range(10)]
impiegato = [Impiegato(sede, i) for i in "ABCDEF"]
utentiFurbetti = [UtenteFurbetto(sede) for p in range(3)] 



for p in utenti:
    p.start()
for p in utentiFurbetti:
    p.start() 
for i in impiegato:
    i.start()