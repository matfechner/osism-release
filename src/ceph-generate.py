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
OSISM_VERSION = os.environ.get("OSISM_VERSION", today.strftime("%Y%m%d"))

DOCKER_REGISTRY = os.environ.get('DOCKER_REGISTRY', 'hub.docker.com')
DOCKER_NAMESPACE = os.environ.get('DOCKER_NAMESPACE', 'osism')

TEMPLATE_PROJECT = "ceph.tmpl"
DESTINATION = "images"


with open("versions/latest.yml", "rb") as fp:
    versions = yaml.load(fp)

loader = jinja2.FileSystemLoader("src/templates")
environment = jinja2.Environment(loader=loader)
template_project = environment.get_template(TEMPLATE_PROJECT)

result = template_project.render({
    "version": versions["ceph_version"],
    "revision": OSISM_VERSION
})

with open(os.path.join(DESTINATION, "ceph-%s.yml" % OSISM_VERSION), "w+") as fp:
    fp.write(result)
