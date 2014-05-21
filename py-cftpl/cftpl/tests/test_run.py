import unittest
from mock import patch, ANY, call, MagicMock, PropertyMock
from cftpl.config import get_settings
import cftpl.run as run
import sys
from cStringIO import StringIO
from contextlib import contextmanager


# source: http://schinckel.net/2013/04/15/capture-and-test-sys.stdout-sys.stderr-in-unittest.testcase/
@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    err, sys.stderr = sys.stderr, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield (sys.stdout.read(), sys.stderr.read())
    sys.stdout = out


class ConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        self.cfstack_patch = patch('cftpl.run.CFStack')
        self.cfstack_mock = self.cfstack_patch.start()
        self.test_config = get_settings('testdata/config.py')
        self.test_password = 'sdfghjklkjhgf'

    def tearDown(self):
        self.cfstack_patch.stop()

    def test_list_stacks(self):
        # create a stack to list:
        stack_mock = MagicMock()
        self.cfstack_mock.return_value.list.return_value = [stack_mock]
        # create a stack event:
        self.cfstack_mock.return_value.connection.describe_stack_events.return_value = [MagicMock()]
        with capture(run.list_stacks, self.test_config, self.test_password) as output:
            # some random assertions
            stack_mock.stack_id.return_value.assert_called_once()
            self.cfstack_mock.assert_called_once_with(self.test_config, self.test_password)
            self.cfstack_mock.return_value.list.assert_called_once_with()

    def test_delete_stack_yes(self):
        # create a stack to list:
        self.cfstack_mock.return_value.list.return_value = [MagicMock()]
        with patch('cftpl.run.raw_input', return_value="yes", create=True):
            with capture(run.delete_stack, self.test_config, self.test_password) as output:
                self.cfstack_mock.return_value.delete.assert_called_once_with()

    def test_delete_stack_no(self):
        self.cfstack_mock.return_value.list.return_value = [MagicMock()]
        with patch('cftpl.run.raw_input', return_value="no", create=True):
            with capture(run.delete_stack, self.test_config, self.test_password) as output:
                self.assertFalse(self.cfstack_mock.return_value.delete.called)

    def test_create_norun(self):
        self.cfstack_mock.return_value.list.return_value = []
        with capture(run.create_or_update, self.test_config, self.test_password, run=False) as output:
            self.assertFalse(self.cfstack_mock.return_value.create.called)
            self.assertFalse(self.cfstack_mock.return_value.update.called)

    def test_create(self):
        self.cfstack_mock.return_value.list.return_value = []
        active = PropertyMock(return_value=False)
        type(self.cfstack_mock.return_value).active = active
        with capture(run.create_or_update, self.test_config, self.test_password, run=True) as output:
            self.assertTrue(self.cfstack_mock.return_value.create.called)
            self.assertFalse(self.cfstack_mock.return_value.update.called)

    def test_update_norun(self):
        self.cfstack_mock.return_value.list.return_value = [MagicMock()]
        with capture(run.create_or_update, self.test_config, self.test_password, run=False) as output:
            self.assertFalse(self.cfstack_mock.return_value.create.called)
            self.assertFalse(self.cfstack_mock.return_value.update.called)

    def test_update(self):
        self.cfstack_mock.return_value.list.return_value = [MagicMock()]
        active = PropertyMock(return_value=True)
        type(self.cfstack_mock.return_value).active = active
        with capture(run.create_or_update, self.test_config, self.test_password, run=True) as output:
            self.assertFalse(self.cfstack_mock.return_value.create.called)
            self.assertTrue(self.cfstack_mock.return_value.update.called)

    @patch('cftpl.run.keyring.get_password', side_effect=[None, 'testpasswort123'])
    @patch('cftpl.run.keyring.set_password')
    @patch('cftpl.run.getpass.getpass')
    def test_get_password(self, getpass_mock, set_password_mock, get_password_mock):
        result = run.get_password(self.test_config)
        self.assertEqual('testpasswort123', result)
        self.assertEqual(get_password_mock.call_count, 2)
        self.assertEqual(set_password_mock.call_count, 1)
        self.assertEqual(getpass_mock.call_count, 1)


    @patch('cftpl.run.keyring.get_password', return_value='testpasswort123')
    @patch('cftpl.run.keyring.set_password')
    @patch('cftpl.run.getpass.getpass')
    def test_get_password(self, getpass_mock, set_password_mock, get_password_mock):
        result = run.get_password(self.test_config)
        self.assertEqual('testpasswort123', result)
        self.assertEqual(get_password_mock.call_count, 1)
        self.assertEqual(set_password_mock.call_count, 0)
        self.assertEqual(getpass_mock.call_count, 0)

    @unittest.skip('TODO: Move to tests/integration.')
    @patch('cftpl.run.get_password', return_value='testpasswort123')
    @patch('cftpl.run.sys.argv', return_value=['list', 'testdata/config.py'])
    def test_run(self, argv_mock, get_password_mock):
        with patch('cftpl.run.get_settings', return_value=self.test_config):
            run.run()
        self.assertEqual('testpasswort123', 'testpasswort123')