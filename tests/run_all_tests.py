import sys, os, subprocess

def run_isolated(cmd_desc, cmd_args):
    print(f'=== Running {cmd_desc} ===')
    res = subprocess.run([sys.executable] + cmd_args, text=True)
    if res.returncode != 0:
        print(f'FAILED: {cmd_desc}')
        return False
    print(f'PASSED: {cmd_desc}\n')
    return True

if __name__ == '__main__':
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    all_ok = True

    all_ok &= run_isolated('Included Files Tests', [os.path.join(tests_dir, 'test_included_files.py')])
    all_ok &= run_isolated('Batch Queue Tests', [os.path.join(tests_dir, 'test_batch_queue.py')])
    all_ok &= run_isolated('CLI & UI Modernization Tests', [os.path.join(tests_dir, 'test_cli_modernization.py')])
    all_ok &= run_isolated('Arch Linux Support Tests', [os.path.join(tests_dir, 'test_arch_package.py')])
    all_ok &= run_isolated('Libadwaita Debian Window Test', ['-c', 'import unittest, sys; sys.path.insert(0, sys.argv[1]); from test_gui_integration import TestGuiIntegrations; suite = unittest.TestSuite([TestGuiIntegrations("test_gtk4_adw_window")]); res = unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(not res.wasSuccessful())', tests_dir])
    all_ok &= run_isolated('Libadwaita Arch Package Window Test', ['-c', 'import unittest, sys; sys.path.insert(0, sys.argv[1]); from test_gui_integration import TestGuiIntegrations; suite = unittest.TestSuite([TestGuiIntegrations("test_gtk4_adw_arch_package")]); res = unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(not res.wasSuccessful())', tests_dir])
    all_ok &= run_isolated('Main Entrypoint Test', ['-c', 'import unittest, sys; sys.path.insert(0, sys.argv[1]); from test_gui_integration import TestGuiIntegrations; suite = unittest.TestSuite([TestGuiIntegrations("test_main_entrypoint")]); res = unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(not res.wasSuccessful())', tests_dir])

    if all_ok:
        print('ALL TEST SUITES PASSED PERFECTLY!')
        sys.exit(0)
    else:
        print('SOME TESTS FAILED.')
        sys.exit(1)
