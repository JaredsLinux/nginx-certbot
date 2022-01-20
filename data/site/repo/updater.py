#!/usr/bin/env python3.9

"""
Update the contents of this repository
AUTHOR: Jared Dyreson
"""

import os
import re
import shutil
from natsort import natsorted, ns # external

_re = re.compile("ubuntu", re.IGNORECASE)
_match = _re.match(os.uname().release)

# if not(_match):
    # raise ValueError("[ERROR] Please run on Ubuntu based systems")

class Updater():
    def __init__(self):
        self.version = 1.0

        self.test_dir = "/tmp/tuffix"
        self.pkg_base = "TuffixInstaller"
        self.pkg_name = "Tuffix"
        self.pkg_arch = os.uname().machine
        self.home_dir = os.getcwd()
        self.build_dir = f'{self.home_dir}/amd64/builds'

    def build_package(self):

        if(os.path.exists(self.test_dir)):
            shutil.rmtree(self.test_dir)

        self.get_git_repo()

        up_to_date_pkg = self.find_debian_packages()[0]
        _pkg_regex = re.compile("(?P<version>[0-9]+\.[0-9]+)\_(?P<revision>[0-9])")

        _pkg_match = _pkg_regex.search(up_to_date_pkg)
        version, revision = None, None
        if(_pkg_match):
            version, revision = _pkg_match.group("version"),_pkg_match.group("revision")

        _git_pkg_version, _git_pkg_revision = self.parse_control_contents()

        if(_git_pkg_revision == revision):
            print(f"[INFO] No need to proceed further, git version renders {_git_pkg_revision} and database provides {revision}. Please update git version if you intended to update PPA")
            return

        deb_output = f'{self.build_dir}/{self.pkg_name}_{_git_pkg_version}_{_git_pkg_revision}_{self.pkg_arch}'

        self.build_deb(self.pkg_base, deb_output)
        self.update_database(deb_output)
        print(f'[INFO] Updating TuffixInstaller from revision {revision} to {_git_pkg_revision}')

    def get_git_repo(self):
        _git_url = "https://github.com/mshafae/tuffix.git"
        os.system(f'git clone {_git_url} {self.test_dir}')
        os.chdir(self.test_dir)
        os.system('git checkout releasebuild')

        if(not os.path.exists(self.pkg_base)):
                raise ValueError('[ERROR] Installer directory is not present, cowardly refusing')

    def find_debian_packages(self) -> list:
        container = []
        for _, _, files in os.walk(os.path.abspath(self.build_dir)):
            if(files):
                container.append(*files)
        return natsorted(container, alg=ns.IC)

    def parse_control_contents(self) -> tuple:
        _pkg_version_regex = re.compile("Version:\s+(?P<version>[0-9]+\.[0-9]+)\-(?P<revision>[0-9]+)")
        with open(f'{self.test_dir}/{self.pkg_base}/DEBIAN/control') as fp:
            for line in fp.readlines():
                _pkg_version_match = _pkg_version_regex.match(line)
                if(_pkg_version_match):
                    return (_pkg_version_match.group("version"), _pkg_version_match.group("revision"))
        return (None, None)

    def build_deb(self, src: str, output: str):
        if (not isinstance(output, str) or
            not isinstance(src, str)):
            raise ValueError

        os.system(f'dpkg-deb --build {src} {output}')

    def update_database(self, src: str):
        if (not isinstance(src, str)):
            raise ValueError

        os.system(f'reprepro --ask-passphrase -Vb . includedeb focal {src}')

U = Updater()
U.build_package()
