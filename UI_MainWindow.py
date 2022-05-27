#!/usr/bin/env python3

# Main Window UI Component

# Created 2022 by James Bishop (james@bishopdynamics.com)

import tkinter
import tkinter.ttk

from Mod_Util import print_traceback


class MainWindowUI(object):
    # our Main Window
    def __init__(self):
        super().__init__()
        self.window = tkinter.Tk()
        self.window_title = 'CommandExplorer'
        self.window_width = 1410
        self.window_height = 865
        self.window_width_min = 1410
        self.window_height_min = 865
        startpoint_offset_x = 0
        startpoint_offset_y = 0
        self.startpoint_x = (self.window.winfo_screenwidth() / 2) - (self.window_width / 2) + startpoint_offset_x  # calculate a starting point, middle of screen
        self.startpoint_y = (self.window.winfo_screenheight() / 2) - (self.window_height / 2) + startpoint_offset_y
        self.max_int = 65536  # int used for max window dimensions
        self.default_pad = 5  # int used for padx and pady by default
        self.no_pad = 0  # int used when minimal to zero padding is desired
        # TODO is this the right way to expose thse?
        self.button_quit = None
        self.button_save_log = None
        self.button_clear_log = None
        self.button_contract_explorer = None
        self.button_create_tickets = None
        self.table_log = None
        self.label_version = None
        self.label_create_tickets_status = None
        self.progressbar_create_tickets = None

    def run_loop(self):
        # run the loop for this window
        self.window.mainloop()

    def setup_ui(self):
        # setup the UI here
        print("Setting up the MainWindow")
        try:
            # set the title
            self.window.title(self.window_title)
            # setup sizing of the main window
            self.window.minsize(width=self.window_width_min, height=self.window_height_min)
            self.window.maxsize(width=self.max_int, height=self.max_int)
            self.window.geometry('%dx%d+%d+%d' % (self.window_width, self.window_height, self.startpoint_x, self.startpoint_y))
            self.window.wm_resizable(True, True)  # make the window resizable
            # window is a 1x1 grid
            self.window.rowconfigure(0, weight=1)
            self.window.columnconfigure(0, weight=1)

            # now lets build out our frames
            # create the root frame with a vertical layout, 1 x 8 with the log at the bottom
            frame_root = tkinter.Frame(self.window)  # this is the overall window, the container of all containers
            frame_root.columnconfigure(0, weight=1)
            for i in range(0, 8):
                frame_root.rowconfigure(i, weight=0)
                if i == 4:
                    frame_root.rowconfigure(i, weight=1)

            frame_root.grid(column=0, row=0, sticky='nsew', padx=self.default_pad, pady=self.default_pad)

            # the top entry holds another frame, inside are a button and a label
            frame_section_0 = tkinter.Frame(frame_root)
            frame_section_0.columnconfigure(0, weight=1)  # configure dimensions of this frame
            frame_section_0.rowconfigure(0, weight=1)  # configure dimensions of this frame
            frame_section_0.grid(column=0, row=0, sticky='ew', padx=self.default_pad, pady=self.default_pad)  # position in parent frame

            # this that other frame
            frame_section_0_0 = tkinter.Frame(frame_section_0)
            frame_section_0_0.columnconfigure(0, weight=1)
            frame_section_0_0.rowconfigure(0, weight=1)
            frame_section_0_0.rowconfigure(1, weight=1)  # 2 rows
            frame_section_0_0.grid(column=0, row=0, sticky='ew', padx=self.default_pad, pady=self.default_pad)

            # and here are the label and button
            label_utilities = tkinter.Label(frame_section_0_0, text='Utilities:')
            label_utilities.grid(column=0, row=0, sticky='w', padx=self.default_pad, pady=self.default_pad)
            self.button_contract_explorer = tkinter.Button(frame_section_0_0, text='Contract Explorer')
            self.button_contract_explorer.grid(column=0, row=1, sticky='w', padx=self.default_pad, pady=self.default_pad)
            self.button_contract_explorer['state'] = 'disabled'

            # end frame_section_0_0

            # this is the label for status of create tickets task
            self.label_create_tickets_status = tkinter.Label(frame_root, text='Status: Idle')
            self.label_create_tickets_status.grid(column=0, row=1, sticky='w')

            # this is the Create Tickets button
            self.button_create_tickets = tkinter.Button(frame_root, text='Create Tickets')
            self.button_create_tickets.grid(column=0, row=2, sticky='ew', padx=self.default_pad, pady=self.default_pad)
            self.button_create_tickets['state'] = 'disabled'

            # progressbar
            self.progressbar_create_tickets = tkinter.ttk.Progressbar(frame_root, value=0)
            self.progressbar_create_tickets.grid(column=0, row=3, sticky='ew', padx=self.default_pad, pady=self.default_pad)

            # this is vertical ^ spacer
            spacer_0 = tkinter.Frame(frame_root)
            spacer_0.grid(column=0, row=4, sticky='nsew', padx=self.no_pad, pady=self.no_pad)

            # line above Log Message
            horizontal_line = tkinter.ttk.Separator(frame_root, orient='horizontal')
            horizontal_line.grid(column=0, row=5, sticky='ews')

            # frame_section_1 is the frame holding the label "Log Messages (newest at top)", save log, clear log, version, spacer, and quit
            #   horizontal layout, 6x1 left-to-right
            frame_section_1 = tkinter.Frame(frame_root)
            frame_section_1.rowconfigure(0, weight=1)
            for i in range(0, 5):
                frame_section_1.columnconfigure(i, weight=0)
                if i == 4:
                    # the space column should be super heavy
                    frame_section_1.columnconfigure(i, weight=1)
            frame_section_1.grid(column=0, row=7, sticky='ews', padx=self.default_pad, pady=self.default_pad)

            # the label for Log Messages
            label_log_messages = tkinter.Label(frame_section_1, text='Log Messages (newest at top)')
            label_log_messages.grid(column=0, row=0, sticky='w')

            # save log button
            self.button_save_log = tkinter.Button(frame_section_1, text='Save Log')
            self.button_save_log.grid(column=1, row=0, sticky='w')
            self.button_save_log['state'] = 'disabled'

            # clear log button
            self.button_clear_log = tkinter.Button(frame_section_1, text='Clear Log')
            self.button_clear_log.grid(column=2, row=0, sticky='w')
            self.button_clear_log['state'] = 'disabled'

            # version label
            self.label_version = tkinter.Label(frame_section_1, text='Version: unknown')
            self.label_version.grid(column=3, row=0, sticky='w')

            # spacer horizontal <--->
            spacer_1 = tkinter.Frame(frame_section_1)
            spacer_1.grid(column=4, row=0, sticky='ew')

            # quit button
            self.button_quit = tkinter.Button(frame_section_1, text='Quit')
            self.button_quit.grid(column=5, row=0, sticky='e')

            # end frame_section_1

            # frame_log is 2x2 and holds the log table and scrollbars
            frame_log = tkinter.Frame(frame_root)
            frame_log.columnconfigure(0, weight=1)  # 2 cols
            frame_log.columnconfigure(1, weight=0)
            frame_log.rowconfigure(0, weight=1)
            frame_log.rowconfigure(1, weight=0)  # 2 rows
            frame_log.grid(column=0, row=8, sticky='ews', padx=self.default_pad, pady=self.default_pad)

            # this is the table for the log messages
            self.table_log = tkinter.ttk.Treeview(frame_log)
            self.table_log.grid(column=0, row=0, sticky='ew', padx=self.default_pad, pady=self.default_pad)
            # NOTE from what i can find you cannot set the header height directly, instead it is influenced by content.
            #   you can add extra\n newline\n to make things taller
            column_widths = [0, 200, 1240]  # widths of columns
            column_headings = ['', 'Timestamp', 'Message']  # column headers
            column_ids = ['#0', 'timestamp', 'message']
            self.table_log['columns'] = ['timestamp', 'message']  # column ids (other than '#0')
            # TODO i actually dont know what #0 is, maybe its the root object of the treeview?
            # iterate over column definitions
            for col_num in range(0, len(column_ids)):
                column_id = column_ids[col_num]
                if col_num == 0:
                    self.table_log.column(column_id, width=column_widths[col_num], stretch=False)
                else:
                    self.table_log.column(column_id, width=column_widths[col_num])
                self.table_log.heading(column_id, anchor='center', text=column_headings[col_num])

            # TODO apparently not needed: scrollbars for log table
            # scrollbar_log_horizontal = tkinter.ttk.Scrollbar(frame_log, orient='horizontal')
            # scrollbar_log_horizontal.grid(column=0, row=1, sticky='ew', padx=self.default_pad, pady=self.default_pad)
            # scrollbar_log_vertical = tkinter.ttk.Scrollbar(frame_log, orient='vertical')
            # scrollbar_log_vertical.grid(column=1, row=0, sticky='ns', padx=self.default_pad, pady=self.default_pad)

        except Exception as ex:
            print('exception while building ui: %s' % ex)
            print_traceback()
