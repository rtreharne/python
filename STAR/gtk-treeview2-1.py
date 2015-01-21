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
    self.model = gtk.ListStore( str, int, bool, float, str) #@+
    for url,download in (["http://root.cz",True],
                         ["http://slashdot.org",True],
                         ["http://mozilla.org",False]):
      adj = gtk.Adjustment( value=0, lower=0, upper=10, step_incr=1)
      self.model.append( [url, 0, download, 0.0, "HTML only"])
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
    # recursion_depth column
    col = gtk.TreeViewColumn( "Depth")
    treeview.append_column( col)
    cell = gtk.CellRendererSpin()
    cell.set_property( "adjustment", gtk.Adjustment( lower=0, upper=10, step_incr=1))
    cell.set_property( "editable", True)
    col.pack_start( cell, expand=False)
    col.set_attributes( cell, text=1)
    cell.connect('edited', self._recursion_depth_changed, 1)
    # State
    col = gtk.TreeViewColumn( "State")
    treeview.insert_column( col, 0)
    cell = gtk.CellRendererPixbuf()
    col.pack_start( cell, expand=False)
    col.set_cell_data_func( cell, self._render_icon)
    # Download column
    col = gtk.TreeViewColumn( "Download")
    treeview.append_column( col)
    cell = gtk.CellRendererToggle()
    cell.set_property( "activatable", True)
    col.pack_start( cell, expand=False)
    col.set_attributes( cell, active=2)
    col.set_sort_column_id( 2)
    cell.connect('toggled', self._download_toggled, 2)
    # What to download column
    col = gtk.TreeViewColumn( "What")
    treeview.append_column( col)
    cell = gtk.CellRendererCombo()
    cell.set_property( "editable", True)
    # we need a separate model for the combo
    model = gtk.ListStore( str)
    for value in ["HTML only", "HTML+CSS", "Everything"]:
      model.append( [value])
    cell.set_property( "model", model)
    cell.set_property( "text-column", 0)
    col.pack_start( cell, expand=False)
    col.set_attributes( cell, text=4)
    col.set_sort_column_id( 4)
    cell.connect('edited', self._what_to_download_changed, 4)
    # Progress column
    col = gtk.TreeViewColumn( "Progress")
    treeview.append_column( col)
    cell = gtk.CellRendererProgress()
    col.pack_start( cell, expand=True)
    col.set_attributes( cell, value=3)
    col.set_sort_column_id( 3)
    # pack the treeview
    self.mainbox.add( treeview)
    # show the box
    self.mainbox.set_size_request( 500, 260)
    self.mainbox.show()
    # set up timer
    self._timer = gobject.timeout_add( 200, self._timeout) #@+

  def _render_icon( self, column, cell, model, iter):
    data = self.model.get_value( iter, 2)
    if data == True:
      stock = gtk.STOCK_YES
    else:
      stock = gtk.STOCK_NO
    pixbuf = self.window.render_icon( stock_id=stock, size=gtk.ICON_SIZE_MENU)
    cell.set_property( 'pixbuf', pixbuf)

  def _download_toggled( self, w, row, column):
    self.model[row][column] = not self.model[row][column]

  def _recursion_depth_changed( self, w, row, new_value, column):
    self.model[row][column] = int( new_value)

  def _what_to_download_changed( self, w, row, new_value, column):
    self.model[row][column] = float(new_value)

  def _timeout( self):
    for row in self.model:
      if row[2] and row[3] < 100:
        # this row is downloadable
        row[3] += 3
        if row[3] > 100:
          row[3] = 100
    return True
      

  def main( self):
    gtk.main()

  def destroy( self, w):
    gobject.source_remove(self._timer)
    gtk.main_quit()


if __name__ == "__main__":
  m = MyGUI( "TreeView example II.")
  m.main()
