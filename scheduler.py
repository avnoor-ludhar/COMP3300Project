from typing import List
from task import Task
from collections import deque
import heapq

class GanttObject:
    """Single execution segment in the Gantt chart (one task on CPU for a time range)."""

    def __init__(self, pid, start, end = None):
        self.pid = pid
        self.start = start
        self.end = end

    def to_dict(self):
        return {
            "pid": self.pid,
            "start": self.start,
            "end": self.end
        }

    def __repr__(self):
        return f"GanttObject(pid={self.pid}, start={self.start}, end={self.end})"


def gantt_to_dicts(gantt: List[GanttObject]) -> List[dict]:
    # Convert Gantt objects to serializable dicts for JSON output.
    return [segment.to_dict() for segment in gantt]


class Scheduler:
    """Orchestrates CPU scheduling across four different policies.

    Entry point is schedule() which delegates to the appropriate algorithm.
    Each algorithm returns a Gantt timeline of process execution segments.
    """

    def __init__(self, policy, jobs, quantum=0):
        self.policy: str = policy
        self.jobs: List[Task] = jobs
        self.quantum: int = quantum  # only used for Round Robin

    def schedule(self):
        # Dispatch to the appropriate scheduling algorithm based on policy.
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

    def round_robin(self) -> List[GanttObject]:
        """Round Robin: preemptive scheduling with fixed time quantum.

        Flow: Sort tasks by arrival -> pop from inactive to active queue ->
        run for quantum or until completion -> handle mid-quantum arrivals ->
        preempted task goes to back of queue -> repeat until all tasks complete.
        """
        inactive_task_queue = deque(sorted(self.jobs, key=lambda task: (task.arrival, task.pid)))
        active_task_queue = deque()
        time = 0
        gantt_timeline: List[GanttObject] = []

        while active_task_queue or inactive_task_queue:
            if not active_task_queue:
                active_task_queue.append(inactive_task_queue.popleft())

            task_to_run: Task = active_task_queue.popleft()
            time_start = max(task_to_run.arrival, time)

            if task_to_run.start_time is None:
                task_to_run.start_time = time_start
        
            time_for_job = min(self.quantum, task_to_run.remaining)
            time = time_start + time_for_job
            task_to_run.remaining -= time_for_job

            # Move tasks that arrived mid-quantum to active queue first
            earlier_arrivals = []
            while inactive_task_queue and time > inactive_task_queue[0].arrival:
                earlier_arrivals.append(inactive_task_queue.popleft())

            # Tasks arriving exactly at quantum boundary need tie-breaking by PID
            boundary_arrivals = []
            while inactive_task_queue and inactive_task_queue[0].arrival == time:
                boundary_arrivals.append(inactive_task_queue.popleft())

            if task_to_run.remaining == 0:
                task_to_run.finish_time = time
            else:
                boundary_arrivals.append(task_to_run)  # preempted task goes back into ready state

            active_task_queue.extend(earlier_arrivals)
            active_task_queue.extend(sorted(boundary_arrivals, key=lambda task: task.pid))  # deterministic tie-break
            gantt_timeline.append(GanttObject(task_to_run.pid, time_start, time))
        
        return gantt_timeline


    def fifo(self) -> List[GanttObject]:
        """First-In-First-Out: non-preemptive, arrival time determines order.

        Flow: Build heap by arrival time -> pop earliest arriving task ->
        run to completion -> repeat until all tasks complete.
        """
        min_heap = [(task.arrival, task.pid, task.burst) for task in self.jobs]
        pid_task_dict = {task.pid: task for task in self.jobs}
        heapq.heapify(min_heap)

        curr_time = 0
        gantt_timeline: List[GanttObject] = []
        while min_heap:
            arrival_t, curr_task_pid, task_length = heapq.heappop(min_heap)
            start_time = max(curr_time, arrival_t)
            end_time = start_time + task_length

            task = pid_task_dict[curr_task_pid]
            task.start_time = start_time
            task.finish_time = end_time

            gantt_timeline.append(GanttObject(curr_task_pid, start_time, end_time))
            curr_time = end_time

        return gantt_timeline

        

    def sjf(self) -> List[GanttObject]:
        """Shortest Job First: non-preemptive, shortest burst time determines order.

        Flow: Build inactive heap by arrival -> move arrived tasks to ready heap by burst time ->
        pop shortest job -> run to completion -> repeat until all tasks complete.
        """
        ready_heap = []  # tasks that have arrived, sorted by burst time (shortest first)
        inactive_heap = [(task.arrival, task.burst, task.pid) for task in self.jobs]  # tasks not yet arrived
        pid_task_dict = {task.pid: task for task in self.jobs}
        heapq.heapify(inactive_heap)

        time = 0
        gantt_timeline: List[GanttObject] = []
        while ready_heap or inactive_heap:
            while inactive_heap and time >= inactive_heap[0][0]:
                curr_arrival, curr_burst, curr_pid = heapq.heappop(inactive_heap)
                heapq.heappush(ready_heap, (curr_burst, curr_pid, curr_arrival))
            if not ready_heap:
                time = inactive_heap[0][0]
                continue

            task_length, task_pid, task_arrival = heapq.heappop(ready_heap)
            start_time = max(time, task_arrival)
            end_time = start_time + task_length

            task = pid_task_dict[task_pid]
            task.start_time = start_time
            task.finish_time = end_time

            gantt_timeline.append(GanttObject(task_pid, start_time, end_time))
            time = end_time

        return gantt_timeline


    def priority(self) -> List[GanttObject]:
        """Priority Scheduling: non-preemptive, lowest priority number determines order.

        Flow: Build inactive heap by arrival -> move arrived tasks to ready heap by priority ->
        pop highest priority job (lowest number) -> run to completion -> repeat until all tasks complete.
        """
        ready_heap = []  # tasks that have arrived, sorted by priority (lower = higher priority)
        inactive_heap = [(task.arrival, task.priority, task.pid) for task in self.jobs]  # tasks not yet arrived
        pid_task_dict = {task.pid: task for task in self.jobs}
        heapq.heapify(inactive_heap)

        time = 0
        gantt_timeline: List[GanttObject] = []

        while ready_heap or inactive_heap:
            while inactive_heap and time >= inactive_heap[0][0]:
                curr_arrival, curr_priority, curr_pid = heapq.heappop(inactive_heap)
                heapq.heappush(ready_heap, (curr_priority, curr_pid, curr_arrival))
            if not ready_heap:
                time = inactive_heap[0][0]
                continue

            task_priority, task_pid, task_arrival = heapq.heappop(ready_heap)
            task = pid_task_dict[task_pid]

            start_time = max(time, task_arrival)
            end_time = start_time + task.burst

            task.start_time = start_time
            task.finish_time = end_time

            gantt_timeline.append(GanttObject(task_pid, start_time, end_time))
            time = end_time

        return gantt_timeline
