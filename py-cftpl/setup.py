#  Copyright (c) 2014, HIT Information-Control GmbH
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or
#  without modification, are permitted provided that the following
#  conditions are met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials
#        provided with the distribution.
#
#      * Neither the name of the HIT Information-Control GmbH nor the names of its
#        contributors may be used to endorse or promote products
#        derived from this software without specific prior written
#        permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
#  CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL HIT Information-Control GmbH BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
#  OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
#  OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
#  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#  OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
#  OF SUCH DAMAGE.


import os
from setuptools import setup, find_packages


#
# Try to convert README.md Markdown to ReStructuredText.
# This mostly matters for pypi registration, so in most cases failure is just fine.
#
try:
    import pypandoc
except ImportError:
    pypandoc = None

README = os.path.join('..', 'README.md')
LONG_DESC = 'Templates and Management for AWS CloudFormation.'
if os.path.isfile(README):
    LONG_DESC = open(README).read()
    if pypandoc:
        try:
            output = pypandoc.convert(LONG_DESC, 'rst', format='md')
        except OSError, e:
            print "ERROR: {}".format(e.message)
        else:
            LONG_DESC = output

tests_require = ['mock', ]

setup(
    name="cftpl",
    description="Templates and Management for AWS CloudFormation.",
    long_description=LONG_DESC,
    version="1.0",

    install_requires=['setuptools', 'boto', 'keyring', 'jinja2', 'PyYAML'] + tests_require,

    entry_points={
        'console_scripts': ['cfmgr = cftpl.run:run', ],
    },
    scripts=[],  # let setuptools handle the script(s)

    package_dir={'': '.'},
    packages=find_packages(),
    test_suite="cftpl.tests",

    url='https://github.com/hinnerk/cftpl',
    license="(c) 2014 HIT Information-Control GmbH",  # open("LICENSE.txt").read(),
    author='Hinnerk Haardt, HIT Information-Control GmbH',
    author_email='haardt@information-control.de',

    keywords=['Amazon Web Services', 'CloudFormation', 'AWS'],
    classifiers=[
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
    ]
)
