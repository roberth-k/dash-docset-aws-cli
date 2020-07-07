#!/usr/bin/env bash
set -euo pipefail

readonly inpath="$1"
readonly progdir=$(dirname $0)
readonly projdir=$(readlink -f "$progdir/..")
readonly docset_name="AWS-CLI-v2"
readonly builddir=$(readlink -f "$projdir/.build")
readonly docsetdir="$builddir/$docset_name.docset"
readonly dbpath="$docsetdir/Contents/Resources/docSet.dsidx"
readonly sqlpath="$(mktemp).sql"
readonly docpath="$inpath/doc/build/html"

[[ ! -d "$docpath" ]] && 1>&2 echo "AWS CLI v2 HTML documentation not built" && exit 1

cd "$projdir"

[[ -d "$docsetdir" ]] && rm -r "$docsetdir"

mkdir -p "$docsetdir/Contents/Resources"

cp "static/Info.plist" "$docsetdir/Contents/"
cp "static/icon.png"   "$docsetdir/"

cp -r "$docpath" "$docsetdir/Contents/Resources/Documents"

./scripts/index.py "$docpath" "$dbpath"

./scripts/postprocess.py "$docsetdir/Contents/Resources/Documents"
