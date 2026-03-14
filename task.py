class Task:
    def __init__(self, pid, arrival, burst, priority):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst
        self.start_time = None
        self.finish_time = None

    def turnaround_time(self):
        return self.finish_time - self.arrival

    def waiting_time(self):
        return self.turnaround_time() - self.burst

    def __repr__(self):
        return f"Task(pid={self.pid}, arrival={self.arrival}, burst={self.burst}, priority={self.priority})"