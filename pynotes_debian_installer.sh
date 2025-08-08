version="${1:-latest}"
url_pynotes="https://raw.githubusercontent.com/rafugafu/PyNotes/main/v$version/PyNotes%20v$version.tar.gz"
wget "$url_pynotes"
tar -xf "PyNotes v$version.tar.gz"
cd "PyNotes v$version"
dpkg -i PyNotes.deb
cd ..
rm -r "PyNotes v$version"
rm "PyNotes v$version.tar.gz"