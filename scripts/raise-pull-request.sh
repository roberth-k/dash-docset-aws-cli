#!/usr/bin/env bash
set -euo pipefail

readonly tag="${GITHUB_REF##*/}"

curl \
    --show-error --fail -i \
    "${GITHUB_API_URL}/repos/Kapeli/Dash-User-Contributions/pulls" \
    -XPOST \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Authorization: token ${CI_USER_ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "
        {
            \"title\": \"aws-cli $tag\",
            \"head\": \"roberth-k:aws-cli-$tag\",
            \"base\": \"master\",
            \"body\": \"This is an automatic PR. Please report issues to https://github.com/roberth-k/dash-docset-aws-cli.\"
        }
    "
