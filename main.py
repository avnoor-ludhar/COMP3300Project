import json
import sys
from scheduler import Scheduler
from task import Task

#Ask prof about if the input will be normalized
#Ask prof about if we can assume input includes unique PIDs
#Ask prof about quantum case that we were going for in RR where 2 tasks after a quantum need to tie break
#Ask prof for Gannt chart in RR if we have C run for 1 quantum and rerun again for another should we merge the gantt chart items
#like in this example: [GanttObject(pid=A, start=0, end=2), GanttObject(pid=A, start=2, end=4), GanttObject(pid=A, start=4, end=6), GanttObject(pid=B, start=6, end=8), GanttObject(pid=C, start=8, end=10), GanttObject(pid=B, start=10, end=12), GanttObject(pid=C, start=12, end=13)]

def parse_tasks(json_load) -> Scheduler:
    parsed_jobs = [Task(j["pid"], j["arrival"], j["burst"], j["priority"]) for j in json_load["jobs"]]
    scheduler = Scheduler(json_load["policy"], parsed_jobs, json_load["quantum"])

    return scheduler

if __name__ == "__main__":
    input_file = sys.argv[1]

    with open(input_file) as f:
        json_load = json.load(f)
    
    scheduler = parse_tasks(json_load)
    result = scheduler.schedule()

    print(result)
    #print(json.dumps(result, indent=2))
