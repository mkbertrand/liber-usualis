#!/bin/bash

set -eu -o pipefail

year_start=1900
year_end=2200
ref_dir="kalendar/testdata"

prompt="Overwrite old reference file? [ynadsq]: "
action_help="y: yes; n: no; a: yes to all; d: no to all; s: skip (accept); q: quit"
opts="s:e:d:h"
usage() {
	echo >&2 "Usage: $0 [-s <start>] [-e <end>] [-d <ref dir>] [action]"
	echo >&2 "Actions: $action_help"
	exit 1
}
while getopts "$opts" opt; do
	case "$opt" in
		s) year_start="$OPTARG" ;;
		e) year_end="$OPTARG" ;;
		d) ref_dir="$OPTARG" ;;
		*) usage ;;
	esac
done
shift "$((OPTIND-1))"

(($# <= 1)) || usage

force="${1:-}"

mkdir -vp "$ref_dir"

n_replaced=0
n_failures=0
n_crashes=0
n_tests=0

trap 'echo -e "\e[95mInterrupted!\e[0m"; exit 1' INT
on_exit() {
	if (($n_crashes)); then
		echo -e "\e[95m$n_crashes/$n_tests tests crashed!\e[0;33m  (\e[91m$n_failures failed, \e[0;33m$n_replaced replaced)\e[0m"
		exit 1
	elif (($n_failures)); then
		echo -e "\e[91m$n_failures/$n_tests tests failed!\e[0;33m  ($n_replaced replaced)\e[0m"
		exit 1
	else
		echo -e "\e[92mAll $n_tests tests passed.\e[0;33m  ($n_replaced replaced)\e[0m"
	fi
	rm -vf kalendar/kalendars/*.json.tmp
}
trap on_exit EXIT

for y in $(seq "$year_start" "$year_end"); do
	((n_tests++,n_failures++)) || :
	tmp="kalendar/kalendars/year-$y.json.tmp"
	out="kalendar/kalendars/year-$y.json"
	ref="$ref_dir/year-$y.json"

	mkdir -vp "$(dirname "$tmp")" "$(dirname "$out")"
	if python -m kalendar.kalendar -y "$y" | jq '.[][] |= sort' > "$tmp"; then
		:
	else
		((n_crashes++)) || :
		continue
	fi
	mv -T "$tmp" "$out"

	act=
	if [[ ! -f $ref ]]; then
		# Force copy if we have no reference
		echo >&2 "Reference file missing: $ref"
		act=y
	elif diff >&2 -s -U5 "$ref" "$out"; then
		# Never copy if there are no differences
		act=s
	fi

	# If we don't have an action yet, use forced action or else prompt.
	while [[ -z "$act" ]]; do
		case "$force" in
			'')
				read >&2 -p "$prompt" -n1 act
				echo >&2 ""
			;;
			*)
				act="$force"
				echo >&2 "$prompt$act"
			;;
		esac
		case "$act" in
			y) force=  ;;
			n) force=  ;;
			a) force=a ;;
			d) force=d ;;
			s) force=  ;;
			q) force=  ;;
			*)
				echo >&2 "Invalid response: $act"
				echo >&2 "$action_help"
				force=
				act=
				continue
			;;
		esac
		break
	done

	case "$act" in
		y|a) ((n_failures--,n_replaced++)) || : ; cp -vT "$out" "$ref" ;;
		n|d) ;;
		s) ((n_failures--)) || : ;;
		q) break ;;
		*) echo >&2 "Invalid action: $act" ; exit 1 ;;
	esac
done
