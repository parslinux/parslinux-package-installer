import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from DebPackage import DebPackage

class TestBatchPackageLogic(unittest.TestCase):
    def setUp(self):
        fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.scratch = fixtures_dir if os.path.exists(fixtures_dir) else os.path.join(os.path.dirname(__file__), '..', 'scratch')
        self.pkgs = [
            os.path.join(self.scratch, 'parslinux-hello_1.0.0_all.deb'),
            os.path.join(self.scratch, 'parslinux-editor_2.0.0_all.deb'),
            os.path.join(self.scratch, 'parslinux-theme_1.0.0_all.deb')
        ]

    def test_batch_deb_parsing(self):
        parsed = []
        for p in self.pkgs:
            self.assertTrue(os.path.exists(p), f'Test deb not found: {p}')
            pkg = DebPackage(p)
            self.assertIsNotNone(pkg.pkgname)
            parsed.append(pkg)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0].pkgname, 'parslinux-hello')
        self.assertEqual(parsed[1].pkgname, 'parslinux-editor')
        self.assertEqual(parsed[2].pkgname, 'parslinux-theme')

if __name__ == '__main__':
    unittest.main()
