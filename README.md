PyNotes is an advanced text-editor made in python.  
System: Ubuntu or Windows 10 / 11 with python 3.10 or above (Everything may not work with older versions).  
**EASYTK REQUIRES TTKTHEMES TO RUN. IT IS ALSO AUTOINSTALLED WITH OTHER PACKAGES FROM PYNOTES VERSION 1.4.2. INSTALL WITH:**  
`pip3 install ttkthemes`  
# Installation:  
## Linux:  
**Note:** In some versions of Linux, tkinter or pip may not come installed. You will then have to manually install tkinter and pip. It is also best to run PyNotes inside a clean virtual environment.  
### Deb Package  
Run the `pynotes_debian_installer.sh` script with root.  
If not given version it will install the latest version.  
**Eg:**  
`sudo ./pynotes_debian_installer.sh`  
### RPM Package  
Downloading and installing the PyNotes RPM package does not have a script.  
You will have to manually download and install the latest version from the [GitHub Repository](https://github.com/rafugafu/pynotes)  
## Windows:  
Run the `pynotes_windows_installer.py` script with python.  
It will open a GUI where you can select the version and install. You will have to allow it to make changes to your system.  
**Eg:**  
`python pynotes_windows_installer.py`  
**Note:** The prompt to allow it to make changes to your system will appear as python not PyNotes.  
**Known Bug:**  
When it asks to install the necessary modules, sometimes it will crash after installing the modules. In this case just restart it and it should work perfectly fine.