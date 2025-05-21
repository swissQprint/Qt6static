from conan import ConanFile
from conan.tools.files import copy, replace_in_file, rename, load
from conan.tools.scm.git import Git
from conan.tools.cmake import CMake, CMakeToolchain
from datetime import datetime

import os
import re


class Qt6Static(ConanFile):
    name = "qt6static"
    user = "3rdparty"
    qt_version = os.environ.get("CI_COMMIT_TAG", "v6.8.0")  # Minimum version is v6.8.0, lower versions use a different configure.bat
    license = "proprietary"
    author = "Qt Company Ltd."
    url = "https://www.qt.io"
    description = "Qt6 C++ framework"
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    exports_sources = ["qt-static-license.json"]

    def set_version(self):
        self.version = self.qt_version.replace("v", "")

    def source(self):
        git = Git(self, "qt-source")
        git.clone(
            url="https://code.qt.io/qt/qt5.git",
            target=".",
        )
        git.checkout(f"{self.qt_version}")
        replace_in_file(self, "./qt-static-license.json", "$CONAN_VERSION$", self.qt_version)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        for dep in self.dependencies.values():
            if dep.package_folder:
                src_license_folder = os.path.join(dep.package_folder, "license")
                if os.path.exists(src_license_folder):
                    copy(self, "*", src=src_license_folder, dst=os.path.join(f"{self.package_folder}", "license"), keep_path=False)

    def build(self):
        if not self.source_folder:
            raise ValueError("source_folder is not set")
        os.chdir(self.source_folder)
        build_type = str(self.settings.build_type).lower() if self.settings.build_type else "release"  # type: ignore
        print(f"Build type: {build_type}")

        # Possible arguments are listed in qtbase/config_help.txt
        self.run(
            f"{self.source_folder}/qt-source/configure.bat "
            "-init-submodules -submodules qtbase "
            "-static "
            f"-{build_type} "
            f"-prefix {self.source_folder}/qt-install "
            "-gui "
            "-widgets "
            "-schannel "
            "-no-openssl "
            "-qt-zlib "
            "-qt-pcre "
            "-qt-libpng "
            "-qt-libjpeg "
            "-no-opengl "
            "-platform win32-msvc "
            "-cmake-generator Ninja "
        )
        print("Config summary:")
        config_summary_path = f"{self.source_folder}/config.summary"
        try:
            with open(config_summary_path, "r") as file:
                print(file.read())
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error accessing config.summary: {e}")
        cmake = CMake(self)
        cmake.build()
        copy(self, "GPL-3.0-only.txt", src=os.path.join(f"{self.source_folder}", "qt-source", "LICENSES"), dst=os.path.join(f"{self.package_folder}", "license"), keep_path=False)
        target_license_path = os.path.join(f"{self.package_folder}", "license", "qt6static.license")
        rename(self, os.path.join(f"{self.package_folder}", "license", "GPL-3.0-only.txt"), target_license_path)
        self.prepend_copyright_to_license(license_file_path=target_license_path, copyright_string=self.copyright_from_file("qt-source/qtbase/src/corelib/text/qstring.h"))

    def package(self):
        os.makedirs(f"{self.source_folder}/qt-install")
        cmake = CMake(self)
        cmake.install()

        copy(self, "config.summary", src=self.source_folder, dst=os.path.join(f"{self.source_folder}", "qt-install"), keep_path=True)
        copy(self, "*", src=os.path.join(f"{self.source_folder}", "qt-install"), dst=self.package_folder, keep_path=True)
        copy(self, "qt-static-license.json", src=self.source_folder, dst=os.path.join(f"{self.package_folder}", "license"), keep_path=False)

    def copyright_from_file(self, copyright_file_path: str) -> str:
        copyright_string = ""
        current_year = datetime.now().year
        file = load(self, copyright_file_path)
        first_line = file.splitlines()[0]
        pattern = r"^//\s*(.*?)(\d{4})\s+(.+)"
        matches = re.findall(pattern, first_line, re.DOTALL)
        if matches:
            if len(matches[0]) == 3:
                copyright_pre_text = matches[0][0]
                copyright_year = matches[0][1]
                copyright_year_range = f"{copyright_year}-{current_year} "
                copyright_post_text = matches[0][2]
                copyright_string = copyright_pre_text + copyright_year_range + copyright_post_text + "\n"
        return copyright_string

    def prepend_copyright_to_license(self, license_file_path: str, copyright_string: str) -> None:
        print(f"open license path: {license_file_path} and prepend copyright string: {copyright_string}")
        with open(f"{license_file_path}", "r+") as license_file:
            license_file_string = license_file.read()
            license_file.seek(0)
            license_file.write(copyright_string + license_file_string)
            license_file.flush()
