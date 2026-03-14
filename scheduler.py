from typing import List
from task import Task

class Scheduler:
    def __init__(self, policy: str, jobs: List[Task], quantum=0,):
        self.policy = policy
        self.jobs = jobs
        self.quantum = quantum

    def schedule(self):
        policy = self.policy.upper()

        if policy == "FIFO":
            return self.fifo()
        elif policy == "SJF":
            return self.sjf()
        elif policy == "RR":
            return self.round_robin()
        elif policy == "PRIORITY":
            return self.priority()
        else:
            raise ValueError(f"Unsupported scheduling policy: {self.policy}")

    def round_robin(self):
        raise NotImplementedError

    def fifo(self):
        raise NotImplementedError

    def sjf(self):
        raise NotImplementedError
    
    #Chooses highest priority process instead of smallest length to determine next run
    def priority(self):
        raise NotImplementedError
    
    #Optional to ensure full marks would probably be fun
    def MLFQ(self):
        pass