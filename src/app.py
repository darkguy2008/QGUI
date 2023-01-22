import gi
import sys
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw

sys.path.insert(0, '.')
from windows.main import MainWindow


def on_activate(app):
    win = MainWindow(app)
    win.present()


app = Adw.Application(application_id='com.darkguy2008.qgui')
app.connect('activate', on_activate)
app.run(None)
