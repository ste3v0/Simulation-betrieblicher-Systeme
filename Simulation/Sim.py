import simpy

env = simpy.Environment()

def kunde(env,kunID,einkaufszeit):
    schlange1 = kasse1.queue
    schlange2 = kasse2.queue
    schlange3 = kasse3.queue

    print ('Kunde ',kunID,' betritt laden', env.now)
    yield env.timeout(einkaufszeit)
    print ('Kunde ', kunID,' steht an Kasse', env.now)

    print (len(schlange1), ' Kunden an Kasse')
    if len(schlange1)<6:
        with kasse1.request(priority=1) as kassereq:
            yield kassereq
            yield env.timeout(1)
            print ('Kunde ',kunID,' verlässt Laden', env.now)
            return 1
    elif len(schlange2)<6:
        with kasse2.request(priority=1) as kassereq:
            yield kassereq
            yield env.timeout(1)
            print ('Kunde ',kunID,' verlässt Laden', env.now)
            return 2
    else:
        with kasse3.request(priority=1) as kassereq:
            yield kassereq
            yield env.timeout(1)
            print ('Kunde ',kunID,' verlässt Laden', env.now)
            return 3

   



def genKunde(env,Kundencount,frequenzzeit):
    kunID = 0
    while kunID<Kundencount:
        kunID +=1
        env.process(kunde(env,kunID,3))
        yield env.timeout(frequenzzeit)

env.process(genKunde(env,100,0.5))
kasse1 = simpy.PriorityResource(env, capacity = 1)
kasse2 = simpy.PriorityResource(env, capacity = 1)
kasse3 = simpy.PriorityResource(env, capacity = 1)

def ware(env,Menge,Uhrzeit):
    while Menge>0:





env.run(until=20)
    
