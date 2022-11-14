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

        return {"release_name": release_name}

class ActionModule(ActionBase):

    def _ensure_invocation(self, result):
        # NOTE: adding invocation arguments here needs to be kept in sync with
        # any no_log specified in the argument_spec in the module.
        if "invocation" not in result:
            if self._play_context.no_log:
                result["invocation"] = "CENSORED: no_log is set"
            else:
                result["invocation"] = self._task.args.copy()
                result["invocation"]["module_args"] = self._task.args.copy()

        return result
    
    def run(self, tmp=None, task_vars=None):
        """handler for k8s options"""
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)



        action_return = validate_github_package(
            packages_info=self._task.args,
        )

        result.update(
            action_return
        )

        return self._ensure_invocation(result)