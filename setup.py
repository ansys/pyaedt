import sys
import setuptools
import glob

with open("pyaedt/version.txt", "r") as f:
    version = f.readline()

if sys.version_info >= (3, 0):
    install_requires = ["pywin32 >= 2.2.7;platform_system=='Windows'", "pythonnet >= 2.4.0;platform_system=='Windows'"]
else:
    install_requires = []

setuptools.setup(
    name="pyaedt",
    version=version,
    maintainer='ANSYS, Inc.',
    author_email="massimo.capodiferro@ansys.com",
    description="higher-level ANSYS Electronics Destkop framework",
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
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
)
