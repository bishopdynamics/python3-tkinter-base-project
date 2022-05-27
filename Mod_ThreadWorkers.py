#!/usr/bin/env python3

# Thread Workers Module
#   workers to run in separate thread from UI, for long-running tasks that would otherwise freeze the UI

# Created 2022 by James Bishop (james@bishopdynamics.com)

import time
from abc import abstractmethod

from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from queue import Queue

from Mod_Util import print_traceback, print_obj


class ThreadChannel(object):
    # communications channel for sending arbitrary data back to parent thread, via queue
    #   a ThreadChannel has a name and a type, and we try to enforce type
    #   data is sent to a queue, which can then be checked regularly
    def __init__(self, parent_name, name,  var_type: type):
        self.parent_name = parent_name
        self.name = name
        self.queue = Queue(maxsize=0)  # TODO do we care about limiting queue size?
        self.var_type = var_type
        self.debug = False  # set to True to get more debug info printed to console
        self.var_type_str = var_type.__name__
        self.max_entries_per_loop = 4  # for any loop cycle, process the queue until empty, or N entries processed
        self.callbacks = []  # list of funcitons to call, passing data

    def log_msg(self, message: str):
        # how to we want to log a message?
        if self.debug:
            print('ThreadChannel %s.%s<%s> : %s' % (self.parent_name, self.name, self.var_type_str,  message))

    def send(self, data: any):
        # child thread wants to send data on this channel
        self.log_msg('sending a message')
        try:
            # we want any data sent to be an instance of the declared type
            if not isinstance(data, self.var_type):
                error_msg = 'send wrong type: %s' % str(type(data))
                self.log_msg(error_msg)
                raise Exception(error_msg)
            self.queue.put(data)
        except Exception as ex:
            self.log_msg('Error while sending: %s' % ex)

    def subscribe(self, on_data: callable):
        # parent thread wants to be notified when data is sent on this channel
        self.log_msg('adding a subscription for: %s' % on_data.__name__)
        # TODO we want to somehow validate that the callable takes the right number of args, and of the right type
        self.callbacks.append(on_data)

    def run_loop(self):
        # for any data in the queue, call each callback with that data
        try:
            num_processed = 0  # track how many we have processed so far, to compare to max
            while not self.queue.empty():
                this_data = self.queue.get()
                for this_callback in self.callbacks:
                    self.log_msg('calling: %s' % this_callback.__name__)
                    this_callback(this_data)
                num_processed += 1
                if num_processed >= self.max_entries_per_loop:
                    break  # only process N entries per loop, so as not to hog the parent thread
        except Exception as ex:
            self.log_msg('Error in run_loop: %s' % ex)


class ThreadWorkerChannels(object):
    def __init__(self, parent_name):
        self.parent_name = parent_name
        self.progress = ThreadChannel(self.parent_name, 'progress', int)
        self.status = ThreadChannel(self.parent_name, 'status', str)
        self.error = ThreadChannel(self.parent_name, 'error', str)
        self.success = ThreadChannel(self.parent_name, 'success', bool)
        self.result = ThreadChannel(self.parent_name, 'result', object)

    def run_loop(self):
        # run each of the channel's loops once
        self.progress.run_loop()
        self.status.run_loop()
        self.error.run_loop()
        self.success.run_loop()
        self.result.run_loop()


class ThreadWorker(object):
    # base ThreadWorker class
    def __init__(self, name):
        self.name = name
        self.loop_delay = 0.1  # seconds, how often to check queues
        self.debug = True  # enable to print more messages
        self.monitor_thread = Thread(target=self.run_loop, daemon=True)
        self.channels = ThreadWorkerChannels(parent_name=self.name)

    def cleanup(self):
        # clean up our monitor thread
        self.log_msg('Cleaning up')
        self.monitor_thread._stop()

    def log_msg(self, message):
        # how to we want to log a message?
        if self.debug:
            print('ThreadWorker %s : %s' % (self.name, message))

    def run_loop(self):
        # repeatedly check for messages in channels
        while True:
            self.channels.run_loop()
            time.sleep(self.loop_delay)

    def report_progress(self, progress: int):
        # report progress as 0-100 int
        self.channels.progress.send(progress)

    def report_status(self, message: str):
        # report a status message
        self.channels.status.send(message)

    def report_error(self, message: str):
        # report that worker failed, and why
        self.report_status('Error')
        self.channels.error.send(message)
        self.channels.success.send(False)

    def report_success(self):
        # report wether worker completed successfully or not
        self.report_status('Success')
        self.channels.success.send(True)

    def report_result(self, result: any):
        # report the output of the worker process, any object can be returned
        self.channels.result.send(result)

    def run(self):
        # this is what gets run
        self.log_msg('Starting')
        self.report_status('Starting')
        self.monitor_thread.start()
        self.report_progress(0)
        try:
            self.thread_action()
        except Exception as ex:
            print('Error while running threadworker: %s' % ex)
        time.sleep(0.2)  # let messages flush
        self.cleanup()
        self.log_msg('Complete')

    @abstractmethod
    def thread_action(self):
        # this is where long-running work goes
        #   this method is responsible for reporting progress:
        #       while working: report_progress, report_status
        #       if failure: report_error (no report_result called if error)
        #       if success: report_result, report_success
        pass


class ThreadWorkerCommunicator:
    # handles communication with a threadworker, progressbar, statuslabel, and handling result
    #   a communicator's job is to run in the parent thread, regularly checking for new items in queues that are filled by the child thread
    def __init__(self, window, name, worker: ThreadWorker, thread_pool: ThreadPoolExecutor, message_function: callable, result_function: callable, progressbar=None, statuslabel=None):
        self.window = window
        self.worker = worker
        self.log_msg = message_function
        self.progressbar = progressbar
        self.statuslabel = statuslabel
        self.thread_pool = thread_pool
        self.result_function = result_function
        self.name = name
        self.debug = True  # enable to print debug messages
        self.thread_future = None
        self.setup()

    def log_msg(self, message):
        # how to we want to log a message?
        if self.debug:
            print('ThreadWorkerCommunicator %s : %s' % (self.name, message))

    def setup(self):
        try:
            self.log_msg('Setting up')
            self.worker.channels.progress.subscribe(self.on_progress)
            self.worker.channels.status.subscribe(self.on_status)
            self.worker.channels.error.subscribe(self.on_error)
            self.worker.channels.success.subscribe(self.on_success)
            self.worker.channels.result.subscribe(self.on_result)
        except Exception as ex:
            print('Error while setting up threadworkercommunicator: %s' % ex)
            print_traceback()

    def run(self):
        try:
            self.log_msg('Running')
            self.thread_future = self.thread_pool.submit(self.worker.run)
            # Note: you can also do: result = self.thread_pool.map(function, values)
            #   where values is an array, and result will be an array of results, one per value
        except Exception as ex:
            print('error while running worker: %s' % ex)
            print_traceback()

    def on_progress(self, progress: int):
        # update a progress bar if assigned
        if self.progressbar:
            self.progressbar['value'] = progress
            self.window.update_idletasks()

    def on_status(self, status: str):
        # update a status label if assigned
        self.log_msg('ThreadWorker %s - Status: %s' % (self.name, status))
        if self.statuslabel:
            self.statuslabel['text'] = status
            self.window.update_idletasks()

    def on_error(self, error: str):
        self.log_msg('ThreadWorker %s - Error: %s' % (self.name, error))

    def on_success(self, value: bool):
        if value:
            self.log_msg('ThreadWorker %s - Success!' % self.name)
        else:
            self.log_msg('ThreadWorker %s - Failed!' % self.name)

    def on_result(self, result: object):
        self.result_function(result)


class TicketCreator(ThreadWorker):
    # all the logic for creating JIRA tickets from selected contracts lives here
    def __init__(self, items: list):
        super().__init__('TicketCreator')
        self.items = items

    def thread_action(self):
        # create tickets based on self.contracts_processed
        num_selected = len(self.items)
        num_created = 0
        num_skipped = 0
        if num_selected == 0:
            self.report_status('Creating 0 tickets, no contracts selected')
        else:
            count = 0
            self.report_status('Creating tickets for %s selected contracts' % num_selected)
            self.report_progress(5)
            for item in self.items:
                contract_id = item['id']
                progress = round(((count + 1) / num_selected) * 100)  # offset so that you can tell things have started
                # work starts here
                self.report_status('Creating tickets for Contract ID: %s' % contract_id)
                time.sleep(1)
                # work done
                self.report_progress(progress)
                # print(progress)
                num_created += 1  # track how many we actually create
                count += 1
            self.report_progress(100)
            self.report_status('Of %s selected contracts, %s tickets were created, and %s were skipped' % (num_selected, num_created, num_skipped))
            self.report_result({
                'created': num_created,
                'selected': num_selected,
                'skipped': num_skipped,
            })
