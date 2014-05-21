# Templates and Management for AWS CloudFormation

* **`cftpl`**: A simple Python library to build and manage CloudFormation Stacks. STacks are built using templates and can use variables, loops and reuse existing code.
* **`cfmgr`:** The executable to manage CloudFormation Stacks from the command line. Based on `cftpl`, has actual password management.


# Why?

* The syntax becomes shorter and much more readable. Using YAML allows comment lines within the stack template.
* An expressive template language enables loops and code reuse (`if`, `for`, `include`, `extends`, `macro`)
* Use all this with a simple command line tool.

# Features

* Build AWS CloudFormation stack templates using JSON, YAML and the Jinja2 template language.
* Create, update and delete CloudFormation stacks (uses [boto](http://boto.readthedocs.org/en/latest/)).
* Use as a standalone executable or as a Python library.
* Provides state of the art password management.

# Installation

## The Lazy:

```
sudo pip install cftpl
```

`cfmgr` should be available now:

```
$ cfmgr

    cfmgr <command> <config>

    Where <command> is one of:

        list:   list all stacks in AWS
        create: create or update the stack (same as 'update')
        update: create or update the stack (same as 'create')
        show:   displays the generated template in the base format (usually YAML) without converting it to JSON
        test:   builds, tests and displays the generated stack template (JSON), does not change any resources
        delete: delete the stack on AWS
        convert: convert a JSON file to YAML syntax

    And <config> it the path of a config.py file.
```

## Everybody else:

```sh
git clone https://github.com/hinnerk/cftpl.git
cd cftpl
python bootstrap.py
./bin/buildout
```

`cfmgr` is available as `bin/cfmgr`. No system packages are modified, all dependencies are installed within the top level directory.

# Example

## First Step: Configuration

Go to the `example` directory or download the example files to an otherwise empty directory:

* [config.py](https://raw.githubusercontent.com/hinnerk/cftpl/master/example/config.py)
* [example.yaml](https://raw.githubusercontent.com/hinnerk/cftpl/master/example/example.yaml)


In `config.py`:

1. Set the `ACCOUNT` to your actual AWS access key id. Keep your secret access key handy, but do not enter it anywhere yet.
2. Set `EMAIL` to your email address. It will be used to inform you about started and stopped instances.


## Second Step: Validate and Create Stack

### Test your Stack

The command `cfmgr test config.py` will validate the configuration online. Because of that you will need to enter your secret access key. This key will be stored in your operating systems encrypted key store (Keychain on Mac OS X, the Linux Secret Service, the Windows Credential Vault) and only used to authenticate AWS API calls.

Additionally it will display the configuration of the stack and all files defined in the configuration file.

```
$ ../bin/cfmgr test config.py
Please enter password for "ABCDEF1234567890":
Validating template... successfull.
This is the configuration we'd use if this was for real:


{
    "AWSTemplateFormatVersion": "2010-09-09",
    [...]
}


Here are all the files you can use:
	"salt-installer":	"install-salt.sh"
```


### Create your Stack

**Warning: This will cost your money.** Because this step creates ressources on AWS charges will occur. Do not proceed if you do not understand what that means.

You might want to open the [AWS  CloudFormation Management Console](https://console.aws.amazon.com/cloudformation) and watch closely while your stack is created.

```
$ ../bin/cfmgr create config.py
Validating template... successfull.
Creating Stack CFTPL-Example-Stack... done.
Showing status messages for stack None:
	2014-05-21 12:01:21.997000: AWS::CloudFormation::Stack    CREATE_IN_PROGRESS                           CFTPL-Example-Stack      	User Initiated
    [...]
```

The command will show all log messages until the stack creation is complete. You can break this any time with Ctrl-C. Please note that this cancels the display of messages only; the stack creation will continue in the background. Again, it is a good idea to watch this in the [AWS  CloudFormation Management Console](https://console.aws.amazon.com/cloudformation) until you are familiar with the system.

**Important: Do not forget to confirm your SNS topic subscription.** The example configuration creates an Amazon Simple Notification Service Topic and subscribes your email to it so you receive emails whenever an EC2 instance is created or deleted.


### Update your stack

**Warning: This will create a running EC2 instance. Do not forget to delete the stack later to prevent charges from piling up.**

Up to now the stack has not created any EC2 instances. While we can just go ahead and add one to the stack, it is usually more serviceable to let AWS handle the creation and destruction of actual instances. This is done through the modification of AutoScalingGroups.

Change the lines 16 and 17 of the example configuration. `MaxSize: '0'` to `MaxSize: '1'` and `DesiredCapacity: '0'` to `DesiredCapacity: '1'`.

From this:

```YAML
      MinSize: 0
      MaxSize: '0'
      DesiredCapacity: '0'
```

To this:

```YAML
      MinSize: 0
      MaxSize: '1'
      DesiredCapacity: '1'
```

Be careful to keep the indention intact.

Now update the running stack:

```
$ ../bin/cfmgr update config.py
Validating template... successfull.
Updating Stack CFTPL-Example-Stack... done.
 done.
Showing status messages for stack CFTPL-Example-Stack:
    [...]
	2014-05-21 12:38:38.201000: AWS::CloudFormation::Stack    UPDATE_IN_PROGRESS                           CFTPL-Example-Stack      	User Initiated
	2014-05-21 12:38:48: AWS::AutoScaling::AutoScalingGroup   UPDATE_IN_PROGRESS                           DemoServerASGroup        	None
	2014-05-21 12:38:49: AWS::AutoScaling::AutoScalingGroup   UPDATE_COMPLETE                              DemoServerASGroup        	None
	2014-05-21 12:38:52.014000: AWS::CloudFormation::Stack    UPDATE_COMPLETE_CLEANUP_IN_PROGRESS          CFTPL-Example-Stack      	None
	2014-05-21 12:38:53.679000: AWS::CloudFormation::Stack    UPDATE_COMPLETE                              CFTPL-Example-Stack      	None
Status:	UPDATE_COMPLETE
```

The AutoScalingGroup now knows that it is supposed to create an EC2 Instance. You can see that instance being created in the [AWS EC2 Management Console](https://console.aws.amazon.com/ec2). Additionally you should receive an email that informs you about the new instance.

The number of running instances is managed by AutoScaling. Thus when you destroy the running instance using Actions => Terminate in the EC2 Management Console, another one is created and you should receive separate emails about the destruction of the old and the creation of a new instance.

To stop all instances from running either change  `MaxSize: '1'` to  `MaxSize: '0'` and `DesiredCapacity: '1'` back to `DesiredCapacity: '0'` and update the stack, or just delete the whole stack.


### Delete your Stack

This deletes the stack and most of its associated ressources. Some ressources, like database backups and S3 buckets are not necessarily removed to prevent data loss. So deleting a stack may not stop all charges. Please read the AWS documentation to find out which ressources will persist.

```
$ ../bin/cfmgr delete config.py
arn:aws:cloudformation:eu-west-1:001408880364:stack/CFTPL-Example-Stack/83772a30-e0ee-11e3-8185-50014118ec7c	CFTPL-Example-Stack	CREATE_COMPLETE
Should I delete CFTPL-Example-Stack? yes
Deleting stack CFTPL-Example-Stack...done.
Showing status messages for stack CFTPL-Example-Stack:
    [...]
	2014-05-21 13:49:27.413000: AWS::CloudFormation::Stack    DELETE_IN_PROGRESS                           CFTPL-Example-Stack      	User Initiated
	2014-05-21 13:49:43: AWS::AutoScaling::AutoScalingGroupDELETE_IN_PROGRESS                           DemoServerASGroup        	None
	2014-05-21 13:49:44: AWS::AutoScaling::AutoScalingGroupDELETE_COMPLETE                              DemoServerASGroup        	None
	2014-05-21 13:49:45: AWS::SNS::Topic               DELETE_IN_PROGRESS                           DemoAutoScalingSNSTopic  	None
	2014-05-21 13:49:45: AWS::AutoScaling::LaunchConfigurationDELETE_IN_PROGRESS                           DemoServerLaunchConfig   	None
	2014-05-21 13:49:46: AWS::AutoScaling::LaunchConfigurationDELETE_COMPLETE                              DemoServerLaunchConfig   	None
	2014-05-21 13:49:46: AWS::SNS::Topic               DELETE_COMPLETE                              DemoAutoScalingSNSTopic  	None
	2014-05-21 13:49:48: AWS::EC2::SecurityGroup       DELETE_IN_PROGRESS                           DemoServerSecurityGroup  	None
	2014-05-21 13:49:49: AWS::EC2::SecurityGroup       DELETE_COMPLETE                              DemoServerSecurityGroup  	None
Status:	DELETE_COMPLETE
```

# Additional Commands


## Converting JSON to YAML

`cfmgr convert config.py` converts an existing JSON into an YAML template:

* Copy your existing JSON stack template file into the directory of the example configuration. Make sure that the file ends with `.json`.
* In the configuration change the value of `TEMPLATE` to the name of that file.

Then call `cfmgr convert config.py`:

```
$ ../bin/cfmgr convert config.py
Reading JSON from:
    example/my-old-stack.json
YAML written to:
    example/my-old-stack.yaml
DONE

$ ls -la
-rw-r--r--   1 user  staff    188 May 16 15:50 config.py
-rw-r--r--   1 user  staff  25984 May 16 16:13 my-old-stack.json
-rw-r--r--   1 user  staff  12562 May 16 16:13 my-old-stack.yaml
```

You can now change `TEMPLATE = 'my-old-stack.json.yaml'`. Do not forget to version control it prior to editing  it. ;)

## Show Template YAML

Sometimes, especially when developing macros, it's nice to see the generated YAML code prior to the further export to JSON. `cfmgr show config.py` does just that:

```
$ ../bin/cfmgr show config.py
This is the rendered template:


AWSTemplateFormatVersion: '2010-09-09'
Description: CFTPL Example.
Resources:
  [...]
```

## List all Stacks

`cfmgr list config.py` returns a list of all existing running and deleted stacks:

```
$ ../bin/cfmgr list config.py

Region:   eu-west-1
Endpoint: cloudformation.eu-west-1.amazonaws.com

NAME         | CFTPL-Example-Stack
-------------+-------------------------------------
STATUS       | DELETE_COMPLETE
REASON       |
[...]
```

# Use as a library

```python
import cftpl

config = cftpl.get_settings('path/to/config.py')
template = cftpl.CFTemplate(config)
stack = cftpl.CFStack(config)
```

TODO: Add documentation here.


# Password Management

## Stand Alone Executable

On the first start the executable will ask for the password and store it in the local encrypted password storage of the operating system. That's Keychain on Mac OS X, the Linux Secret Service and the Windows Credential Vault.

This password will be reused on further calls, so you don't have to type it while it is still stored adequately secure.

## Library Calls

Whenever the library is running on an AWS instance, [Temporary Security Credentials](http://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html#use-roles) are the solution you're looking for.

Cftpl will use temporary security credentials by default whenever available.

If your company has implemented some kind of password management, you can call `CFStack()` with a password:

```python
from cftpl import CFStack

password = ge_password()
config = get_config()
stack = CFStack(config, password=password)

stack.update()
```

Lastly one could create boto configuration files and leave them lie about, so they can be read by an attacker or accidentally checked into a public repository. Honestly, AWS has a perfectly serviceable key management right built in, so why not use it?


# JSON vs. YAML + Jinja2

This is part of a template we actually use. Being written in YAML and using a Jinja2 `for` loop it's quite readable. Note, that YAML allows comments:

```YAML
SOMEDNS:
  Type: AWS::Route53::RecordSetGroup
  Properties:
    Comment: TEST CASE Zone Records
    HostedZoneName: test.local.
    # just to show off: YAML does comments
    RecordSets:
      {% for name in ('calendar', 'chat', 'docs', 'mail', 'start') %}
      - Name: {{ name }}.test.local.
        Type: CNAME
        TTL: "43200"
        ResourceRecords: ["ghs.google.com."]
      {% endfor %}
```

This is the same as above in the format CloudFormation accepts (JSON). Please note that while it's quite a bit longer, JSON does not allow comments.:


```JSON
"SOMEDNS": {
    "Type": "AWS::Route53::RecordSetGroup",
    "Properties": {
        "Comment": "TEST CASE Zone Records",
        "HostedZoneName": "test.local.",
        "RecordSets": [
            {
                "ResourceRecords": [
                    "ghs.google.com."
                ],
                "Type": "CNAME",
                "Name": "calendar.test.local.",
                "TTL": "43200"
            },
            {
                "ResourceRecords": [
                    "ghs.google.com."
                ],
                "Type": "CNAME",
                "Name": "chat.test.local.",
                "TTL": "43200"
            },
            {
                "ResourceRecords": [
                    "ghs.google.com."
                ],
                "Type": "CNAME",
                "Name": "docs.test.local.",
                "TTL": "43200"
            },
            {
                "ResourceRecords": [
                    "ghs.google.com."
                ],
                "Type": "CNAME",
                "Name": "mail.test.local.",
                "TTL": "43200"
            },
            {
                "ResourceRecords": [
                    "ghs.google.com."
                ],
                "Type": "CNAME",
                "Name": "start.test.local.",
                "TTL": "43200"
            }
        ]
    }
},
```

[j2]: http://jinja.pocoo.org/docs/templates/
