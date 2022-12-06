
from ecolib.threader import Threader
from threading import Thread

y = 2000

threader_pool = []


def printYear(triggerToSuspendAll):
    global y
    print(y)
    y += 1

    if y == 2005:
        print("2005 atingido, esperando 20 segs")
        triggerToSuspendAll()


T = Threader(lambda: threader_pool, 6, delay_config={"delay": 5, "instances_before_delay": 10})
for x in range(0, 20):
    threader_pool.append(Thread(target=printYear, args=(lambda: T.suspendAllForXTime(20),)))
T.dispatch(endFunc=lambda s, e: print("end_cycle: [" + str(s) + "->" + str(e) + "]"))
