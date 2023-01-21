# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys

try:
    from portage.emaint.modules.sync.sync import SyncRepos  # type: ignore
except ImportError:
    sys.exit(1)


class RepoSync:

    @staticmethod
    def sync_auto_sync_enabled_repos():
        """Sync auto-sync enabled repos"""
        return SyncRepos().auto_sync()

    @staticmethod
    def sync_all_repos():
        """Sync all repos defined in repos.conf"""
        return SyncRepos().all_repos()

    @staticmethod
    def sync_only_specified_repo():
        """Sync the specified repo"""
        SyncRepos().repo()
