import Queue
import threading
import time


exitFlag = 0
queueLock = threading.Lock()
global exitFlag,queueLock

exitFlag = 0
queueLock = threading.Lock()

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.q)
        print "Exiting " + self.name

def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            data.download()
            data.parse()
            data.nlp()
            print " %s processing" % (threadName)
        else:
            queueLock.release()
        time.sleep(1)

