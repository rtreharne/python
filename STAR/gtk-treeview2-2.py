# ensure that PyGTK 2.0 is loaded - not an older version
import pygtk
pygtk.require('2.0')
# import the GTK module
import gtk
import gobject

class MyGUI:

  def __init__( self, title):
    self.window = gtk.Window()
    self.title = title
    self.window.set_title( title)
    self.window.set_size_request( -1, -1)
    self.window.connect( "destroy", self.destroy)
    self.create_interior()
    self.window.show_all()

  def create_interior( self):
    self.mainbox = gtk.ScrolledWindow()
    self.mainbox.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.window.add( self.mainbox)
    # model creation
    # URL, recursion_depth, download, processed part, what to download
    self.model = gtk.ListStore( str, bool) #@+
    for url,download in (["http://root.cz",True],
                         ["http://slashdot.org",True],
                         ["http://mozilla.org",False]):
      
      self.model.append( [url, download])
    # the treeview
    treeview = gtk.TreeView( self.model) #@+
    # individual columns
    # URL column
    col = gtk.TreeViewColumn( "URL")
    treeview.append_column( col)
    cell = gtk.CellRendererText()
    col.pack_start( cell, expand=False)
    col.set_attributes( cell, text=0)
    col.set_sort_column_id( 0)

    col = gtk.TreeViewColumn( "Download")
    treeview.append_column( col)
    cell = gtk.CellRendererToggle()
    cell.set_property( "activatable", True)
    col.pack_start( cell, expand=False)
    col.set_attributes( cell, active=1)
    col.set_sort_column_id( 1)
    cell.connect('toggled', self._download_toggled, 1)

    # pack the treeview
    self.mainbox.add( treeview)
    # show the box
    self.mainbox.set_size_request( 500, 260)
    self.mainbox.show()


  def _download_toggled( self, w, row, column):
    self.model[row][column] = not self.model[row][column]

  def main( self):
    gtk.main()

  def destroy( self, w):
    gtk.main_quit()


if __name__ == "__main__":
  m = MyGUI( "TreeView example II.")
  m.main()
