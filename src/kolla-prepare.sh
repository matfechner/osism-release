#!/bin/sh

IGNOREFILE=src/files/ignore.lst
VERSION_KOLLA_ANSIBLE=4.0.2

mkdir -p tmp

if [[ ! -e tmp/kolla-ansible-repository ]]; then
  git clone -b $VERSION_KOLLA_ANSIBLE http://github.com/openstack/kolla-ansible tmp/kolla-ansible-repository
fi

for role in $(ls -1 tmp/kolla-ansible-repository/ansible/roles); do
  if [[ -e tmp/kolla-ansible-repository/ansible/roles/$role/defaults/main.yml ]]; then
    grep _image: tmp/kolla-ansible-repository/ansible/roles/$role/defaults/main.yml | grep -v -f $IGNOREFILE | awk -F: '{ print $1 }' | sed -e "s/_image$//" > tmp/tmp-$role.lst
  fi
done

while read ignore; do
  echo $ignore > tmp/tmp-$ignore.lst
done < $IGNOREFILE
