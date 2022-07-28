from collections import OrderedDict

defaultparametricSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "Sim. Setups": [],
        "Sweeps": OrderedDict(
            {"SweepDefinition": OrderedDict({"Variable": "", "Data": "", "OffsetF1": False, "Synchronize": 0})}
        ),
        "Sweep Operations": OrderedDict(),
        "Goals": OrderedDict(),
    }
)


defaultdxSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "Sim. Setups": [],
        "Sweeps": OrderedDict(
            {"SweepDefinition": OrderedDict({"Variable": "", "Data": "", "OffsetF1": False, "Synchronize": 0})}
        ),
        "Sweep Operations": OrderedDict(),
        "CostFunctionName": "Cost",
        "CostFuncNormType": "L2",
        "CostFunctionGoals": OrderedDict(),
        "EmbeddedParamSetup": -1,
        "Goals": OrderedDict(),
    }
)

defaultoptiSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "Optimizer": "Quasi Newton",
        "AnalysisStopOptions": OrderedDict(
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
        "Variables": OrderedDict(),
        "LCS": OrderedDict(),
        "Goals": OrderedDict(),
        "Acceptable_Cost": 0,
        "Noise": 0.0001,
        "UpdateDesign": False,
        "UpdateIteration": 5,
        "KeepReportAxis": True,
        "UpdateDesignWhenDone": True,
    }
)

defaultsensitivitySetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "MaxIterations": 10,
        "PriorPSetup": "",
        "PreSolvePSetup": True,
        "Variables": OrderedDict(),
        "LCS": OrderedDict(),
        "Goals": OrderedDict(),
        "Primary Goal": 0,
        "PrimaryError": 0.0001,
        "Perform Worst Case Analysis": False,
    }
)

defaultstatisticalSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "MaxIterations": 50,
        "SeedValue": 0,
        "PriorPSetup": "",
        "Variables": OrderedDict(),
        "Goals": OrderedDict(),
    }
)

defaultdoeSetup = OrderedDict(
    {
        "IsEnabled": True,
        "ProdOptiSetupDataV2": OrderedDict({"SaveFields": False, "CopyMesh": False, "SolveWithCopiedMeshOnly": True}),
        "StartingPoint": OrderedDict(),
        "Sim. Setups": [],
        "CostFunctionName": "Cost",
        "CostFuncNormType": "L2",
        "CostFunctionGoals": OrderedDict(),
        "Variables": OrderedDict(),
        "Goals": OrderedDict(),
        "DesignExprData": OrderedDict(
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
        "RespSurfaceSetupData": OrderedDict({"Type": "kGenAggr", "RefineType": "kManual"}),
        "ResponsePoints": OrderedDict({"NumOfStrs": 0}),
        "ManualRefinePoints": OrderedDict({"NumOfStrs": 0}),
        "CustomVerifyPoints": OrderedDict({"NumOfStrs": 0}),
        "Tolerances": [],
    }
)
