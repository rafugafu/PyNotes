if [ "$EUID" -ne 0 ]; then
  echo "error: run the script with sudo."
  exit 1
fi
version="${1:-latest}"
url_pynotes="https://raw.githubusercontent.com/rafugafu/PyNotes/main/v$version/PyNotes%20v$version.tar.gz"
wget "$url_pynotes"
tar -xf "PyNotes v$version.tar.gz"
cd "PyNotes v$version"
dnf install *.rpm
cd ..
rm -r "PyNotes v$version"
rm "PyNotes v$version.tar.gz"