#!/usr/bin/env bash
set -euo pipefail

readonly repo=$(mktemp -d)
readonly artefact=$(mktemp)

tag="${GITHUB_REF##*/}"
if [[ "$tag" == "master" ]]; then
  tag="2.0.31"  # xxx
fi

readonly release=$(curl -fs "${GITHUB_API_URL}/repos/${GITHUB_REPOSITORY}/releases/tags/$tag")
readonly artefact_url=$(echo "$release" | jq -r ".assets[0].browser_download_url")

curl -sfL -o "$artefact" "$artefact_url"

git clone \
	--depth 10 \
	--branch master \
	https://github.com/Kapeli/Dash-User-Contributions.git \
	"$repo"

cd "$repo"

readonly branch_name="aws-cli-$tag"

git checkout -b "$branch_name"
cd docsets/AWS_CLI

readonly tgz_name="AWS-CLI.tgz"

docset_json=$(mktemp)
cat docset.json | \
	jq \
		--arg tag "$tag" \
		--arg tgz "$tgz_name" \
		--indent 4 \
		'
			.version = $tag |
			.specific_versions =
				[{
					version: $tag,
					archive: ("versions/"+$tag+"/"+$tgz)
				}] +
				.specific_versions
		' \
	> "$docset_json"

mkdir -p "versions/$tag"

mv "$docset_json" docset.json
cp "$artefact" "$tgz_name"
cp "$artefact" "versions/$tag/$tgz_name"

git add -A
git commit -m "AWS-CLI.docset $tag"

git push \
	"https://${CI_USER_USERNAME}:${CI_USER_ACCESS_TOKEN}@github.com/roberth-k/Dash-User-Contributions.git" \
	"HEAD:$branch_name"
