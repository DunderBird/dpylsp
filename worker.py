import threading
import queue
import logging

logger = logging.getLogger(__name__)
class Worker:
    '''
        Producer-Consumer
    '''
    def __init__(self, name='', count=1):
        self.q = queue.Queue()
        self.count = count
        self.name = name
        self.worker_list = [threading.Thread(target=self.work) for i in range(count)]
    
    def start(self):
        for worker in self.worker_list:
            worker.start()
    
    def close(self):
        self.q.join()
        for i in range(self.count):
            self.q.put(None)
        for worker in self.worker_list:
            worker.join()
    
    def assign(self, func, *args, **kwargs):
        self.q.put((func, args, kwargs))

    def work(self):
        while True:
            task = self.q.get()
            if task is None:
                break
            task[0](*task[1], **task[2])
            self.q.task_done()