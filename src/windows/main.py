import os
from gi.repository import Gtk, Adw
from configparser import ConfigParser
from core.helpers import adw_clear_preferences_group, is_array_empty
from core.manager import Manager


class MainWindow(Adw.ApplicationWindow):

    # Visual elements
    header = Gtk.HeaderBar()
    window = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    scroll_content = Gtk.ScrolledWindow()
    scroll_content_box = Gtk.Box()
    no_vm_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
    vm_list_container = Adw.PreferencesPage()
    vm_list_container_content = Adw.PreferencesGroup(title="Virtual Machines")
    btn_add = Gtk.Button()

    # Variables
    vm_list = []
    config = ConfigParser

    def __init__(self, app):
        super(MainWindow, self).__init__(application=app, title="QEMU GUI")

        # Read VMs directory
        self.config = ConfigParser()
        self.config.read("qgui.conf")

        # Create main window
        self.set_default_size(800, 600)  # Max size
        self.set_size_request(300, 200)  # Min size
        self.get_style_context().add_class('devel')
        self.layout_main()
        self.update_content()

    def layout_main(self):
        self.window.append(self.header)
        self.set_content(self.window)
        # Add VM button
        self.btn_add.set_icon_name("list-add")
        self.header.pack_start(self.btn_add)
        # Scrolled content region
        self.scroll_content_box.set_hexpand(True)
        self.scroll_content_box.set_vexpand(True)
        self.scroll_content_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.scroll_content.set_child(self.scroll_content_box)
        self.vm_list_container.add(self.vm_list_container_content)
        self.scroll_content_box.append(self.vm_list_container)
        # No VMs, add one!
        self.no_vm_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        status_widget = Adw.StatusPage(icon_name='computer-symbolic', valign=Gtk.Align.CENTER, vexpand=True)
        status_widget.set_title("QEMU GUI")
        status_widget.set_description("No VMs. Try creating one!")
        btn_add_vm = Gtk.Button(label="Add your first VM", halign=Gtk.Align.CENTER)
        btn_add_vm.add_css_class("suggested-action")
        status_widget.set_child(btn_add_vm)
        # Apply element hierarchy
        self.no_vm_container.append(status_widget)
        self.scroll_content_box.append(self.no_vm_container)
        self.window.append(self.scroll_content)

    def update_content(self):

        adw_clear_preferences_group(self.vm_list_container_content)

        self.vm_list = Manager().list_vms_in_folder(self.config["paths"]["config"])
        for vm in enumerate(self.vm_list):
            action_row = Adw.ActionRow(title=vm[1].config["VM"]["Name"])
            action_row.set_activatable(True)

            btn_play = Gtk.Button(valign=Gtk.Align.CENTER, icon_name="media-playback-start-symbolic")
            btn_play.add_css_class("flat")
            btn_play.connect('clicked', self.do_launch_vm, vm[1].file, vm[1].config)
            action_row.add_suffix(btn_play)

            img_next = Gtk.Image(valign=Gtk.Align.CENTER, icon_name="go-next-symbolic")
            img_next.add_css_class("dim-label")
            action_row.add_suffix(img_next)

            self.vm_list_container_content.add(action_row)

        if is_array_empty(self.vm_list):
            self.no_vm_container.set_visible(True)
            self.vm_list_container.set_visible(False)
        else:
            self.no_vm_container.set_visible(False)
            self.vm_list_container.set_visible(True)

    def do_launch_vm(self, widget, *data):
        file: os.DirEntry = data[0]
        config: ConfigParser = data[1]
        Manager().launch_vm(file, config)
