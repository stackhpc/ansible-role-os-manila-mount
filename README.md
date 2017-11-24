stackhpc.os-manila-mount
========================

[![Build Status](https://www.travis-ci.org/stackhpc/ansible-role-os-manila-mount.svg?branch=master)](https://www.travis-ci.org/stackhpc/ansible-role-os-manila-mount)

Mount a share created by OpenStack Manila.

Currently only supports CephFS. We have plans to add GlusterFS.

Requirements
------------

This role only requires Ansible.

Role Variables
--------------

TODO.

Dependencies
------------

This role depends on openstack configuration being placed at
`/etc/openstack/clouds.yaml`
One way to do that is using the role ``stackhpc.os-config``.

Example Playbook
----------------

This example pulls a few things together so you push the OpenStack config,
and then mount a preexisting manila share:

    ---
    - hosts: all
      vars:
        my_cloud_config: |
          ---
          clouds:
            mycloud:
              auth:
                auth_url: http://openstack.example.com:5000
                project_name: p3
                username: user
                password: secretpassword
              region: RegionOne
      roles:
        - { role: stackhpc.os-config,
            os_config_content: "{{ my_cloud_config }}" }
        - { role: stackhpc.os-manila-mount,
            os_manila_mount_os_config_name: "mycloud",
            os_manila_mount_share_name: my-share,
            os_manila_mount_share_user: fakeuser }

An easy way to this example is:

    sudo yum install python-virtualenv libselinux-python

    virtualenv .venv --system-site-packages
    . .venv/bin/activate
    pip install -U pip
    pip install -U ansible

    ansible-galaxy install stackhpc.os-manila-mount \
                           stackhpc.os-config

    ansible-playbook -i "localhost," -c local test.yml

License
-------

Apache

Author Information
------------------

http://www.stackhpc.com
