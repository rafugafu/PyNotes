#!/bin/bash
if [ "$EUID" -ne 0 ]; then
  printf "\033[31merror: run the script with sudo.\033[0m\n"
  exit 1
fi
version="${1:-latest}"
url_pynotes="https://raw.githubusercontent.com/rafugafu/PyNotes/main/v$version/PyNotes%20v$version.tar.gz"
if ! wget -O "PyNotes v$version.tar.gz" "$url_pynotes"; then
  printf "\033[31merror: could not download PyNotes version '%s', check that it exists and is correct.\033[0m\n" "$version"
  rm -f "PyNotes v$version.tar.gz"
  exit 1
fi
tar -xf "PyNotes v$version.tar.gz"
cd "PyNotes v$version"
apt install --reinstall --allow-downgrades ./PyNotes.deb
cd ..
rm -rf "PyNotes v$version"
rm -f "PyNotes v$version.tar.gz"
printf '\n\033[32msuccessfully installed PyNotes v%s!\033[0m\n' "$version"