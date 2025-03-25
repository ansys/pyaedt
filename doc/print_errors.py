"""Read errors output from a sphinx build and remove duplicate groups"""
import sys
import os
from pathlib import Path
sys.tracebacklimit = 0
my_path = Path(__file__).parent.resolve()

errors = set()
error_file = Path(my_path) / "build_errors.txt"
if Path(error_file).is_file():
    with open(error_file) as fid:
        group = []
        for line in fid.readlines():
            line = line.strip()
            if line:
                group.append(line)
            else:
                errors.add("\n".join(group))
                group = []

    for error in list(errors):
        print(error)
        print()

    # There should be no errors here since sphinx will have exited
    print()
    if errors:
        raise Exception(f"Sphinx reported unique {len(errors)} warnings\n\n")

print(f"Sphinx Reported no warnings\n\n")
