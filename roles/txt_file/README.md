Txt_file
========

This role creates a text file with the specified name, path, and content using the txt_file module.

Role Variables
--------------

| variable | default value | description |
| -------- | ------------- | ----------- |
| `txt_file_name` | test_txt_file | Name of the file being created without specifying the extension |
| `txt_file_path` | /tmp | The directory in which the file being created is created |
| `txt_file_contenet` | '' | Contents of the created file |
| `txt_file_overwrite` | false | File overwrite flag |

Example Playbook
----------------

```yaml
- name: 'Play name'   
  hosts: servers   
  roles:   
    - txt_file
```

License
-------

MIT

Author Information
------------------

Yaroslav Lysenko