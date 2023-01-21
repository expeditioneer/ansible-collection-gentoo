# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: package
short_description: Manages packages for a Gentoo system
description:
  - Manages Gentoo packages
version_added: '1.0.0'

options:
  package:
    description:
      - Package atom or set, e.g. C(sys-apps/foo) or C(>foo-2.13) or C(@world)

  state:
    description:
      - State of the package atom
    required: false
    default: "present"
    choices: [ "present", "installed", "emerged", "absent", "removed", "unmerged" ]

  update:
    description:
      - Update packages to the best version available (--update)
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  deep:
    description:
      - Consider the entire dependency tree of packages (--deep)
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  newuse:
    description:
      - Include installed packages where USE flags have changed (--newuse)
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  changed_use:
    description:
      - Include installed packages where USE flags have changed, except when
      - flags that the user has not enabled are added or removed
      - (--changed-use)
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  oneshot:
    description:
      - Do not add the packages to the world file (--oneshot)
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  noreplace:
    description:
      - Do not re-emerge installed packages (--noreplace)
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  nodeps:
    description:
      - Only merge packages but not their dependencies (--nodeps)
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  onlydeps:
    description:
      - Only merge packages' dependencies but not the packages (--onlydeps)
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  depclean:
    description:
      - Remove packages not needed by explicitly merged packages (--depclean)
      - If no package is specified, clean up the world's dependencies
      - Otherwise, --depclean serves as a dependency aware version of --unmerge
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  sync:
    description:
      - Sync package repositories first
      - If yes, perform "emaint sync -all"
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  getbinpkg:
    description:
      - Prefer packages specified at PORTAGE_BINHOST in make.conf
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  usepkg:
    description
      - Use binary packages (from $PKGDIR) if they are available
    required: false
    default: "no"
    choices: [ "true", "false" ]

  usepkgonly:
    description:
      - Merge only binaries (no compiling). This sets getbinpkg=yes.
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  keepgoing:
    description:
      - Continue as much as possible after an error.
    required: false
    default: "no"
    choices: [ "yes", "no" ]

  jobs:
    description:
      - Specifies the number of packages to build simultaneously.
    required: false
    default: None
    type: int

  loadavg:
    description:
      - Specifies that no new builds should be started if there are other builds running and the load average is at 
        least LOAD
    required: false
    default: None
    type: float

author:
    - "William L Thomson Jr (@wltjr)"
    - "Yap Sok Ann (@sayap)"
    - "Andrew Udvare"
notes:  []
requirements: [ portage ]
'''

EXAMPLES = '''
# Make sure package foo is installed
- expeditioneer.gentoo.portage:
    package: foo
    state: present

# Make sure package foo is not installed
- expeditioneer.gentoo.portage:
    package: foo
    state: absent

# Update package foo to the "best" version
- expeditioneer.gentoo.portage:
    package: foo
    update: yes

# Install package foo using PORTAGE_BINHOST setup
- expeditioneer.gentoo.portage:
    package: foo
    getbinpkg: yes

# Re-install world from binary packages only and do not allow any compiling
- expeditioneer.gentoo.portage:
    package: @world
    usepkgonly: yes

# Sync repositories and update world
- expeditioneer.gentoo.portage:
    package: @world
    update: yes
    deep: yes
    sync: yes

# Remove unneeded packages
- expeditioneer.gentoo.portage:
    depclean: yes

# Remove package foo if it is not explicitly needed
- expeditioneer.gentoo.portage:
    package: foo
    state: absent
    depclean: yes
'''

from ansible.module_utils.basic import AnsibleModule  # type: ignore
from ansible_collections.expeditioneer.gentoo.plugins.module_utils.portage_package_management import PortagePackageManagement, portage_argument_spec  # type: ignore


def main():

    module: AnsibleModule = AnsibleModule(
        **portage_argument_spec
    )

    portage_package_management = PortagePackageManagement(module)

#    try:
    portage_package_management.run()
#    except:
#        TBD


if __name__ == '__main__':
    main()
