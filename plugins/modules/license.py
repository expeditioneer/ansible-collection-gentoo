# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = f'''
---
module: license
short_description: Manages accepted licenses
description:
  - Manages Gentoo accepted licenses
version_added: '1.0.0'

options:
  license:
    description:
      - The license name which should be accepted
    required: true
    
  package:
    description:
      - The package for which the provided license should be accepted
    required: true 
      
  state:
    description:
      - State of the license
    required: false
    default: "present"
    choices: [ "present", "absent" ]
'''

EXAMPLES = '''
'''

from ansible.module_utils.basic import AnsibleModule  # type: ignore
from ansible_collections.expeditioneer.gentoo.plugins.module_utils.license_management import license_argument_spec, LicenseManagement  # type: ignore


def main():

    module: AnsibleModule = AnsibleModule(**license_argument_spec)
    license_management = LicenseManagement(module)

    #    try:
    license_management.run()
#    except:
#        TBD


if __name__ == '__main__':
    main()
