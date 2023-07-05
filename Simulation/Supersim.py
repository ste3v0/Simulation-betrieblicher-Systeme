import simpy
import random

def stundenZuSekunden(stundenzahl):
    return stundenzahl*3600
def minutenZuSekunden(minutenzahl):
    return minutenzahl*60
def sekundenZuStunden(sekundenzahl):
    return sekundenzahl/3600

env = simpy.rt.RealtimeEnvironment(initial_time = stundenZuSekunden(5),factor = 0.0001, strict = False)

class Supermarkt:
    def __init__(self, env, mitarbeiterzahl):
        self.env = env
        self.mitarbeiterzahl = mitarbeiterzahl
        self.kasse1 = simpy.PreemptiveResource(env, capacity = 1)
        self.kasse2 = simpy.PreemptiveResource(env, capacity = 1)
        self.kasse3 = simpy.PreemptiveResource(env, capacity = 1)
        if mitarbeiterzahl > 3:
            self.anderemitarbeiter = simpy.PreemptiveResource(env, capacity=mitarbeiterzahl-3)
        self.kunden_in_kasse = 5  # Mindestanzahl von Kunden, um Kasse 2 zu öffnen

    def setMitarbeiterzahl(self,mitarbeiterzahl):
        self.mitarbeiterzahl = mitarbeiterzahl
            

    def einkauf(self, kunID, einkaufszeit):
        schlange1 = self.kasse1.queue
        schlange2 = self.kasse2.queue
        #print(f"{self.env.now}: Kunde {kunID} betritt Markt")
        yield self.env.timeout(einkaufszeit)
        #print(f"{self.env.now}: Kunde {kunID} steht an Kasse")

        if len(schlange1)<=self.kunden_in_kasse:
            with self.kasse1.request(priority=1,preempt=True) as kassereq:
                yield kassereq
                #print(f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} wird an Kasse 1 bedient.")
                yield self.env.timeout(40)
                #print (f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} verlässt laden")
        elif len(schlange2)<=self.kunden_in_kasse:
            with self.kasse2.request(priority=1, preempt= True) as kassereq:
                yield kassereq
                #print(f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} wird an Kasse 2 bedient.")
                yield self.env.timeout(40)
                #print (f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} verlässt laden")
        else:
            with self.kasse3.request(priority=1,preempt= True) as kassereq:
                yield kassereq
                #print(f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} wird an Kasse 3 bedient.")
                yield self.env.timeout(40)
                #print (f"{sekundenZuStunden(self.env.now)}: Kunde {kunID} verlässt laden")

    def ware(self, rolliID,processtime):
        if len(self.kasse3.queue) == 0:
            with self.kasse3.request(priority=3,preempt=False) as req1:
                yield req1
                print (f"{sekundenZuStunden(self.env.now)}: Rolli {rolliID} wird angefangen")
                beginn = self.env.now
                try:
                    yield self.env.timeout(stundenZuSekunden(processtime))
                    print (f"{sekundenZuStunden(self.env.now)}: Rolli {rolliID} ist fertig")
                except simpy.Interrupt as interrupt:
                    restzeit = self.env.now - beginn
                    print (f"{sekundenZuStunden(self.env.now)}: Kasse 3 wird besetzt")
                    self.env.process(self.ware(rolliID,processtime-sekundenZuStunden(restzeit)))
        elif len(self.kasse2.queue) == 0:
            with self.kasse2.request(priority=3,preempt= False) as req2:
                yield req2
                print (f"{sekundenZuStunden(self.env.now)}: Rolli {rolliID} wird angefangen")
                beginn = self.env.now
                try:
                    yield self.env.timeout(stundenZuSekunden(processtime))
                    print (f"{sekundenZuStunden(self.env.now)}: Rolli {rolliID} ist fertig")
                except simpy.Interrupt as interrupt:
                    restzeit = self.env.now - beginn
                    print (f"{sekundenZuStunden(self.env.now)}: Kasse 2 wird besetzt")
                    self.env.process(self.ware(rolliID,processtime-sekundenZuStunden(restzeit)))
        else:
            if self.mitarbeiterzahl > 3:
                with self.anderemitarbeiter.request(priority=3,preempt=False) as req3:
                    yield req3
                    print (f"{sekundenZuStunden(self.env.now)}: Rolli {rolliID} wird angefangen")
                    yield self.env.timeout(stundenZuSekunden(processtime))
                    print (f"{sekundenZuStunden(self.env.now)}: Rolli {rolliID} ist fertig")



            



    
def genKunden(env, supermarkt,frequenzzeit,zeitfenster):
    kunID = 0
    while env.now < stundenZuSekunden(zeitfenster):
        kunID+=1
        env.process(supermarkt.einkauf(kunID,3))
        yield env.timeout(minutenZuSekunden(frequenzzeit))

def genWare(env, supermarkt, Menge, ankunftszeit):
    yield env.timeout(stundenZuSekunden(ankunftszeit-5))
    rolliID = 1
    while rolliID <= Menge:
        env.process(supermarkt.ware(rolliID,0.75))
        rolliID +=1
        yield env.timeout(0)


def genWare(env, supermarkt, Menge, ankunftszeit):
    yield env.timeout(stundenZuSekunden(ankunftszeit-5))
    rolliID = 1
    while rolliID <= Menge:
        env.process(supermarkt.ware(rolliID,0.75))
        rolliID +=1
        yield env.timeout(0)








def Dienstag(env):
    supermarkt = Supermarkt(env,4)

    env.process(genWare(env,supermarkt,4,5))
    env.process(genWare(env, supermarkt, 12,10))
    env.process(genWare(env, supermarkt,3,19))

    env.process(genKunden(env, supermarkt, 1, 9))
    env.process(genKunden(env, supermarkt,0.5,11))
    env.process(genKunden(env, supermarkt, 0.7, 16))
    env.process(genKunden(env, supermarkt, 0.4, 19))
    env.process(genKunden(env, supermarkt, 0.6, 21.5))
    env.process(genKunden(env, supermarkt, 0.4, 22))
    yield env.timeout(0)








    
env.process(Dienstag(env))
env.run(until=stundenZuSekunden(22.3))






