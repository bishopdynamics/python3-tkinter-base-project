#!/usr/bin/env python3

# MainWindow Module
#   all the control logic for main window lives here, the ui lives in MainWindow.py
#   MainWindow.py is baked from MainWindow.ui

# Created 2022 by James Bishop (james@bishopdynamics.com)

import platform
import sys
import json
import yaml

from concurrent.futures import ThreadPoolExecutor

from UI_MainWindow import MainWindowUI
from Mod_Constants import *
from Mod_Util import get_version, get_timestamp
from Mod_Util import print_traceback, print_obj

from Mod_DialogContractExplorer import DialogContractExplorer
from Mod_ThreadWorkers import ThreadWorkerCommunicator, TicketCreator


class MainWindow(MainWindowUI):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.log = []
        self.thread_pool = ThreadPoolExecutor(max_workers=5)
        self.communicators = []
        self.config = {}
        self.window.after(100, self.setup_backend)  # schedule setup_backend to run within the loop
        self.run_loop()

    def log_msg(self, message):
        # write text to the log and console
        timestamp = get_timestamp()
        print('%s - %s' % (timestamp, message))
        self.log.append([timestamp, message])
        # reverse the log order for the UI table, but not for the console or file output
        log_reversed = self.log.copy()
        log_reversed.reverse()
        # clear the table
        self.table_log.delete(*self.table_log.get_children())
        # now repopulate it
        for index, entry in enumerate(log_reversed):
            self.table_log.insert('', index=index, values=entry)

    def read_config(self):
        # load config from file, else return useless defaults, but maintaining schema
        # NOTE config standards: <units or type>_<name_using_underscore>
        default_config = {'saving': {'bool_save_on_close': True, 'mins_autosave_timeout': 10}}
        if not CONFIG_FILE.is_file():
            self.log_msg('No config file found at: %s' % str(CONFIG_FILE))
            return default_config
        else:
            self.log_msg('Loading config from: %s' % str(CONFIG_FILE))
            try:
                with open(CONFIG_FILE) as cf:
                    config = yaml.load(cf, Loader=yaml.FullLoader)
                self.log_msg('Autosave mins: %s' % config['saving']['mins_autosave_timeout'])
                return config
            except Exception as ex:
                self.log_msg('Error while trying to read config: %s' % ex)
                print_traceback()
                return default_config

    def log_platform_info(self):
        # log information about this run, machine, python, etc
        try:
            version = get_version(COMMIT_ID_FILE, VERSION_FILE)
            self.log_msg('Version: %s' % version)
            version_text = 'Version: %s' % version
            self.label_version.config(text=version_text)
            self.log_msg('App basedir: %s' % APP_FOLDER)
            python_vstring = '%s %s %s' % (platform.python_implementation(), platform.python_version(), platform.python_build())
            self.log_msg('hostname: %s' % platform.node())
            self.log_msg('platform: %s' % platform.platform())
            self.log_msg('python: %s' % python_vstring)
            self.log_msg('now: %s' % get_timestamp())
        except Exception as ex:
            self.log_msg('Error while logging platform information')
        return None

    def setup_backend(self):
        # setup non-ui stuff so that everything is ready
        self.log_msg('Logging has begun')
        self.log_platform_info()  # show all the platform info
        self.connect_signals()
        self.config = self.read_config()
        self.ready()

    def connect_signals(self):
        self.log_msg('Connecting UI signals')
        try:
            self.button_quit.config(command=sys.exit)
            self.button_create_tickets.config(command=self.create_tickets)
            self.button_clear_log.config(command=self.clear_log)
            self.button_save_log.config(command=self.save_log)
            self.button_contract_explorer.config(command=self.show_contract_explorer)
        except Exception as ex:
            self.log_msg('Error while connecting signals: %s' % ex)
            print_traceback()

    def ready(self):
        # called when MainWindow is has finished setting up everything and we are ready for the user to interact
        self.button_clear_log['state'] = 'normal'
        self.button_save_log['state'] = 'normal'
        self.button_contract_explorer['state'] = 'normal'
        self.button_create_tickets['state'] = 'normal'
        self.log_msg('Ready')

    def show_contract_explorer(self):
        # show dialog to explore all contract data
        # dialog will handle the work
        self.log_msg('Showing Contract Explorer Dialog')
        example_data = [
            {'vendor': 'Adobe', 'id': '47', 'start': 'soon', 'end': 'also soon', 'partners': ['Bob', 'Sam', 'Jane']},
            {'vendor': 'Jetbrains', 'id': '52', 'start': 'soon', 'end': 'also soon', 'partners': ['Bob', 'Sam', 'Jane']},
        ]  # TODO just example
        dialog = DialogContractExplorer(example_data)
        dialog.run_loop()

    def create_tickets(self):
        # create tickets based on self.contracts_processed
        try:
            input_data = [
                {'id': '42', 'name': 'Albert'},
                {'id': '12', 'name': 'Michael'},
                {'id': '07', 'name': 'Kinsley'},
            ]  # TODO this is just sample data
            worker = TicketCreator(input_data)
            communicator = ThreadWorkerCommunicator(name='Create JIRA Tickets',
                                                    window=self.window,
                                                    worker=worker,
                                                    thread_pool=self.thread_pool,
                                                    message_function=self.log_msg,
                                                    result_function=self.create_tickets_on_result,
                                                    progressbar=self.progressbar_create_tickets,
                                                    statuslabel=self.label_create_tickets_status)
            self.communicators.append(communicator)
            communicator.run()
        except Exception as ex:
            self.log_msg('Error while kicking off load_csv_data worker: %s' % ex)
            print_traceback()

    def create_tickets_on_result(self, result):
        # handle result of create ticket process
        self.log_msg('CreateTicket results: %s' % json.dumps(result))

    def clear_log(self):
        # clear the log window in the UI, as well as the history. does not affect what is printed to console
        self.log = []
        self.log_msg('Log cleared')
        return None

    def save_log(self):
        # save log to a file in users Downloads folder
        timestamp = get_timestamp()
        homedir = pathlib.Path.home().joinpath('Downloads')
        filename = homedir.joinpath('CommandExplorer_log_%s.txt' % timestamp)
        with open(filename, 'w') as of:
            for i, (timestamp, message) in enumerate(self.log):
                of.write('%s - %s \n' % (timestamp, message))
        self.log_msg('Log saved to %s' % str(filename))
        return None
