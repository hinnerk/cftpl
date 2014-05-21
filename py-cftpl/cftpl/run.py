from __future__ import print_function
import getpass
import json
import os
import sys
import boto.exception
import keyring
import yaml
from cftpl.stack import CFStack, CFStackError
from cftpl.config import get_settings
from cftpl.template import CFTemplate


def get_args(*args):
    result = []
    for key in args:
        try:
            result.append(sys.argv[key])
        except IndexError:
            result.append(None)
    return result if len(result) > 1 else result[0]


def get_password(config):
    name = "CFMGR: %s (Account %s)" % (config['STACK_NAME'], config['ACCOUNT'])
    key = keyring.get_password(name, config['ACCOUNT'])
    if not key:
        pw = getpass.getpass('Please enter password for "%s": ' % config['ACCOUNT'])
        keyring.set_password(name, config['ACCOUNT'], pw)
        key = keyring.get_password(name, config['ACCOUNT'])
    return key


def run():
    helptext = """
    {} <command> <config>

    Where <command> is one of:

        list:   list all stacks in AWS
        create: create or update the stack (same as 'update')
        update: create or update the stack (same as 'create')
        show:   displays the generated template in the base format (usually YAML) without converting it to JSON
        test:   builds, tests and displays the generated stack template (JSON), does not change any resources
        delete: delete the stack on AWS
        convert: convert a JSON file to YAML syntax

    And <config> it the path of a config.py file.
    """.format(get_args(0))
    if len(sys.argv) == 1:
        print(helptext)
        sys.exit(1)
    operation = get_args(1)
    config_file = get_args(2)
    config = get_settings(config_file)
    password = get_password(config)

    try:
        if not operation or operation == 'list':
            list_stacks(config, password)
            sys.exit(0)
        elif operation in ('create', 'make', 'update', 'run', 'start'):
            create_or_update(config, password)
            sys.exit(0)
        elif operation in ('norun', 'test'):
            create_or_update(config, password, run=False)
            sys.exit(0)
        elif operation in ('show', 'display'):
            display_yaml(config)
            sys.exit(0)
        elif operation in ('kill', 'destroy', 'eradicate', 'delete', 'erase', 'inhume'):
            delete_stack(config, password)
            sys.exit(0)
        elif operation in ('convert'):
            convert_json_to_yaml(config)
            sys.exit(0)
        else:
            print(helptext)
            sys.exit(1)
    except boto.exception.BotoServerError, e:
        print("\nERROR:\n\t{}".format(e.error_message))
        sys.exit(42)
    except CFStackError, e:
        print("Error:{}:".format(e))
        sys.exit(23)


def list_stacks(config, password):
    stack = CFStack(config, password)
    print('\nRegion:   {}\nEndpoint: {}\n'.format(stack.connection.region.name, stack.connection.region.endpoint))
    stacks = stack.list()
    if len(stacks) == 0:
        print('No stacks found.')
    for x in stacks:
        print("NAME         | {}".format(getattr(x, 'stack_name')))
        print('-------------+-' + '-' * len(x.stack_id))
        for a, b in (('STATUS       | {}', 'stack_status'),
                     ('REASON       | {}', 'StackStatusReason'),
                     ('LAST UPDATED | {}', 'LastUpdatedTime'),
                     ('DELETED      | {}', 'deletion_time'),
                     ('ID           | {}', 'stack_id')):
            try:
                print(a.format(getattr(x, b)))
            except AttributeError:
                print(a.format("None"))
        if x.stack_status != 'DELETE_COMPLETE':
            print("STACK EVENTS:")
            for e in stack.connection.describe_stack_events(x.stack_id):
                print('\t{}: {}'.format(e.timestamp, e))
        print('\n')


def delete_stack(config, password):
    stack = CFStack(config, password)
    if not stack.get_stack():
        print("No running stack detected.")
        return None
    print('{}\t{}\t{}'.format(stack.stack_id, stack.stack_name, stack.stack_status))
    yesno = raw_input('Should I delete {}? '.format(stack.stack_name))
    if yesno.lower() in ('y', 'j', 'ja', 'yes'):
        print('Deleting stack {}...'.format(stack.name), end='')
        stack.delete()
        print('done.')
        print_stack_events(stack)
    else:
        print('Keeping "{}" for now.'.format(stack.stack_id))


def create_or_update(config, password, run=True):
    stack = CFStack(config, password)
    print('Validating template... ', end='', file=sys.stderr)
    stack.validate()    # raises if defect
    print('successfull.', file=sys.stderr)
    if run:
        if stack.active:
            print("Updating Stack {}...".format(stack.name), end='', file=sys.stderr)
            stack.update()
            print(' done.')
        else:
            print("Creating Stack {}...".format(stack.name), end='', file=sys.stderr)
            stack.create()
        print(' done.', file=sys.stderr)
        print_stack_events(stack)
        return stack
    # IF WE'RE NOT ACTIVELY CREATING OR UPDATING A STACK, WE'RE SHOWING THE CONFIG INSTEAD:
    print("This is the configuration we'd use if this was for real:\n\n", file=sys.stderr)
    if not config['JSON_INDENT']:
        config['JSON_INDENT'] = 4
    template = CFTemplate(config)
    print(template.create_json())
    if config['FILES']:
        print("\n\nHere are all the files you can use:", file=sys.stderr)
        for name, path in config['FILES'].iteritems():
            print('\t"{}":\t"{}"'.format(name, path), file=sys.stderr)
    return None


def display_yaml(config):
    print("This is the rendered template:\n\n", file=sys.stderr)
    template = CFTemplate(config)
    print(template.create())
    return None


def print_stack_events(stack):
    print("Showing status messages for stack {}:".format(stack.stack_name))
    for event in stack.get_stack_events():
        if isinstance(event, (str, unicode)):
            print("Status:\t{}".format(event))
        else:
            print('\t{}: {:<30}{:<45}{:<25}\t{}'.format(event.timestamp, event.resource_type,
                                                        event.resource_status,
                                                        event.logical_resource_id,
                                                        event.resource_status_reason))


def convert_json_to_yaml(config):
    path = os.path.join(config['TEMPLATE_PATH'], config['TEMPLATE'])
    print('Reading JSON from:\n{}'.format(path))
    data = json.loads(open(path).read())
    result = yaml.safe_dump(data)
    if path.lower().endswith('json'):
        path = path[:-4] + 'yaml'
    else:
        path = path + '.yaml'
    open(path, 'wb').write(result)
    print('YAML written to:\n{}'.format(path))
    print('DONE')