#!/usr/bin/env python

import collections
import datetime
import glob
import os

import jinja2
import json
import requests
import semver
import yaml

today = datetime.date.today()
OSISM_VERSION = os.environ.get("OSISM_VERSION", today.strftime("%Y%m%d"))

DOCKER_NAMESPACE = os.environ.get('DOCKER_NAMESPACE', 'osism')

TEMPLATE_PROJECT = "kolla.tmpl"
DESTINATION = "images"

with open("versions/%s.yml" % OSISM_VERSION, "rb") as fp:
    versions = yaml.load(fp)

# http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
all_projects = versions["openstack_projects"].copy()
all_projects.update(versions["infrastructure_projects"])

for project in ["common", "chrony", "memcached", "keepalived", "openvswitch_db", "openvswitch_vswitchd", "telegraf"]:
    all_projects[project] = versions["kolla_version"]

loader = jinja2.FileSystemLoader("src/templates")
environment = jinja2.Environment(loader=loader)
template_project = environment.get_template(TEMPLATE_PROJECT)

projects = []
for lstfile in glob.iglob("tmp/tmp-*.lst"):
    project_name = (lstfile[:-4])[8:]
    if project_name in all_projects:
        projects.append(project_name)

all_projects = collections.OrderedDict(sorted(all_projects.items()))
for project in all_projects:
    version = semver.parse_version_info(str(all_projects[project]))
    all_projects[project] = "%s.%s" % (version.major, version.minor)

with open(os.path.join(DESTINATION, "kolla-%s.yml" % OSISM_VERSION), "w") as fp:
    fp.write("---\n")
    fp.write("osism_version: %s\n" % OSISM_VERSION)
    fp.write("docker_registry: index.docker.io\n\n")

for lstfile in glob.iglob("tmp/tmp-*.lst"):
    with open(lstfile) as fp:
        images = fp.read().splitlines()

    project_name = (lstfile[:-4])[8:]
    if project_name in all_projects:
        result = template_project.render({
            "docker_namespace": DOCKER_NAMESPACE,
            "project_name": project_name,
            "project_version": all_projects[project_name],
            "project_images": images,
            "osism_version": OSISM_VERSION
        })

        with open(os.path.join(DESTINATION, "kolla-%s.yml" % OSISM_VERSION), "a+") as fp:
            fp.write(result)
