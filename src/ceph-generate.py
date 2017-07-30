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
DOCKER_NAMESPACE = os.environ.get('DOCKER_NAMESPACE', 'osism')

TEMPLATE_PROJECT = "ceph.tmpl"
DESTINATION = "images"


def get_tags_of_image(image):
    response = requests.get("https://%s/v2/repositories/%s/%s/tags/" % (DOCKER_REGISTRY, DOCKER_NAMESPACE, image))

    result = []
    for tag in response.json().get('results', []):
        result.append(tag['name'])
    return result


def get_last_revision_of_image(image, tag):
    last_revision = 0
    for itag in get_tags_of_image(image):
         if str(itag).startswith(str(tag)) and "-" in str(itag) and not str(itag).endswith("latest"):
             revision = itag.split("-")[1]
             if revision > last_revision:
                 last_revision = revision

    return last_revision


with open("versions/current.yml", "rb") as fp:
    versions = yaml.load(fp)

loader = jinja2.FileSystemLoader("src/templates")
environment = jinja2.Environment(loader=loader)
template_project = environment.get_template(TEMPLATE_PROJECT)

result = template_project.render({
    "version": versions["ceph_version"],
    "revision": get_last_revision_of_image("ceph-daemon", versions["ceph_version"])
})

with open(os.path.join(DESTINATION, "ceph-%s.yml" % BUILD), "w+") as fp:
    fp.write(result)
