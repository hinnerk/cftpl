#!/bin/bash
set -e -x
export DEBIAN_FRONTEND=noninteractive

# add the salt stack repository
add-apt-repository -y ppa:saltstack/salt

# update the apt library with the current versions
apt-get --yes --quiet update

# install salt stack and dependencies
# apt-get --yes install python-software-properties
apt-get --yes install debconf-utils
apt-get --yes install salt-minion
apt-get --yes upgrade

# instantiate the local minion, set initial role
# printf '\nstartup_states: highstate\nmaster: master.local\n\ngrains:\n  roles:\n    - some-role\n\n' >> /etc/salt/minion
# /sbin/restart salt-minion