import copy
import inspect
import os

try:
    # SourceFileLoader is the recommended way in 3.3+
    from importlib.machinery import SourceFileLoader

    load_source = lambda name, path: SourceFileLoader(name, path).load_module()
except ImportError:
    # but it does not exist in 3.2-, so fall back to imp
    import imp

    load_source = imp.load_source


class CFStackError(Exception):
    pass


class ConfigurationError(CFStackError):
    pass


DEFAULT_CONFIG = {
    'TEMPLATE': '',
    'TEMPLATE_PATH': 'templates',
    'JINJA_EXTENSIONS': (),
    'JINJA_FILTERS': {},  # add custom filters here
    'ENDPOINT': "eu-west-1",
    'TAGS': {},
    'FILES': {},
    'JSON_INDENT': None,
    'STACK_NAME': '',
    'CAPABILITIES': ['CAPABILITY_IAM'],
}


def clean_settings(settings):
    required_config = ('STACK_NAME', 'CAPABILITIES', 'TAGS', 'ACCOUNT', 'ENDPOINT')
    for keyword in required_config:
        if not keyword in settings:
            raise ConfigurationError('Keyword "{}" missing in configuration'.format(keyword))
    if not settings['ACCOUNT']:
        raise ConfigurationError('Please specify an ACCOUNT in your config.')
    return settings


def get_settings(path=None, cleaner=clean_settings):
    path = path or 'config.py'
    name, ext = os.path.splitext(os.path.basename(path))
    module = load_source(name, path)
    settings = copy.deepcopy(DEFAULT_CONFIG)
    if module is not None:
        settings.update(
            (k, v) for k, v in inspect.getmembers(module) if k.isupper())
    if cleaner:
        return cleaner(settings)
    return settings
