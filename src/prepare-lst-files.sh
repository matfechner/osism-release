#!/bin/sh

IGNOREFILE=src/files/ignore.lst
VERSION_KOLLA_ANSIBLE=4.0.2

if [[ ! -e kolla-ansible-repository ]]; then
  git clone -b $VERSION_KOLLA_ANSIBLE http://github.com/openstack/kolla-ansible kolla-ansible-repository
fi

for role in $(ls -1 kolla-ansible-repository/ansible/roles); do
  if [[ -e kolla-ansible-repository/ansible/roles/$role/defaults/main.yml ]]; then
    grep _image: kolla-ansible-repository/ansible/roles/$role/defaults/main.yml | grep -v -f $IGNOREFILE | awk -F: '{ print $1 }' | sed -e "s/_image$//" > tmp-$role.lst
  fi
done

while read ignore; do
  echo $ignore > tmp-$ignore.lst
done < $IGNOREFILE
