#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#-----------------------------------------------------------------------#
# SetWallGnome3.py                                                      #
#                                                                       #
# Copyright (C) 2013 Germán A. Racca - <gracca[AT]gmail[DOT]com>        #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.  #
#-----------------------------------------------------------------------#

__author__ = "Germán A. Racca"
__copyright__ = "Copyright (C) 2013, Germán A. Racca"
__email__ = "gracca@gmail.com"
__license__ = "GPLv3+"
__version__ = "0.1"


import os
import mimetypes
import ConfigParser

from gi.repository import Gtk, GdkPixbuf, Gio


class SetWallGnome3(Gtk.Window):
    """Gtk+ 3 interface for SetWallGnome3"""

    def __init__(self):
        """Initialize the window"""
        Gtk.Window.__init__(self, title='Set the wallpaper in Gnome 3')
        self.set_default_size(400, 500)
        self.set_icon_name('applications-graphics')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)

        # read or create a config file
        #-------------------------------
        home_path = os.environ.get('HOME')
        self.conf_path = os.path.join(home_path, '.SetWallGnome3.cfg')

        self.conf_file = ConfigParser.SafeConfigParser()
        self.conf_file.read(self.conf_path)

        if os.path.isfile(self.conf_path):
            # read config file
            pics_path = self.conf_file.get('pictures_folder', 'pics')
        else:
            # write a default config file
            pics_default = os.path.join(home_path, 'Pictures')
            self.conf_file.add_section('pictures_folder')
            self.conf_file.set('pictures_folder', 'pics', pics_default)
            self.conf_file.write(open(self.conf_path, 'w'))
            pics_path = pics_default

        # read pics path recursively
        #----------------------------
        self.pics_names_list(pics_path)

        # create a grid
        #---------------
        self.grid = Gtk.Grid(column_homogeneous=True,
                             column_spacing=10,
                             row_spacing=10)
        self.add(self.grid)

        # create a window with scroll bars
        #----------------------------------
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER,
                                       Gtk.PolicyType.AUTOMATIC)

        # create a list store: picture, name, path
        #------------------------------------------
        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        for name, pic in zip(self.pics_name, self.pics_list):
            try:
                pxbf = GdkPixbuf.Pixbuf.new_from_file_at_scale(pic,
                                                               100,
                                                               100,
                                                               True)
                self.liststore.append([pxbf, name, pic])
            except:
                skip = "\033[1m[ SKIP ]\033[0m"
                print skip + " Error reading file %s" % pic

        # create the tree view
        #----------------------
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_hexpand(True)
        self.treeview.set_vexpand(True)

        # create the columns for the tree view
        #--------------------------------------
        renderer_pixbuf = Gtk.CellRendererPixbuf()  # column for picture
        column_pixbuf = Gtk.TreeViewColumn('Picture', renderer_pixbuf,
                                           pixbuf=0)
        column_pixbuf.set_alignment(0.5)
        self.treeview.append_column(column_pixbuf)

        renderer_text = Gtk.CellRendererText(weight=600)  # column for name
        renderer_text.set_fixed_size(200, -1)
        column_text = Gtk.TreeViewColumn('Name', renderer_text, text=1)
        column_text.set_sort_column_id(1)
        column_text.set_alignment(0.5)
        self.treeview.append_column(column_text)

        self.scrolledwindow.add_with_viewport(self.treeview)
        self.grid.attach(self.scrolledwindow, 0, 0, 1, 1)
        
        self.treeview.connect('row-activated', self.on_row_activated)

        # create a combo box for wallpaper rendering options
        #----------------------------------------------------
        self.option_store = Gtk.ListStore(str, str)
        opts_list = ['centered', 'scaled', 'spanned', 'stretched', 'wallpaper',
                     'zoom']
        opts_name = ['Centered', 'Scaled', 'Spanned', 'Stretched', 'Wallpaper',
                     'Zoom']
        for opts, names in zip(opts_list, opts_name):
            self.option_store.append([opts, names])

        self.option_combo = Gtk.ComboBox.new_with_model(self.option_store)
        renderer_combo_text = Gtk.CellRendererText()
        self.option_combo.pack_start(renderer_combo_text, True)
        self.option_combo.add_attribute(renderer_combo_text, 'text', 1)
        self.option_combo.set_active(0)

        # create the buttons
        #--------------------
        self.buttonbox = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
        self.buttonbox.set_layout(Gtk.ButtonBoxStyle.END)

        self.button_about = Gtk.Button(stock=Gtk.STOCK_ABOUT)
        self.button_about.connect('clicked', self.on_button_about_clicked)
        self.buttonbox.add(self.button_about)
        self.buttonbox.set_child_secondary(self.button_about,
                                           is_secondary=True)

        self.button_prefs = Gtk.Button(stock=Gtk.STOCK_PREFERENCES)
        self.button_prefs.connect('clicked', self.on_button_prefs_clicked)
        self.buttonbox.add(self.button_prefs)
        self.buttonbox.set_child_secondary(self.button_prefs,
                                           is_secondary=True)

        # add the combo box created before
        self.buttonbox.add(self.option_combo)

        self.button_apply = Gtk.Button(stock=Gtk.STOCK_APPLY)
        self.button_apply.connect('clicked', self.on_button_apply_clicked)
        self.buttonbox.add(self.button_apply)

        self.grid.attach_next_to(self.buttonbox, self.scrolledwindow,
                                 Gtk.PositionType.BOTTOM, 1, 1)


    # open image on double-click
    #----------------------------
    def on_row_activated(self, widget, path, column):
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            name, pic = model[treeiter][1:]
            img = ViewPic(name, pic)
        
    # function to read the pictures folder
    #--------------------------------------
    def pics_names_list(self, pics_path):
        """Scan the pictures folder recursively"""
        self.pics_list = []
        self.pics_name = []
        # read recursively
        for root, dirs, files in os.walk(pics_path):
            for fn in files:
                if self.mmtype(fn):
                    self.pics_name.append(fn)
                    f = os.path.join(root, fn)
                    self.pics_list.append(f)

    # filter file by mime type
    #--------------------------
    def mmtype(self, filein):
        """Select images based on mime types"""
        mime_list = ['image/png',
                     'image/jpeg',
                     'image/gif',
                     'image/tiff',
                     'image/bmp']
        mime = mimetypes.guess_type(filein)[0]
        if mime in mime_list:
            return True

    # callback for button Apply
    #---------------------------
    def on_button_apply_clicked(self, widget):
        """Apply the selected wallpaper"""
        # get rendering option
        treeiter_combo = self.option_combo.get_active_iter()
        if treeiter_combo is not None:
            model_combo = self.option_combo.get_model()
            option = model_combo[treeiter_combo][0]
        # apply the wallpaper
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            name, pic = model[treeiter][1:]
            pic_uri = 'file://' + pic
            background = Gio.Settings('org.gnome.desktop.background')
            background.set_string('picture-options', option)
            background.set_string('picture-uri', pic_uri)

    # callback for button About
    #---------------------------
    def on_button_about_clicked(self, widget):
        """Show about dialog"""
        about = Gtk.AboutDialog()
        lic = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
        about.set_program_name('SetWallGnome3')
        about.set_version('0.1')
        about.set_copyright('Copyright (C) 2013 Germán A. Racca')
        about.set_license(lic)
        about.set_website('http://gracca.github.com')
        about.set_comments('A simple program to set the wallpaper in Gnome 3')
        about.set_authors(['Germán A. Racca <gracca@gmail.com>'])
        about.set_documenters(['Germán A. Racca <gracca@gmail.com>'])
        about.connect('response', self.on_about_closed)
        about.show()

    # close about dialog
    #--------------------
    def on_about_closed(self, widget, parameter):
        """Destroy about dialog"""
        widget.destroy()

    # callback for button Preferences
    #---------------------------------
    def on_button_prefs_clicked(self, widget):
        """Show preferences dialog and update pictures folder"""
        dialog = PrefsDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            pics_new_path = dialog.entry_dir.get_text()
            if pics_new_path != '':
                # update pics folder in config file
                self.conf_file.set('pictures_folder', 'pics', pics_new_path)
                self.conf_file.write(open(self.conf_path, 'w'))
                # read pics path
                self.pics_names_list(pics_new_path)
                # reload tree view
#                dialog.progressbar.set_fraction(0.0)
#                frac = 1.0 / len(self.pics_list)
#                print "frac: ", frac
                self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
                for name, pic in zip(self.pics_name, self.pics_list):
                    try:
                        pxbf = GdkPixbuf.Pixbuf.new_from_file_at_scale(pic,
                                                                       100,
                                                                       100,
                                                                       True)
                        self.liststore.append([pxbf, name, pic])
                    except:
                        skip = "\033[1m[ SKIP ]\033[0m"
                        print skip + " Error reading file %s" % pic
                    self.treeview.set_model(model=self.liststore)
#                    new_val = dialog.progressbar.get_fraction() + frac
#                    print "new val: ", new_val
#                    dialog.progressbar.set_fraction(new_val)
        dialog.destroy()


class PrefsDialog(Gtk.Dialog):
    """Preferences dialog"""

    def __init__(self, parent):
        """Initialize the window"""
        Gtk.Dialog.__init__(self, 'Select pictures folder', parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(300, 100)
        self.set_modal(True)

        self.grid = Gtk.Grid(column_spacing=5, row_spacing=5)

        self.entry_dir = Gtk.Entry()
        self.entry_dir.set_hexpand(True)
        self.grid.add(self.entry_dir)

        self.button_open = Gtk.Button(stock=Gtk.STOCK_OPEN)
        self.button_open.connect('clicked', self.on_button_open_clicked)
        self.grid.attach(self.button_open, 1, 0, 1, 1)

#        self.progressbar = Gtk.ProgressBar()
#        self.progressbar.set_fraction(0.0)
#        self.grid.attach(self.progressbar, 0, 1, 2, 1)

        box = self.get_content_area()
        box.add(self.grid)
        self.show_all()

    def on_button_open_clicked(self, widget):
        """Open a file chooser to select the pictures folder"""
        dialog = Gtk.FileChooserDialog('Select pictures folder', self,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dname = dialog.get_filename()
            self.entry_dir.set_text(dname)
        dialog.destroy()


class ViewPic(Gtk.Window):
    """View selected picture on double-click"""
    
    def __init__(self, name, pic):
        """Initialize the window"""
        Gtk.Window.__init__(self)
        self.set_title(name)
        self.set_resizable(False)
        self.set_icon_name('applications-graphics')
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.image = Gtk.Image()
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(pic,
                                                            600,
                                                            600,
                                                            True)
        self.image.set_from_pixbuf(self.pixbuf)

        self.grid.add(self.image)
        self.show_all()
        

def main():
    """Show the window"""
    win = SetWallGnome3()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()
    return 0

if __name__ == '__main__':
    main()
