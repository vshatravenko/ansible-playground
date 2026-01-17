#!/usr/bin/env bash

if [[ -z "${TARGET_USER}" ]]; then
    echo '$TARGET_USER must be defined!'
    exit 1
fi

target_home="/home/${TARGET_USER}"
default_key_path=${target_home}/.ssh/id_ed25519
auth_keys_path="${target_home}/.ssh/authorized_keys"

mkdir -p "$(dirname ${auth_keys_path})"

gen_default_ssh_key() {
    ssh-keygen -N '' -f "${default_key_path}"
    chmod 0600 "${default_key_path}"
}

if [[ -z "${SSH_PUB_KEY_B64}" ]]; then
    echo "No key passed in SSH_PUB_KEY_B64, generating a new one"
    gen_default_ssh_key
    ssh_pub_key="$(cat ${default_key_path}.pub)"
else
    echo "Using the configured SSH_PUB_KEY_B64"
    ssh_pub_key="$(echo ${SSH_PUB_KEY_B64} | base64 -d)"
fi

echo "${ssh_pub_key}" >>"${auth_keys_path}"

sshd_path=$(which sshd)

echo "Generating host keys"
ssh-keygen -A

echo "Started sshd"
$sshd_path -D
