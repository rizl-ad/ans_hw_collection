#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: yc_vm_create

short_description: This module creates compute instances in Yandex Cloud.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This module creates compute instances in Yandex Cloud.

options:
    folder_id:
        description: Yandex Cloud folder ID.
        required: True
        type: str
    zone:
        description: Yandex Cloud availability zone.
        required: True
        type: str
    subnet_id:
        description: The subnet to which the compute instance will be connected.
        required: True
        type: str
    vm_name:
        description: Compute instance name.
        required: True
        type: str
    image_family_id:
        description: Compute instance boot disk image.
        required: False
        type: str
    memory:
        description: Compute instance RAM.
        required: False
        type: int
    cores:
        description: Compute instance virtual CPU count.
        required: False
        type: int
    core_fraction:
        description: Compute instance virtual CPU guaranteed share.
        required: False
        type: int
    disk_size:
        description: Compute instance disk size.
        required: False
        type: int
    user_name:
        description: The name of the user that will be created on the compute instance.
        required: True
        type: str
    pub_ssh_key:
        description: Path to the public SSH authentication key file.
        required: True
        type: path
    priv_ssh_key:
        description: Path to the private SSH authentication key file.
        required: True
        type: path
    sa_key:
        description: Path to the service account key JSON file.
        required: True
        type: path
    host_group:
        description: Host group for ansible inventory.
        required: False
        type: str
    playbook_dir:
        description: Path to the directory containing the playbook calling the module
        required: True
        type: path
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Yaroslav Lysenko (@rizl-ad)
'''

EXAMPLES = r'''
# Create YC compute instance
- name: Create YC compute instance
  rizl_ad.my_collection.yc_vm_create:
    folder_id: "_folder id value_"
    zone: "ru-central1-a"
    subnet_id: "_subnet id value_"
    vm_name: "test-vm"
    image_family_id: "ubuntu-2404-lts-oslogin"
    memory: 2
    cores: 2
    core_fraction: 20
    disk_size: 10
    user_name: "rizl"
    pub_ssh_key: "~/.ssh/pub-ssh-key"
    priv_ssh_key: "~/.ssh/id_rsa"
    sa_key: "~/.ssh/.authorized_key.json"
    host_group: "test"
    playbook_dir: "{{ playbook_dir }}"
'''

RETURN = r'''
# These are the possible return messages.
message:
    description: The output message that the module generates.
    type: str
    returned: always
    sample: 'VM {vm_name} with ID {instance_id} was created successfully'
'''

from ansible.module_utils.basic import AnsibleModule

import json
import yaml
import grpc
import yandexcloud

from pathlib import Path
from yandex.cloud.compute.v1.image_service_pb2 import GetImageLatestByFamilyRequest
from yandex.cloud.compute.v1.image_service_pb2_grpc import ImageServiceStub
from yandex.cloud.compute.v1.instance_pb2 import IPV4, Instance
from yandex.cloud.compute.v1.instance_service_pb2 import (
    AttachedDiskSpec,
    CreateInstanceMetadata,
    CreateInstanceRequest,
    NetworkInterfaceSpec,
    OneToOneNatSpec,
    PrimaryAddressSpec,
    ResourcesSpec,
)
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        folder_id=dict(type='str', required=True),
        zone=dict(type='str', required=True),
        subnet_id=dict(type='str', required=True),
        vm_name=dict(type='str', required=True),
        image_family_id=dict(type='str', required=False, default='ubuntu-2404-lts-oslogin'),
        memory=dict(type='int', required=False, default=2),
        cores=dict(type='int', required=False, default=2),
        core_fraction=dict(type='int', required=False, default=20),
        disk_size=dict(type='int', required=False, default=10),
        user_name=dict(type='str', required=True),
        pub_ssh_key=dict(type='path', required=True),
        priv_ssh_key=dict(type='path', required=True),
        sa_key=dict(type='path', required=True),
        host_group=dict(type='str', required=False, default='ungrouped'),
        playbook_dir=dict(type='path', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        failed=False,
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    def create_instance(sdk, folder_id, zone, name, subnet_id, image_family_id, memory, cores, core_fraction, disk_size, user_name, pub_ssh_key):

        with open(pub_ssh_key) as ssh_key_file:
            ssh_key_value = ssh_key_file.read()

        user_data_template = f"""
        #cloud-config
        users:
        - name: {user_name}
          groups: sudo
          shell: /bin/bash
          sudo: 'ALL=(ALL) NOPASSWD:ALL'
          ssh_authorized_keys:
          - {ssh_key_value}
        """

        image_service = sdk.client(ImageServiceStub)
        source_image = image_service.GetLatestByFamily(
            GetImageLatestByFamilyRequest(folder_id="standard-images", family=image_family_id)
        )
        subnet_id = subnet_id or sdk.helpers.get_subnet(folder_id, zone)
        instance_service = sdk.client(InstanceServiceStub)
        instance = instance_service.Create(
            CreateInstanceRequest(
                folder_id=folder_id,
                name=name,
                resources_spec=ResourcesSpec(
                    memory=memory * 2**30,
                    cores=cores & ~1,
                    core_fraction=core_fraction,
                ),
                zone_id=zone,
                platform_id="standard-v3",
                boot_disk_spec=AttachedDiskSpec(
                    auto_delete=True,
                    disk_spec=AttachedDiskSpec.DiskSpec(
                        type_id="network-hdd",
                        size=disk_size * 2**30,
                        image_id=source_image.id,
                    ),
                ),
                network_interface_specs=[
                    NetworkInterfaceSpec(
                        subnet_id=subnet_id,
                        primary_v4_address_spec=PrimaryAddressSpec(
                            one_to_one_nat_spec=OneToOneNatSpec(
                                ip_version=IPV4,
                            )
                        ),
                    ),
                ],
                metadata={
                    "user-data": user_data_template,
                },
            )
        )
        return instance

    def create_inventory(playbook_dir, group, hostname, ip_adress, user, ssh_key):
        # playbook_dir_parent = Path(playbook_dir).resolve().parent
        inventory_path = Path(f'{playbook_dir}/inventory/yc_hosts.yml')
        if inventory_path.exists():
            with open(inventory_path) as f:
                inventory = yaml.safe_load(f)
                if inventory is None:
                    inventory = {}
        else:
            inventory = {}
            inventory_path.parent.mkdir(parents=True, exist_ok=True)
        inventory.setdefault(group, {}).setdefault('hosts', {})
        inventory[group]['hosts'][hostname] = {
            "ansible_host": ip_adress,
            "ansible_user": user,
            "ansible_ssh_private_key_file": ssh_key
        }
        with open(inventory_path, 'w') as f:
            yaml.dump(inventory, f)

    retry_policy = yandexcloud.RetryPolicy(
        max_attempts=5,
        status_codes=[grpc.StatusCode.UNAVAILABLE]
    )
    with open(module.params['sa_key']) as sa_key_f:
        sdk = yandexcloud.SDK(retry_policy=retry_policy, service_account_key=json.load(sa_key_f))
    try:
        instance = create_instance(
            sdk,
            module.params['folder_id'],
            module.params['zone'],
            module.params['vm_name'],
            module.params['subnet_id'],
            module.params['image_family_id'],
            module.params['memory'],
            module.params['cores'],
            module.params['core_fraction'],
            module.params['disk_size'],
            module.params['user_name'],
            module.params['pub_ssh_key']
        )
        instance_result = sdk.wait_operation_and_get_result(
            instance,
            response_type=Instance,
            meta_type=CreateInstanceMetadata,
        )
        instance_id = instance_result.response.id
        public_ip_adress = instance_result.response.network_interfaces[0].primary_v4_address.one_to_one_nat.address
        try:
            create_inventory(
                module.params['playbook_dir'],
                module.params['host_group'],
                module.params['vm_name'],
                public_ip_adress,
                module.params['user_name'],
                module.params['priv_ssh_key']
            )
            result['changed'] = True
            result['message'] = f'Compute instance {module.params['vm_name']} with ID {instance_id} was created successfully'
        except Exception as e:
            module.fail_json(msg=f'An exception occurred while creating inventory file: {e}', **result)
    except Exception as e:
        if 'ALREADY_EXISTS' in str(e):
            result['message'] = f'Compute instance with name {module.params['vm_name']} already exists'
        else:
            result['failed'] = True
            module.fail_json(msg=f'An exception occurred while creating compute instance {module.params['vm_name']}: {e}', **result)

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    # if module.params['name'] == 'fail me':
    #     module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)



def main():
    run_module()


if __name__ == '__main__':
    main()
