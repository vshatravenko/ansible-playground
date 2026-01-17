# Ansible Playground

This repo aims to provide all the necessary tooling to
quickly provision Docker containers that could be directly
used as Ansible targets for local testing
and pass them to Ansible via a dynamic inventory implementation

## Usage

To run a single local target, run:

```sh
    make run-local
```

To connect to the local target, run:

```sh
    make ssh-local
```

Instructions on provisioning multiple hosts and
passing them to Ansible TBD.
