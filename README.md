# Qt6static
## Overview

Qt6static is a repository maintained by swissQprint for building a static version of Qt 6. This setup is useful when you do not want to rely on external Qt libraries at runtime.

## Features

    Static Linking: Generate static Qt 6 libraries.

    Customizable Build: Easily modify required modules to suit specific needs.

## Prerequisites

Before building, ensure you have the following installed:

    Windows:

        Conan2

        CMake

        Ninja

        Git

        MSVC

## Building Qt6static
### Windows

    Open Terminal

    $env:CI_COMMIT_TAG = "v6.8.3" // This needs to be a valid tag from the https://github.com/swissQprint/qt5.git repository and min v6.8.0

    conan create . -s build_type=Release // build_type has to be either 'Debug' or 'Release


## License
The Qt6static project is licensed under the Qt License (GPL v3).

## Additional documentation

Static building doumentation of Qt -> https://doc.qt.io/Boot2Qt/b2qt-meta-qt6.html#building-static-version-of-qt

For statically linking your library see -> https://doc.qt.io/Boot2Qt/b2qt-static-linking.html 

## Getting Help

If you think you found a bug, please report it to

https://bugreports.qt.io/browse/QTIFW

General questions are best asked on interest@qt-project.org.
