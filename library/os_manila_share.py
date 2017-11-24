#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule

import os_client_config


ANSIBLE_METADATA = {'metadata_version': '1.0'}


def get_share_client(module):
    # NOTE: set OS_CLOUD environment variable to choose from clouds.yaml
    try:
        cloud_config = os_client_config.get_config()
        share_client = cloud_config.get_session_client("sharev2")
    except Exception, e:
        module.fail_json(
            msg="Please check your OpenStack credentials: %s" % e)

    return share_client


def get_share_details(share_client, share_name):
    headers={"X-Openstack-Manila-Api-Version": "2.6"}
    raw_shares = share_client.get(
        "/shares/detail?name=%s" % "jmfg2-spark-test",
        headers=headers).json()['shares']
    if not raw_shares:
        # TODO - we could create the share, if given enough info
        raise Exception("Unable to find requested share.")

    raw_share = raw_shares[0]

    share = {
        "name": raw_share['name'],
        "id": raw_share['id'],
        "size" : raw_share['size'],
        "protocol": raw_share['share_proto'],
        "type": raw_share['share_type_name'],
        "type_id": raw_share['share_type'],
    }

    # TODO - some drivers have a preferred export.
    exports = raw_share['export_locations']
    if exports:
        share['export'] = exports[0]

    # Looking for either host:port:path or host:path in export
    split_export = share['export'].split(":")
    split_len = len(split_export)
    if split_len == 2 or split_len == 3:
        share['path']= split_export[-1]
    if split_len == 2:
        share['host'] = split_export[0]
    if split_len == 3:
        share['host'] = "%s:%s" % (split_export[0], split_export[1])

    return share


def get_access_key(share_client, share_id, user):
    headers={"X-Openstack-Manila-Api-Version": "2.40"}
    payload = {"access_list": None}
    raw_access_list = share_client.post(
            "/shares/%s/action" % share_id,
            json=payload, headers=headers).json()['access_list']

    access_key = None
    for access in raw_access_list:
        if access['access_to'] == "spark":
            access_key = access['access_key']
            break

    return access_key


def main():
    module = AnsibleModule(
        argument_spec = dict(
            name=dict(required=True, type='str'),
            user=dict(required=True, type='str'),
            protocol=dict(required=False, type='str'),
            size_gb=dict(required=False, type='int'), # only checks the size
            type=dict(required=False, type='str'),  # unused - for creation
        ),
        supports_check_mode=False
    )

    share_client = get_share_client(module)

    share_name = module.params['name']
    share = get_share_details(share_client, share_name)

    user = module.params['user']
    share_id = share['id']
    access_key = get_access_key(share_client, share_id, user)

    if not access_key:
        # TODO we could add access here
        module.fail_json(msg="User does not have access to share.")
    share['access_key'] = access_key

    required_protocal = module.params.get('protocol')
    if required_protocal and share['protocol'] != required_protocal:
        module.fail_json(
            msg="Protocol %s does not match requested." % share['protocol'])

    required_size = module.params.get('size')
    if required_size and share['size'] != required_size:
        # TODO if size doesn't match, we could expand the share
        module.fail_json(
            msg="Size %s does not match requested." % share['size'])

    module.exit_json(changed=False, details=share)

if __name__ == '__main__':
    main()
