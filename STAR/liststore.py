#!/usr/bin/env python

# example treemodelfilter.py

import pygtk
pygtk.require('2.0')
import gtk

bugdata="""-- 0.0 -- --"""


class TreeModelFilterExample:

    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("TreeModelFilter Example")

        self.window.set_size_request(400, 400)

        self.window.connect("delete_event", self.delete_event)

        # create a liststore with one string column to use as the model
        self.liststore = gtk.ListStore(str, float, str, str)

        self.modelfilter = self.liststore.filter_new()

        # create the TreeView
        self.treeview = gtk.TreeView()

        # create the TreeViewColumns to display the data
        self.treeview.columns = [None]*4
        self.treeview.columns[0] = gtk.TreeViewColumn('Param.')
        self.treeview.columns[1] = gtk.TreeViewColumn('Value')
        self.treeview.columns[2] = gtk.TreeViewColumn('Unit')
        self.treeview.columns[3] = gtk.TreeViewColumn('Fit?')

        # add bug data
        #self.states = []
        for line in bugdata.split('\n'):
            l = line.split()
            self.liststore.append([(l[0]), float(l[1]), (l[2]), (l[3])])
            #if not l[1] in self.states:
                #self.states.append(l[1])

        #self.show_states = self.states[:]
        self.modelfilter.set_visible_func(self.visible_cb)

        self.treeview.set_model(self.modelfilter)

        for n in range(4):
            # add columns to treeview
            self.treeview.append_column(self.treeview.columns[n])
            # create a CellRenderers to render the data
            self.treeview.columns[n].cell = gtk.CellRendererText()
            # add the cells to the columns
            self.treeview.columns[n].pack_start(self.treeview.columns[n].cell,
                                                True)
            # set the cell attributes to the appropriate liststore column
            self.treeview.columns[n].set_attributes(
                self.treeview.columns[n].cell, text=n)


        # make treeview searchable
        self.treeview.set_search_column(3)

        # make ui layout
        self.vbox = gtk.VBox()
        self.scrolledwindow = gtk.ScrolledWindow()
        
        self.vbox.pack_start(self.scrolledwindow)
       

        self.scrolledwindow.add(self.treeview)
        self.window.add(self.vbox)

        self.window.show_all()
        #return

    # visibility determined by state matching active toggle buttons
    def visible_cb(self, model, iter, data):
        return model.get_value(iter, 1) in data

    

def main():
    gtk.main()

if __name__ == "__main__":
    tmfexample = TreeModelFilterExample()
    main()

