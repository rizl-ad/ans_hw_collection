Lighthouse
=========

This role downloads the Vector installation package, installs it, and creates a configuration file.

Role Variables
--------------

| variable | default value | description |
| -------- | ------------- | ----------- |
| `vector_version` | 0.50.0-1 | Vector installation package version. Overridable variable |


Example Playbook
----------------

```yaml
- name: 'Play name'   
  hosts: servers   
  roles:   
    - vector
```

License
-------

MIT

Author Information
------------------

Yaroslav Lysenko
