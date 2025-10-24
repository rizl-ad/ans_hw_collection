#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: txt_file

short_description: This is my test module

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    name:
        description: This is the name of the text file being created (without specifying the extension).
        required: true
        type: str
    path:
        description: This is the directory in which you need to create the file.
        required: true
        type: str
    content:
        description: This is the content of the text file being created.
        required: false
        type: str
    overwrite:
        description: Specifies whether to overwrite the file if it already exists. If the file exists and is set to false, file creation will be skipped.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Yaroslav Lysenko (@rizl-ad)
'''

EXAMPLES = r'''
# Create empty text file
- name: Create emprty text file
  my_namespace.my_collection.txt_file:
    name: test
    path: /tmp

# Create text file with content
- name: Create text file
  my_namespace.my_collection.txt_file:
    name: test
    path: /tmp
    content: 'test text'
'''

RETURN = r'''
# These are the possible return messages.
message:
    description: The output message that the module generates.
    type: str
    returned: always
    sample: 'File {full_path} was created successfully'
'''

from ansible.module_utils.basic import AnsibleModule
import hashlib


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        path=dict(type='str', required=True),
        content=dict(type='str', required=False, default=''),
        overwrite=dict(type='bool', required=False, default=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        failed=False,
        skipped=False,
        # original_message='',
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

    def file_hash(path):
        hashing = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hashing.update(chunk)
        return hashing.hexdigest()

    def compare_file_hash(path, content):
        existing_hash = file_hash(path)
        new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        if existing_hash == new_hash:
            return True
        else:
            return False

    full_path = f'{module.params['path']}/{module.params['name']}.txt'
    try:
        txt_file = open(f'{full_path}', 'x')
        txt_file.write(f'{module.params['content']}')
        txt_file.close()
        result['changed'] = True
        result['message'] = f'File {full_path} was created successfully'
    except FileExistsError:
        if compare_file_hash(full_path, module.params['content']):
            result['message'] = f'File {full_path} already exists'
        else:
            if module.params['overwrite']:
                if 'txt_file' in locals() and not txt_file.closed:
                    txt_file.close()
                txt_file = open(f'{full_path}', 'w')
                txt_file.write(f'{module.params['content']}')
                txt_file.close()
                result['changed'] = True
                result['message'] = f'File {full_path} was created successfully'
            else:
                result['skipped'] = True
                result['message'] = f'File {full_path} already exists and is different from being created'
    except PermissionError:
        result['failed'] = True
        module.fail_json(msg = f'Insufficient permission to write file {full_path}', **result)
    except Exception as e:
        result['failed'] = True
        module.fail_json(msg = f'An exception occurred while writing the file {full_path}: {e}', **result)
    finally:
        if 'txt_file' in locals() and not txt_file.closed:
            txt_file.close()

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
