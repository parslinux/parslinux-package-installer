import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from DebPackage import DebPackage

class TestIncludedFiles(unittest.TestCase):
    def setUp(self):
        fixture = os.path.join(os.path.dirname(__file__), 'fixtures', 'parslinux-editor_2.0.0_all.deb')
        scratch = os.path.join(os.path.dirname(__file__), '..', 'scratch', 'parslinux-editor_2.0.0_all.deb')
        self.deb_path = fixture if os.path.exists(fixture) else scratch

    def test_file_details_extraction(self):
        pkg = DebPackage(self.deb_path)
        details = pkg.get_file_details()
        self.assertGreater(len(details), 0, 'No file details returned')
        
        # Verify fields
        for d in details:
            self.assertIn('name', d)
            self.assertIn('size', d)
            self.assertIn('is_dir', d)
            self.assertIn('is_exec', d)
            self.assertIn('is_sym', d)
        
        # Check specific known files
        file_names = [d['name'] for d in details]
        self.assertIn('/usr/bin/parslinux-editor', file_names)
        self.assertIn('/etc/parslinux-editor.conf', file_names)
        
        # Check executable flag
        bin_entry = next(d for d in details if d['name'] == '/usr/bin/parslinux-editor')
        self.assertTrue(bin_entry['is_exec'], 'Binary should have is_exec=True')
        self.assertFalse(bin_entry['is_dir'], 'Binary should not be a directory')

    def test_file_list_backward_compat(self):
        pkg = DebPackage(self.deb_path)
        file_list = pkg.get_file_list()
        self.assertIsInstance(file_list, list)
        self.assertIn('/usr/bin/parslinux-editor', file_list)

if __name__ == '__main__':
    unittest.main()
