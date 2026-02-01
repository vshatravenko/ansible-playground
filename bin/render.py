#!/usr/bin/env python3

from os import path

import jinja2
import yaml

DEFAULT_COMPOSE_RECIPE = "config/compose_recipe.yml"
TPL_DIR = "tpl"
COMPOSE_TPL = "docker-compose.yml.j2"
COMPOSE_OUT = "docker-compose.yml"
DOCKER_INV_TPL = "inventory_docker.yml"
DOCKER_INV_OUT = "config/inventory_docker.yml"
DEFAULT_PLATFORM = "linux/amd64"


def main():
    with open(DEFAULT_COMPOSE_RECIPE, "r") as f:
        recipe = yaml.safe_load(f)

    target = {"services": [], "volumes": []}

    containers = recipe["containers"]

    groups = {k: v for k, v in recipe["groups"].items() if v.get("enabled")}

    for name, config in groups.items():
        if not config["enabled"]:
            continue

        print(f"Parsing {name} group")
        container = containers.get(config["container"])
        if not container:
            raise ValueError(f"{config['container']} container config not found!")

        for i in range(config["count"]):
            svc_name = f"{name}-{i+1}"

            volumes = container["volumes"].copy()

            for i, vol in enumerate(volumes):
                if "$dynamic" in vol:
                    vol_name = f"{svc_name}_data"
                    elems = vol.split(":")
                    if len(elems) == 1:
                        volumes[i] = vol_name
                    else:
                        volumes[i] = f"{vol_name}:{elems[1]}"
                    target["volumes"].append(vol_name)
                    break

            target["services"].append(
                {
                    "name": svc_name,
                    "image": container["image"],
                    "ports": container["ports"],
                    "volumes": volumes,
                    "platform": container.get("platform", DEFAULT_PLATFORM),
                }
            )

    print("Rendering the Compose template")
    jloader = jinja2.FileSystemLoader(TPL_DIR)
    jenv = jinja2.Environment(loader=jloader)
    tpl = jenv.get_template(COMPOSE_TPL)
    res = tpl.render(services=target["services"], volumes=target["volumes"])

    print("Updating the Docker inventory")
    update_docker_inventory(list(groups.keys()))

    print(f"Writing the output to {COMPOSE_OUT}")
    with open(COMPOSE_OUT, "w") as f:
        f.write(res)


def update_docker_inventory(groups: list[str]):
    with open(path.join(TPL_DIR, DOCKER_INV_TPL), "r") as f:
        inventory = yaml.safe_load(f)

    if "groups" not in inventory:
        inventory["groups"] = {}

    for group in groups:
        inventory["groups"][group] = f'"{group}" in docker_name'

    with open(DOCKER_INV_OUT, "w") as f:
        f.write(yaml.safe_dump(inventory))


if __name__ == "__main__":
    main()
