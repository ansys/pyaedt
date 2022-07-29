import os.path
from collections import OrderedDict

from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file

meshlink = [("ImportMesh", False)]
autosweep = [("RangeType", "LinearStep"), ("RangeStart", "1GHz"), ("RangeEnd", "10GHz"), ("RangeStep", "1GHz")]
autosweeps = [("Sweep", autosweep)]
multifreq = [("1GHz", [0.02]), ("2GHz", [0.02]), ("5GHz", [0.02])]
sweepsbr = [("RangeType", "LinearStep"), ("RangeStart", "1GHz"), ("RangeEnd", "10GHz"), ("RangeStep", "1GHz")]
sweepssbr = [("Sweep", sweepsbr)]
muoption = [("MuNonLinearBH", True)]
transientelectrostatic = [("SaveField", True), ("Stop", "100s"), ("InitialStep", "0.01s"), ("MaxStep", "5s")]
transienthfss = [
    ("TimeProfile", "Broadband Pulse"),
    ("HfssFrequency", "5GHz"),
    ("MinFreq", "100MHz"),
    ("MaxFreq", "1GHz"),
    ("NumFreqsExtracted", 401),
    ("SweepMinFreq", "100MHz"),
    ("SweepMaxFreq", "1GHz"),
    ("UseAutoTermination", 1),
    ("SteadyStateCriteria", 0.01),
    ("UseMinimumDuration", 0),
    ("TerminateOnMaximum", 0),
]
HFSSDrivenAuto = [
    ("IsEnabled", True),
    ("MeshLink", meshlink),
    ("AutoSolverSetting", "Balanced"),
    ("Sweeps", autosweeps),
    ("SaveRadFieldsOnly", False),
    ("SaveAnyFields", True),
    ("Type", "Discrete"),
]
"""HFSS automatic setup properties and default values."""

HFSSDrivenDefault = [
    ("SolveType", "Single"),
    ("MultipleAdaptiveFreqsSetup", multifreq),
    ("Frequency", "5GHz"),
    ("MaxDeltaS", 0.02),
    ("PortsOnly", False),
    ("UseMatrixConv", False),
    ("MaximumPasses", 6),
    ("MinimumPasses", 1),
    ("MinimumConvergedPasses", 1),
    ("PercentRefinement", 30),
    ("IsEnabled", True),
    ("MeshLink", meshlink),
    ("BasisOrder", 1),
    ("DoLambdaRefine", True),
    ("DoMaterialLambda", True),
    ("SetLambdaTarget", False),
    ("Target", 0.3333),
    ("UseMaxTetIncrease", False),
    ("PortAccuracy", 2),
    ("UseABCOnPort", False),
    ("SetPortMinMaxTri", False),
    ("UseDomains", False),
    ("UseIterativeSolver", False),
    ("SaveRadFieldsOnly", False),
    ("SaveAnyFields", True),
    ("IESolverType", "Auto"),
    ("LambdaTargetForIESolver", 0.15),
    ("UseDefaultLambdaTgtForIESolver", True),
    ("IE Solver Accuracy", "Balanced"),
]
"""HFSS driven properties and default values."""

HFSSEigen = [
    ("MinimumFrequency", "2GHz"),
    ("NumModes", 1),
    ("MaxDeltaFreq", 10),
    ("ConvergeOnRealFreq", False),
    ("MaximumPasses", 3),
    ("MinimumPasses", 1),
    ("MinimumConvergedPasses", 1),
    ("PercentRefinement", 30),
    ("IsEnabled", True),
    ("MeshLink", meshlink),
    ("BasisOrder", 1),
    ("DoLambdaRefine", True),
    ("DoMaterialLambda", True),
    ("SetLambdaTarget", False),
    ("Target", 0.2),
    ("UseMaxTetIncrease", False),
]
"""HFSS Eigenmode properties and default values."""

HFSSTransient = [
    ("Frequency", "5GHz"),
    ("MaxDeltaS", 0.02),
    ("MaximumPasses", 20),
    ("UseImplicitSolver", True),
    ("IsEnabled", True),
    ("MeshLink", meshlink),
    ("BasisOrder", -1),
    ("Transient", transienthfss),
]
"""HFSS transient setup properties and default values."""

HFSSSBR = [
    ("IsEnabled", True),
    ("MeshLink", meshlink),
    ("IsSbrRangeDoppler", False),
    ("RayDensityPerWavelength", 4),
    ("MaxNumberOfBounces", 5),
    ("RadiationSetup", ""),
    ("PTDUTDSimulationSettings", "None"),
    ("Sweeps", sweepssbr),
    ("ComputeFarFields", False),
]
"""HFSS SBR+ setup properties and default values."""

MaxwellTransient = [
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("NonlinearSolverResidual", "0.005"),
    ("ScalarPotential", "Second Order"),
    ("SmoothBHCurve", False),
    ("StopTime", "10000000ns"),
    ("TimeStep", "2000000ns"),
    ("OutputError", False),
    ("UseControlProgram", False),
    ("ControlProgramName", ""),
    ("ControlProgramArg", ""),
    ("CallCtrlProgAfterLastStep", False),
    ("FastReachSteadyState", False),
    ("AutoDetectSteadyState", False),
    ("IsGeneralTransient", True),
    ("IsHalfPeriodicTransient", False),
    ("SaveFieldsType", "None"),
    ("CacheSaveKind", "Count"),
    ("NumberSolveSteps", 1),
    ("RangeStart", "0s"),
    ("RangeEnd", "0.1s"),
]
"""Maxwell transient setup properties and default values."""

Magnetostatic = [
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("MaximumPasses", 10),
    ("MinimumPasses", 2),
    ("MinimumConvergedPasses", 1),
    ("PercentRefinement", 30),
    ("SolveFieldOnly", False),
    ("PercentError", 1),
    ("SolveMatrixAtLast", True),
    ("PercentError", 1),
    ("UseIterativeSolver", False),
    ("RelativeResidual", 1e-06),
    ("NonLinearResidual", 0.001),
    ("SmoothBHCurve", False),
    ("MuOption", muoption),
]
"""Maxwell magnetostatic setup properties and default values."""

Electrostatic = [
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("MaximumPasses", 10),
    ("MinimumPasses", 2),
    ("MinimumConvergedPasses", 1),
    ("PercentRefinement", 30),
    ("SolveFieldOnly", False),
    ("PercentError", 1),
    ("SolveMatrixAtLast", True),
    ("PercentError", 1),
    ("UseIterativeSolver", False),
    ("RelativeResidual", 1e-06),
    ("NonLinearResidual", 0.001),
]
"""Maxwell electrostatic setup properties and default values."""

subrange = [
    ("SweepSetupType", "LinearStep"),
    ("StartValue", "1e-08GHz"),
    ("StopValue", "1e-06GHz"),
    ("StepSize", "1e-08GHz"),
]
subranges = [("Subrange", subrange)]

EddyCurrent = [
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("MaximumPasses", 6),
    ("MinimumPasses", 1),
    ("MinimumConvergedPasses", 1),
    ("PercentRefinement", 30),
    ("SolveFieldOnly", False),
    ("PercentError", 1),
    ("SolveMatrixAtLast", True),
    ("PercentError", 1),
    ("UseIterativeSolver", False),
    ("RelativeResidual", 1e-5),
    ("NonLinearResidual", 0.0001),
    ("SmoothBHCurve", False),
    ("Frequency", "60Hz"),
    ("HasSweepSetup", False),
    ("SweepRanges", subranges),
    ("UseHighOrderShapeFunc", False),
    ("UseMuLink", False),
]
"""Maxwell eddy current setup properties and default values."""

ElectricTransient = [
    ("Enabled",),
    ("MeshLink", meshlink),
    ("Tolerance", 0.005),
    ("ComputePowerLoss", False),
    ("Data", transientelectrostatic),
    ("Initial Voltage", "0mV"),
]
"""Maxwell electric transient setup properties and default values."""

SteadyTemperatureAndFlow = [
    ("Enabled", True),
    ("Flow Regime", "Laminar"),
    ("Include Temperature", True),
    ("Include Flow", True),
    ("Include Gravity", False),
    ("Solution Initialization - X Velocity", "0m_per_sec"),
    ("Solution Initialization - Y Velocity", "0m_per_sec"),
    ("Solution Initialization - Z Velocity", "0m_per_sec"),
    ("Solution Initialization - Temperature", "AmbientTemp"),
    ("Solution Initialization - Turbulent Kinetic Energy", "1m2_per_s2"),
    ("Solution Initialization - Turbulent Dissipation Rate", "1m2_per_s3"),
    ("Solution Initialization - Specific Dissipation Rate", "1diss_per_s"),
    ("Convergence Criteria - Flow", "0.001"),
    ("Convergence Criteria - Energy", "1e-07"),
    ("Convergence Criteria - Turbulent Kinetic Energy", "0.001"),
    ("Convergence Criteria - Turbulent Dissipation Rate", "0.001"),
    ("Convergence Criteria - Specific Dissipation Rate", "0.001"),
    ("Convergence Criteria - Discrete Ordinates", "1e-06"),
    ("IsEnabled", False),
    ("Radiation Model", "Off"),
    ("Under-relaxation - Pressure", "0.7"),
    ("Under-relaxation - Momentum", "0.3"),
    ("Under-relaxation - Temperature", "1"),
    ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
    ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
    ("Under-relaxation - Specific Dissipation Rate", "0.8"),
    ("Discretization Scheme - Pressure", "Standard"),
    ("Discretization Scheme - Momentum", "First"),
    ("Discretization Scheme - Temperature", "Second"),
    ("Secondary Gradient", False),
    ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
    ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
    ("Discretization Scheme - Specific Dissipation Rate", "First"),
    ("Discretization Scheme - Discrete Ordinates", "First"),
    ("Linear Solver Type - Pressure", "V"),
    ("Linear Solver Type - Momentum", "flex"),
    ("Linear Solver Type - Temperature", "F"),
    ("Linear Solver Type - Turbulent Kinetic Energy", "flex"),
    ("Linear Solver Type - Turbulent Dissipation Rate", "flex"),
    ("Linear Solver Type - Specific Dissipation Rate", "flex"),
    ("Linear Solver Termination Criterion - Pressure", "0.1"),
    ("Linear Solver Termination Criterion - Momentum", "0.1"),
    ("Linear Solver Termination Criterion - Temperature", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Dissipation  Rate", "0.1"),
    ("Linear Solver Termination Criterion - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Pressure", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Momentum", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Temperature", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Stabilization - Pressure", "None"),
    ("Linear Solver Stabilization - Temperature", "None"),
    ("Frozen Flow Simulation", False),
    ("Sequential Solve of Flow and Energy Equations", False),
    ("Convergence Criteria - Max Iterations", 100),
]
"""Icepack steady temperature and steady flow setup properties and default values."""

SteadyTemperatureOnly = [
    ("Enabled", True),
    ("Flow Regime", "Laminar"),
    ("Include Temperature", True),
    ("Include Gravity", False),
    ("Solution Initialization - X Velocity", "0m_per_sec"),
    ("Solution Initialization - Y Velocity", "0m_per_sec"),
    ("Solution Initialization - Z Velocity", "0m_per_sec"),
    ("Solution Initialization - Temperature", "AmbientTemp"),
    ("Solution Initialization - Turbulent Kinetic Energy", "1m2_per_s2"),
    ("Solution Initialization - Turbulent Dissipation Rate", "1m2_per_s3"),
    ("Solution Initialization - Specific Dissipation Rate", "1diss_per_s"),
    ("Convergence Criteria - Flow", "0.001"),
    ("Convergence Criteria - Energy", "1e-07"),
    ("Convergence Criteria - Turbulent Kinetic Energy", "0.001"),
    ("Convergence Criteria - Turbulent Dissipation Rate", "0.001"),
    ("Convergence Criteria - Specific Dissipation Rate", "0.001"),
    ("Convergence Criteria - Discrete Ordinates", "1e-06"),
    ("IsEnabled", False),
    ("Radiation Model", "Off"),
    ("Under-relaxation - Pressure", "0.7"),
    ("Under-relaxation - Momentum", "0.3"),
    ("Under-relaxation - Temperature", "1"),
    ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
    ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
    ("Under-relaxation - Specific Dissipation Rate", "0.8"),
    ("Discretization Scheme - Pressure", "Standard"),
    ("Discretization Scheme - Momentum", "First"),
    ("Discretization Scheme - Temperature", "Second"),
    ("Secondary Gradient", False),
    ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
    ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
    ("Discretization Scheme - Specific Dissipation Rate", "First"),
    ("Discretization Scheme - Discrete Ordinates", "First"),
    ("Linear Solver Type - Pressure", "V"),
    ("Linear Solver Type - Momentum", "flex"),
    ("Linear Solver Type - Temperature", "F"),
    ("Linear Solver Type - Turbulent Kinetic Energy", "flex"),
    ("Linear Solver Type - Turbulent Dissipation Rate", "flex"),
    ("Linear Solver Type - Specific Dissipation Rate", "flex"),
    ("Linear Solver Termination Criterion - Pressure", "0.1"),
    ("Linear Solver Termination Criterion - Momentum", "0.1"),
    ("Linear Solver Termination Criterion - Temperature", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Dissipation  Rate", "0.1"),
    ("Linear Solver Termination Criterion - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Pressure", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Momentum", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Temperature", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Stabilization - Pressure", "None"),
    ("Linear Solver Stabilization - Temperature", "None"),
    ("Sequential Solve of Flow and Energy Equations", False),
    ("Convergence Criteria - Max Iterations", 100),
]
"""Icepack steady temperature setup properties and default values."""

SteadyFlowOnly = [
    ("Enabled", True),
    ("Flow Regime", "Laminar"),
    ("Include Flow", True),
    ("Include Gravity", False),
    ("Solution Initialization - X Velocity", "0m_per_sec"),
    ("Solution Initialization - Y Velocity", "0m_per_sec"),
    ("Solution Initialization - Z Velocity", "0m_per_sec"),
    ("Solution Initialization - Temperature", "AmbientTemp"),
    ("Solution Initialization - Turbulent Kinetic Energy", "1m2_per_s2"),
    ("Solution Initialization - Turbulent Dissipation Rate", "1m2_per_s3"),
    ("Solution Initialization - Specific Dissipation Rate", "1diss_per_s"),
    ("Convergence Criteria - Flow", "0.001"),
    ("Convergence Criteria - Energy", "1e-07"),
    ("Convergence Criteria - Turbulent Kinetic Energy", "0.001"),
    ("Convergence Criteria - Turbulent Dissipation Rate", "0.001"),
    ("Convergence Criteria - Specific Dissipation Rate", "0.001"),
    ("Convergence Criteria - Discrete Ordinates", "1e-06"),
    ("IsEnabled", False),
    ("Radiation Model", "Off"),
    ("Under-relaxation - Pressure", "0.7"),
    ("Under-relaxation - Momentum", "0.3"),
    ("Under-relaxation - Temperature", "1"),
    ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
    ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
    ("Under-relaxation - Specific Dissipation Rate", "0.8"),
    ("Discretization Scheme - Pressure", "Standard"),
    ("Discretization Scheme - Momentum", "First"),
    ("Discretization Scheme - Temperature", "First"),
    ("Secondary Gradient", False),
    ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
    ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
    ("Discretization Scheme - Specific Dissipation Rate", "First"),
    ("Discretization Scheme - Discrete Ordinates", "First"),
    ("Linear Solver Type - Pressure", "V"),
    ("Linear Solver Type - Momentum", "flex"),
    ("Linear Solver Type - Temperature", "F"),
    ("Linear Solver Type - Turbulent Kinetic Energy", "flex"),
    ("Linear Solver Type - Turbulent Dissipation Rate", "flex"),
    ("Linear Solver Type - Specific Dissipation Rate", "flex"),
    ("Linear Solver Termination Criterion - Pressure", "0.1"),
    ("Linear Solver Termination Criterion - Momentum", "0.1"),
    ("Linear Solver Termination Criterion - Temperature", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Dissipation  Rate", "0.1"),
    ("Linear Solver Termination Criterion - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Pressure", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Momentum", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Temperature", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Stabilization - Pressure", "None"),
    ("Linear Solver Stabilization - Temperature", "None"),
    ("Frozen Flow Simulation", False),
    ("Sequential Solve of Flow and Energy Equations", False),
    ("Convergence Criteria - Max Iterations", 100),
]
"""Icepack steady flow setup properties and default values."""

Q3DCond = [("MaxPass", 10), ("MinPass", 1), ("MinConvPass", 1), ("PerError", 1), ("PerRefine", 30)]
Q3DMult = [("MaxPass", 1), ("MinPass", 1), ("MinConvPass", 1), ("PerError", 1), ("PerRefine", 30)]
Q3DDC = [("SolveResOnly", False), ("Cond", Q3DCond), ("Mult", Q3DMult)]
Q3DCap = [
    ("MaxPass", 10),
    ("MinPass", 1),
    ("MinConvPass", 1),
    ("PerError", 1),
    ("PerRefine", 30),
    ("AutoIncreaseSolutionOrder", True),
    ("SolutionOrder", "High"),
    ("Solver Type", "Iterative"),
]
Q3DAC = [("MaxPass", 10), ("MinPass", 1), ("MinConvPass", 1), ("PerError", 1), ("PerRefine", 30)]
Matrix = [
    ("AdaptiveFreq", "1GHz"),
    ("SaveFields", False),
    ("Enabled", True),
    ("Cap", Q3DCap),
    ("DC", Q3DDC),
    ("AC", Q3DAC),
]
"""Q3D Extractor setup properties and default values."""

OutputQuantities = []
NoiseOutputQuantities = []
SweepDefinition = [("Variable", "Freq"), ("Data", "LINC 1GHz 5GHz 501"), ("OffsetF1", False), ("Synchronize", 0)]
NexximLNA = [
    ("DataBlockID", 16),
    ("OptionName", "(Default Options)"),
    ("AdditionalOptions", ""),
    ("AlterBlockName", ""),
    ("FilterText", ""),
    ("AnalysisEnabled", 1),
    ("OutputQuantities", OutputQuantities),
    ("NoiseOutputQuantities", NoiseOutputQuantities),
    ("Name", "LinearFrequency"),
    ("LinearFrequencyData", [False, 0.1, False, "", False]),
    ("SweepDefinition", SweepDefinition),
]
"""Nexxim linear network setup properties and default values."""

NexximDC = [
    ("DataBlockID", 15),
    ("OptionName", "(Default Options)"),
    ("AdditionalOptions", ""),
    ("AlterBlockName", ""),
    ("FilterText", ""),
    ("AnalysisEnabled", 1),
    ("OutputQuantities", OutputQuantities),
    ("NoiseOutputQuantities", NoiseOutputQuantities),
    ("Name", "LinearFrequency"),
]
"""Nexxim DC setup properties and default values."""

NexximTransient = [
    ("DataBlockID", 10),
    ("OptionName", "(Default Options)"),
    ("AdditionalOptions", ""),
    ("AlterBlockName", ""),
    ("FilterText", ""),
    ("AnalysisEnabled", 1),
    ("OutputQuantities", OutputQuantities),
    ("NoiseOutputQuantities", NoiseOutputQuantities),
    ("Name", "LinearFrequency"),
    ("TransientData", ["0.1ns", "10ns"]),
    ("TransientNoiseData", [False, "", "", 0, 1, 0, False, 1]),
    ("TransientOtherData", ["default"]),
]
"""Nexxim transient setup properties and default values."""

NexximQuickEye = [
    ("DataBlockID", 28),
    ("OptionName", "(Default Options)"),
    ("AdditionalOptions", ""),
    ("AlterBlockName", ""),
    ("FilterText", ""),
    ("AnalysisEnabled", 1),
    ("OutputQuantities", OutputQuantities),
    ("NoiseOutputQuantities", NoiseOutputQuantities),
    ("Name", "QuickEyeAnalysis"),
    ("QuickEyeAnalysis", [False, "1e-9", False, "0", "", True]),
]
NexximVerifEye = [
    ("DataBlockID", 27),
    ("OptionName", "(Default Options)"),
    ("AdditionalOptions", ""),
    ("AlterBlockName", ""),
    ("FilterText", ""),
    ("AnalysisEnabled", 1),
    ("OutputQuantities", OutputQuantities),
    ("NoiseOutputQuantities", NoiseOutputQuantities),
    ("Name", "VerifEyeAnalysis"),
    ("VerifEyeAnalysis", [False, "1e-9", False, "0", "", True]),
]
NexximAMI = [
    ("DataBlockID", 29),
    ("OptionName", "(Default Options)"),
    ("AdditionalOptions", ""),
    ("AlterBlockName", ""),
    ("FilterText", ""),
    ("AnalysisEnabled", 1),
    ("OutputQuantities", OutputQuantities),
    ("NoiseOutputQuantities", NoiseOutputQuantities),
    ("Name", "AMIAnalysis"),
    ("AMIAnalysis", [32, False, False]),
]
NexximOscillatorRSF = []
NexximOscillator1T = []
NexximOscillatorNT = []
NexximHarmonicBalance1T = []
NexximHarmonicBalanceNT = []
NexximSystem = [
    ("DataBlockID", 32),
    ("OptionName", "(Default Options)"),
    ("AdditionalOptions", ""),
    ("AlterBlockName", ""),
    ("FilterText", ""),
    ("AnalysisEnabled", 1),
    ("OutputQuantities", OutputQuantities),
    ("NoiseOutputQuantities", NoiseOutputQuantities),
    ("Name", "HSPICETransient"),
    ("HSPICETransientData", ["0.1ns", "10ns"]),
    ("HSPICETransientOtherData", [3]),
]
NexximTVNoise = []
HSPICE = [
    ("DataBlockID", 30),
    ("OptionName", "(Default Options)"),
    ("AdditionalOptions", ""),
    ("AlterBlockName", ""),
    ("FilterText", ""),
    ("AnalysisEnabled", 1),
    ("OutputQuantities", OutputQuantities),
    ("NoiseOutputQuantities", NoiseOutputQuantities),
    ("Name", "SystemFDAnalysis"),
    ("SystemFDAnalysis", [False]),
]

HFSS3DLayout_Properties = [("Enable", "true")]
HFSS3DLayout_AdvancedSettings = [
    ("AccuracyLevel", 2),
    ("GapPortCalibration", True),
    ("ReferenceLengthRatio", 0.25),
    ("RefineAreaRatio", 4),
    ("DRCOn", False),
    ("FastSolverOn", False),
    ("StartFastSolverAt", 3000),
    ("LoopTreeOn", True),
    ("SingularElementsOn", False),
    ("UseStaticPortSolver", False),
    ("UseThinMetalPortSolver", False),
    ("ComputeBothEvenAndOddCPWModes", False),
    ("ZeroMetalLayerThickness", 0),
    ("ThinDielectric", 0),
    ("UseShellElements", False),
    ("SVDHighCompression", False),
    ("NumProcessors", 1),
    ("UseHfssIterativeSolver", False),
    ("UseHfssMUMPSSolver", True),
    ("RelativeResidual", 1e-06),
    ("EnhancedLowFreqAccuracy", False),
    ("OrderBasis", -1),
    ("MaxDeltaZo", 2),
    ("UseRadBoundaryOnPorts", False),
    ("SetTrianglesForWavePort", False),
    ("MinTrianglesForWavePort", 100),
    ("MaxTrianglesForWavePort", 500),
    ("numprocessorsdistrib", 1),
    ("CausalMaterials", True),
    ("enabledsoforopti", True),
    ("usehfsssolvelicense", False),
    ("ExportAfterSolve", False),
    ("ExportDir", ""),
    ("CircuitSparamDefinition", False),
    ("CircuitIntegrationType", "FFT"),
    ("DesignType", "generic"),
    ("MeshingMethod", "Phi"),
    ("EnableDesignIntersectionCheck", True),
]
HFSS3DLayout_CurveApproximation = [
    ("ArcAngle", "30deg"),
    ("StartAzimuth", "0deg"),
    ("UseError", False),
    ("Error", "0meter"),
    ("MaxPoints", 8),
    ("UnionPolys", True),
    ("Replace3DTriangles", True),
]
HFSS3DLayout_Q3D_DCSettings = [
    ("SolveResOnly", True),
    ("Cond", Q3DCond),
    ("Mult", Q3DMult),
    ("Solution Order", "Normal"),
]
# HFSS3DLayout_AdaptiveFrequencyData = [
#     ("AdaptiveFrequency", "5GHz"),
#     ("MaxDelta", "0.02"),
#     ("MaxPasses", 10),
#     ("Expressions", [])]
CGDataBlock = [
    ("MaxPass", 10),
    ("MinPass", 1),
    ("MinConvPass", 1),
    ("PerError", 1),
    ("PerRefine", 30),
    ("DataType", "CG"),
    ("Included", True),
    ("UseParamConv", True),
    ("UseLossyParamConv", False),
    ("PerErrorParamConv", 1),
    ("UseLossConv", True),
]
RLDataBlock = [
    ("MaxPass", 10),
    ("MinPass", 1),
    ("MinConvPass", 1),
    ("PerError", 1),
    ("PerRefine", 30),
    ("DataType", "CG"),
    ("Included", True),
    ("UseParamConv", True),
    ("UseLossyParamConv", False),
    ("PerErrorParamConv", 1),
    ("UseLossConv", True),
]
Open = [
    ("AdaptiveFreq", "1GHz"),
    ("SaveFields", True),
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("CGDataBlock", CGDataBlock),
    ("RLDataBlock", RLDataBlock),
    ("CacheSaveKind", "Delta"),
    ("ConstantDelta", "0s"),
]
"""Q2D open setup properties and default values."""

Close = [
    ("AdaptiveFreq", "1GHz"),
    ("SaveFields", True),
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("CGDataBlock", CGDataBlock),
    ("RLDataBlock", RLDataBlock),
    ("CacheSaveKind", "Delta"),
    ("ConstantDelta", "0s"),
]
"""Q2D close setup properties and default values."""


TransientTemperatureAndFlow = [
    ("Enabled", True),
    ("Flow Regime", "Laminar"),
    ("Include Temperature", True),
    ("Include Flow", True),
    ("Include Gravity", False),
    ("Include Solar", False),
    ("Solution Initialization - X Velocity", "0m_per_sec"),
    ("Solution Initialization - Y Velocity", "0m_per_sec"),
    ("Solution Initialization - Z Velocity", "0m_per_sec"),
    ("Solution Initialization - Temperature", "AmbientTemp"),
    ("Solution Initialization - Turbulent Kinetic Energy", "1m2_per_s2"),
    ("Solution Initialization - Turbulent Dissipation Rate", "1m2_per_s3"),
    ("Solution Initialization - Specific Dissipation Rate", "1diss_per_s"),
    ("Solution Initialization - Use Model Based Flow Initialization", False),
    ("Convergence Criteria - Flow", "0.001"),
    ("Convergence Criteria - Energy", "1e-07"),
    ("Convergence Criteria - Turbulent Kinetic Energy", "0.001"),
    ("Convergence Criteria - Turbulent Dissipation Rate", "0.001"),
    ("Convergence Criteria - Specific Dissipation Rate", "0.001"),
    ("Convergence Criteria - Discrete Ordinates", "1e-06"),
    ("IsEnabled:=", False),
    ("Radiation Model", "Off"),
    ("Solar Radiation Model", "Solar Radiation Calculator"),
    ("Solar Radiation - Scattering Fraction", "0"),
    ("Solar Radiation - Day", 1),
    ("Solar Radiation - Month", 1),
    ("Solar Radiation - Hours", 0),
    ("Solar Radiation - Minutes", 0),
    ("Solar Radiation - GMT", "0"),
    ("Solar Radiation - Latitude", "0"),
    ("Solar Radiation - Latitude Direction", "East"),
    ("Solar Radiation - Longitude", "0"),
    ("Solar Radiation - Longitude Direction", "North"),
    ("Solar Radiation - Ground Reflectance", "0"),
    ("Solar Radiation - Sunshine Fraction", "0"),
    ("Solar Radiation - North X", "0"),
    ("Solar Radiation - North Y", "0"),
    ("Solar Radiation - North Z", "1"),
    ("Under-relaxation - Pressure", "0.3"),
    ("Under-relaxation - Momentum", "0.7"),
    ("Under-relaxation - Temperature", "1"),
    ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
    ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
    ("Under-relaxation - Specific Dissipation Rate", "0.8"),
    ("Discretization Scheme - Pressure", "Standard"),
    ("Discretization Scheme - Momentum", "First"),
    ("Discretization Scheme - Temperature", "First"),
    ("Secondary Gradient", False),
    ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
    ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
    ("Discretization Scheme - Specific Dissipation Rate", "First"),
    ("Discretization Scheme - Discrete Ordinates", "First"),
    ("Linear Solver Type - Pressure", "V"),
    ("Linear Solver Type - Momentum", "flex"),
    ("Linear Solver Type - Temperature", "F"),
    ("Linear Solver Type - Turbulent Kinetic Energy", "flex"),
    ("Linear Solver Type - Turbulent Dissipation Rate", "flex"),
    ("Linear Solver Type - Specific Dissipation Rate", "flex"),
    ("Linear Solver Termination Criterion - Pressure", "0.1"),
    ("Linear Solver Termination Criterion - Momentum", "0.1"),
    ("Linear Solver Termination Criterion - Temperature", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Termination Criterion - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Pressure", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Momentum", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Temperature", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Stabilization - Pressure", "None"),
    ("Linear Solver Stabilization - Temperature", "None"),
    ("Coupled pressure-velocity formulation", False),
    ("Frozen Flow Simulation", False),
    ("Start Time:=", "0s"),
    ("Stop Time:=", "20s"),
    ("Time Step:=", "1s"),
    ("Iterations per Time Step", 20),
    ("Import Start Time", False),
    ("Copy Fields From Source", False),
    ("SaveFieldsType", "Every N Steps"),
    ("N Steps:=", "10s"),
    ("Enable Control Program", False),
    ("Control Program Name", ""),
]

TransientTemperatureOnly = [
    ("Enabled", True),
    ("Flow Regime", "Laminar"),
    ("Include Temperature", True),
    ("Include Flow", False),
    ("Include Gravity", False),
    ("Include Solar", False),
    ("Solution Initialization - X Velocity", "0m_per_sec"),
    ("Solution Initialization - Y Velocity", "0m_per_sec"),
    ("Solution Initialization - Z Velocity", "0m_per_sec"),
    ("Solution Initialization - Temperature", "AmbientTemp"),
    ("Solution Initialization - Turbulent Kinetic Energy", "1m2_per_s2"),
    ("Solution Initialization - Turbulent Dissipation Rate", "1m2_per_s3"),
    ("Solution Initialization - Specific Dissipation Rate", "1diss_per_s"),
    ("Solution Initialization - Use Model Based Flow Initialization", False),
    ("Convergence Criteria - Flow", "0.001"),
    ("Convergence Criteria - Energy", "1e-07"),
    ("Convergence Criteria - Turbulent Kinetic Energy", "0.001"),
    ("Convergence Criteria - Turbulent Dissipation Rate", "0.001"),
    ("Convergence Criteria - Specific Dissipation Rate", "0.001"),
    ("Convergence Criteria - Discrete Ordinates", "1e-06"),
    ("IsEnabled:=", False),
    ("Radiation Model", "Off"),
    ("Solar Radiation Model", "Solar Radiation Calculator"),
    ("Solar Radiation - Scattering Fraction", "0"),
    ("Solar Radiation - Day", 1),
    ("Solar Radiation - Month", 1),
    ("Solar Radiation - Hours", 0),
    ("Solar Radiation - Minutes", 0),
    ("Solar Radiation - GMT", "0"),
    ("Solar Radiation - Latitude", "0"),
    ("Solar Radiation - Latitude Direction", "East"),
    ("Solar Radiation - Longitude", "0"),
    ("Solar Radiation - Longitude Direction", "North"),
    ("Solar Radiation - Ground Reflectance", "0"),
    ("Solar Radiation - Sunshine Fraction", "0"),
    ("Solar Radiation - North X", "0"),
    ("Solar Radiation - North Y", "0"),
    ("Solar Radiation - North Z", "1"),
    ("Under-relaxation - Pressure", "0.3"),
    ("Under-relaxation - Momentum", "0.7"),
    ("Under-relaxation - Temperature", "1"),
    ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
    ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
    ("Under-relaxation - Specific Dissipation Rate", "0.8"),
    ("Discretization Scheme - Pressure", "Standard"),
    ("Discretization Scheme - Momentum", "First"),
    ("Discretization Scheme - Temperature", "First"),
    ("Secondary Gradient", False),
    ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
    ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
    ("Discretization Scheme - Specific Dissipation Rate", "First"),
    ("Discretization Scheme - Discrete Ordinates", "First"),
    ("Linear Solver Type - Pressure", "V"),
    ("Linear Solver Type - Momentum", "flex"),
    ("Linear Solver Type - Temperature", "F"),
    ("Linear Solver Type - Turbulent Kinetic Energy", "flex"),
    ("Linear Solver Type - Turbulent Dissipation Rate", "flex"),
    ("Linear Solver Type - Specific Dissipation Rate", "flex"),
    ("Linear Solver Termination Criterion - Pressure", "0.1"),
    ("Linear Solver Termination Criterion - Momentum", "0.1"),
    ("Linear Solver Termination Criterion - Temperature", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Termination Criterion - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Pressure", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Momentum", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Temperature", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Stabilization - Pressure", "None"),
    ("Linear Solver Stabilization - Temperature", "None"),
    ("Coupled pressure-velocity formulation", False),
    ("Frozen Flow Simulation", False),
    ("Start Time:=", "0s"),
    ("Stop Time:=", "20s"),
    ("Time Step:=", "1s"),
    ("Iterations per Time Step", 20),
    ("Import Start Time", False),
    ("Copy Fields From Source", False),
    ("SaveFieldsType", "Every N Steps"),
    ("N Steps:=", "10s"),
    ("Enable Control Program", False),
    ("Control Program Name", ""),
]

TransientFlowOnly = [
    ("Enabled", True),
    ("Flow Regime", "Laminar"),
    ("Include Temperature", False),
    ("Include Flow", True),
    ("Include Gravity", False),
    ("Include Solar", False),
    ("Solution Initialization - X Velocity", "0m_per_sec"),
    ("Solution Initialization - Y Velocity", "0m_per_sec"),
    ("Solution Initialization - Z Velocity", "0m_per_sec"),
    ("Solution Initialization - Temperature", "AmbientTemp"),
    ("Solution Initialization - Turbulent Kinetic Energy", "1m2_per_s2"),
    ("Solution Initialization - Turbulent Dissipation Rate", "1m2_per_s3"),
    ("Solution Initialization - Specific Dissipation Rate", "1diss_per_s"),
    ("Solution Initialization - Use Model Based Flow Initialization", False),
    ("Convergence Criteria - Flow", "0.001"),
    ("Convergence Criteria - Energy", "1e-07"),
    ("Convergence Criteria - Turbulent Kinetic Energy", "0.001"),
    ("Convergence Criteria - Turbulent Dissipation Rate", "0.001"),
    ("Convergence Criteria - Specific Dissipation Rate", "0.001"),
    ("Convergence Criteria - Discrete Ordinates", "1e-06"),
    ("IsEnabled:=", False),
    ("Radiation Model", "Off"),
    ("Solar Radiation Model", "Solar Radiation Calculator"),
    ("Solar Radiation - Scattering Fraction", "0"),
    ("Solar Radiation - Day", 1),
    ("Solar Radiation - Month", 1),
    ("Solar Radiation - Hours", 0),
    ("Solar Radiation - Minutes", 0),
    ("Solar Radiation - GMT", "0"),
    ("Solar Radiation - Latitude", "0"),
    ("Solar Radiation - Latitude Direction", "East"),
    ("Solar Radiation - Longitude", "0"),
    ("Solar Radiation - Longitude Direction", "North"),
    ("Solar Radiation - Ground Reflectance", "0"),
    ("Solar Radiation - Sunshine Fraction", "0"),
    ("Solar Radiation - North X", "0"),
    ("Solar Radiation - North Y", "0"),
    ("Solar Radiation - North Z", "1"),
    ("Under-relaxation - Pressure", "0.3"),
    ("Under-relaxation - Momentum", "0.7"),
    ("Under-relaxation - Temperature", "1"),
    ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
    ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
    ("Under-relaxation - Specific Dissipation Rate", "0.8"),
    ("Discretization Scheme - Pressure", "Standard"),
    ("Discretization Scheme - Momentum", "First"),
    ("Discretization Scheme - Temperature", "First"),
    ("Secondary Gradient", False),
    ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
    ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
    ("Discretization Scheme - Specific Dissipation Rate", "First"),
    ("Discretization Scheme - Discrete Ordinates", "First"),
    ("Linear Solver Type - Pressure", "V"),
    ("Linear Solver Type - Momentum", "flex"),
    ("Linear Solver Type - Temperature", "F"),
    ("Linear Solver Type - Turbulent Kinetic Energy", "flex"),
    ("Linear Solver Type - Turbulent Dissipation Rate", "flex"),
    ("Linear Solver Type - Specific Dissipation Rate", "flex"),
    ("Linear Solver Termination Criterion - Pressure", "0.1"),
    ("Linear Solver Termination Criterion - Momentum", "0.1"),
    ("Linear Solver Termination Criterion - Temperature", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Termination Criterion - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Termination Criterion - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Pressure", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Momentum", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Temperature", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Kinetic Energy", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Turbulent Dissipation Rate", "0.1"),
    ("Linear Solver Residual Reduction Tolerance - Specific Dissipation Rate", "0.1"),
    ("Linear Solver Stabilization - Pressure", "None"),
    ("Linear Solver Stabilization - Temperature", "None"),
    ("Coupled pressure-velocity formulation", False),
    ("Frozen Flow Simulation", False),
    ("Start Time:=", "0s"),
    ("Stop Time:=", "20s"),
    ("Time Step:=", "1s"),
    ("Iterations per Time Step", 20),
    ("Import Start Time", False),
    ("Copy Fields From Source", False),
    ("SaveFieldsType", "Every N Steps"),
    ("N Steps:=", "10s"),
    ("Enable Control Program", False),
    ("Control Program Name", ""),
]


def HFSS3DLayout_AdaptiveFrequencyData(freq):
    """Update HFSS 3D adaptive frequency data.

    Parameters
    ----------
    freq : float
        Adaptive frequency value.


    Returns
    -------
    list
        List of frequency data.

    """
    value = [("AdaptiveFrequency", freq), ("MaxDelta", "0.02"), ("MaxPasses", 10), ("Expressions", [], None)]
    return value


HFSS3DLayout_SingleFrequencyDataList = [("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("5GHz"))]
HFSS3DLayout_BroadbandFrequencyDataList = [
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("5GHz")),
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("10GHz")),
]
HFSS3DLayout_MultiFrequencyDataList = [
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("2.5GHz")),
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("5GHz")),
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("10GHz")),
]
HFSS3DLayout_AdaptiveSettings = [
    ("DoAdaptive", True),
    ("SaveFields", False),
    ("SaveRadFieldsOnly", False),
    ("MaxRefinePerPass", 30),
    ("MinPasses", 1),
    ("MinConvergedPasses", 1),
    ("AdaptType", "kSingle"),  # possible values are "kSingle", "kMultiFrequencies", "kBroadband"
    ("Basic", True),
    ("SingleFrequencyDataList", HFSS3DLayout_SingleFrequencyDataList),
    ("BroadbandFrequencyDataList", HFSS3DLayout_BroadbandFrequencyDataList),
    ("MultiFrequencyDataList", HFSS3DLayout_MultiFrequencyDataList),
]
HFSS3DLayout = [
    ("Properties", HFSS3DLayout_Properties),
    ("CustomSetup", False),
    ("SolveSetupType", "HFSS"),
    ("PercentRefinementPerPass", 30),
    ("MinNumberOfPasses", 1),
    ("MinNumberOfConvergedPasses", 1),
    ("UseDefaultLambda", True),
    ("UseMaxRefinement", False),
    ("MaxRefinement", 1000000),
    ("SaveAdaptiveCurrents", False),
    ("SaveLastAdaptiveRadFields", False),
    ("ProdMajVerID", -1),
    ("ProjDesignSetup", ""),
    ("ProdMinVerID", -1),
    ("Refine", False),
    ("Frequency", "10GHz"),
    ("LambdaRefine", True),
    ("MeshSizeFactor", 1.5),
    ("QualityRefine", True),
    ("MinAngle", "15deg"),
    ("UniformityRefine", False),
    ("MaxRatio", 2),
    ("Smooth", False),
    ("SmoothingPasses", 5),
    ("UseEdgeMesh", False),
    ("UseEdgeMeshAbsLength", False),
    ("EdgeMeshRatio", 0.1),
    ("EdgeMeshAbsLength", "1000mm"),
    ("LayerProjectThickness", "0meter"),
    ("UseDefeature", True),
    ("UseDefeatureAbsLength", False),
    ("DefeatureRatio", 1e-06),
    ("DefeatureAbsLength", "0mm"),
    ("InfArrayDimX", 0),
    ("InfArrayDimY", 0),
    ("InfArrayOrigX", 0),
    ("InfArrayOrigY", 0),
    ("InfArraySkew", 0),
    ("ViaNumSides", 6),
    ("ViaMaterial", "copper"),
    ("Style25DVia", "Mesh"),
    ("Replace3DTriangles", True),
    ("LayerSnapTol", "1e-05"),
    ("ViaDensity", 0),
    ("HfssMesh", True),
    ("Q3dPostProc", False),
    ("UnitFactor", 1000),
    ("Verbose", False),
    ("NumberOfProcessors", 0),
    ("SmallVoidArea", -2e-09),
    ("HealingOption", 1),
    ("InclBBoxOption", 1),
    ("AuxBlock", []),
    ("DoAdaptive", True),
    ("Color", ["R:=", 0, "G:=", 0, "B:=", 0], None),  # TODO: create something smart for color arrays, like a class
    ("AdvancedSettings", HFSS3DLayout_AdvancedSettings),
    ("CurveApproximation", HFSS3DLayout_CurveApproximation),
    ("Q3D_DCSettings", HFSS3DLayout_Q3D_DCSettings),
    ("AdaptiveSettings", HFSS3DLayout_AdaptiveSettings),
]
"""HFSS 3D Layout setup properties and default values."""

HFSS3DLayout_SweepDataList = []
HFSS3DLayout_SIWAdvancedSettings = [
    ("IncludeCoPlaneCoupling", True),
    ("IncludeInterPlaneCoupling:=", False),
    ("IncludeSplitPlaneCoupling:=", True),
    ("IncludeFringeCoupling", True),
    ("IncludeTraceCoupling", True),
    ("XtalkThreshold", "-34"),
    ("MaxCoupledLines", 12),
    ("MinVoidArea", "2mm2"),
    ("MinPadAreaToMesh", "1mm2"),
    ("MinPlaneAreaToMesh", "6.25e-6mm2"),
    ("SnapLengthThreshold", "2.5um"),
    ("MeshAutoMatic", True),
    ("MeshFrequency", "4GHz"),
    ("ReturnCurrentDistribution", False),
    ("IncludeVISources", False),
    ("IncludeInfGnd", False),
    ("InfGndLocation", "0mm"),
    ("PerformERC", False),
    ("IgnoreNonFunctionalPads", True),
]
HFSS3DLayout_SIWDCSettings = [
    ("UseDCCustomSettings", False),
    ("PlotJV", True),
    ("ComputeInductance", False),
    ("ContactRadius", "0.1mm"),
    ("DCSliderPos", 1),
]
HFSS3DLayout_SIWDCAdvancedSettings = [
    ("DcMinPlaneAreaToMesh", "0.25mm2"),
    ("DcMinVoidAreaToMesh", "0.01mm2"),
    ("MaxInitMeshEdgeLength", "2.5mm"),
    ("PerformAdaptiveRefinement", True),
    ("MaxNumPasses", 5),
    ("MinNumPasses", 1),
    ("PercentLocalRefinement", 20),
    ("EnergyError", 2),
    ("MeshBws", True),
    ("RefineBws", False),
    ("MeshVias", True),
    ("RefineVias", False),
    ("NumBwSides", 8),
    ("NumViaSides", 8),
]
HFSS3DLayout_SIWDCIRSettings = [
    ("IcepakTempFile", "D:/Program Files/AnsysEM/AnsysEM21.2/Win64/"),
    ("SourceTermsToGround", []),
    ("ExportDCThermalData", False),
    ("ImportThermalData", False),
    ("FullDCReportPath", ""),
    ("ViaReportPath", ""),
    ("PerPinResPath", ""),
    ("DCReportConfigFile", ""),
    ("DCReportShowActiveDevices", False),
    ("PerPinUsePinFormat", False),
    ("UseLoopResForPerPin", False),
]

HFSS3DLayout_SimulationSettings = [
    ("Enabled", True),
    ("UseSISettings", True),
    ("UseCustomSettings", False),
    ("SISliderPos", 1),
    ("PISliderPos", 1),
    ("SIWAdvancedSettings", HFSS3DLayout_SIWAdvancedSettings),
    ("SIWDCSettings", HFSS3DLayout_SIWDCSettings),
    ("SIWDCAdvancedSettings", HFSS3DLayout_SIWDCAdvancedSettings),
    ("SIWDCIRSettings", HFSS3DLayout_SIWDCIRSettings),
]

HFSS3DLayout_ACSimulationSettings = [
    ("Enabled", True),
    ("UseSISettings", True),
    ("UseCustomSettings", False),
    ("SISliderPos", 1),
    ("PISliderPos", 1),
    ("SIWAdvancedSettings", HFSS3DLayout_SIWAdvancedSettings),
    ("SIWDCSettings", HFSS3DLayout_SIWDCSettings),
    ("SIWDCAdvancedSettings", HFSS3DLayout_SIWDCAdvancedSettings),
]
SiwaveDC3DLayout = [
    ("Properties", HFSS3DLayout_Properties),
    ("CustomSetup", False),
    ("SolveSetupType", "SIwave"),
    ("Color", ["R:=", 0, "G:=", 0, "B:=", 0]),
    ("Position", 0),
    ("SimSetupType", "kSIwave"),
    ("SimulationSettings", HFSS3DLayout_SimulationSettings),
    ("SweepDataList", HFSS3DLayout_SweepDataList),
]

SiwaveAC3DLayout = [
    ("Properties", HFSS3DLayout_Properties),
    ("CustomSetup", False),
    ("SolveSetupType", "SIwaveDCIR"),
    ("Position", 0),
    ("SimSetupType", "kSIwaveDCIR"),
    ("SimulationSettings", HFSS3DLayout_ACSimulationSettings),
    ("SweepDataList", HFSS3DLayout_SweepDataList),
]

HFSS3DLayout_LNASimulationSettings = [
    ("Enabled", True),
    ("GroupDelay", False),
    ("Perturbation", 0.1),
    ("Noise", False),
    ("Skip_DC", False),
    ("AdditionalOptions", ""),
    ("BaseOptionName", "(Default Options)"),
    ("FilterText", ""),
]
LNA_Sweep = [
    ("DataId", "Sweep0"),
    ("Properties", HFSS3DLayout_Properties),
    ("Sweep", SweepDefinition),
    ("SolutionID", -1),
]
HFSS3DLayout_LNAData = [("LNA Sweep 1", LNA_Sweep)]
LNA3DLayout = [
    ("Properties", HFSS3DLayout_Properties),
    ("CustomSetup", False),
    ("SolveSetupType", "LNA"),
    ("Position", 0),
    ("SimSetupType", "kLNA"),
    ("SimulationSettings", HFSS3DLayout_LNASimulationSettings),
    ("SweepDataList", HFSS3DLayout_SweepDataList),
    ("Data", HFSS3DLayout_LNAData),
]
MechTerm = [
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("Solver", "Program Controlled"),
    ("Stepping", "Program Controlled"),
]
"""Mechanical thermal setup properties and default values."""

MechModal = [
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("Max Modes", 6),
    ("Limit Search", True),
    ("Range Max", "100MHz"),
    ("Range Min", "0Hz"),
    ("Solver", "Program Controlled"),
]
"""Mechanical modal setup properties and default values."""

MechStructural = [
    ("Enabled", True),
    ("MeshLink", meshlink),
    ("Solver", "Program Controlled"),
    ("Stepping", "Program Controlled"),
]
"""Mechanical structural setup properties and default values."""

# TODO complete the list of templates for other Solvers

RmxprtDefault = [
    ("Enabled", True),
    ("OperationType", "Motor"),
    ("LoadType", "ConstPower"),
    ("RatedOutputPower", "1kW"),
    ("RatedVoltage", "100V"),
    ("RatedSpeed", "1000rpm"),
    ("OperatingTemperature", "75cel"),
]
"""RMxprt Default setup properties and default values."""

GRM = RmxprtDefault + [
    ("RatedPowerFactor", "0.8"),
    ("Frequency", "60Hz"),
    ("CapacitivePowerFactor", False),
]
"""RMxprt GRM (Generic Rotating Machine) setup properties and default values."""

DFIG = [
    ("Enabled", True),
    ("RatedOutputPower", "1kW"),
    ("RatedVoltage", "100V"),
    ("RatedSpeed", "1000rpm"),
    ("OperatingTemperature", "75cel"),
    ("OperationType", "Wind Generator"),
    ("LoadType", "InfiniteBus"),
    ("RatedPowerFactor", "0.8"),
    ("Frequency", "60Hz"),
    ("CapacitivePowerFactor", False),
]
"""RMxprt DFIG (Doubly-fed induction generator) setup properties."""

TPIM = RmxprtDefault + [("Frequency", "60Hz"), ("WindingConnection", 0)]
"""RMxprt TPIM (Three-Phase Induction Machine) setup properties."""

SPIM = RmxprtDefault + [
    ("Frequency", "60Hz"),
]
"""RMxprt SPIM (Single-Phase Induction Machine setup properties."""

TPSM = [
    ("Enabled", True),
    ("RatedOutputPower", "100"),
    ("RatedVoltage", "100V"),
    ("RatedSpeed", "1000rpm"),
    ("OperatingTemperature", "75cel"),
    ("OperationType", "Generator"),
    ("LoadType", "InfiniteBus"),
    ("RatedPowerFactor", 0.8),
    ("WindingConnection", False),
    ("ExciterEfficiency", 90),
    ("StartingFieldResistance", "0ohm"),
    ("InputExcitingCurrent", False),
    ("ExcitingCurrent", "0A"),
]
"""RMxprt TPSM=SYNM (Three-phase Synchronous Machine/Generator) setup properties."""

NSSM = TPSM  # Non-salient Synchronous Machine defaults, same as salient synch mach

ASSM = BLDC = PMDC = SRM = RmxprtDefault
# --- ALL USING RMxprt DEFAULT VALUES --- #
# ASSM = Adjustable-speed Synchronous Machine
# BLDC = Brushless DC Machine
# PMDC = Permanent Magnet DC Machine
# SRM = Switched Reluctance Machine

LSSM = RmxprtDefault + [
    ("WindingConnection", False),
]
"""RMxprt LSSM (Line-start Synchronous Machine) setup properties."""

UNIM = RmxprtDefault + [
    ("Frequency", "60Hz"),
]
"""RMxprt UNIM (Universal Machine) setup properties."""

DCM = [
    ("Enabled", True),
    ("RatedOutputPower", "1kW"),
    ("RatedVoltage", "100V"),
    ("RatedSpeed", "1000rpm"),
    ("OperatingTemperature", "75cel"),
    ("OperationType", "Generator"),
    ("LoadType", "InfiniteBus"),
    ("FieldExcitingType", False),
    ("DeterminedbyRatedSpeed", False),
    ("ExcitingVoltage", "100V"),
    ("SeriesResistance", "1ohm"),
]
"""RMxprt DCM (DC Machine/Generator) setup properties."""

CPSM = [
    ("Enabled", True),
    ("RatedOutputPower", "100"),
    ("RatedVoltage", "100V"),
    ("RatedSpeed", "1000rpm"),
    ("OperatingTemperature", "75cel"),
    ("OperationType", "Generator"),
    ("LoadType", "InfiniteBus"),
    ("RatedPowerFactor", "0.8"),
    ("InputExcitingCurrent", False),
    ("ExcitingCurrent", "0A"),
]
"""RMxprt CPSM (Claw-pole synchronous machine/generator) setup properties."""

TR = []


class SweepHFSS(object):
    """Initializes, creates, and updates sweeps in HFSS.

    Parameters
    ----------
    oanalysis :

    setupname : str
        Name of the setup.
    sweeptype : str, optional
        Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
        and ``"Discrete"``. The default is ``"Interpolating"``.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which case
        the default properties are retrieved.

    """

    def __init__(self, app, setupname, sweepname, sweeptype="Interpolating", props=None):
        self._app = app
        self.oanalysis = app.omodule
        self.props = {}
        self.setupname = setupname
        self.name = sweepname
        if props:
            self.props = props
        else:
            self.setupname = setupname
            self.name = sweepname
            self.props["Type"] = sweeptype
            self.props["IsEnabled"] = True
            self.props["RangeType"] = "LinearCount"
            self.props["RangeStart"] = "2.5GHz"
            self.props["RangeEnd"] = "7.5GHz"
            self.props["SaveSingleField"] = False
            self.props["RangeCount"] = 401
            self.props["RangeStep"] = "1MHz"
            self.props["RangeSamples"] = 11
            self.props["SaveFields"] = True
            self.props["SaveRadFields"] = True
            self.props["GenerateFieldsForAllFreqs"] = False
            self.props["InterpTolerance"] = 0.5
            self.props["InterpMaxSolns"] = 250
            self.props["InterpMinSolns"] = 0
            self.props["InterpMinSubranges"] = 1
            self.props["InterpUseS"] = True
            self.props["InterpUsePortImped"] = False
            self.props["InterpUsePropConst"] = True
            self.props["UseDerivativeConvergence"] = False
            self.props["InterpDerivTolerance"] = 0.2
            self.props["EnforcePassivity"] = True
            self.props["UseFullBasis"] = True
            self.props["PassivityErrorTolerance"] = 0.0001
            self.props["EnforceCausality"] = False
            self.props["UseQ3DForDCSolve"] = False
            self.props["SMatrixOnlySolveMode"] = "Auto"
            self.props["SMatrixOnlySolveAbove"] = "1MHz"
            self.props["SweepRanges"] = {"Subrange": []}

    @property
    def is_solved(self):
        """Verify if solutions are available for given sweep.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        sol = self._app.p_app.post.reports_by_category.standard(setup_name="{} : {}".format(self.setupname, self.name))
        return True if sol.get_solution_data() else False

    @property
    def frequencies(self):
        """Get the list of all frequencies of the active sweep.
        The project has to be saved and solved in order to see values.

        Returns
        -------
        list of float
            Frequency points.
        """
        sol = self._app.p_app.post.reports_by_category.standard(setup_name="{} : {}".format(self.setupname, self.name))
        soldata = sol.get_solution_data()
        if soldata and "Freq" in soldata.intrinsics:
            return soldata.intrinsics["Freq"]
        return []

    @property
    def basis_frequencies(self):
        """Get the list of all frequencies which have fields available.
        The project has to be saved and solved in order to see values.

        Returns
        -------
        list of float
            Frequency points.
        """
        solutions_file = os.path.join(self._app.p_app.results_directory, "{}.asol".format(self._app.p_app.design_name))
        fr = []
        if os.path.exists(solutions_file):
            solutions = load_entire_aedt_file(solutions_file)
            for k, v in solutions.items():
                if "SolutionBlock" in k and "SolutionName" in v and v["SolutionName"] == self.name and "Fields" in v:
                    try:
                        new_list = [float(i) for i in v["Fields"]["IDDblMap"][1::2]]
                        new_list.sort()
                        fr.append(new_list)
                    except (KeyError, NameError, IndexError):
                        pass

        count = 0
        for el in self._app.p_app.setups:
            if el.name == self.setupname:
                for sweep in el.sweeps:
                    if sweep.name == self.name:
                        return fr[count] if len(fr) >= count + 1 else []
            else:
                for sweep in el.sweeps:
                    if sweep.name == self.name:
                        count += 1
        return []

    @pyaedt_function_handler()
    def add_subrange(self, rangetype, start, end=None, count=None, unit="GHz", save_single_fields=False, clear=False):
        """Add a subrange to the sweep.

        Parameters
        ----------
        rangetype : str
            Type of the subrange. Options are ``"LinearCount"``,
            ``"LinearStep"``, ``"LogScale"`` and ``"SinglePoints"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency. Required for ``rangetype="LinearCount"|"LinearStep"|"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step. Required for ``rangetype="LinearCount"|"LinearStep"|"LogScale"``.
        unit : str, optional
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"GHz"``.
        save_single_fields : bool, optional
            Whether to save the fields of the single point. The default is ``False``.
            Used only for ``rangetype="SinglePoints"``.
        clear : boolean, optional
            If set to ``True``, all other subranges will be suppressed except the current one under creation.
            Default value is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        Create a setup in an HFSS design and add multiple sweep ranges.

        >>> setup = hfss.create_setup(setupname="MySetup")
        >>> sweep = setup.add_sweep()
        >>> sweep.change_type("Interpolating")
        >>> sweep.change_range("LinearStep", 1.1, 2.1, 0.4, "GHz")
        >>> sweep.add_subrange("LinearCount", 1, 1.5, 5, "MHz")
        >>> sweep.add_subrange("LogScale", 1, 3, 10, "GHz")

        """
        if rangetype == "LinearCount" or rangetype == "LinearStep" or rangetype == "LogScale":
            if not end or not count:
                raise AttributeError("Parameters 'end' and 'count' must be present.")

        if clear:
            self.props["RangeType"] = rangetype
            self.props["RangeStart"] = str(start) + unit
            if rangetype == "LinearCount":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeCount"] = count
            elif rangetype == "LinearStep":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeStep"] = str(count) + unit
            elif rangetype == "LogScale":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeSamples"] = count
            elif rangetype == "SinglePoints":
                self.props["RangeEnd"] = str(start) + unit
                self.props["SaveSingleField"] = save_single_fields
            self.props["SweepRanges"] = {"Subrange": []}
            return self.update()

        range = {}
        range["RangeType"] = rangetype
        range["RangeStart"] = str(start) + unit
        if rangetype == "LinearCount":
            range["RangeEnd"] = str(end) + unit
            range["RangeCount"] = count
        elif rangetype == "LinearStep":
            range["RangeEnd"] = str(end) + unit
            range["RangeStep"] = str(count) + unit
        elif rangetype == "LogScale":
            range["RangeEnd"] = str(end) + unit
            range["RangeCount"] = self.props["RangeCount"]
            range["RangeSamples"] = count
        elif rangetype == "SinglePoints":
            range["RangeEnd"] = str(start) + unit
            range["SaveSingleField"] = save_single_fields
        self.props["SweepRanges"]["Subrange"].append(range)

        return self.update()

    @pyaedt_function_handler()
    def create(self):
        """Create a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.oanalysis.InsertFrequencySweep(self.setupname, self._get_args())
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.oanalysis.EditFrequencySweep(self.setupname, self.name, self._get_args())
        return True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve arguments.

        Parameters
        ----------
        props :dict, optional
             Dictionary of the properties. The default is ``None``, in which
             case the default properties are retrieved.

        Returns
        -------
        dict
            Dictionary of the properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg


class SweepHFSS3DLayout(object):
    """Initializes, creates, and updates sweeps in HFSS 3D Layout.

    Parameters
    ----------
    oanaysis :

    setupname : str
        Name of the setup.
    sweepname : str
        Name of the sweep.
    sweeptype : str, optional
        Type of the sweep. Options are ``"Interpolating"`` and ``"Discrete"``. The default is ``"Interpolating"``.
    save_fields : bool, optional
        Whether to save the fields. The default is ``True``.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which
        case the default properties are retrieved.

    """

    def __init__(
        self,
        app,
        setupname,
        sweepname,
        sweeptype="Interpolating",
        save_fields=True,
        props=None,
    ):
        self._app = app
        self.oanalysis = app.omodule
        self.props = {}
        self.setupname = setupname
        self.name = sweepname
        if props:
            self.props = props
        else:
            self.setupname = setupname
            self.name = sweepname

            self.props["Properties"] = OrderedDict({"Enable": True})
            self.props["Sweeps"] = OrderedDict(
                {"Variable": "Sweep 1", "Data": "LIN 1Hz 20GHz 0.05GHz", "OffsetF1": False, "Synchronize": 0}
            )
            self.props["GenerateSurfaceCurrent"] = save_fields
            self.props["SaveRadFieldsOnly"] = False
            if sweeptype == "Interpolating":
                self.props["FastSweep"] = True
            elif sweeptype == "Discrete":
                self.props["FastSweep"] = False
            else:
                raise AttributeError("Allowed sweeptype options are 'Interpolating' and 'Discrete'.")
            # self.props["SaveSingleField"] = False
            self.props["ZoSelected"] = False
            self.props["SAbsError"] = 0.005
            self.props["ZoPercentError"] = 1
            self.props["GenerateStateSpace"] = False
            self.props["EnforcePassivity"] = False
            self.props["PassivityTolerance"] = 0.0001
            self.props["UseQ3DForDC"] = False
            self.props["ResimulateDC"] = False
            self.props["MaxSolutions"] = 250
            self.props["InterpUseSMatrix"] = True
            self.props["InterpUsePortImpedance"] = True
            self.props["InterpUsePropConst"] = True
            self.props["InterpUseFullBasis"] = True
            self.props["AdvDCExtrapolation"] = False
            self.props["MinSolvedFreq"] = "0.01GHz"
            self.props["CustomFrequencyString"] = ""
            self.props["AllEntries"] = False
            self.props["AllDiagEntries"] = False
            self.props["AllOffDiagEntries"] = False
            self.props["MagMinThreshold"] = 0.01

    @property
    def combined_name(self):
        """Compute the setupname : sweepname string.

        Returns
        -------
        str
        """
        return "{} : {}".format(self.setupname, self.name)

    @property
    def is_solved(self):
        """Verify if solutions are available for given sweep.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        sol = self._app._app.post.reports_by_category.standard(setup_name=self.combined_name)
        return True if sol.get_solution_data() else False

    @pyaedt_function_handler()
    def change_type(self, sweeptype):
        """Change the type of the sweep.

        Parameters
        ----------
        sweeptype : str
            Type of the sweep. Options are ``"Interpolating"`` and ``"Discrete"``.
            The default is ``"Interpolating"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if sweeptype == "Interpolating":
            self.props["FastSweep"] = True
        elif sweeptype == "Discrete":
            self.props["FastSweep"] = False
        else:
            raise AttributeError("Allowed sweeptype options are 'Interpolating' and 'Discrete'.")
        return self.update()

    @pyaedt_function_handler()
    def set_save_fields(self, save_fields, save_rad_fields=False):
        """Choose whether the fields are saved.

        Parameters
        ----------
        save_fields : bool
            Whether to save the fields.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.props["GenerateSurfaceCurrent"] = save_fields
        self.props["SaveRadFieldsOnly"] = save_rad_fields
        return self.update()

    @pyaedt_function_handler()
    def add_subrange(self, rangetype, start, end=None, count=None, unit="GHz"):
        """Add a subrange to the sweep.

        Parameters
        ----------
        rangetype : str
            Type of the subrange. Options are ``"LinearCount"``, ``"SinglePoint"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency.
            Mandatory for ``"LinearCount"``, ``"LinearStep"``, and ``"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step.
            Mandatory for ``"LinearCount"``, ``"LinearStep"``, and ``"LogScale"``.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"GHz"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if rangetype == "SinglePoint" and self.props["FastSweep"]:
            raise AttributeError("'SinglePoint is allowed only when sweeptype is 'Discrete'.'")
        if rangetype == "LinearCount" or rangetype == "LinearStep" or rangetype == "LogScale":
            if not end or not count:
                raise AttributeError("Parameters 'end' and 'count' must be present.")

        if rangetype == "LinearCount":
            sweep_range = " LINC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
        elif rangetype == "LinearStep":
            sweep_range = " LIN " + str(start) + unit + " " + str(end) + unit + " " + str(count) + unit
        elif rangetype == "LogScale":
            sweep_range = " DEC " + str(start) + unit + " " + str(end) + unit + " " + str(count) + unit
        elif rangetype == "SinglePoint":
            sweep_range = " " + str(start) + unit
        else:
            raise AttributeError('Allowed rangetype are "LinearCount", "SinglePoint", "LinearStep", and "LogScale".')
        self.props["Sweeps"]["Data"] += sweep_range
        return self.update()

    @pyaedt_function_handler()
    def change_range(self, rangetype, start, end=None, count=None, unit="GHz"):
        """Change the range of the sweep.

        Parameters
        ----------
        rangetype : str
            Type of the subrange. Options are ``"LinearCount"``, ``"SinglePoint"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float
            Starting frequency.
        end : float, optional
            Stopping frequency.
            Mandatory for ``"LinearCount"``, ``"LinearStep"``, and ``"LogScale"``.
        count : int or float, optional
            Frequency count or frequency step.
            Mandatory for ``"LinearCount"``, ``"LinearStep"``, and ``"LogScale"``.
        unit : str, optional
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"GHz"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if rangetype == "LinearCount":
            sweep_range = "LINC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
        elif rangetype == "LinearStep":
            sweep_range = "LIN " + str(start) + unit + " " + str(end) + unit + " " + str(count) + unit
        elif rangetype == "LogScale":
            sweep_range = "DEC " + str(start) + unit + " " + str(end) + unit + " " + str(count) + unit
        elif rangetype == "SinglePoint":
            sweep_range = str(start) + unit
        else:
            raise AttributeError('Allowed rangetype are "LinearCount", "SinglePoint", "LinearStep", and "LogScale".')
        self.props["Sweeps"]["Data"] = sweep_range
        return self.update()

    @pyaedt_function_handler()
    def create(self):
        """Create a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.oanalysis.AddSweep(self.setupname, self._get_args())
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.oanalysis.EditSweep(self.setupname, self.name, self._get_args())
        return True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve properties.

        Parameters
        ----------
        props : dict
             Dictionary of the properties. The default is ``None``, in which case
             the default properties are retrieved.

        Returns
        -------
        dict
            Dictionary of the properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg


class SweepQ3D(object):
    """Initializes, creates, and updates sweeps in Q3D.

    Parameters
    ----------
    oanaysis :

    setupname :str
        Name of the setup.
    sweepname : str
        Name of the sweep.
    sweeptype : str, optional
        Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
        and ``"Discrete"``. The default is ``"Interpolating"``.
    props : dict
        Dictionary of the properties.  The default is ``None``, in which case
        the default properties are retrieved.

    """

    def __init__(self, app, setupname, sweepname, sweeptype="Interpolating", props=None):
        self._app = app
        self.oanalysis = app.omodule
        self.setupname = setupname
        self.name = sweepname
        self.props = {}
        if props:
            self.props = props
        else:
            self.props["Type"] = sweeptype
            if sweeptype == "Discrete":
                self.props["isenabled"] = True
                self.props["RangeType"] = "LinearCount"
                self.props["RangeStart"] = "2.5GHz"
                self.props["RangeStep"] = "1GHz"
                self.props["RangeEnd"] = "7.5GHz"
                self.props["SaveSingleField"] = False

                self.props["RangeSamples"] = 3
                self.props["RangeCount"] = 401
                self.props["SaveFields"] = False
                self.props["SaveRadFields"] = False
                self.props["SweepRanges"] = []
            else:
                self.props["IsEnabled"] = True
                self.props["RangeType"] = "LinearStep"
                self.props["RangeStart"] = "1GHz"
                self.props["RangeStep"] = "1GHz"
                self.props["RangeEnd"] = "20GHz"
                self.props["SaveFields"] = False
                self.props["SaveRadFields"] = False
                self.props["InterpTolerance"] = 0.5
                self.props["InterpMaxSolns"] = 50
                self.props["InterpMinSolns"] = 0
                self.props["InterpMinSubranges"] = 1

    @property
    def is_solved(self):
        """Verify if solutions are available for given sweep.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        sol = self._app.p_app.post.reports_by_category.standard(setup_name="{} : {}".format(self.setupname, self.name))
        return True if sol.get_solution_data() else False

    @pyaedt_function_handler()
    def add_subrange(self, type, start, end=None, count=None, unit="GHz", clear=False):
        """Add a subrange to the sweep.

        Parameters
        ----------
        type : str
            Type of the subrange. Options are ``"LinearCount"``,
            ``"LinearStep"``, and ``"LogScale"``.
        start : float
            Starting frequency.
        end : float
            Stopping frequency.
        count : int or float
            Frequency count or frequency step.
        unit : str, optional
            Frequency Units.
        clear : bool, optional
            Either if the subrange has to be appended to existing ones or replace them.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if clear:
            self.props["RangeType"] = type
            self.props["RangeStart"] = str(start) + unit
            if type == "LinearCount":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeCount"] = count
            elif type == "LinearStep":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeStep"] = str(count) + unit
            elif type == "LogScale":
                self.props["RangeEnd"] = str(end) + unit
                self.props["RangeSamples"] = count
            self.props["SweepRanges"] = {"Subrange": []}
            return self.update()
        range = {}
        range["RangeType"] = type
        range["RangeStart"] = str(start) + unit
        if type == "LinearCount":
            range["RangeEnd"] = str(end) + unit
            range["RangeCount"] = count
        elif type == "LinearStep":
            range["RangeEnd"] = str(end) + unit
            range["RangeStep"] = str(count) + unit
        elif type == "LogScale":
            range["RangeEnd"] = str(end) + unit
            range["RangeCount"] = self.props["RangeCount"]
            range["RangeSamples"] = count
        if not self.props.get("SweepRanges") or not self.props["SweepRanges"].get("Subrange"):
            self.props["SweepRanges"] = {"Subrange": []}
        self.props["SweepRanges"]["Subrange"].append(range)
        return self.update()

    @pyaedt_function_handler()
    def create(self):
        """Create a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.oanalysis.InsertSweep(self.setupname, self._get_args())
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.oanalysis.EditSweep(self.setupname, self.name, self._get_args())

        return True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve properties.

        Parameters
        ----------
        props : dict
             Dictionary of the properties. The default is ``None``, in which case
             the default properties are retrieved.

        Returns
        -------
        dict
            Dictionary of the properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg


class SetupKeys(object):
    """Provides setup keys."""

    SetupTemplates = {
        0: HFSSDrivenAuto,
        1: HFSSDrivenDefault,
        2: HFSSEigen,
        3: HFSSTransient,
        4: HFSSSBR,
        5: MaxwellTransient,
        6: Magnetostatic,
        7: EddyCurrent,
        8: Electrostatic,
        9: Electrostatic,
        10: ElectricTransient,
        11: SteadyTemperatureAndFlow,
        12: SteadyTemperatureOnly,
        13: SteadyFlowOnly,
        14: Matrix,
        15: NexximLNA,
        16: NexximDC,
        17: NexximTransient,
        18: NexximQuickEye,
        19: NexximVerifEye,
        20: NexximAMI,
        21: NexximOscillatorRSF,
        22: NexximOscillator1T,
        23: NexximOscillatorNT,
        24: NexximHarmonicBalance1T,
        25: NexximHarmonicBalanceNT,
        26: NexximSystem,
        27: NexximTVNoise,
        28: HSPICE,
        29: HFSS3DLayout,
        30: Open,
        31: Close,
        32: MechTerm,
        33: MechModal,
        34: GRM,
        35: TR,
        36: TransientTemperatureAndFlow,
        37: TransientTemperatureOnly,
        38: TransientFlowOnly,
        39: MechStructural,
        40: SiwaveDC3DLayout,
        41: SiwaveAC3DLayout,
        42: LNA3DLayout,
        43: DFIG,
        44: TPIM,
        45: SPIM,
        46: TPSM,
        47: BLDC,
        48: ASSM,
        49: PMDC,
        50: SRM,
        51: LSSM,
        52: UNIM,
        53: DCM,
        54: CPSM,
        55: NSSM,
    }

    SetupNames = [
        "HFSSDrivenAuto",
        "HFSSDriven",
        "HFSSEigen",
        "HFSSTransient",
        "HFSSDriven",
        "Transient",
        "Magnetostatic",
        "EddyCurrent",
        "Electrostatic",
        "ElectroDCConduction",
        "ElectroDCConduction",
        "IcepakSteadyState",
        "IcepakSteadyState",
        "IcepakSteadyState",
        "Matrix",
        "NexximLNA",
        "NexximDC",
        "NexximTransient",
        "NexximQuickEye",
        "NexximVerifEye",
        "NexximAMI",
        "NexximOscillatorRSF",
        "NexximOscillator1T",
        "NexximOscillatorNT",
        "NexximHarmonicBalance1T",
        "NexximHarmonicBalanceNT",
        "NexximSystem",
        "NexximTVNoise",
        "HSPICE",
        "HFSS3DLayout",
        "2DMatrix",
        "2DMatrix",
        "MechThermal",
        "MechModal",
        "GRM",
        "TR",
        "IcepakTransient",
        "IcepakTransient",
        "IcepakTransient",
        "MechStructural",
        "SiwaveDC3DLayout",
        "SiwaveAC3DLayout",
        "LNA3DLayout",
        "GRM",  # DFIG
        "TPIM",
        "SPIM",
        "SYNM",  # TPSM/SYNM
        "BLDC",
        "ASSM",
        "PMDC",
        "SRM",
        "LSSM",
        "UNIM",
        "DCM",
        "CPSM",
        "NSSM",
    ]


class SetupProps(OrderedDict):
    """AEDT Boundary Component Internal Parameters."""

    def __setitem__(self, key, value):
        if isinstance(value, (dict, OrderedDict)):
            OrderedDict.__setitem__(self, key, SetupProps(self._pyaedt_setup, value))
        else:
            OrderedDict.__setitem__(self, key, value)
        if self._pyaedt_setup.auto_update:
            res = self._pyaedt_setup.update()
            if not res:
                self._pyaedt_setup._app.logger.warning("Update of %s Failed. Check needed arguments", key)

    def __init__(self, setup, props):
        OrderedDict.__init__(self)
        if props:
            for key, value in props.items():
                if isinstance(value, (dict, OrderedDict)):
                    OrderedDict.__setitem__(self, key, SetupProps(setup, value))
                else:
                    OrderedDict.__setitem__(self, key, value)
        self._pyaedt_setup = setup

    def _setitem_without_update(self, key, value):
        OrderedDict.__setitem__(self, key, value)
