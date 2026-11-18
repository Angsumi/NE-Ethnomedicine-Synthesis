#!/bin/bash
# usage: dl.sh SID URL  -> sources/pdf/SID.pdf, keeps only real PDFs
sid=$1; url=$2; dir=${3:-sources/pdf}; out=$dir/$sid.pdf; tmp=$(mktemp -p $dir .dl.XXXX)
curl -sSL --max-time 90 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36" -o "$tmp" "$url"
if head -c 5 "$tmp" | grep -q '%PDF'; then mv "$tmp" "$out"; echo "$sid OK $(du -k "$out"|cut -f1)KB pages=$(pdfinfo "$out" 2>/dev/null|awk '/^Pages/{print $2}') :: $(pdftotext -l 1 "$out" - 2>/dev/null | tr -s ' \n' ' ' | cut -c1-140)";
else echo "$sid FAIL ($(file -b "$tmp"|cut -c1-40)) $url"; rm -f "$tmp"; fi
