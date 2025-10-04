# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ctypes import CFUNCTYPE
from ctypes import PyDLL
from ctypes import c_bool
from ctypes import c_int
from ctypes import c_wchar_p
from ctypes import py_object
import os
from pathlib import Path
import re
import types

import grpc

from ansys.aedt.core.generic.general_methods import _retry_ntimes
from ansys.aedt.core.generic.general_methods import inclusion_list
from ansys.aedt.core.generic.general_methods import settings
from ansys.aedt.core.internal.errors import GrpcApiError

logger = settings.logger


class AedtBlockObj(list):
    def GetName(self):
        if len(self) > 0:
            f = self[0]
            if isinstance(f, str):
                d = f.split(":")
                if len(d) == 2:
                    if d[0] == "NAME":
                        return d[1]

    def __GetValueIdxByKey__(self, keyName):
        for i in range(0, len(self) - 1):
            if isinstance(self[i], str):
                toks = self[i].split(":")
                if len(toks) == 2:
                    if toks[1] == "=" and toks[0] == keyName:
                        return i + 1
        raise GrpcApiError(keyName + " is not a key!")

    def __getitem__(self, idxOrKey):
        if isinstance(idxOrKey, str):
            idx = self.__GetValueIdxByKey__(idxOrKey)
            if idx is not None:
                return super().__getitem__(idx)
        return super().__getitem__(idxOrKey)

    def __setitem__(self, idxOrKey, newVal):
        if isinstance(idxOrKey, int):
            if idxOrKey >= 0 or idxOrKey < len(self):
                oldItem = self.__getitem__(idxOrKey)
                if isinstance(oldItem, str):
                    toks = oldItem.split(":")
                    if len(toks) == 2 and (toks[1] == "=" or toks[0] == "NAME"):
                        raise GrpcApiError("The element is a key. It should not be overwritten.")
            return super().__setitem__(idxOrKey, newVal)
        if isinstance(idxOrKey, str):
            idx = self.__GetValueIdxByKey__(idxOrKey)
            if idx is not None:
                return super().__setitem__(idx, newVal)
            raise GrpcApiError("Key is not found.")
        raise GrpcApiError("Must be a key name or index.")

    def keys(self):
        arr = []
        for i in range(0, len(self) - 1):
            if isinstance(self[i], str):
                toks = self[i].split(":")
                if len(toks) == 2 and toks[1] == "=":
                    arr.append(toks[0])
        return arr


exclude_list = ["GetAppDesktop", "GetProcessID", "GetGrpcServerPort"]


class AedtObjWrapper:
    def __init__(self, objID, listFuncs, AedtAPI=None):
        self.__dict__["objectID"] = objID  # avoid derive class overwrite __setattr__
        self.__dict__["__methodNames__"] = listFuncs
        self.dllapi = AedtAPI
        self.is_linux = os.name == "posix"

    # print(self.objectID)

    def __str__(self):
        return "Instance of an Aedt object:" + str(self.objectID)

    def __Invoke__(self, funcName, argv):
        if settings.enable_debug_grpc_api_logger:
            settings.logger.debug(f" {funcName}{argv}")
        try:
            if (settings.use_multi_desktop and funcName not in exclude_list) or funcName in inclusion_list:
                self.dllapi.recreate_application(True)
            ret = _retry_ntimes(
                settings.number_of_grpc_api_retries,
                self.dllapi.AedtAPI.InvokeAedtObjMethod,
                self.objectID,
                funcName,
                argv,
            )  # Call C function
            if ret and isinstance(ret, (AedtObjWrapper, AedtPropServer)):
                ret.AedtAPI = self.AedtAPI
            return ret
        except Exception:  # pragma: no cover
            raise GrpcApiError(f"Failed to execute gRPC AEDT command: {funcName}")

    def __dir__(self):
        return self.__methodNames__

    def __GetObjMethod__(self, funcName):
        try:

            def DynamicFunc(self, *args):
                return self.__Invoke__(funcName, args)

            return types.MethodType(DynamicFunc, self)
        except (AttributeError, GrpcApiError):
            raise GrpcApiError("This AEDT object has no attribute '" + funcName + "'")

    def __getattr__(self, funcName):
        try:
            if funcName == "ScopeID":  # backward compatible for IronPython wrapper.
                return self.objectID
            return self.__GetObjMethod__(funcName)
        except Exception:
            raise GrpcApiError(f"Failed to get gRPC API AEDT attribute {funcName}")

    def __setattr__(self, attrName, val):
        if attrName == "objectID" or attrName == "__methodNames__":
            raise GrpcApiError("This attribute cannot be modified.")
        elif attrName in self.__methodNames__:
            raise GrpcApiError(attrName + " is a function name.")
        else:
            super().__setattr__(attrName, val)

    def __del__(self):
        if "ReleaseAedtObject" in dir(self.dllapi):
            self.dllapi.ReleaseAedtObject(self.objectID)

    def match(self, patternStr):  # IronPython wrapper implemented this function return IEnumerable<string>.
        class IEnumerable(list):
            def __getattr__(self, key):
                if key == "Count":
                    return len(self)

        pattern = re.compile(patternStr)
        found = IEnumerable()
        allMethods = self.__methodNames__
        for method in allMethods:
            if pattern.match(method):
                found.append(method)
        return found

    def GetHashCode(self):  # IronPython build in function
        return self.__hash__()


class AedtPropServer(AedtObjWrapper):
    def __init__(self, objID, listFuncs, aedtapi):
        AedtObjWrapper.__init__(self, objID, listFuncs, aedtapi)
        self.__dict__["__propMap__"] = None
        self.__dict__["__propNames__"] = None

    def __GetPropAttributes(self):
        if self.__propMap__ is None:
            propMap = {}
            propNames = self.GetPropNames()
            for prop in propNames:
                attrName = ""
                if prop[0].isdigit():
                    attrName += "_"
                for c in prop:
                    if c.isalnum():
                        attrName += c
                    else:
                        attrName += "_"
                propMap[attrName] = prop
            self.__propMap__ = propMap
        return self.__propMap__

    def __dir__(self):
        ret = super().__dir__().copy()
        try:
            for attrName, _ in self.__GetPropAttributes().items():
                ret.append(attrName)
        except Exception:
            try:
                for attrName, _ in self.__GetPropAttributes():
                    ret.append(attrName)
            except Exception:
                return ret
        return ret

    def __getattr__(self, attrName):
        try:
            return super().__getattr__(attrName)
        except AttributeError:
            # if AedtAPI.IsAedtObjPropName(self.objectID, attrName, False):
            #    return self.GetPropValue(attrName)
            propMap = self.__GetPropAttributes()
            if attrName in propMap:
                return self.GetPropValue(propMap[attrName])
            raise GrpcApiError(f"Failed to retrieve attribute {attrName} from gRPC API")

    def __setattr__(self, attr, val):
        if attr in self.__dict__:
            self.__dict__[attr] = val
            return
        propMap = self.__GetPropAttributes()
        try:
            if attr in propMap:
                self.SetPropValue(propMap[attr], val)
                return
        except Exception:
            settings.logger.debug(f"Failed to update attribute {attr} of AedtPropServer instance.")
        super().__setattr__(attr, val)

    def GetName(self):
        return self.__Invoke__("GetName", ())

    def GetObjPath(self):
        return self.__Invoke__("GetObjPath", ())

    def GetChildNames(self, childType=""):
        return self.__Invoke__("GetChildNames", (childType))

    def GetPropNames(self, includeReadOnly=True):
        if includeReadOnly:
            if self.__propNames__ is None:
                self.__propNames__ = self.__Invoke__("GetPropNames", (includeReadOnly,))
            return self.__propNames__
        return self.__Invoke__("GetPropNames", (includeReadOnly,))

    def GetPropValue(self, propName=""):
        return self.__Invoke__("GetPropValue", (propName,))

    def SetPropValue(self, propName, val):
        return self.__Invoke__("SetPropValue", (propName, val))


class AEDT:
    def __init__(self, pathDir):
        is_linux = os.name == "posix"
        is_windows = not is_linux
        pathDir = Path(pathDir)
        self.original_path = pathDir
        self.pathDir = pathDir.parents[1]

        # Plugin filename depends on OS
        if is_linux:
            pluginFileName = r"libPyDesktopPlugin.so"
        else:
            pluginFileName = r"PyDesktopPlugin.dll"

        AedtAPIDll_file = self.pathDir / pluginFileName  # install dir

        if not AedtAPIDll_file.is_file():
            self.pathDir = self.pathDir.parents[2]
            AedtAPIDll_file = self.pathDir / r"build_output\64Release\PyDesktopPlugin.dll"  # develop dir

        # load dll
        if is_windows:
            # on windows, modify path
            aedtDir = AedtAPIDll_file.parent
            originalPath = os.environ["PATH"]
            os.environ["PATH"] = originalPath + os.pathsep + str(aedtDir)
            AedtAPI = PyDLL(str(AedtAPIDll_file))
            os.environ["PATH"] = originalPath
        else:
            AedtAPI = PyDLL(str(AedtAPIDll_file))
        # AedtAPI.SetPyObjCalbacks.argtypes = py_object, py_object, py_object
        AedtAPI.SetPyObjCalbacks.restype = None

        # Must use global variable to hold those functions reference
        self.callbackToCreateObj = None
        self.callbackCreateBlock = None
        self.callbackGetObjID = None
        version = None
        with open(self.pathDir / "product.info", "r") as f:
            for line in f:
                if "AnsProductVersion" in line:
                    version = line.split("=")[1].strip('\n"')
                    break

        if version >= "24.1":
            AedtAPI.CreateAedtApplication.argtypes = c_wchar_p, py_object, c_bool, c_bool
        else:
            AedtAPI.CreateAedtApplication.argtypes = c_wchar_p, c_int, c_bool, c_bool

        AedtAPI.CreateAedtApplication.restype = py_object

        AedtAPI.InvokeAedtObjMethod.argtypes = c_int, c_wchar_p, py_object
        AedtAPI.InvokeAedtObjMethod.restype = py_object

        AedtAPI.ReleaseAedtObject.argtypes = (c_int,)
        AedtAPI.ReleaseAedtObject.restype = None
        self.AedtAPI = AedtAPI
        self.SetPyObjCalbacks()
        self.aedt = None
        self.non_graphical = False

    def SetPyObjCalbacks(self):
        self.callback_type = CFUNCTYPE(py_object, c_int, c_bool, py_object)
        self.callbackToCreateObj = self.callback_type(
            self.CreateAedtObj
        )  # must use global variable to hold this function reference
        RetObj_InObj_Func_type = CFUNCTYPE(py_object, py_object)
        self.callbackCreateBlock = RetObj_InObj_Func_type(self.CreateAedtBlockObj)
        self.callbackGetObjID = RetObj_InObj_Func_type(self.GetAedtObjId)
        self.AedtAPI.SetPyObjCalbacks(self.callbackToCreateObj, self.callbackCreateBlock, self.callbackGetObjID)

    def CreateAedtApplication(self, machine="", port=0, NGmode=False, alwaysNew=True):
        if not alwaysNew and port:
            grpc_channel = grpc.insecure_channel(f"{machine}:{port}")
            try:
                grpc.channel_ready_future(grpc_channel).result(settings.desktop_launch_timeout)
            except grpc.FutureTimeoutError:
                settings.logger.error("Failed to connect to Desktop Session")
                return
        try:
            self.aedt = self.AedtAPI.CreateAedtApplication(machine, port, NGmode, alwaysNew)
        except Exception:
            settings.logger.warning("Failed to create AedtApplication.")
        if not self.aedt:
            raise GrpcApiError("Failed to connect to Desktop Session")
        self.machine = machine
        self.non_graphical = NGmode
        if port == 0:
            self.port = self.aedt.GetAppDesktop().GetGrpcServerPort()
        else:
            self.port = port

        return self.aedt

    @property
    def odesktop(self):
        return self.recreate_application()

    def recreate_application(self, force=False):
        def run():
            self.ReleaseAedtObject(self.aedt.objectID)
            port = self.port
            machine = self.machine
            self.__init__(self.original_path)
            self.port = port
            self.machine = machine
            self.aedt = self.AedtAPI.CreateAedtApplication(self.machine, self.port, self.non_graphical, False)
            return self.aedt.GetAppDesktop()

        if force:
            return run()
        else:
            try:
                odesktop = self.aedt.GetAppDesktop()
                if odesktop:
                    return odesktop
            except Exception:
                return run()

    def InvokeAedtObjMethod(self, objectID, funcName, argv):
        return self.AedtAPI.InvokeAedtObjMethod(objectID, funcName, argv)

    def ReleaseAedtObject(self, objectID):
        self.AedtAPI.ReleaseAedtObject(objectID)

    def ReleaseAll(self):
        self.AedtAPI.ReleaseAll()

    def IsEmbedded(self):
        return False

    def CreateAedtObj(self, objectID, bIsPropSvr, listFuncs):
        # print("Create " + str(objectID))
        if bIsPropSvr:
            return AedtPropServer(
                objectID,
                listFuncs,
                self,
            )

        return AedtObjWrapper(
            objectID,
            listFuncs,
            self,
        )

    def CreateAedtBlockObj(self, list_in):
        count = len(list_in)
        if count > 1:
            if isinstance(list_in[0], str):
                toks = list_in[0].split(":")
                if len(toks) == 2:
                    start = -1
                    if count % 2 == 0:
                        if toks[1] == "=":
                            start = 2
                    elif count > 2:
                        if toks[0] == "NAME":
                            start = 1
                    if start > 0:
                        isBlock = True
                        for i in range(start, count - 1, 2):
                            if isinstance(list_in[i], str):
                                toks = list_in[i].split(":")
                                if len(toks) != 2 or toks[1] != "=":
                                    isBlock = False
                                    break
                            else:
                                isBlock = False
                                break
                        if isBlock:
                            return AedtBlockObj(list_in)
        return list_in

    def GetAedtObjId(self, obj):
        if isinstance(obj, AedtObjWrapper):
            return obj.objectID
        return None

    def Release(self):
        self.AedtAPI.ReleaseAll()
