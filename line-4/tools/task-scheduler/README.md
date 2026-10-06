# Task scheduler

Turns task dependencies, durations, deadlines, and shared resource capacities into an offline schedule. Uses Python 3 standard library only, reads JSON from stdin, and never reads files, environment variables, credentials or chain state. Nothing is sent.

From repository root:

```sh
python3 line-4/tools/task-scheduler/schedule.py --demo
```

The demo plans inspection, building, writing tests and verification for two workers. It finished in 8 time units and met the verification deadline. This is an illustrative plan, not a claim about measured worker execution times.

For real work, pipe your own JSON object to the same command without `--demo`. Input has `resources` (name to positive integer capacity) and a nonempty `tasks` array. Each task has a unique string `id`, positive integer `duration`, optional `after` array of dependency ids, optional `resources` demands and optional nonnegative integer `deadline`. Choose one common time unit. All tasks are available at time zero and run without interruption. A task with no resource demand can overlap freely. Dependencies must finish before a task starts; equality at a deadline passes.

The algorithm starts ready tasks in deadline then id order when capacity permits. It rejects unknown dependencies, cycles and invalid demands. Output reports the schedule, makespan and missed deadlines. A missed deadline is a limitation of this heuristic schedule, not proof that no feasible schedule exists. No execution, worker discovery, cost estimation or payment is implemented. This piece needs no coin; future payment features should use real ZTO first and IMD second.

Local checks covered parallelism, dependency ordering, resource limits, cycles, invalid inputs and deadline misses. The next useful pieces are measured duration estimates, release times and improved search for deadline feasibility.
