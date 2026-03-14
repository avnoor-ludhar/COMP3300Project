class Task:
    def __init__(self, pid, arrival, burst, priority):
        self.pid: str = pid
        self.arrival: int = arrival
        self.burst: int = burst
        self.priority: int = priority
        self.remaining: int = burst
        self.start_time: int | None = None
        self.finish_time: int | None = None

    def turnaround_time(self) -> int:
        return self.finish_time - self.arrival

    def waiting_time(self) -> int:
        return self.turnaround_time() - self.burst

    def __repr__(self):
        return f"Task(pid={self.pid}, arrival={self.arrival}, burst={self.burst}, priority={self.priority})"