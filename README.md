# Ansible Playground

This repo aims to provide all the necessary tooling to
quickly provision Docker containers that could be directly
used as Ansible targets for local testing
and pass them to Ansible via a dynamic inventory implementation

## Usage

First, add all the desired groups and container configurations
to [config/compose-recipe.yml](./config/compose-recipe.yml)
Then, render `docker-compose.yml` and the Docker inventory file:

```sh
make render
```

Now, you can bring up Compose service using `docker-compose` or `make`:

```sh
make compose-up
```

Once all the containers are up, you should detect them via dynamic inventory:

```sh
ansible-inventory --graph
```

Containers belonging to each group from the recipe file will be mapped:

```sh
$ ansible-inventory --graph
@all:
  |--@ungrouped:
  |--@deployer:
  |  |--ap-deployer-1
  |--@licensemanager:
  |  |--ap-licensemanager-1
```

Thus, they can be managed using Ansible(either ad-hoc or playbooks):

```sh
$ ansible -a "hostname" all
ap-licensemanager-1 | CHANGED | rc=0 >>
45a1a0263173
ap-deployer-1 | CHANGED | rc=0 >>
f35dd5ef2bb0
```

### Remote Playground Instance

Due to performance limitations of emulating amd64 on ARM,
testing amd64-only Ansible roles/playbooks is feasible
only on a remote host.
If you have an instance you'd like to configure the playground
on, set its IP address in `config/inventory_remote.yml`
Then, provision the playground:

```sh
ansible-playbook \
  -i config/inventory_remote.yml \
  playbooks/setup_remote.yml
```

Once done, you should have all the deps installed
and `ansible_playground/` dir present in target user's `$HOME`

### Ansible Target Docker image

To build the target image:

```sh
make build
```

To run the local target:

```sh
    make run-local
```

To connect to the local target over SSH:

```sh
    make ssh-local
```
