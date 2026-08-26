#!/bin/bash
if [ "$EUID" -ne 0 ]; then
  printf "\033[31merror: run the script with sudo.\033[0m\n"
  exit 1
fi
version="${1:-latest}"
if [ "$version" = "latest" ]; then
  version=$(curl -s https://api.github.com/repos/rafugafu/PyNotes/releases/latest | grep -oP '"tag_name":\s*"v?\K[^"]+')
fi
url_pynotes="https://github.com/rafugafu/PyNotes/releases/download/v$version/pynotes-$version-1.noarch.rpm"
if ! wget -O "pynotes-$version-1.noarch.rpm" "$url_pynotes"; then
  printf "\033[31merror: could not download PyNotes version '%s', check that it exists and is correct.\033[0m\n" "$version"
  rm -f "pynotes-$version-1.noarch.rpm"
  exit 1
fi
dnf reinstall --allow-downgrade "pynotes-$version-1.noarch.rpm"
rm -f "pynotes-$version-1.noarch.rpm"
printf '\n\033[32msuccessfully installed PyNotes v%s!\033[0m\n' "$version"