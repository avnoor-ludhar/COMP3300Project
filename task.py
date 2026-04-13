class Task:
    def __init__(self, pid, arrival, burst, priority):
        self.pid: str = pid
        self.arrival: int = arrival
        self.burst: int = burst
        self.priority: int = priority
        self.remaining: int = burst  # tracks remaining time for preemptive scheduling
        self.start_time: int | None = None  # populated when scheduler runs
        self.finish_time: int | None = None  # populated when process completes

    def turnaround_time(self) -> int:
        # Total time from arrival to completion (finish - arrival).
        return self.finish_time - self.arrival

    def waiting_time(self) -> int:
        # Time spent waiting in ready queue (turnaround - burst).
        return self.turnaround_time() - self.burst

    def __repr__(self):
        return f"Task(pid={self.pid}, arrival={self.arrival}, burst={self.burst}, priority={self.priority})"