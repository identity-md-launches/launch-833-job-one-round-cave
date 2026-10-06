#!/usr/bin/env python3
"""Deterministic, offline list scheduling; no filesystem or network access."""
import argparse
import json
import sys


def schedule(data):
    capacities = data.get('resources', {})
    if not isinstance(capacities, dict) or any(type(v) is not int or v < 1 for v in capacities.values()):
        raise ValueError('resource capacities must be positive integers')
    tasks = data.get('tasks')
    if not isinstance(tasks, list) or not tasks:
        raise ValueError('tasks must be a nonempty list')
    by_id = {}
    for task in tasks:
        name = task.get('id')
        if not isinstance(name, str) or not name or name in by_id:
            raise ValueError('task ids must be unique nonempty strings')
        if type(task.get('duration')) is not int or task['duration'] < 1:
            raise ValueError('durations must be positive integer time units')
        deps = task.get('after', [])
        if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps) or len(set(deps)) != len(deps):
            raise ValueError('after must contain unique task ids')
        demand = task.get('resources', {})
        if not isinstance(demand, dict) or any(r not in capacities or type(n) is not int or n < 1 or n > capacities[r] for r, n in demand.items()):
            raise ValueError('resource demand exceeds capacity or is invalid')
        deadline = task.get('deadline')
        if deadline is not None and (type(deadline) is not int or deadline < 0):
            raise ValueError('deadline must be a nonnegative integer')
        by_id[name] = task
    for task in tasks:
        if any(d not in by_id for d in task.get('after', [])):
            raise ValueError('unknown dependency')
    pending = set(by_id)
    completed = set()
    running = {}
    rows = {}
    now = 0
    while pending or running:
        for name in list(running):
            if running[name] <= now:
                completed.add(name)
                del running[name]
        available = dict(capacities)
        for name in running:
            for resource, amount in by_id[name].get('resources', {}).items():
                available[resource] -= amount
        ready = sorted((name for name in pending if set(by_id[name].get('after', [])) <= completed),
                       key=lambda name: (by_id[name].get('deadline', float('inf')), name))
        for name in ready:
            task = by_id[name]
            demand = task.get('resources', {})
            if all(available[r] >= n for r, n in demand.items()):
                end = now + task['duration']
                rows[name] = {'id': name, 'start': now, 'end': end}
                running[name] = end
                pending.remove(name)
                for resource, amount in demand.items():
                    available[resource] -= amount
        if running:
            now = min(running.values())
        elif pending:
            raise ValueError('dependency cycle: ' + ', '.join(sorted(pending)))
    result = sorted(rows.values(), key=lambda row: (row['start'], row['id']))
    missed = [row['id'] for row in result if by_id[row['id']].get('deadline') is not None and row['end'] > by_id[row['id']]['deadline']]
    return {'schedule': result, 'makespan': max(row['end'] for row in result),
            'deadlines_met': not missed, 'missed_deadlines': missed,
            'method': 'nonpreemptive earliest-deadline list scheduling; heuristic, not an optimality proof'}


DEMO = {'resources': {'worker': 2}, 'tasks': [
    {'id': 'inspect', 'duration': 2, 'resources': {'worker': 1}},
    {'id': 'build', 'duration': 4, 'after': ['inspect'], 'resources': {'worker': 1}},
    {'id': 'write-tests', 'duration': 3, 'after': ['inspect'], 'resources': {'worker': 1}},
    {'id': 'verify', 'duration': 2, 'after': ['build', 'write-tests'], 'resources': {'worker': 2}, 'deadline': 8}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true', help='run the built-in worker planning example')
    args = parser.parse_args()
    try:
        data = DEMO if args.demo else json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError('input must be an object')
        print(json.dumps(schedule(data), indent=2))
    except (ValueError, TypeError, AttributeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
