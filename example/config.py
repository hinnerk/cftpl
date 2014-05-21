import os

#
# EVERYTHING UPPERCASE IS AVAILABLE TO ANY TEMPLATE (and some things will be used elsewhere)
#


#
# AWS related stuff
#

# The aws_access_key_id
ACCOUNT = "<INSERT YOUR KEY HERE>"  # AWS_ACCESS_KEY_ID

# The name of the stack. Making this user friendly might be a good idea - must be unique though.
STACK_NAME = 'CFTPL-Example-Stack'

# one of us-east-1, us-west-1, us-west-2, eu-west-1, ap-southeast-1, ap-southeast-2, ap-northeast-1, sa-east-1
ENDPOINT = 'eu-west-1'

# Tags are propagated to resources and can be used to identify costs
# a maximum of 10 tags can be set
TAGS = {
    'Project': STACK_NAME
}

# Needed to create IAM ressources. More details:
# http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#capabilities
CAPABILITIES = ['CAPABILITY_IAM']


#
# Template related stuff
#

# The main template used to build the CloudFormation configuration
TEMPLATE = 'example.yaml'

# Path to the TEMPLATE and everything else, this assumes everything below cwd
TEMPLATE_PATH = os.path.dirname(os.path.abspath(__file__))

# Add custom jinja2 extensions
JINJA_EXTENSIONS = ()

# Add custom jinja2 filters
JINJA_FILTERS = {}

# Whe generating the result, use indention to make it mor readable?
JSON_INDENT = None      # or 4

# Values are replaced with the content of the files. Very handy when used with our base64 filter in jinja2.
FILES = {
    'salt-installer': 'install-salt.sh',
}

# Just here to be available in the template
EMAIL = '<INSERT YOUR EMAIL ADDRESS HERE'
