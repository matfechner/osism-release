#!/usr/bin/env bash
set -x

build=$(date +%Y%m%d)

src/prepare-lst-files.sh
src/generate-yml-files.py

rm *.lst
rm -rf kolla-ansible-repository

pushd images/kolla

for f in $(ls -1 $build-*.yml); do
    git rm -f current-${f#$build-}
    ln -s $f current-${f#$build-}
    git add current-${f#$build-}
    git add $f
done
popd

git commit -a -m "Add versions for $build"
git push
