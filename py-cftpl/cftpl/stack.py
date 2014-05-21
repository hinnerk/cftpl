from __future__ import print_function
import boto
import boto.cloudformation
import boto.exception
import time
from cftpl.template import CFTemplate
import logging

log = logging.getLogger(__name__)


class CFStackError(Exception):
    pass


class CFStack(object):
    def __init__(self, config, password=None):
        """
        A thin layer over boto.connect_cloudformation adding templates.
        config: the usual dict
        password_getter: an executable that yields the password or None to use AWS IAM.
        """
        self.conf = config
        self.password = password
        self.name = config['STACK_NAME']
        self.connection = self.__make_cloud_formation_connection()
        self.template = CFTemplate(self.conf)

    def get_stack(self):
        temp = [x for x in self.list() if x.stack_name == self.name and
                                          x.stack_status != 'DELETE_COMPLETE']
        if len(temp) > 1:
            raise CFStackError('Confused, too many stacks found: {}'.format(", ".join([x.stack_id for x in temp])))
        if len(temp) == 1:
            return temp[0]
        return None

    def __getattr__(self, item):
        stack = self.get_stack()
        if hasattr(stack, item):
            return getattr(stack, item)

    def delete(self, stack_name_or_id=None):
        stack = stack_name_or_id or self.name
        return self.connection.delete_stack(stack)

    def list(self):
        return self.connection.list_stacks()

    def update(self):
        return self.connection.update_stack(self.name,
                                            template_body=self.template.create_json(),
                                            capabilities=self.conf['CAPABILITIES'],
                                            tags=self.conf['TAGS'])

    def create(self):
        return self.connection.create_stack(self.name,
                                            template_body=self.template.create_json(),
                                            capabilities=self.conf['CAPABILITIES'],
                                            tags=self.conf['TAGS'])

    @property
    def active(self):
        stack = self.get_stack()
        if stack and stack.stack_status.endswith('_COMPLETE'):
            return stack
        return False

    def get_stack_event(self):
        stack = self.get_stack()
        if stack:
            return self.connection.describe_stack_events(stack.stack_id)
        return None

    def get_stack_events(self, interval_wait_time=5):
        events = set()
        wait = 0
        while wait < 1000:  # make sure we're not running endlessly
            try:
                event_list = self.connection.describe_stack_events(self.name)
            except boto.exception.BotoServerError:
                yield 'DELETE_COMPLETE'
                break
            event_list.reverse()  # we'd like to see the most recent message last.
            for event in event_list:
                if event.event_id not in events:
                    yield event
                    events.add(event.event_id)
            wait += 1
            stack = self.get_stack()
            if stack.stack_status.endswith('_COMPLETE'):
                yield stack.stack_status
                break
            time.sleep(interval_wait_time)

    def price(self):
        return self.connection.estimate_template_cost(template_body=self.template.create_json())

    def validate(self):
        return self.connection.validate_template(template_body=self.template.create_json())

    def cancel_update(self):
        return self.connection.cancel_update_stack(self.name)

    def __make_cloud_formation_connection(self):
        cf_region = [x for x in boto.cloudformation.regions() if x.name == self.conf['ENDPOINT']]
        return boto.connect_cloudformation(self.conf['ACCOUNT'], aws_secret_access_key=self.password,
                                           region=cf_region[0])
