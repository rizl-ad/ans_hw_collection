yc_vm_create
============

The role creates compute instances with specified parameters in Yandex Cloud. The role uses the yc_vm_create module.

Role Variables
--------------
| argument | default value | description |
| -------- | ------------- | ----------- |
| `folder_id` | No default value | Required argument. Yandex Cloud folder ID |
| `zone` | No default value | Required argument. Yandex Cloud availability zone. |
| `subnet_id` | No default value | Required argument. The subnet to which the compute instance will be connected. |
| `vm_name` | No default value | Required argument. Compute instance name. |
| `image_family_id` | 'ubuntu-2404-lts-oslogin' | Compute instance boot disk image. |
| `memory` | 2 | Compute instance RAM. |
| `cores` | 2 | Compute instance virtual CPU count. |
| `core_fraction` | 20 | Compute instance virtual CPU guaranteed share. |
| `disk_size` | 10 | Compute instance disk size in GB. |
| `user_name` | No default value | Required argument. The name of the user that will be created on the compute instance. |
| `pub_ssh_key` | No default value | Required argument. Path to the public SSH authentication key file. |
| `priv_ssh_key` | No default value | Required argument. Path to the private SSH authentication key file. |
| `sa_key` | No default value | Required argument. Path to the Yandex Cloud service account key JSON file. |
| `host_group` | 'ungrouped' | Host group for ansible inventory. |
| `playbook_dir` | No default value | Path to the directory containing the playbook calling the module. |

Example Playbook
----------------

```yaml
- name: Create compute instance
  hosts: localhost
  gather_facts: false

  roles:
    - yc_vm_create
  vars:
    playbook_dir: '{{ playbook_dir }}'
```

License
-------

MIT

Author Information
------------------

Yaroslav Lysenko