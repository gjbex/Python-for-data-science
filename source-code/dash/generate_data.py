#!/usr/bin/env python

from argparse import ArgumentParser
import csv
from datetime import datetime, timedelta
import random


class Node_info:

    def __init__(self, node_name):
        self._name = node_name
        self._cpu_load = None
        self._mem_load = None
        self._jobs = list()

    @property
    def name(self):
        return self._name

    def add_job_id(self, job_id):
        self._jobs.append(job_id)

    @property
    def _job_ids(self):
        return ','.join(self._jobs)

    @property
    def job_ids(self):
        return self._jobs.copy()

    @property
    def state(self):
        return 'busy' if self._jobs else 'idle'

    @property
    def cpu_load(self):
        return self._cpu_load

    @cpu_load.setter
    def cpu_load(self, cpu_load):
        self._cpu_load = cpu_load

    @property
    def mem_load(self):
        return self._mem_load

    @mem_load.setter
    def mem_load(self, mem_load):
        self._mem_load = mem_load

    def __repr__(self):
        repr = f'{self.name}\n'
        repr += f'\tstate = {self.state}\n'
        repr += f'\tjobs = {self._job_ids}\n'
        repr += f'\tstatus = cpu_load={self.cpu_load};mem_load={self.mem_load}\n'
        return repr

    
class Job:

    def __init__(self, job_id, nr_nodes, walltime):
        self._job_id = job_id
        self._nr_nodes = nr_nodes
        self._nodes = list()
        self._walltime = timedelta(seconds=walltime)
        self._remaining = None

    @property
    def job_id(self):
        return f'{self._job_id:05d}'

    @property
    def nr_nodes(self):
        return self._nr_nodes

    @property
    def nodes(self):
        return self._nodes.copy()

    @property
    def walltime(self):
        return self._walltime

    @property
    def remaining(self):
        return self._remaining

    def start(self, nodes):
        self._nodes = nodes.copy()
        self._remaining = self._walltime

    def update(self, delta):
        self._remaining -= delta

    @property
    def is_done(self):
        return self._remaining <= timedelta(seconds=0)

    def __repr__(self):
        return f'{self.job_id}  {self.nr_nodes}  {self.walltime}'


class ResoureManager:

    def __init__(self, nodes):
        self._free_nodes = list(nodes)
        self._busy_nodes = set()
        self._queue = list()
        self._running = set()
        self._completed = set()
        self._next_id = 1

    @property
    def nr_nodes(self):
        return len(self._free_nodes) + len(self._busy_nodes)
    
    @property
    def nr_free_nodes(self):
        return len(self._free_nodes)

    @property
    def running_jobs(self):
        return self._running

    def is_free(self, node):
        return node in self._free_nodes

    def is_busy(self, node):
        return node in self._busy_nodes

    def qstat(self):
        for job in self._queue:
            print(job, 'Q')
        for job in self._running:
            print(job, job.remaining, 'R')

    def submit(self):
        self._queue.append(Job(self._next_id,
                               random.randrange(1, self.nr_nodes),
                               random.randint(5, 50)))
        self._next_id += 1
        
    def cycle(self, delta):
        # check running jobs to see whether they are done
        for job in self._running:
            job.update(delta)
            if job.is_done:
                nodes = job.nodes
                for node in nodes:
                    self._busy_nodes.remove(node)
                self._free_nodes.extend(nodes)
                self._completed.add(job)
        for job in self._completed:
            if job in self._running:
                self._running.remove(job)
        # start all jobs that can be started
        for job in self._queue:
            if not self._free_nodes:
                break
            if job.nr_nodes <= self.nr_free_nodes:
                nodes = [self._free_nodes.pop(0) for _ in range(job.nr_nodes)]
                for node in nodes:
                    self._busy_nodes.add(node)
                job.start(nodes)
                self._running.add(job)
        for job in self._running:
            if job in self._queue:
                self._queue.remove(job)


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='generate data')
    arg_parser.add_argument('--nr-nodes', type=int, default=1,
                            help='number of nodes to generate data for')
    arg_parser.add_argument('--nr-timesteps', type=int, default=10,
                            help='number of timesteps')
    arg_parser.add_argument('--nr-jobs', type=int, default=5,
                            help='number of jobs to submit')
    arg_parser.add_argument('file', help='prefix name of the file to write to')
    options = arg_parser.parse_args()
    time = datetime.now()
    delta = timedelta(seconds=5)
    nodes = [f'node_{i + 1:03d}' for i in range(options.nr_nodes)]
    resource_manager = ResoureManager(nodes)
    for _ in range(options.nr_jobs):
        resource_manager.submit()
    with open(f'{options.file}_load.csv', 'w', newline='') as csv_load_file:
        csv_load_writer = csv.writer(csv_load_file)
        csv_load_writer.writerow(['time', 'node', 'cpu_load', 'mem_load'])
        with open(f'{options.file}_jobs.csv', 'w', newline='') as csv_jobs_file:
            csv_jobs_writer = csv.writer(csv_jobs_file)
            csv_jobs_writer.writerow(['time', 'job_id', 'node'])
            for _ in range(options.nr_timesteps):
                print('-'*36)
                print(f'---- {time} ----')
                node_infos = dict()
                time_str = datetime.strftime(time, '%Y-%m-%d %H:%M:%S')
                resource_manager.qstat()
                for node in nodes:
                    if resource_manager.is_busy(node):
                        cpu_load = f'{50 + 50*random.random():.2f}'
                        mem_load = f'{10 + 90*random.random():.2f}'
                    else:
                        cpu_load = f'{10*random.random():.2f}'
                        mem_load = f'{10*random.random():.2f}'
                    csv_load_writer.writerow([time_str, node, cpu_load, mem_load])
                    node_info = Node_info(node)
                    node_info.cpu_load = cpu_load
                    node_info.mem_load = mem_load
                    node_infos[node] = node_info
                resource_manager.cycle(delta)
                for job in resource_manager.running_jobs:
                    for node in job.nodes:
                        csv_jobs_writer.writerow([time_str, job.job_id, node])
                        node_infos[node].add_job_id(job.job_id)
                timestamp = datetime.strftime(time, '%Y%m%d_%H%M%S')
                log_file_name = f'{options.file}_log_{timestamp}.txt'
                with open(log_file_name, 'w') as log_file:
                    for node in sorted(node_infos.keys()):
                        print(node_infos[node], file=log_file)
                time += delta
