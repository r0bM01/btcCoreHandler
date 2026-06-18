
import queue
import lib.base_logger


class Logger:
    def __init__(self, logs_dir):
        self.base_logger = lib.base_logger.BaseLogger(logs_dir, verbose = True)
        self.is_working = False
        self.queue = queue.Queue()
    
    def worker(self):
        while self.is_working:
            log = self.queue.get()
            self.base_logger.add(log['type'], log['message'], log['args'])
            self.queue.task_done()
    
    def info(self, message, *args):
        log = {
            'type': "log",
            'message': message,
            'args': [a for a in args]}
        self.queue.put(log)

    def warning(self):
        pass

    def critical(self):
        pass

        