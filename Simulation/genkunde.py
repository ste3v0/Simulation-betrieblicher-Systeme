def genKunden(env, supermarkt, a, b, c, d ,e):
    yield env.timeout(stundenZuSekunden(2))
    global kunID
    hebel = 0,5
    kunID = 0
    while True:
        
        if 7 <= sekundenZuStunden(env.now) < 8:      # 7-8 Uhr
            frequenzzeit = random.uniform(a - hebel, a + hebel)
        elif 8 <= sekundenZuStunden(env.now) < 10:   # 8-10 Uhr
            frequenzzeit = random.uniform(b - hebel, b + hebel)
        elif 10 <= sekundenZuStunden(env.now) < 15:  # 10-15 Uhr
            frequenzzeit = random.uniform(c - hebel, c + hebel)
        elif 15 <= sekundenZuStunden(env.now) < 20:  # 15-20 Uhr
            frequenzzeit = random.uniform(d - hebel, d + hebel)
        elif 20 <= sekundenZuStunden(env.now) < 22:  # 20-22 Uhr
            frequenzzeit = random.uniform(e - hebel, e + hebel)
        else:                                        # nach 22 Uhr 
            frequenzzeit = 1

        kunID+=1
        
        env.process(supermarkt.einkauf(kunID,minutenZuSekunden(random.uniform(1, 29))))
        yield env.timeout(minutenZuSekunden(frequenzzeit))
