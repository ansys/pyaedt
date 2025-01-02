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


defaultparametricSetup = dict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": dict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": {},
        "Sim. Setups": [],
        "Sweeps": dict({"SweepDefinition": dict({"Variable": "", "Data": "", "OffsetF1": False, "Synchronize": 0})}),
        "Sweep Operations": {},
        "Goals": {},
    }
)


defaultdxSetup = dict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": dict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": {},
        "Sim. Setups": [],
        "Sweeps": dict({"SweepDefinition": dict({"Variable": "", "Data": "", "OffsetF1": False, "Synchronize": 0})}),
        "Sweep Operations": {},
        "CostFunctionName": "Cost",
        "CostFuncNormType": "L2",
        "CostFunctionGoals": {},
        "EmbeddedParamSetup": -1,
        "Goals": {},
    }
)

defaultoptiSetup = dict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": dict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": {},
        "Optimizer": "Quasi Newton",
        "AnalysisStopOptions": dict(
            {
                "StopForNumIteration": True,
                "StopForElapsTime": False,
                "StopForSlowImprovement": False,
                "StopForGrdTolerance": False,
                "MaxNumIteration": 1000,
                "MaxSolTimeInSec": 3600,
                "RelGradientTolerance": 0,
                "MinNumIteration": 10,
            }
        ),
        "CostFuncNormType": "L2",
        "PriorPSetup": "",
        "PreSolvePSetup": True,
        "Variables": {},
        "LCS": {},
        "Goals": {},
        "Acceptable_Cost": 0,
        "Noise": 0.0001,
        "UpdateDesign": False,
        "UpdateIteration": 5,
        "KeepReportAxis": True,
        "UpdateDesignWhenDone": True,
    }
)

defaultsensitivitySetup = dict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": dict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": {},
        "MaxIterations": 10,
        "PriorPSetup": "",
        "PreSolvePSetup": True,
        "Variables": {},
        "LCS": {},
        "Goals": {},
        "Primary Goal": 0,
        "PrimaryError": 0.0001,
        "Perform Worst Case Analysis": False,
    }
)

defaultstatisticalSetup = dict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": dict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": {},
        "MaxIterations": 50,
        "SeedValue": 0,
        "PriorPSetup": "",
        "Variables": {},
        "Goals": {},
    }
)

defaultdoeSetup = dict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": dict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": {},
        "Sim. Setups": [],
        "CostFunctionName": "Cost",
        "CostFuncNormType": "L2",
        "CostFunctionGoals": {},
        "Variables": {},
        "Goals": {},
        "DesignExprData": dict(
            {
                "Type": "kOSF",
                "CCDDeignType": "kFaceCentered",
                "CCDTemplateType": "kStandard",
                "LHSSampleType": "kCCDSample",
                "RamdomSeed": 0,
                "NumofSamples": 10,
                "OSFDeignType": "kOSFD_MAXIMINDIST",
                "MaxCydes": 10,
            }
        ),
        "RespSurfaceSetupData": dict({"Type": "kGenAggr", "RefineType": "kManual"}),
        "ResponsePoints": dict({"NumOfStrs": 0}),
        "ManualRefinePoints": dict({"NumOfStrs": 0}),
        "CustomVerifyPoints": dict({"NumOfStrs": 0}),
        "Tolerances": [],
    }
)
