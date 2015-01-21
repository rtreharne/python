import pygtk
pygtk.require('2.0')
import os
import add_user
import user_commands_wrapper

class PyParty:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('PyParty')
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_border_width(5)

        self.window.connect('delete_event', self.closeWindow)

        self.table = gtk.Table(5, 2, False)

        self.title_label = gtk.Label('Users')
        self.add_button = gtk.Button('Add')
        self.edit_button = gtk.Button('Edit')
        self.delete_button = gtk.Button('Delete')
        self.exit_button = gtk.Button('Exit')

        self.add_button.connect('clicked', self.addUser)

        self.tree_store = gtk.TreeStore(str, str)

        #Remover passagem de valores para o construtor
        for user in user_commands_wrapper.User('', '').get_all_users():
            self.tree_store.append(None, [user.pw_name, user.pw_gecos])

        self.tree_view = gtk.TreeView(self.tree_store)
        self.tree_view.connect('cursor_changed', self.get_selected_user)

        self.username_tree_view_column = gtk.TreeViewColumn('username')
        self.realname_tree_view_column = gtk.TreeViewColumn('realname')

        self.tree_view.append_column(self.username_tree_view_column)
        self.tree_view.append_column(self.realname_tree_view_column)

        self.username_cell = gtk.CellRendererText()
        self.username_tree_view_column.pack_start(self.username_cell, True)
        self.username_tree_view_column.add_attribute(self.username_cell, 'text', 0)

        self.realname_cell = gtk.CellRendererText()
        self.realname_tree_view_column.pack_start(self.realname_cell, True)
        self.realname_tree_view_column.add_attribute(self.realname_cell, 'text', 1)

        self.table.attach(self.title_label, 0, 2, 0, 1)
        self.table.attach(self.tree_view, 0, 1, 1, 5)
        self.table.attach(self.add_button, 1, 2, 1, 2)
        self.table.attach(self.edit_button, 1, 2, 2, 3)
        self.table.attach(self.delete_button, 1, 2, 3, 4)
        self.table.attach(self.exit_button, 1, 2, 4, 5)

        self.window.add(self.table)

        self.window.show_all()
        gtk.main()

    # Callback methods
    def closeWindow(self, widget, data = None):
        print self.selected_user
        gtk.main_quit()

    def addUser(self, widget, data = None):
        add_user.AddUser()

    def get_selected_user(self, widget, data = None):
        selection = self.tree_view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        param, value, fit = selection.get_selected()
        selected = param.get_value()

if __name__ == '__main__':
    # Remover
    if os.getenv('USER') == 'root':
        PyParty()
    else:
        print 'Only root can run that!'
