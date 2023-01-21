# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import re
import traceback
from typing import List
from ansible.module_utils.basic import AnsibleModule, missing_required_lib  # type: ignore
from ansible_collections.expeditioneer.gentoo.plugins.module_utils.reposync import RepoSync  # type: ignore
from ansible_collections.expeditioneer.gentoo.plugins.module_utils.errors import PortageSetCanNotBeRemovedError  # type: ignore

PORTAGE_IMPORT_ERROR: str = ''
try:
    import portage  # type: ignore
    PORTAGE_FOUND: bool = True
except ImportError:
    PORTAGE_IMPORT_ERROR = traceback.format_exc()
    PORTAGE_FOUND: bool = False  # type: ignore

portage_present_states = ['present', 'emerged', 'installed']
portage_absent_states = ['absent', 'unmerged', 'removed']

mutually_exclusive = [['usepkg', 'usepkgonly']]

portage_argument_spec = dict(
    argument_spec=dict(
        package=dict(type='list', required=True),
        state=dict(
            default=portage_present_states[0],
            choices=portage_present_states + portage_absent_states,
        ),
        update=dict(default=False, type='bool'),
        deep=dict(default=False, type='bool'),
        newuse=dict(default=False, type='bool'),
        changed_use=dict(default=False, type='bool'),
        oneshot=dict(default=False, type='bool'),
        noreplace=dict(default=False, type='bool'),
        nodeps=dict(default=False, type='bool'),
        onlydeps=dict(default=False, type='bool'),
        depclean=dict(default=False, type='bool'),
        sync=dict(default=False, type='bool'),
        getbinpkg=dict(default=False, type='bool'),
        usepkgonly=dict(default=False, type='bool'),
        usepkg=dict(default=False, type='bool'),
        keepgoing=dict(default=False, type='bool'),
        jobs=dict(default=None, type='int'),
        loadavg=dict(default=None, type='float'),
    ),
    required_one_of=[['package', 'sync', 'depclean']],
    mutually_exclusive=mutually_exclusive,
    supports_check_mode=True
)

system_sets = [
    '@live-rebuild',
    '@module-rebuild',
    '@preserved-rebuild',
    '@security',
    '@selected',
    '@system',
    '@world',
    '@x11-module-rebuild'
]


class PortagePackageManagement:

    def __init__(self, module: AnsibleModule):
        if not PORTAGE_FOUND:
            module.fail_json(msg=missing_required_lib('portage'), exception=PORTAGE_IMPORT_ERROR)

        self._module = module
        self._params = module.params
        self._emerge = module.get_bin_path('emerge', required=True)

    @staticmethod
    def query_atom(atom: str) -> bool:
        installed: List = portage.vartree().dbapi.match(atom)
        return bool(installed)

    @staticmethod
    def query_set(package_set: str, action: str) -> bool:
        if package_set in system_sets:
            if action == 'unmerge':
                raise PortageSetCanNotBeRemovedError(package_set)

        world_sets_path = os.path.join(portage.root, portage.const.WORLD_SETS_FILE)
        with open(world_sets_path) as world_sets:
            for world_set in world_sets:
                if package_set in world_set:
                    return True

        return False

    @staticmethod
    def query_package(package, action) -> bool:
        if package.startswith('@'):
            return PortagePackageManagement.query_set(package, action)
        return PortagePackageManagement.query_atom(package)

    def sync_repositories(self):
        if self._module.check_mode:
            self._module.exit_json(msg='check mode not supported by sync')
        return RepoSync.sync_all_repos()

    # Note: In the 3 functions below, equery is done one-by-one, but emerge is done in one go.
    # If that is not desirable, split the packages into multiple tasks instead of joining them together with comma.
    def emerge_packages(self, packages):
        p = self._params

        if not (p['update'] or p['noreplace'] or p['changed_use'] or p['newuse']):
            for package in packages:
                if not PortagePackageManagement.query_package(package, 'emerge'):
                    break
            else:
                self._module.exit_json(changed=False, msg='Packages already present.')
            if self._module.check_mode:
                self._module.exit_json(changed=True, msg='Packages would be installed.')

        args = []
        emerge_flags = {
            'update': '--update',
            'deep': '--deep',
            'newuse': '--newuse',
            'changed_use': '--changed-use',
            'oneshot': '--oneshot',
            'noreplace': '--noreplace',
            'nodeps': '--nodeps',
            'onlydeps': '--onlydeps',
            'getbinpkg': '--getbinpkg',
            'usepkgonly': '--usepkgonly',
            'usepkg': '--usepkg',
            'keepgoing': '--keep-going',
        }

        for flag, arg in emerge_flags.items():
            if p[flag]:
                args.append(arg)

        emerge_flags = {
            'jobs': '--jobs=',
            'loadavg': '--load-average ',
        }

        for flag, arg in emerge_flags.items():
            if p[flag] is not None:
                args.append(arg + str(p[flag]))

        cmd, (rc, out, err) = self.run_emerge(packages, *args)
        if rc != 0:
            self._module.fail_json(
                cmd=cmd, rc=rc, stdout=out, stderr=err,
                msg='Packages not installed.',
            )

        # Check for SSH error with PORTAGE_BINHOST, since rc is still 0 despite this error
        if (p['usepkgonly'] or p['getbinpkg']) and 'Permission denied (publickey).' in err:
            self._module.fail_json(
                cmd=cmd, rc=rc, stdout=out, stderr=err,
                msg='Please check your PORTAGE_BINHOST configuration in make.conf '
                    'and your SSH authorized_keys file',
            )

        changed = True
        for line in out.splitlines():
            if re.match(r'(?:>+) Emerging (?:binary )?\(1 of', line):
                msg = 'Packages installed.'
                break
            elif self._module.check_mode and re.match(r'\[(binary|ebuild)', line):
                msg = 'Packages would be installed.'
                break
        else:
            changed = False
            msg = 'No packages installed.'

        self._module.exit_json(
            changed=changed,
            cmd=cmd,
            rc=rc,
            stdout=out,
            stderr=err,
            msg=msg,
        )

    def unmerge_packages(self, packages):
        p = self._module.params

        for package in packages:
            if PortagePackageManagement.query_package(package, 'unmerge'):
                break
        else:
            self._module.exit_json(changed=False, msg='Packages already absent.')

        args = ['--unmerge']

        cmd, (rc, out, err) = self.run_emerge(packages, *args)

        if rc != 0:
            self._module.fail_json(
                cmd=cmd,
                rc=rc,
                stdout=out,
                stderr=err,
                msg='Packages not removed.',
            )

        self._module.exit_json(
            changed=True,
            cmd=cmd,
            rc=rc,
            stdout=out,
            stderr=err,
            msg='Packages removed.'
        )

    def cleanup_packages(self, packages):
        if packages:
            for package in packages:
                if PortagePackageManagement.query_package(package, 'unmerge'):
                    break
            else:
                self._module.exit_json(changed=False, msg='Packages already unmerged.')

        args = ['--depclean']

        cmd, (rc, out, err) = self.run_emerge(self, packages, *args)
        if rc != 0:
            self._module.fail_json(cmd=cmd, rc=rc, stdout=out, stderr=err)

        removed = 0
        for line in out.splitlines():
            if not line.startswith('Number removed:'):
                continue
            parts = line.split(':')
            removed = int(parts[1].strip())
        changed = removed > 0

        self._module.exit_json(
            changed=changed,
            cmd=cmd,
            rc=rc,
            stdout=out,
            stderr=err,
            msg='depclean completed.'
        )

    def run_emerge(self, packages, *args):
        args = list(args)

        args.append('--ask=n')
        if self._module.check_mode:
            args.append('--pretend')

        cmd = [self._emerge] + args + packages
        return cmd, self._module.run_command(cmd)

    def run(self):

        p = self._module.params

        if p['sync']:
            self.sync_repositories()
            # TODO: below sync and depclean are currently mutually exclusive
            if not p['package']:
                self._module.exit_json(msg='Sync successfully finished.')

        packages: List = list()
        if p['package']:
            packages.extend(p['package'])

        if p['depclean']:
            if packages and p['state'] not in portage_absent_states:
                self._module.fail_json(
                    msg=f'Depclean can only be used with package when the state is one of: {portage_absent_states}'
                )
            self.cleanup_packages(packages)

        elif p['state'] in portage_present_states:
            self.emerge_packages(packages)

        elif p['state'] in portage_absent_states:
            self.unmerge_packages(packages)
