import setuptools
import sys

from _setup_common import name, version, author, maintainer, maintainer_email, description, long_description, packages, data_files, license, classifiers

if sys.version_info >= (3, 0):
    install_requires = ["pywin32 >= 2.2.7;platform_system=='Windows'",
                        "pythonnet >= 2.4.0;platform_system=='Windows'"]
else:
    install_requires = []

setuptools.setup(
    name=name,
    version=version,
    author=author,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=install_requires,
    packages=packages,
    data_files=data_files,
    include_package_data=True,
    license=license,
    classifiers=classifiers,
)
