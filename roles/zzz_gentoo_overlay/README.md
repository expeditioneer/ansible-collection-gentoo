# gentoo_overlay

This role adds a custom overlay 



auto-sync = yes|no|true|false
    This setting determines if the repo will be synced during "emerge --sync" or "emaint sync --auto" runs.  This allows for repositories to be synced only
    when desired via "emaint sync --repo foo".
    If unset, the repo will be treated as set yes, true.

location will be /var/db/repos/{{ repository_name }}
    Specifies location of given repository.

sync-type
   Specifies type of synchronization performed by `emerge --sync`.
   Valid non-empty values: cvs, git, mercurial, rsync, svn, webrsync (emerge-webrsync)
   This attribute can be set to empty value to disable synchronization of given repository. Empty value is default.

sync-uri
   Specifies URI of repository used for synchronization performed by `emerge --sync`.
   This attribute can be set to empty value to disable synchronization of given repository. Empty value is default.

   Syntax:
          cvs: [cvs://]:access_method:[username@]hostname[:port]:/path
          git: (git|git+ssh|http|https)://[username@]hostname[:port]/path
          rsync: (rsync|ssh)://[username@]hostname[:port]/(module|path)

   Examples:
          rsync://private-mirror.com/portage-module
          rsync://rsync-user@private-mirror.com:873/gentoo-portage
          ssh://ssh-user@192.168.0.1:22/var/db/repos/gentoo
          ssh://ssh-user@192.168.0.1:22/\${HOME}/portage-storage

   Note: For the ssh:// scheme, key-based authentication might be of interest.

priority
    Specifies priority of given repository.

Example usage with HomeAssistant Repository from @onkelbeh
```yaml
- name: add homeassistant overlay
  include_role:
    name: expeditioneer.gentoo.gentoo_overlay
  vars:
    repository_name: HomeAssistantRepository
    auto_sync: 'yes'
    sync_type: git
    sync_uri: 'https://git.edevau.net/onkelbeh/HomeAssistantRepository.git'
    priority: 10
```

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

## License

[GPL-3.0 License](../../LICENSE)

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
