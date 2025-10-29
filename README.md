Ansible Collection - rizl_ad.my_collection
------------------------------------------

This collection contains the following modules and roles:

Modules:
| module name | description |
| ----------- | ----------- |
| txt_file | Create a text file with a specified name, path, and contents. |
| yc_vm_create | Creates a compute instance with the specified parameters in Yandex Cloud and dynamically creates an Ansible inventory file `inventory/inventory.yml.` |

Roles:
| role name | description |
| --------- | ----------- |
| lighthouse | Installing and configuring Lighthouse |
| txt_file | Create text file |
| yc_vm_create | Create compute instance with inventory |
| vector |  Installing and configuring Vector |

See the role description in the role meta directory.

txt_file
--------

The txt_file module contains the following arguments:

| argument | type | default value | description |
| -------- | ---- | ------------- | ----------- |
| `name` | str | No default value | Required argument. Name of the file being created without specifying the extension |
| `path` | str | No default value | Required argument. The directory in which the file being created is created |
| `contenet` | str | '' | Optional argument. Contents of the created file |
| `overwrite` | bool | False | Optional argument. File overwrite flag |

> [!NOTE]
> If the 'overwrite' argument is true and a file with the specified path and name exists, and the existing file's hash equals the hash of the file being created, the file will not be overwritten.
>
> If the 'overwrite' argument is false and a file with the specified path and name exists, and the existing file's hash does not equal the hash of the file being created, the file creation will be skipped.


Usage example
-------------

```yaml
- name: Create text file
  rizl_ad.my_collection.txt_file:
    name: file_name
    path: /tmp
    content: 'file content'
    overwrite: true
```


yc_vm_create
------------

The yc_vm_create module contains the following arguments:

| argument | type | default value | description |
| -------- | ---- | ------------- | ----------- |
| `folder_id` | str | No default value | Required argument. Yandex Cloud folder ID |
| `zone` | str | No default value | Required argument. Yandex Cloud availability zone. |
| `subnet_id` | str | No default value | Required argument. The subnet to which the compute instance will be connected. |
| `vm_name` | str | No default value | Required argument. Compute instance name. |
| `image_family_id` | str | 'ubuntu-2404-lts-oslogin' | Compute instance boot disk image. |
| `memory` | int | 2 | Compute instance RAM. |
| `cores` | int | 2 | Compute instance virtual CPU count. |
| `core_fraction` | int | 20 | Compute instance virtual CPU guaranteed share. |
| `disk_size` | int | 10 | Compute instance disk size in GB. |
| `user_name` | str | No default value | Required argument. The name of the user that will be created on the compute instance. |
| `pub_ssh_key` | path | No default value | Required argument. Path to the public SSH authentication key file. |
| `priv_ssh_key` | path | No default value | Required argument. Path to the private SSH authentication key file. |
| `sa_key` | path | No default value | Required argument. Path to the Yandex Cloud service account key JSON file. |
| `host_group` | str | 'ungrouped' | Host group for ansible inventory. |
| `playbook_dir` | path | No default value | Path to the directory containing the playbook calling the module. |

> [!NOTE]
> Count of cores must be even, if an odd number is specified, it will be automatically reduced to an even number.
>
> If a compute instance with the specified name already exists, the module will do nothing and return an "ok" result.
>
> If a host with the specified name already exists in the file `inventory/inventory.yml`, the entry for that host will be updated.

Dependencies
------------

grpcio   
grpcio-tools   
pathlib   
yandexcloud >= 0.364.0


Usage example
-------------

```yaml
- name: Create YC compute instance
  rizl_ad.my_collection.yc_vm_create:
    folder_id: "_you_folder_id_value_"
    zone: "ru-central1-a"
    subnet_id: "_you_subnet_id_value_"
    vm_name: "test-vm"
    image_family_id: "ubuntu-2404-lts-oslogin"
    memory: 2
    cores: 2
    core_fraction: 20
    disk_size: 10
    user_name: "app"
    pub_ssh_key: "~/.ssh/pub-ssh-key"
    priv_ssh_key: "~/.ssh/id_rsa"
    sa_key: "~/.authorized_key.json"
    host_group: "test"
    playbook_dir: "{{ playbook_dir }}"
```


License
-------

MIT


Author Information
------------------

Yaroslav Lysenko
