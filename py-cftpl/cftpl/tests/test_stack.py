import os
import unittest
from mock import patch, ANY, call, MagicMock
from cftpl.stack import CFStack
from cftpl.config import get_settings


class CFStackTestCase(unittest.TestCase):
    def setUp(self):
        self.boto_patch = patch('boto.connect_cloudformation')
        self.boto_mock = self.boto_patch.start()
        self.test_config = get_settings('testdata/config.py')
        self.test_password = 'sdfghjklkjhgf'

    def tearDown(self):
        self.boto_patch.stop()

    def test_init_configured(self):
        # TODO: This tests nothing!
        self.assertTrue(CFStack(self.test_config, self.test_password))

    def test_delete(self):
        stack = CFStack(self.test_config, self.test_password)
        result = stack.delete()
        self.boto_mock.return_value.delete_stack.assert_called_with(self.test_config['STACK_NAME'])

    def test_create(self):
        stack = CFStack(self.test_config, self.test_password)
        result = stack.create()
        self.boto_mock.return_value.create_stack.assert_called_with(self.test_config['STACK_NAME'],
                                                                    template_body=ANY,
                                                                    capabilities=self.test_config['CAPABILITIES'],
                                                                    tags=self.test_config['TAGS'])

    def test_list(self):
        stack = CFStack(self.test_config, self.test_password)
        result = stack.list()
        self.boto_mock.return_value.list_stacks.assert_called_with()

    def test_update(self):
        stack = CFStack(self.test_config, self.test_password)
        result = stack.update()
        test_result_json = open(os.path.join(self.test_config['TEMPLATE_PATH'], 'output.json')).read()
        self.boto_mock.return_value.update_stack.assert_called_with(self.test_config['STACK_NAME'],
                                                                    # TODO: Check if equal to test_result_json:
                                                                    template_body=ANY,
                                                                    capabilities=self.test_config['CAPABILITIES'],
                                                                    tags=self.test_config['TAGS'])

    def test_active_stacks(self):
        stack = CFStack(self.test_config, self.test_password)
        result = stack.active
        self.boto_mock.return_value.list_stacks.assert_called_with()
        self.assertEqual(result, False)

    def test_make_connection(self):
        stack = CFStack(self.test_config, self.test_password)
        self.boto_mock.assert_called_once_with(self.test_config['ACCOUNT'],
                                          region=ANY,
                                          aws_secret_access_key=self.test_password)