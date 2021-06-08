import os
import sys
import setuptools
import glob

with open("pyaedt/version.txt", "r") as f:
    version = f.readline()

if sys.version_info >= (3, 0):
    install_requires = ["pywin32 >= 2.2.7;platform_system=='Windows'",
                        "pythonnet >= 2.4.0;platform_system=='Windows'"]
else:
    install_requires = []


# loosely from https://packaging.python.org/guides/single-sourcing-package-version/
HERE = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(HERE, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="pyaedt",
    version=version,
    maintainer='ANSYS, Inc.',
    author_email="massimo.capodiferro@ansys.com",
    description="higher-level ANSYS Electronics Destkop framework",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=install_requires,
    packages=['pyaedt', 'pyaedt.misc', 'pyaedt.application', 'pyaedt.modeler', 'pyaedt.modules',
              'pyaedt.generic', 'pyaedt.edb_core', 'pyaedt.examples'],
    data_files=[('dlls', glob.iglob('pyaedt/dlls/**/*', recursive=True)),
                ('License', glob.iglob('./*.md', recursive=True)),
                ('version', ['pyaedt/version.txt'])],
    include_package_data=True,
    license="MIT License",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
)
