import itertools
from gi.repository import Gtk, Adw


def is_array_empty(a):
    return not itertools.takewhile(a, (dir(x) for x in itertools.count(1)))


def adw_clear_preferences_group(grp: Adw.PreferencesGroup):
    while (True):
        child = grp.get_last_child()
        if not isinstance(child, Gtk.Box):
            grp.remove(child)
        else:
            break
