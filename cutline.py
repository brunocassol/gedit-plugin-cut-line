# -*- coding: utf-8 -*-

#  Copyright (C) 2012 - Bruno Cassol
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

import os
from gi.repository import GObject, Gio, Gtk, Gedit, Gdk

ui_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="EditMenu" action="Edit">
      <placeholder name="EditOps_5">
        <menuitem name="CutLine" action="CutLineAction"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class CutLinePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "CutLinePlugin"

    window = GObject.property(type=Gedit.Window)
    gdk_control_mask = 1 << 2
    
    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.window.connect('key-press-event', self.on_key_press)
        self._install_menu()

    def do_deactivate(self):
        self._uninstall_menu()

    def _uninstall_menu(self):
        manager = self.window.get_ui_manager()

        manager.remove_ui(self._ui_id)
        manager.remove_action_group(self._action_group)

        manager.ensure_update()

    def _install_menu(self):
        manager = self.window.get_ui_manager()
        self._action_group = Gtk.ActionGroup(name="GeditCutLinePluginActions")
        self._action_group.add_actions([
            ("CutLineAction", Gtk.STOCK_OPEN, _("Cut line"),
             '<Ctrl>X', _("Cut line"),
             self.on_cut_line_key_press)
        ])

        manager.insert_action_group(self._action_group)
        self._ui_id = manager.add_ui_from_string(ui_str)

    def on_cut_line_key_press(self, action=None, user_data=None):
        doc = self.window.get_active_document()
        selection_iter = doc.get_selection_bounds()

        # if no text selected cut line
        if len(selection_iter) == 0:
            view = self.window.get_active_view()
            itstart = doc.get_iter_at_mark(doc.get_insert())
            offset = itstart.get_line_offset()
            itstart.set_line_offset(0)
            itend = doc.get_iter_at_mark(doc.get_insert())
            itend.forward_line()
            doc.begin_user_action()
            doc.select_range(itstart, itend)
            view.cut_clipboard()
            itstart = doc.get_iter_at_mark(doc.get_insert())
            itstart.set_line_offset(offset)
            doc.end_user_action()
            doc.place_cursor(itstart)
            
    def on_key_press(self, term, event):
        modifiers = event.state & Gtk.accelerator_get_default_mod_mask()
        if event.keyval in (Gdk.KEY_X, Gdk.KEY_x):
            if modifiers == Gdk.ModifierType.CONTROL_MASK:
                self.on_cut_line_key_press(self);

        return False
