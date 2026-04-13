# COMP3300 Project
Project Option 1: CPU Scheduling Simulator

Group members (alphabetical):
- Aleksa Vucak
- Avnoor Ludhar
- Fied Elahresh
- Hashir Khan

## Scheduler Design Decisions

The CPU scheduling simulations are implemented in `scheduler.py` using data structures to manage tasks across the four different scheduling policies.

### 1. First-In, First-Out (FIFO)
**Design:** FIFO is implemented as a non-preemptive algorithm using a basic minimum heap (`min_heap`). The heap primarily sorts tasks based on their arrival time and tie-breaks with lexicographically smallest PID. As tasks arrive, they are popped from the heap and sequentially processed to completion without interruption.

### 2. Shortest Job First (SJF)
**Design:** SJF is implemented as a non-preemptive algorithm utilizing a two-heap structure:
- **`inactive_heap`**: Stores processes that haven't arrived yet, sorted by their expected arrival time.
- **`ready_heap`**: Stores processes that have arrived and are active in the system, sorted primarily by their burst time (task length) with ties broken using PID.
As time progresses, tasks move from the inactive heap to the ready heap. The task with the shortest burst time is popped and run to completion.

### 3. Round Robin (RR)
**Design:** Round Robin is a preemptive scheduling algorithm constructed using double-ended queues (`deque`):
- **`inactive_task_queue`**: Sequentially stores tasks waiting to arrive.
- **`active_task_queue`**: Maintains the cyclical queue of ready-to-execute tasks.
Tasks pop off the active queue and run up to a specified time `quantum`. If a task isn't finished within this limit, its remaining time is decremented, and it is placed back into the active queue. The scheduler at the same time ensures that newly arriving tasks join the active queue properly.

### 4. Priority Algorithm
**Design:** The Priority scheduling algorithm mirrors SJF's non-preemptive two-heap structure (`inactive_heap` and `ready_heap`).
- Priority is numerically determined, where a lower priority number means higher precedence (e.g. 1 is higher priority than 2).
- The `ready_heap` surfaces tasks based on their priority number, allocating the CPU to the highest priority processes first.

---

## Tie-Breaking Policies

To guarantee deterministic and consistent behavior when multiple tasks contend with one another when they have the same scheduling metric, the tie-breaking protocols below have been enforced:

- **SJF and Priority:** In the `ready_heap`, if multiple processes share the exact same burst time (SJF) or equal priority status (Priority), the tie is broken lexicographically by the smallest Process ID (PID). (e.g. "A" is prioritized over "B").
- **Round Robin:** When a task's quantum expires at the same time new tasks arrive, the preempted task and newly arrived tasks are grouped and sorted by PID before being appended to the active queue, ensuring deterministic tie-breaking.
- **FIFO:** The `min_heap` resolves arrival collisions by checking PID. If two or more tasks possess an identical arrival time, the task with the lexicographically smallest PID is prioritized.

---

## Complexity Analysis

- **FIFO:** Time complexity is O(n log n) due to heap construction and n extractions. Space complexity is O(n) for the heap.
- **SJF:** Time complexity is O(n log n) since each task is inserted and removed from heaps in O(log n). Space complexity is O(n).
- **Round Robin:** Time complexity is O(n log n) due to initial sorting and occasional sorting for tie-breaking; scheduling itself is O(n) with a fixed quantum. Space complexity is O(n) for the queues.
- **Priority:** Time complexity is O(n log n) from heap operations for selecting the next task. Space complexity is O(n).

---

## Testing

The test suite validates all scheduling algorithms using JSON fixtures. Tests exercise the same code paths as the CLI (`main.py`).

### Running Tests

Install development dependencies (pytest):

```bash
pip install -r requirements-dev.txt
```

Execute the full test suite:

```bash
python3 -m pytest tests/ -v
```

Runs 32 tests (8 per algorithm).

### Test Structure

**Test Files:** `test_fifo.py`, `test_sjf.py`, `test_rr.py`, `test_priority.py`

**Fixtures:** `/tests/fixtures/{fifo,sjf,rr,priority}/` - 8 JSON test cases per algorithm

### Coverage

- **Single task:** Basic scheduling without contention
- **Simultaneous arrivals:** Tie-breaking at time 0
- **Idle periods:** CPU idle behavior
- **Staggered arrivals:** Tasks arriving mid-execution
- **Boundary conditions:** Tasks arriving exactly at completion times
- **Tie-breaking:** PID-based resolution for equal priority/burst times

The `_load_and_test()` helper mirrors `main.py`: `open()` -> `json.load()` -> `parse_tasks()` -> `schedule()` -> `build_output()`. This validates the full JSON loading pipeline, not just scheduling logic.

---

## CI/CD

GitHub Actions runs the test suite on every push and pull request to `main`. The workflow:

1. Checks out the repository
2. Sets up Python 3.13 with pip caching
3. Installs dependencies from `requirements-dev.txt`
4. Runs `pytest -q`

See `.github/workflows/tests.yml` for configuration.

---

## AI Usage Statement

AI tools were used as a collaborative assistant across key stages of the project, supporting discussions around algorithm implementation details such as queue management in Round Robin and heap utilization in SJF and Priority scheduling. They helped reason through complex edge cases (e.g., tie-breaking protocols during arrival collisions and preemption boundaries) during the refinement of the CPU scheduling simulator. AI tools were also used to generate test cases to ensure the correctness of the scheduling logic. Additionally, AI tools were used to review written work, providing feedback on clarity, structure, and overall quality to improve the final documentation. We acknowledge that we understand all submitted code and that we remain responsible for correctness and design.
