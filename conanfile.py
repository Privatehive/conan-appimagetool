#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.files import download, copy, rm
from conan.tools.system.package_manager import Apt
from conan.errors import ConanInvalidConfiguration
import json, os

required_conan_version = ">=2.0"

class AppImageToolConan(ConanFile):

    jsonInfo = json.load(open("info.json", 'r'))
    # ---Package reference---
    name = jsonInfo["projectName"]
    version = jsonInfo["version"]
    user = jsonInfo["domain"]
    channel = "stable"
    # ---Metadata---
    description = jsonInfo["projectDescription"]
    license = jsonInfo["license"]
    author = jsonInfo["vendor"]
    topics = jsonInfo["topics"]
    homepage = jsonInfo["homepage"]
    url = jsonInfo["repository"]
    # ---Requirements---
    requires = []
    tool_requires = []
    # ---Sources---
    exports = ["info.json"]
    exports_sources = []
    # ---Binary model---
    settings = "os", "arch"
    options = {}
    default_options = {}
    # ---Build---
    generators = []
    # ---Folders---
    no_copy_source = True

    valid_arch = ["x86_64", "x86", "armv6", "armv7", "armv8"]

    def validate(self):
        valid_os = ["Linux"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(f"{self.name} {self.version} is only supported for the following operating systems: {valid_os}")
        if str(self.settings.arch) not in self.valid_arch:
            raise ConanInvalidConfiguration(f"{self.name} {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")

    def system_requirements(self):
        if self.settings.os == "Linux":
            apt = Apt(self)
            pack_names = ["libgpgme11"]
            apt.install(pack_names, update=True)

    def build(self):
        appimagetool = self.conan_data["sources"][self.version]["tool"][str(self.settings.arch)]["filename"]
        download(self, **self.conan_data["sources"][self.version]["tool"][str(self.settings.arch)])
        self.run("chmod +x ./%s" % appimagetool)
        self.run("./%s --appimage-extract" % appimagetool)
        rm(self, "%s" % appimagetool, ".")
        for arch in self.valid_arch:
            runtime = self.conan_data["sources"][self.version]["runtime"][arch]["filename"]
            download(self, **self.conan_data["sources"][self.version]["runtime"][arch])
            self.run("chmod +x %s" % runtime)

    def package(self):
        copy(self, pattern="*", src=self.build_folder, dst=self.package_folder)

    def package_info(self):
        appimage_bin = os.path.join(self.package_folder, "squashfs-root", "usr", "bin")
        self.output.info('Prepending to PATH environment variable: %s' % appimage_bin)
        self.buildenv_info.prepend_path("PATH", appimage_bin)
        self.cpp_info.bindirs = ['squashfs-root/usr/bin', './']
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
