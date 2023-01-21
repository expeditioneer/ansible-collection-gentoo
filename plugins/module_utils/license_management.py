# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import inspect
import os
import re
import tempfile
from typing import Dict, List
from ansible.module_utils.errors import ArgumentValueError  # type: ignore
from ansible.module_utils.basic import AnsibleModule  # type: ignore

try:
    import portage  # type: ignore
except ImportError:
    sys.exit(1)  # type: ignore

try:
    from ansible import constants as C  # type: ignore
except ImportError:
    from ansible_collections.expeditioneer.gentoo.plugins.module_utils import constants as C  # type: ignore

license_argument_spec: Dict = dict(
    argument_spec=dict(
        license=dict(type='str', required=True),
        package=dict(type='str', required=True),
        state=dict(default='present', choices=['absent', 'present']),
    ),
    supports_check_mode=True
)


class LicenseManagement:

    def __init__(self, module: AnsibleModule):
        self._module = module
        self._operation = self.get_operation_from_parameter_state(module.params['state'])

    def get_operation_from_parameter_state(self, parameter_state: str):
        if parameter_state == 'present':
            return self.add_license
        elif parameter_state == 'absent':
            return 'remove'
        else:
            raise ArgumentValueError(f"Invalid selection for parameter state with '{parameter_state}'")

    @staticmethod
    def get_header() -> str:
        return inspect.cleandoc(f'''
            #
            # {C.DEFAULT_MANAGED_STR}
            #
            '''.lstrip('\n').lstrip(' ').rstrip(' ')) + '\n'

    @staticmethod
    def _get_accepted_licenses(lines) -> List[Dict[str, str]]:
        accepted_licenses: List[Dict[str, str]] = list()
        for line in lines:
            if re.search("^[a-z]", line) is not None:
                atom, lic = line.strip().split()
                entry = dict(atom=atom, license=lic)
                if entry not in accepted_licenses:
                    accepted_licenses.append(entry)
        return accepted_licenses

    @staticmethod
    def create_new_license_file_content(accepted_licenses: List[str]) -> str:
        license_file_content: str = LicenseManagement.get_header()
        license_file_content += '\n'
        license_file_content += '\n'.join(accepted_licenses)
        license_file_content += '\n'
        return license_file_content

    @property
    def package_license_file(self) -> str:
        return os.path.join(portage.db._target_eroot, 'etc/portage/package.license')

    def read_license_file(self) -> List[str]:  # type: ignore
        try:
            with open(self.package_license_file, 'r') as read_file:
                return read_file.readlines()
        except IOError as e:
            self._module.fail_json(msg=f'Failed to open {self.package_license_file}: {e}')

    def license_file_exists(self) -> bool:
        return os.path.isfile(self.package_license_file)

    def get_licenses_from_file(self) -> List[Dict[str, str]]:
        accepted_licenses: List[Dict[str, str]] = list()
        if self.license_file_exists():
            try:
                lines = self.read_license_file()
                accepted_licenses = self._get_accepted_licenses(lines)
            except IOError as e:
                self._module.fail_json(msg=f'Failed to open {self.package_license_file}: {e}')
        return accepted_licenses

    def write_licensefile(self, new_license_file_content: str):
        try:
            _, tmp_path = tempfile.mkstemp(suffix='.conf', prefix='.ansible_m_license_', dir=os.path.dirname(self.package_license_file))
            with open(tmp_path, "w") as f:
                f.write(new_license_file_content)
        except PermissionError as e:
            self._module.fail_json(msg=f'Missing permission to write to file: {e}')
        except IOError as e:
            self._module.fail_json(msg=f'Failed to write to file {tmp_path}: {e}')
        self._module.atomic_move(tmp_path, self.package_license_file)

    # TODO: add new license
    # a) per license base
    # b) per package
    # c) complete match --> switch SIMPLIFY to remove individual from license affected packages(?)
    # TODO: remove license
    # a) per license base
    # b) per package
    # c) complete match
    # TODO: check for wildcard and or group/wildcard
    def add_license(self):
        changed: bool = False

        accepted_licenses: List[Dict[str, str]] = self.get_licenses_from_file()
        atom: str = self._module.params['package']
        lic: str = self._module.params['license']
        
        provided_license = dict(atom=atom, license=lic)
        if provided_license not in accepted_licenses:
            accepted_licenses.append(provided_license)
            changed = True

        sorted_accepted_licenses = sorted(accepted_licenses, key=lambda i: i['atom'])
        atom_space_to_license: int = max(len(entry['atom']) for entry in sorted_accepted_licenses)

        new_accepted_licenses: List[str] = list()
        for entry in sorted_accepted_licenses:
            new_accepted_licenses.append(f"{entry['atom']:{atom_space_to_license}} {entry['license']}")

        new_license_file_content: str = self.create_new_license_file_content(new_accepted_licenses)

        if not self._module.check_mode:
            self.write_licensefile(new_license_file_content)

        self._module.exit_json(changed=changed, msg=f'{self.package_license_file} updated.')

    def run(self):
        self._operation()
