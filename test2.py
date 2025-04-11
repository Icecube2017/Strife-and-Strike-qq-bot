import threading
import time

EndTimer = 0

class TimingThread(threading.Thread):
    def __init__(self, threadid, name, counter):
        threading.Thread.__init__(self)
        self.id = threadid
        self.name = name
        self.counter = counter

    def run(self):
        global EndTimer
        print('Starting ' + self.name)
        while self.counter:
            if EndTimer == 1:
                EndTimer = 0
                break
            print(self.counter)
            time.sleep(1)
            self.counter -= 1
        print('Exiting ' + self.name)

class EndThread(threading.Thread):
    def __init__(self, threadid, name):
        threading.Thread.__init__(self)
        self.id = threadid
        self.name = name
    
    def run(self):
        global EndTimer
        print('Starting ' + self.name)
        EndTimer = 1

def toendthread():
    global EndTimer
    EndTimer = 1

'''thread1 = TimingThread(1, 'Thread-1', 15)
thread2 = EndThread(2, "Thread-2")
thread1.start()
time.sleep(5)
thread2.start()'''


def part_same(part: str, whole: str):
    is_same = False
    _x = len(whole) - len(part)
    for i in range(0, _x + 1):
        if part == whole[i:i + len(part)]:
            is_same = True
    return is_same

s1 = 'asdf'
s2 = s1 *2
print(s2)