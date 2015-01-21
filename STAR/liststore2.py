#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk

# Toggle Button Cell Renderer

# Add three columns to the GtkTreeView. This time first
# Boolean 'Buy' column will appear as check-button, the
# other two columns 'Count' and 'Product' remain Integer
# and String respectively.
def setup_tree_view(treeview)
  renderer = Gtk::CellRendererToggle.new
  column = Gtk::TreeViewColumn.new("Buy", renderer, "active" => GItm::BUY_INDEX)
  renderer.signal_connect('toggled') do |w, path|
    iter = treeview.model.get_iter(path)
    iter[GItm::BUY_INDEX] = !iter[GItm::BUY_INDEX] if (iter)
  end
  treeview.append_column(column)

  renderer = Gtk::CellRendererText.new
  column = Gtk::TreeViewColumn.new("Count", renderer, "text" => GItm::QTY_INDEX)
  treeview.append_column(column) 
  renderer = Gtk::CellRendererText.new
  column = Gtk::TreeViewColumn.new("Product", renderer, "text" => GItm::PROD_INDEX)
  treeview.append_column(column)
end

class GItm
  attr_accessor :product_type, :buy, :quantity, :product
  def initialize(t,b,q,p)
    @product_type, @buy, @quantity, @product = t, b, q, p
  end
  BUY_INDEX = 0; QTY_INDEX = 1; PROD_INDEX = 2
  PROD_CTG = 0; CHILD = 1
end

list = [
  GItm.new(GItm::PROD_CTG, true,  0, "Cleaning Supplies"),
  GItm.new(GItm::CHILD,    true,  1, "Paper Towels"),
  GItm.new(GItm::CHILD,    true,  3, "Toilet Paper"),
  GItm.new(GItm::PROD_CTG, true,  0, "Food"),
  GItm.new(GItm::CHILD,    true,  2, "Bread"),
  GItm.new(GItm::CHILD,    false, 1, "Butter"),
  GItm.new(GItm::CHILD,    true,  1, "Milk"),
  GItm.new(GItm::CHILD,    false, 3, "Chips"),
  GItm.new(GItm::CHILD,    true,  4, "Soda")
]
treeview = Gtk::TreeView.new
setup_tree_view(treeview)

# Create a new tree model with three columns, as Boolean, 
# integer and string.
store = Gtk::TreeStore.new(TrueClass, Integer, String)

# Avoid creation of iterators on every iterration, since they
# need to provide state information for all iterations. Hence:
# establish closure variables for iterators parent and child.
parent = child = nil

# Add all of the products to the GtkListStore.
list.each_with_index do |e, i|

  # If the product type is a category, count the quantity
  # of all of the products in the category that are going
  # to be bought.
  if (e.product_type == GItm::PROD_CTG)
    j = i + 1

    # Calculate how many products will be bought in
    # the category.
    while j < list.size && list[j].product_type != GItm::PROD_CTG
      list[i].quantity += list[j].quantity if list[j].buy
      j += 1
    end

    # Add the category as a new root (parent) row (element).
    parent = store.append(nil)
    # store.set_value(parent, GItm::BUY_INDEX, list[i].buy) # <= same as below
    parent[GItm::BUY_INDEX]  = list[i].buy
    parent[GItm::QTY_INDEX]  = list[i].quantity
    parent[GItm::PROD_INDEX] = list[i].product

  # Otherwise, add the product as a child row of the category.
  else
    child = store.append(parent)
    # store.set_value(child, GItm::BUY_INDEX, list[i].buy) # <= same as below
    child[GItm::BUY_INDEX]  = list[i].buy
    child[GItm::QTY_INDEX]  = list[i].quantity
    child[GItm::PROD_INDEX] = list[i].product
  end
end

# Add the tree model to the tree view
treeview.model = store
treeview.expand_all

scrolled_win = Gtk::ScrolledWindow.new
scrolled_win.add(treeview)
scrolled_win.set_policy(Gtk::POLICY_AUTOMATIC, Gtk::POLICY_AUTOMATIC)

window = Gtk::Window.new("Grocery List")
window.resizable = true
window.border_width = 10
window.signal_connect('destroy') { Gtk.main_quit }
window.set_size_request(275, 200)
window.add(scrolled_win)
window.show_all
Gtk.main
