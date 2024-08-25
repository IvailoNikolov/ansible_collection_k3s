# Ansible Collection - frantchenco.k3s

Documentation for the collection.

### Modules


Name | Description
--- | ---
frantchenco.k3s.github_get_release_name|Get github release name

## Installation and Usage

### Installing the Collection from Ansible Galaxy

create a file name "requirements.yml"
```yaml
---
collections:
    - name: community.general
    version: 5.7.0
    - name: ansible.posix
    - name: git+https://github.com/IvailoNIkolov/ansible_collection_k3s.git,master
```

Before using the Kubernetes collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy install -r ./requirements.yml

### Ansible configuration:

```bash
[defaults]
host_key_checking = False
deprecation_warnings=False
interpreter_python = /usr/bin/python
roles_path = ./roles
inventory  = ./inventory/hosts.yaml
```

### Inventory example:

Please find below the configuration files example for an K3s HA cluster constitues of :
* 3 masters
* 3 agents k3s cluster
* 1 Virtual IP

#### inventory/hosts.yaml
```yaml
---
---
all:
    children:
        k3s_cluster:
            children:
                master:
                    hosts:
                        192.168.0.1: {}
                        192.168.0.2: {}
                        192.168.0.3: {}
                agent:
                    hosts:
                        192.168.0.4: {}
                        192.168.0.5: {}
                        192.168.0.6: {}

```

#### inventory/groups_vars/all.yaml
```yaml
---
ansible_user: root
systemd_dir: "/etc/systemd/system"
master_ip: 192.168.0.1
extra_server_args: ""
extra_agent_args: ""

k3s_token: ChangeThisImportantToken

k3s_github_release_name: latest

keepalived_shared_iface: "eth0"
k3s_flannel_iface: "eth0"
```

#### inventory/groups_vars/master/haproxy.yaml
```yaml
---
haproxy_backend_servers:
  - name: 192.168.0.1
    address: 192.168.0.1
  - name: 192.168.0.2
    address: 192.168.0.2
  - name: 192.168.0.3
    address: 192.168.0.3
```

#### inventory/groups_vars/master/keepalived.yaml
```yaml
---
keepalived_shared_ip: 192.168.0.7
```

#### inventory/host_vars/<master ip example 192.168.0.1>/keepalived.yaml
```yaml
---
keepalived_role: MASTER for "192.168.0.1" else BACKUP
keepalived_priority: VM index
keepalived_router_id: "52"
vnic_id: 11

```

### Playbook example

Inventory example:


```yaml
---

- hosts: k3s_cluster
  gather_facts: yes
  become: yes
  roles:
    - role: frantchenco.k3s.download
    - role: frantchenco.k3s.prereq

- hosts: master
  become: yes
  roles:
    - role: frantchenco.k3s.haproxy
    - role: frantchenco.k3s.keepalived

- hosts: master[0]
  become: no
  strategy: debug
  roles:
    - role: frantchenco.k3s.delete_node_set_variables

- hosts: master
  serial: 1
  become: yes
  roles:
    - role: frantchenco.k3s.master
    - role: frantchenco.k3s.delete_node_systemd_master

- hosts: agent
  serial: "30%"
  become: yes
  roles:
    - role: frantchenco.k3s.node
    - role: frantchenco.k3s.delete_node_systemd_agent
```