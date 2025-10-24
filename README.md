Ansible Collection - rizl_ad.my_collection
------------------------------------------

This collection contains the txt_file role and module, designed to create a text file with a specified name, path, and contents.
See the role description in the role meta directory.


Module arguments
----------------

The txt_file module contains the following arguments:

| argument | type | default value | description |
| -------- | ---- | ------------- | ----------- |
| `name` | str | No default value | Required argument. Name of the file being created without specifying the extension |
| `path` | str | No default value | Required argument. The directory in which the file being created is created |
| `contenet` | str | '' | Optional argument. Contents of the created file |
| `overwrite` | bool | False | Optional argument. File overwrite flag |

> [!NOTE]
> If the 'overwrite' argument is true and a file with the specified path and name exists, and the existing file's hash equals the hash of the file being created, the file will not be overwritten.
> If the 'overwrite' argument is false and a file with the specified path and name exists, and the existing file's hash does not equal the hash of the file being created, the file creation will be skipped.


Usage example
-------------

```yaml
- name: Create text file
  txt_file:
    name: file_name
    path: /tmp
    content: 'file content'
    overwrite: true
```


License
-------

MIT


Author Information
------------------

Yaroslav Lysenko
