stackhpc.os-manila-mount
========================

Mount one or more shares created by OpenStack Manila.

Currently only supports:
- CephFS-protocol shares
- RockyLinux 8 and 9
- Ubuntu Jammy and Noble

Requirements
------------

The host running the lookup action (see below) requires the following python packages:

- `openstacksdk`
- `python-openstackclient`
- `python-manilaclient`

That host also requires OpenStack credentials and access to the OpenStack APIs.

Role Taskfiles
--------------

The default `tasks/main.yml` task file will install packages, lookup Manila share
details, create client configuration and mount shares. However it is possible to
separate out these actions using specific task files:
- `install.yml`: Only install release repo and packages.
- `lookup.yml`: Only lookup share details.
- `mount.yml`: Only create client configuration and mount shares.

This may be useful for image build, or for situations where it is undesirable to
dynamically retrieve share information during mount.

Role Variables
--------------

* `os_manila_mount_shares`: List of dicts defining the shares to mount, each
containing:
  - `share_name`: Required. Name in Manila for the share ("Name" from `openstack share
  list`).
  - `share_user`: Optional if share only has one access rule defined, otherwise required.
  CephX user for access ("Access To" from `openstack share access list <share_name>`).
  - `mount_path`: Required. Directory path to mount the share at (will be created).
  - `mount_user`: Optional. User to mount as (default: become user).
  - `mount_group`: Optional. Group to mount as (default: become user).
  - `mount_mode`: Optional. Permissions for mounted directory, as for [ansible.builtin.file:mode](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html#parameter-mode)
  - `mount_opts`: Optional. List of strings defining mount options. Default from
  `os_manila_mount_opts` (i.e. same for all mounts).
  - `mount_state`: Optional. Mount state, default from `os_manila_mount_state` (i.e. same for
  all mounts).

* `os_manila_share_lookup_host`: Optional. Inventory hostname of host to run lookup on.
Default `localhost`.
* `os_manila_share_lookup_once`: Optional. Bool controlling whether to run the lookup
task on only one host. Default is `true` for speed, but if 
`os_manila_mount_shares` varies between hosts in the play this must be set to `false`.

* `os_manila_mount_state`: Optional. As for `state` of [ansible.posix.mount](https://docs.ansible.com/ansible/latest/collections/ansible/posix/mount_module.html). Default `mounted`.
* `os_manila_mount_opts`: Optional. List of strings defining default mount options
(see `defaults/main.yml`).

* `os_manila_mount_share_info`: Automatically populated by lookup task. If not running
that, this should be a list of dicts each containing:
  - `host`: Host/port for Ceph mon(s), e.g. `mon1:port,mon2:port,mon3:port`
  - `export`: Exported path.
  - `access_key`: The access key for this share for the `share_user`.
  **WARNING: This value should be kept secret.**

  If necessary for debugging, set `no_log=false` to see this variable. Note that running ansible with
`-v` will expose `access_key`.

Ceph variables:
* `os_manila_mount_ceph_version`: Optional. Ceph numerical version string, e.g. '17.2.7' not 'quincy'. Default is the oldest supported by the hosts' distribution/version. Must be 15.2.x (Octopus) or later. Note that on RockyLinux changing this and rerunning the role can change the installed version, but on Ubuntu it cannot. After Ubuntu Jammy, this variable has no effect and the version of `ceph-common` available in the distribution repository is installed.
* `os_manila_mount_ceph_repo_key`: Optional. URL for Ceph repo key. No effect after Ubuntu Jammy.
* `os_manila_mount_ceph_release_repo`: Optional. URL for Ceph release repo. No effect after Ubuntu Jammy.
* `os_manila_mount_ceph_conf_path`: Optional. Path for Ceph configuration directory,
default `/etc/ceph`.


Example Playbook
----------------

Note this role must be run with `become`.

    ---
    - hosts: all
      become: yes
      gather_facts: no
      vars:
        os_manila_mount_shares:
        - share_name: manila-test-share
          share_user: testuser
          mount_path: /mnt/manila
          mount_user: "{{ ansible_user }}"
          mount_group: "{{ ansible_user }}"
      tasks:
        - import_role:
            name: stackhpc.os-manila-mount

An easy way to run this example with both the lookup and the mount done on localhost is:

    python -m venv venv
    . .venv/bin/activate
    pip install -U pip
    pip install -U ansible python-openstackclient python-manilaclient
    ansible-galaxy install stackhpc.os-manila-mount

    ansible-playbook -v local test.yml

License
-------

Apache

Author Information
------------------

http://www.stackhpc.com
