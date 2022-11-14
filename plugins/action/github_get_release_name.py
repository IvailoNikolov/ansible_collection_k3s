from ansible.plugins.action import ActionBase
import copy
from ansible.errors import (
    AnsibleError,
    AnsibleFileNotFound,
    AnsibleAction,
    AnsibleActionFail,
)

import requests
import yaml

class ActionModule(ActionBase):

    def validate_github_package(packages_info):
    # retrieve package information
    owner = packages_info.get('owner')
    repo = packages_info.get('repo')
    release_name = packages_info.get('release_name')

    r_release_name = requests.get(f'https://api.github.com/repos/{owner}/{repo}/releases/tags/{release_name}')

    if r_release_name.status_code != 200:
        r_last_release_name = requests.get(f'https://api.github.com/repos/{owner}/{repo}/releases/latest')
        r_last_release_name_yaml = yaml.safe_load(r_last_release_name.content)

        release_name = r_last_release_name_yaml.get('tag_name')

    return release_name
    
    def run(self, tmp=None, task_vars=None):
        """handler for k8s options"""
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)


        new_module_args = self._task.args

        # helm install 
        module_return = self.validate_github_package(
            packages_info=new_module_args,
        )

        result.update(
            self.validate_github_package(
            packages_info=new_module_args,
            )
        )

        return result