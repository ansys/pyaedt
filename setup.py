import setuptools
import sys

from _setup_common import name, version, author, maintainer, maintainer_email, description, long_description, packages, data_files, license, classifiers

dependency_links = []
if sys.version_info >= (3, 9):
    install_requires = ["pywin32 >= 2.2.7;platform_system=='Windows'",
                        'pythonnet']
    dependency_links = ['https://github.com/pyansys/PyAEDT/raw/release/0.3/pythonnet-2.5.2-cp39-cp39-win_amd64.whl']
elif sys.version_info >= (3, 0):
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
    dependency_links=dependency_links,
    packages=packages,
    data_files=data_files,
    include_package_data=True,
    license=license,
    classifiers=classifiers,
)
