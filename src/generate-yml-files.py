#!/usr/bin/env python

import collections
import datetime
import glob
import os

import jinja2
import json
import requests
import yaml

today = datetime.date.today()
BUILD = os.environ.get("BUILD", today.strftime("%Y%m%d"))

DOCKER_REGISTRY = os.environ.get('DOCKER_REGISTRY', 'hub.docker.com')
DOCKER_NAMESPACE = os.environ.get('DOCKER_NAMESPACE', 'betacloud')

TEMPLATE_PROJECT = "project.tmpl"
DESTINATION = "images/kolla"


def get_tags_of_image(image):
    response = requests.get("https://%s/v2/repositories/%s/%s/tags/" % (DOCKER_REGISTRY, DOCKER_NAMESPACE, image))

    result = []
    for tag in response.json().get('results', []):
        result.append(tag['name'])
    return result


def get_last_revision_of_project(project, tag):
    with open("tmp-%s.lst" % project, 'r') as fp:
        image = fp.readline().strip().replace("_", "-")

    if project == "openvswitch_db":
        image = "openvswitch-db-server"

    last_revision = 0
    for itag in get_tags_of_image(image):
         if str(itag).startswith(str(tag)) and "-" in str(itag) and not str(itag).endswith("latest"):
             revision = itag.split("-")[1]
             if revision > last_revision:
                 last_revision = revision

    return last_revision


with open("versions/current.yml", "rb") as fp:
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
revisions = {}
for lstfile in glob.iglob("tmp-*.lst"):
    project_name = (lstfile[:-4])[4:]
    if project_name in all_projects:
        revisions[project_name] = get_last_revision_of_project(project_name, all_projects[project_name])
        projects.append(project_name)

all_projects = collections.OrderedDict(sorted(all_projects.items()))

for lstfile in glob.iglob("tmp-*.lst"):
    with open(lstfile) as fp:
        images = fp.read().splitlines()

    project_name = (lstfile[:-4])[4:]
    if project_name in all_projects:
        result = template_project.render({
            "docker_namespace": DOCKER_NAMESPACE,
            "project_name": project_name,
            "project_version": all_projects[project_name],
            "project_images": images,
            "revisions": revisions,
            "build": BUILD
        })

        with open(os.path.join(DESTINATION, "%s-%s.yml" % (BUILD, project_name)), "a+") as fp:
            fp.write(result)
