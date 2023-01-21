# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

class PortageSetCanNotBeRemovedError(Exception):
    """Portage system sets can not be removed"""

    def __init__(self, atom: str):
        self.error_message = f'Portage system set {atom} can not be removed'

    @property
    def msg(self):
        return self.args[0]
