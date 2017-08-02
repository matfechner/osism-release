#!/usr/bin/env bash
set -x

build=$(date +%Y%m%d)

##########################
# kolla

src/kolla-prepare.sh
src/kolla-generate.py

sed -e 's/-{{ osism_version }}//' images/kolla-$build.yml > images/kolla-current.yml
sed -e 's/\(.*_tag:\).*/\1 latest/' -e '/.*_version:.*/d' images/kolla-$build.yml > images/kolla-latest.yml

git add images/kolla-current.yml
git add images/kolla-latest.yml
git add images/kolla-$build.yml

rm -rf tmp

##########################
# ceph

src/ceph-generate.py

git rm -f images/ceph-current.yml
ln -s ceph-$build.yml images/ceph-current.yml
git add images/ceph-current.yml
git add images/ceph-$build.yml

##########################
# git

git commit -a -m "Add version files for $build"
git push
