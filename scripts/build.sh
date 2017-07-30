#!/usr/bin/env bash
set -x

build=$(date +%Y%m%d)

##########################
# kolla

src/kolla-prepare.sh
src/kolla-generate.py

sed -e 's/\(.*_revision: \).*/\1 latest/g' images/kolla-$build.yml > images/kolla-latest.yml

git rm -f images/kolla-current.yml
ln -s kolla-$build.yml images/kolla-current.yml
git add images/kolla-current.yml
git add images/kolla-latest.yml
git add images/kolla-$build.yml

rm -rf tmp

##########################
# ceph

src/ceph-generate.py

sed -e 's/\(.*_revision: \).*/\1 latest/g' images/ceph-$build.yml > images/ceph-latest.yml

git rm -f images/ceph-current.yml
ln -s ceph-$build.yml images/ceph-current.yml
git add images/ceph-current.yml
git add images/ceph-latest.yml
git add images/ceph-$build.yml

##########################
# git

git commit -a -m "Add version files for $build"
git push
