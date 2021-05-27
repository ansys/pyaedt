"""Miscelanous functions for pyaedt"""
import warnings
import os


def list_installed_ansysem():
    """Return a list of installed versions of ANSYSEM based on ANSYSEM_ROOT"""
    aedt_env_var_prefix = "ANSYSEM_ROOT"
    version_list = sorted([x for x in os.environ if x.startswith(aedt_env_var_prefix)], reverse=True)
    
    if not version_list:
        warnings.warn("No Installed versions of AEDT found in system environment variables ANSYSEM_ROOTxxx")

    return version_list
