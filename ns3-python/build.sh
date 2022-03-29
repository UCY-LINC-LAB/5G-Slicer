#!/bin/sh -e

section() {
	echo "##[section]$@"
}

set_env() {
	echo "$1=$2"
	echo "$1=$2" >> $GITHUB_ENV
}

command() {
	echo "##[command]$@"
	"$@"
}

workdir() {
	if [ ! -d "$1" ]; then
		command mkdir -p "$1"
	fi
	command cd "$1"
}

run() {
	echo "##[group]$@"
	local code=0
	("$@") || code=$?
	echo "##[endgroup]"
	return $code
}

runsh() {
	echo "##[group]$1"
	local code=0
	(sh -c "$1") || code=$?
	echo "##[endgroup]"
	return $code
}

asset_index=0
asset() {
	set_env "ASSET_PATH_$asset_index" "$1"
	set_env "ASSET_NAME_$asset_index" "${2-"${1##*/}"}"
	asset_index=$((asset_index + 1))
}

. ns-3/build.sh