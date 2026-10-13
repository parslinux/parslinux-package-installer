import sys, os, unittest, subprocess
import gi

class TestGuiIntegrations(unittest.TestCase):
    def test_gtk3_mainwindow(self):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gio, GLib
        from MainWindow import MainWindow

        class DummyApp(Gtk.Application):
            def __init__(self):
                super().__init__(application_id='org.parslinux.test.gtk3')

        app = DummyApp()
        fixture = os.path.join(os.path.dirname(__file__), 'fixtures', 'parslinux-editor_2.0.0_all.deb')
        deb_file = fixture if os.path.exists(fixture) else os.path.join(os.path.dirname(__file__), '..', 'scratch', 'parslinux-editor_2.0.0_all.deb')
        win = MainWindow(app, Gio.File.new_for_path(deb_file))
        
        loop = GLib.MainLoop()
        def verify():
            self.assertEqual(win.pacname.get_text(), 'parslinux-editor')
            self.assertEqual(len(win.files_store), 11)
            loop.quit()

        GLib.timeout_add(250, verify)
        loop.run()

    def test_gtk4_adw_window(self):
        import subprocess
        # PyGObject cannot load both GTK3 and GTK4 in the same runtime process.
        # Check if GTK3 is already loaded and isolate GTK4 in a subprocess if so.
        if 'gi.repository.Gtk' in sys.modules:
            sub_code = (
                "import sys, os, gi\n"
                "sys.path.insert(0, os.path.abspath('src'))\n"
                "gi.require_version('Gtk', '4.0')\n"
                "gi.require_version('Adw', '1')\n"
                "from gi.repository import Adw\n"
                "from MainWindowAdw import MainWindowAdw\n"
                "app = Adw.Application(application_id='org.parslinux.test.adw_sub')\n"
                "deb_file = os.path.abspath('scratch/parslinux-editor_2.0.0_all.deb')\n"
                "def on_act(app):\n"
                "    win = MainWindowAdw(app, deb_file)\n"
                "    assert win.lbl_pkgname.get_label() == 'parslinux-editor'\n"
                "    assert len(win.file_items) == 11\n"
                "    app.quit()\n"
                "app.connect('activate', on_act)\n"
                "app.run([])\n"
            )
            res = subprocess.run([sys.executable, "-c", sub_code], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"GTK4 subprocess test failed: {res.stderr}")
            return

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        import gi
        gi.require_version('Gtk', '4.0')
        gi.require_version('Adw', '1')
        from gi.repository import Adw
        from MainWindowAdw import MainWindowAdw

        app = Adw.Application(application_id='org.parslinux.test.adw2')
        deb_file = os.path.join(os.path.dirname(__file__), '..', 'scratch', 'parslinux-editor_2.0.0_all.deb')

        def on_act(app):
            win = MainWindowAdw(app, deb_file)
            self.assertEqual(win.lbl_pkgname.get_label(), 'parslinux-editor')
            self.assertEqual(len(win.file_items), 11)
            app.quit()

        app.connect('activate', on_act)
        app.run([])

if __name__ == '__main__':
    unittest.main()
