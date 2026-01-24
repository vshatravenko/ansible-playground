#!/usr/bin/env python3

import os

import jinja2
import yaml

DEFAULT_COMPOSE_RECIPE = "config/compose_recipe.yml"
JINJA_TPL_DIR = "tpl"
COMPOSE_TPL = "docker-compose.yml.j2"
COMPOSE_OUT = "output/docker-compose.yml"


if __name__ == "__main__":
    with open(DEFAULT_COMPOSE_RECIPE, "r") as f:
        recipe = yaml.safe_load(f)

    target = {"services": [], "volumes": []}

    containers = recipe["containers"]

    for name, config in recipe["groups"].items():
        print(f"Parsing {name} group")
        container = containers.get(config["container"])
        if not container:
            raise ValueError(f"{config['container']} container config not found!")

        for i in range(config["count"]):
            svc_name = f"{name}_{i+1}"

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
                }
            )

    print("Rendering the template")
    jloader = jinja2.FileSystemLoader(JINJA_TPL_DIR)
    jenv = jinja2.Environment(loader=jloader)
    tpl = jenv.get_template(COMPOSE_TPL)
    res = tpl.render(services=target["services"], volumes=target["volumes"])

    print(f"Writing the output to {COMPOSE_OUT}")
    with open(COMPOSE_OUT, "w") as f:
        f.write(res)
