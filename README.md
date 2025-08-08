PyNotes is an advanced text-editor made in python.  
System: Ubuntu or Windows 10 / 11 with python 3.10 or above (Everything may not work with older versions).  
**EASYTK REQUIRES TTKTHEMES TO RUN IN OLD VERSIONS. IT IS ALSO AUTOINSTALLED WITH OTHER PACKAGES FROM PYNOTES VERSION 1.4.2. INSTALL WITH:**  
`pip3 install ttkthemes`  
# Installation:  
## Linux:  
**Note:** In some versions of Linux, tkinter or pip may not come installed. You will then have to manually install tkinter and pip. It is also best to run PyNotes inside a clean virtual environment.  
### Deb Package  
**Note:** If you are using Ubuntu 23 or later, you may get an error like:  
```
error: externally-managed-environment  
  
× This environment is externally managed  
╰─> To install Python packages system-wide, try apt install  
    python3-xyz, where xyz is the package you are trying to  
    install.  
      
    If you wish to install a non-Debian-packaged Python package,  
    create a virtual environment using python3 -m venv path/to/venv.  
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make  
    sure you have python3-full installed.  
      
    If you wish to install a non-Debian packaged Python application,  
    it may be easiest to use pipx install xyz, which will manage a  
    virtual environment for you. Make sure you have pipx installed.  
      
    See /usr/share/doc/python3.12/README.venv for more information.  
  
note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.  
hint: See PEP 668 for the detailed specification.  

```
If this happens, you can either create a virtual environment of Python and run PyNotes inside it, OR remove the `/usr/lib/python3.*/EXTERNALLY-MANAGED` file.  
  
Run the `pynotes_debian_installer.sh` script with root.  
If not given version it will install the latest version.  
**Eg:**  
`sudo ./pynotes_debian_installer.sh`  
### RPM Package  
Run the `pynotes_rpm_installer.sh` script with root.  
If not given version it will install the latest version.  
**Eg:**  
`sudo ./pynotes_rpm_installer.sh`  
## Windows:  
Run the `pynotes_windows_installer.py` script with python.  
It will open a GUI where you can select the version and install. You will have to allow it to make changes to your system.  
**Eg:**  
`python pynotes_windows_installer.py`  
**Note:** The prompt to allow it to make changes to your system will appear as Python not PyNotes.  
**Known Bug:**  
When it asks to install the necessary modules, sometimes it will crash after installing the modules. In this case just restart it and it should work perfectly fine.