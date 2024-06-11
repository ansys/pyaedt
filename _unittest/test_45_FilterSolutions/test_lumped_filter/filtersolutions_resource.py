import os


def resources_driectory():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    test_dir = os.path.dirname(dir_path)
    resources_path = os.path.join(test_dir, "resources")
    return resources_path


def resource_path(resource_file_name):
    return os.path.join(resources_driectory(), resource_file_name)
