#!/usr/bin/env python3

#  Contract Explorer Dialog Module
#   all the control logic for dialog lives here, the ui lives in DialogContractExplorer.py
#   DialogContractExplorer.py is baked from DialogContractExplorer.ui

# Created 2022 by James Bishop (james@bishopdynamics.com)
import uuid
import tkinter

from Mod_Util import print_traceback, list_to_dict
from UI_DialogContractExplorer import DialogContractExplorerUI


class DialogContractExplorer(DialogContractExplorerUI):
    # contract explorer dialog
    def __init__(self, contracts: list):
        super().__init__()
        self.setup_ui()
        self.contracts = contracts
        self.contract_nodes = []  # track all the tree nodes as we make them so we can iterate for expand and collapse
        self.combobox_values = {}
        self.combobox_textvariable = tkinter.StringVar()
        self.window.after(100, self.setup_backend)  # schedule setup_backend to run within the loop
        self.run_loop()

    def setup_backend(self):
        # setup non-ui stuff so that everything is ready
        self.button_close.config(command=self.cleanup)
        self.load_contract(self.contracts[0])
        self.button_expand.config(command=self.expand_tree)
        self.button_collapse.config(command=self.collapse_tree)
        self.populate_combobox()
        self.ready()

    def ready(self):
        # called when MainWindow is has finished setting up everything and we are ready for the user to interact
        print('dialogContractExplorer is ready')

    def cleanup(self):
        # cleanup any connections
        self.window.destroy()

    def expand_tree(self):
        # expand all items of treeview
        for item in self.contract_nodes:
            self.treeview_result.item(item, open=True)

    def collapse_tree(self):
        # collapse all items of treeview
        for item in self.contract_nodes:
            self.treeview_result.item(item, open=False)

    def json_tree(self, tree, parent, dictionary, node_list):
        for key in dictionary:
            uid = uuid.uuid4()
            node_list.append(uid)
            if isinstance(dictionary[key], dict):
                tree.insert(parent, 'end', uid, text=key)
                self.json_tree(tree, uid, dictionary[key], node_list)
            elif isinstance(dictionary[key], list):
                tree.insert(parent, 'end', uid, text=key + ':')
                self.json_tree(tree, uid, list_to_dict(dictionary[key]), node_list)
            else:
                value = dictionary[key]
                if value is None:
                    value = 'None'
                value = '"%s"' % value
                tree.insert(parent, 'end', uid, text=key, value=value)

    def load_contract(self, contract: dict):
        # load contract data into treeview
        try:
            # load first contract into treeview
            self.contract_nodes = []  # store nodes for later expand and collapse
            # clear out existing nodes
            for item in self.treeview_result.get_children():
                self.treeview_result.delete(item)
            # now populate it from the contract
            self.json_tree(self.treeview_result, '', contract, self.contract_nodes)
        except Exception as ex:
            print('failed to load contract: %s' % ex)
            print_traceback()

    def populate_combobox(self, ):
        sorted_contracts = sorted(self.contracts, key=lambda x: str(x['vendor']).lower())
        for contract in sorted_contracts:
            item_display = '%s (%s) %s - %s' % (contract['vendor'], contract['id'], contract['start'], contract['end'])
            item_value = contract['id']
            self.combobox_values[item_display] = item_value
        values = list(self.combobox_values.keys())
        self.combobox_contracts['textvariable'] = self.combobox_textvariable
        self.combobox_contracts['values'] = values
        self.combobox_contracts.current(0)
        self.combobox_contracts.bind('<<ComboboxSelected>>', self.combobox_changed)

    def combobox_changed(self, event):
        item_display = event.widget.get()
        selected_contract_id = self.combobox_values[item_display]
        print('got contract id: %s' % selected_contract_id)
        selected_contract = {}
        for contract in self.contracts:
            if contract['id'] == selected_contract_id:
                selected_contract = contract
                break
        self.load_contract(selected_contract)
