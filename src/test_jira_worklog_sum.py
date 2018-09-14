import unittest

from jira_worklog_sum import check_arguments_number

class TestCheckArguments(unittest.TestCase):
    def test_zero_arguments(self):
        with self.assertRaises(SystemExit) as cm:
            check_arguments_number()
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
