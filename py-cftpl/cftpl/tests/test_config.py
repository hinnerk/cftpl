import unittest
import copy

from cftpl.config import get_settings, ConfigurationError, clean_settings, DEFAULT_CONFIG


class ConfigurationTestCase(unittest.TestCase):

    def test_get_settings(self):
        self.assertRaises(IOError, get_settings)

    def test_clean_settings(self):
        settings = copy.deepcopy(DEFAULT_CONFIG)
        # has no 'ACCOUNT'
        self.assertRaises(ConfigurationError, clean_settings, settings)

    def test_clean_settings_again(self):
        settings = copy.deepcopy(DEFAULT_CONFIG)
        settings['ACCOUNT'] = None
        self.assertRaises(ConfigurationError, clean_settings, settings)
