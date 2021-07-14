from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from ..application.DataHandlers import dict2arg
from collections import OrderedDict

meshlink = [("ImportMesh", False)]
autosweep = [("RangeType", "LinearStep"), ("RangeStart", "1GHz"), ("RangeEnd", "10GHz"), ("RangeStep", "1GHz")]
autosweeps = [("Sweep", autosweep)]
multifreq = [("1GHz", [0.02]), ("2GHz", [0.02]), ("5GHz", [0.02])]
sweepsbr = [("RangeType", "LinearStep"), ("RangeStart", "1GHz"),
            ("RangeEnd", "10GHz"), ("RangeStep", "1GHz")]
sweepssbr = [("Sweep", sweepsbr)]
muoption = [("MuNonLinearBH", True)]
transientelectrostatic = [("SaveField", True), ("Stop", "100s"), ("InitialStep", "0.01s"),
                          ("MaxStep", "5s")]
transienthfss = [("TimeProfile", "Broadband Pulse"), ("HfssFrequency", "1GHz"),
                 ("MinFreq", "100MHz"), ("MaxFreq", "1GHz"),
                 ("NumFreqsExtracted", 401), ("SweepMinFreq", "100MHz"),
                 ("SweepMaxFreq", "1GHz"), ("UseAutoTermination", 1),
                 ("SteadyStateCriteria", 0.01), ("UseMinimumDuration", 0),
                 ("TerminateOnMaximum", 0)]
HFSSDrivenAuto = [("IsEnabled", True), ("MeshLink", meshlink), ("AutoSolverSetting", "Balanced"),
                  ("Sweeps", autosweeps),
                  ("SaveRadFieldsOnly", False), ("SaveAnyFields", True), ("Type", "Discrete")]
HFSSDrivenDefault = [("AdaptMultipleFreqs", False), ("MultipleAdaptiveFreqsSetup", multifreq), ("Frequency", "5GHz"),
                     ("MaxDeltaS", 0.02), ("PortsOnly", False),
                     ("UseMatrixConv", False), ("MaximumPasses", 6), ("MinimumPasses", 1),
                     ("MinimumConvergedPasses", 1),
                     ("PercentRefinement", 30), ("IsEnabled", True), ("MeshLink", meshlink), ("BasisOrder", 1),
                     ("DoLambdaRefine", True), ("DoMaterialLambda", True), ("SetLambdaTarget", False),
                     ("Target", 0.3333),
                     ("UseMaxTetIncrease", False), ("PortAccuracy", 2), ("UseABCOnPort", False), ("SetPortMinMaxTri",
                                                                                                  False),
                     ("UseDomains", False), ("UseIterativeSolver", False), ("SaveRadFieldsOnly", False),
                     ("SaveAnyFields", True),
                     ("IESolverType", "Auto"), ("LambdaTargetForIESolver", 0.15),
                     ("UseDefaultLambdaTgtForIESolver", True),
                     ("IE Solver Accuracy", "Balanced")]
HFSSEigen = [("MinimumFrequency", "2GHz"), ("NumModes", 1), ("MaxDeltaFreq", 10), ("ConvergeOnRealFreq", False),
             ("MaximumPasses", 3), ("MinimumPasses", 1), ("MinimumConvergedPasses", 1),
             ("PercentRefinement", 30), ("IsEnabled", True), ("MeshLink", meshlink),
             ("BasisOrder", 1), ("DoLambdaRefine", True), ("DoMaterialLambda", True),
             ("SetLambdaTarget", False), ("Target", 0.2), ("UseMaxTetIncrease", False)]
HFSSTransient = [("Frequency", "5GHz"), ("MaxDeltaS", 0.02), ("MaximumPasses", 20), ("UseImplicitSolver", True),
                 ("IsEnabled", True), ("MeshLink", meshlink), ("BasisOrder", -1), ("Transient", transienthfss)]
HFSSSBR = [("IsEnabled", True), ("MeshLink", meshlink), ("IsSbrRangeDoppler", False),
           ("RayDensityPerWavelength", 4), ("MaxNumberOfBounces", 5), ("RadiationSetup", ""),
           ("PTDUTDSimulationSettings", "None"), ("Sweeps", sweepssbr), ("ComputeFarFields", False)]
MaxwellTransient = [("Enabled", True), ("MeshLink", meshlink), ("NonlinearSolverResidual", "0.005"),
                    ("ScalarPotential", "Second Order"), ("SmoothBHCurve", False), ("StopTime", "10000000ns"),
                    ("TimeStep", "2000000ns"),
                    ("OutputError", False), ("UseControlProgram", False), ("ControlProgramName", ""),
                    ("ControlProgramArg", ""), ("CallCtrlProgAfterLastStep", False),
                    ("FastReachSteadyState", False), ("AutoDetectSteadyState", False),
                    ("IsGeneralTransient", True), ("IsHalfPeriodicTransient", False),
                    ("SaveFieldsType", "None"), ("CacheSaveKind", "Count"), ("NumberSolveSteps", 1),
                    ("RangeStart", "0s"), ("RangeEnd", "0.1s")]
Magnetostatic = [("Enabled", True), ("MeshLink", meshlink), ("MaximumPasses", 10), ("MinimumPasses", 2),
                 ("MinimumConvergedPasses", 1), ("PercentRefinement", 30), ("SolveFieldOnly", False),
                 ("PercentError", 1), ("SolveMatrixAtLast", True), ("PercentError", 1),
                 ("UseIterativeSolver", False), ("RelativeResidual", 1E-06), ("NonLinearResidual", 0.001),
                 ("SmoothBHCurve", False), ("MuOption", muoption)]
Electrostatic = [("Enabled", True), ("MeshLink", meshlink), ("MaximumPasses", 10), ("MinimumPasses", 2),
                 ("MinimumConvergedPasses", 1), ("PercentRefinement", 30), ("SolveFieldOnly", False),
                 ("PercentError", 1), ("SolveMatrixAtLast", True), ("PercentError", 1),
                 ("UseIterativeSolver", False), ("RelativeResidual", 1E-06), ("NonLinearResidual", 0.001)]
EddyCurrent = [("Enabled", True), ("MeshLink", meshlink), ("MaximumPasses", 6), ("MinimumPasses", 1),
               ("MinimumConvergedPasses", 1), ("PercentRefinement", 30), ("SolveFieldOnly", False), ("PercentError", 1),
               ("SolveMatrixAtLast", True), ("PercentError", 1), ("UseIterativeSolver", False),
               ("RelativeResidual", 1E-5), ("NonLinearResidual", 0.0001), ("SmoothBHCurve", False),
               ("Frequency", "60Hz"), ("HasSweepSetup", False), ("SweepSetupType", "LinearStep"),
               ("StartValue", "1e-08GHz"), ("StopValue", "1e-06GHz"), ("StepSize", "1e-08GHz"),
               ("UseHighOrderShapeFunc", False), ("UseMuLink", False)]
ElectricTransient = [("Enabled",), ("MeshLink", meshlink), ("Tolerance", 0.005), ("ComputePowerLoss", False),
                     ("Data", transientelectrostatic),
                     ("Initial Voltage", "0mV")]
SteadyTemperatureAndFlow = [("Enabled", True), ("Flow Regime", "Laminar"), ("Include Temperature", True),
                            ("Include Flow", True), ("Include Gravity", False),
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
                            ("IsEnabled", False), ("Radiation Model", "Off"),
                            ("Under-relaxation - Pressure", "0.7"), ("Under-relaxation - Momentum", "0.3"),
                            ("Under-relaxation - Temperature", "1"),
                            ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
                            ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
                            ("Under-relaxation - Specific Dissipation Rate", "0.8"),
                            ("Discretization Scheme - Pressure", "Standard"),
                            ("Discretization Scheme - Momentum", "First"),
                            ("Discretization Scheme - Temperature", "Second"), ("Secondary Gradient", False),
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
                            ("Convergence Criteria - Max Iterations", 100)]
SteadyTemperatureOnly = [("Enabled", True), ("Flow Regime", "Laminar"), ("Include Temperature", True),
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
                         ("IsEnabled", False), ("Radiation Model", "Off"),
                         ("Under-relaxation - Pressure", "0.7"), ("Under-relaxation - Momentum", "0.3"),
                         ("Under-relaxation - Temperature", "1"),
                         ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
                         ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
                         ("Under-relaxation - Specific Dissipation Rate", "0.8"),
                         ("Discretization Scheme - Pressure", "Standard"),
                         ("Discretization Scheme - Momentum", "First"),
                         ("Discretization Scheme - Temperature", "Second"), ("Secondary Gradient", False),
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
                         ("Convergence Criteria - Max Iterations", 100)]
SteadyFlowOnly = [("Enabled", True), ("Flow Regime", "Laminar"), ("Include Flow", True), ("Include Gravity", False),
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
                  ("IsEnabled", False), ("Radiation Model", "Off"),
                  ("Under-relaxation - Pressure", "0.7"), ("Under-relaxation - Momentum", "0.3"),
                  ("Under-relaxation - Temperature", "1"), ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
                  ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
                  ("Under-relaxation - Specific Dissipation Rate", "0.8"),
                  ("Discretization Scheme - Pressure", "Standard"), ("Discretization Scheme - Momentum", "First"),
                  ("Discretization Scheme - Temperature", "First"), ("Secondary Gradient", False),
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
                  ("Convergence Criteria - Max Iterations", 100)]
Q3DCond = [("MaxPass", 10), ("MinPass", 1), ("MinConvPass", 1), ("PerError", 1), ("PerRefine", 30)]
Q3DMult = [("MaxPass", 1), ("MinPass", 1), ("MinConvPass", 1), ("PerError", 1), ("PerRefine", 30)]
Q3DDC = [("SolveResOnly", False), ("Cond", Q3DCond), ("Mult", Q3DMult)]
Q3DCap = [("MaxPass", 10), ("MinPass", 1), ("MinConvPass", 1), ("PerError", 1),
          ("PerRefine", 30), ("AutoIncreaseSolutionOrder", True), ("SolutionOrder", "High"),
          ("Solver Type", "Iterative")]
Q3DAC = [("MaxPass", 10), ("MinPass", 1), ("MinConvPass", 1), ("PerError", 1), ("PerRefine", 30)]
Matrix = [("AdaptiveFreq", "1GHz"), ("SaveFields", False), ("Enabled", True), ("Cap", Q3DCap), ("DC", Q3DDC),
          ("AC", Q3DAC)]
OutputQuantities = []
NoiseOutputQuantities = []
SweepDefinition = [("Variable", "Freq"), ("Data", "LINC 1GHz 5GHz 501"), ("OffsetF1", False),
                   ("Synchronize", 0)]
NexximLNA = [("DataBlockID", 16), ("OptionName", "(Default Options)"), ("AdditionalOptions", ""),
             ("AlterBlockName", ""), ("FilterText", ""), ("AnalysisEnabled", 1), ("OutputQuantities", OutputQuantities),
             ("NoiseOutputQuantities", NoiseOutputQuantities), ("Name", "LinearFrequency"),
             ("LinearFrequencyData", [False, 0.1, False, "", False]),
             ("SweepDefinition", SweepDefinition)]
NexximDC = [("DataBlockID", 15), ("OptionName", "(Default Options)"), ("AdditionalOptions", ""),
            ("AlterBlockName", ""), ("FilterText", ""), ("AnalysisEnabled", 1), ("OutputQuantities", OutputQuantities),
            ("NoiseOutputQuantities", NoiseOutputQuantities), ("Name", "LinearFrequency")]
NexximTransient = [("DataBlockID", 10), ("OptionName", "(Default Options)"), ("AdditionalOptions", ""),
                   ("AlterBlockName", ""), ("FilterText", ""), ("AnalysisEnabled", 1),
                   ("OutputQuantities", OutputQuantities), ("NoiseOutputQuantities", NoiseOutputQuantities),
                   ("Name", "LinearFrequency"),
                   ("TransientData", ["0.1ns", "10ns"]), ("TransientNoiseData", [False, "", "", 0, 1, 0, False, 1]),
                   ("TransientOtherData", ["default"])]
NexximQuickEye = []
NexximVerifEye = []
NexximAMI = []
NexximOscillatorRSF = []
NexximOscillator1T = []
NexximOscillatorNT = []
NexximHarmonicBalance1T = []
NexximHarmonicBalanceNT = []
NexximSystem = []
NexximTVNoise = []
HSPICE = []

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
    ("RelativeResidual", 1E-06),
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
    ("EnableDesignIntersectionCheck", True)]
HFSS3DLayout_CurveApproximation = [
    ("ArcAngle", "30deg"),
    ("StartAzimuth", "0deg"),
    ("UseError", False),
    ("Error", "0meter"),
    ("MaxPoints", 8),
    ("UnionPolys", True),
    ("Replace3DTriangles", True)]
HFSS3DLayout_Q3D_DCSettings = [
    ("SolveResOnly", True),
    ("Cond", Q3DCond),
    ("Mult", Q3DMult),
    ("Solution Order", "Normal")]
# HFSS3DLayout_AdaptiveFrequencyData = [
#     ("AdaptiveFrequency", "5GHz"),
#     ("MaxDelta", "0.02"),
#     ("MaxPasses", 10),
#     ("Expressions", [])]
CGDataBlock = [("MaxPass", 10),
               ("MinPass", 1),
               ("MinConvPass", 1),
               ("PerError", 1),
               ("PerRefine", 30),
               ("DataType", "CG"),
               ("Included", True),
               ("UseParamConv", True),
               ("UseLossyParamConv", False),
               ("PerErrorParamConv", 1),
               ("UseLossConv", True)]
RLDataBlock = [("MaxPass", 10),
               ("MinPass", 1),
               ("MinConvPass", 1),
               ("PerError", 1),
               ("PerRefine", 30),
               ("DataType", "CG"),
               ("Included", True),
               ("UseParamConv", True),
               ("UseLossyParamConv", False),
               ("PerErrorParamConv", 1),
               ("UseLossConv", True)]
Open = [("AdaptiveFreq", "1GHz"), ("SaveFields", True), ("Enabled", True), ("MeshLink", meshlink),
        ("CGDataBlock", CGDataBlock), ("RLDataBlock", RLDataBlock), ("CacheSaveKind", "Delta"), ("ConstantDelta", "0s")]

Close = [("AdaptiveFreq", "1GHz"), ("SaveFields", True), ("Enabled", True), ("MeshLink", meshlink),
         ("CGDataBlock", CGDataBlock), ("RLDataBlock", RLDataBlock), ("CacheSaveKind", "Delta"),
         ("ConstantDelta", "0s")]

TransientTemperatureAndFlow = [("Enabled", True), ("Flow Regime", "Laminar"), ("Include Temperature", True),
                               ("Include Flow", True), ("Include Gravity", False), ("Include Solar", False),
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
                               ("Convergence Criteria - Discrete Ordinates", "1e-06"), ("IsEnabled:=", False),
                               ("Radiation Model", "Off"),
                               ("Solar Radiation Model", "Solar Radiation Calculator"),
                               ("Solar Radiation - Scattering Fraction", "0"),
                               ("Solar Radiation - Day", 1), ("Solar Radiation - Month", 1),
                               ("Solar Radiation - Hours", 0),
                               ("Solar Radiation - Minutes", 0), ("Solar Radiation - GMT", "0"),
                               ("Solar Radiation - Latitude", "0"),
                               ("Solar Radiation - Latitude Direction", "East"), ("Solar Radiation - Longitude", "0"),
                               ("Solar Radiation - Longitude Direction", "North"),
                               ("Solar Radiation - Ground Reflectance", "0"),
                               ("Solar Radiation - Sunshine Fraction", "0"), ("Solar Radiation - North X", "0"),
                               ("Solar Radiation - North Y", "0"), ("Solar Radiation - North Z", "1"),
                               ("Under-relaxation - Pressure", "0.3"),
                               ("Under-relaxation - Momentum", "0.7"), ("Under-relaxation - Temperature", "1"),
                               ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
                               ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
                               ("Under-relaxation - Specific Dissipation Rate", "0.8"),
                               ("Discretization Scheme - Pressure", "Standard"),
                               ("Discretization Scheme - Momentum", "First"),
                               ("Discretization Scheme - Temperature", "First"), ("Secondary Gradient", False),
                               ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
                               ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
                               ("Discretization Scheme - Specific Dissipation Rate", "First"),
                               ("Discretization Scheme - Discrete Ordinates", "First"),
                               ("Linear Solver Type - Pressure", "V"), ("Linear Solver Type - Momentum", "flex"),
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
                               ("Frozen Flow Simulation", False), ("Start Time:=", "0s"), ("Stop Time:=", "20s"),
                               ("Time Step:=", "1s"), ("Iterations per Time Step", 20), ("Import Start Time", False),
                               ("Copy Fields From Source", False), ("SaveFieldsType", "Every N Steps"),
                               ("N Steps:=", "10s"), ("Enable Control Program", False), ("Control Program Name", "")]

TransientTemperatureOnly = [("Enabled", True), ("Flow Regime", "Laminar"), ("Include Temperature", True),
                            ("Include Flow", False), ("Include Gravity", False), ("Include Solar", False),
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
                            ("Convergence Criteria - Discrete Ordinates", "1e-06"), ("IsEnabled:=", False),
                            ("Radiation Model", "Off"),
                            ("Solar Radiation Model", "Solar Radiation Calculator"),
                            ("Solar Radiation - Scattering Fraction", "0"),
                            ("Solar Radiation - Day", 1), ("Solar Radiation - Month", 1),
                            ("Solar Radiation - Hours", 0),
                            ("Solar Radiation - Minutes", 0), ("Solar Radiation - GMT", "0"),
                            ("Solar Radiation - Latitude", "0"),
                            ("Solar Radiation - Latitude Direction", "East"), ("Solar Radiation - Longitude", "0"),
                            ("Solar Radiation - Longitude Direction", "North"),
                            ("Solar Radiation - Ground Reflectance", "0"),
                            ("Solar Radiation - Sunshine Fraction", "0"), ("Solar Radiation - North X", "0"),
                            ("Solar Radiation - North Y", "0"), ("Solar Radiation - North Z", "1"),
                            ("Under-relaxation - Pressure", "0.3"),
                            ("Under-relaxation - Momentum", "0.7"), ("Under-relaxation - Temperature", "1"),
                            ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
                            ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
                            ("Under-relaxation - Specific Dissipation Rate", "0.8"),
                            ("Discretization Scheme - Pressure", "Standard"),
                            ("Discretization Scheme - Momentum", "First"),
                            ("Discretization Scheme - Temperature", "First"), ("Secondary Gradient", False),
                            ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
                            ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
                            ("Discretization Scheme - Specific Dissipation Rate", "First"),
                            ("Discretization Scheme - Discrete Ordinates", "First"),
                            ("Linear Solver Type - Pressure", "V"), ("Linear Solver Type - Momentum", "flex"),
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
                            ("Frozen Flow Simulation", False), ("Start Time:=", "0s"), ("Stop Time:=", "20s"),
                            ("Time Step:=", "1s"), ("Iterations per Time Step", 20), ("Import Start Time", False),
                            ("Copy Fields From Source", False), ("SaveFieldsType", "Every N Steps"),
                            ("N Steps:=", "10s"), ("Enable Control Program", False), ("Control Program Name", "")]

TransientFlowOnly = [("Enabled", True), ("Flow Regime", "Laminar"), ("Include Temperature", False),
                     ("Include Flow", True), ("Include Gravity", False), ("Include Solar", False),
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
                     ("Convergence Criteria - Discrete Ordinates", "1e-06"), ("IsEnabled:=", False),
                     ("Radiation Model", "Off"),
                     ("Solar Radiation Model", "Solar Radiation Calculator"),
                     ("Solar Radiation - Scattering Fraction", "0"),
                     ("Solar Radiation - Day", 1), ("Solar Radiation - Month", 1),
                     ("Solar Radiation - Hours", 0),
                     ("Solar Radiation - Minutes", 0), ("Solar Radiation - GMT", "0"),
                     ("Solar Radiation - Latitude", "0"),
                     ("Solar Radiation - Latitude Direction", "East"), ("Solar Radiation - Longitude", "0"),
                     ("Solar Radiation - Longitude Direction", "North"),
                     ("Solar Radiation - Ground Reflectance", "0"),
                     ("Solar Radiation - Sunshine Fraction", "0"), ("Solar Radiation - North X", "0"),
                     ("Solar Radiation - North Y", "0"), ("Solar Radiation - North Z", "1"),
                     ("Under-relaxation - Pressure", "0.3"),
                     ("Under-relaxation - Momentum", "0.7"), ("Under-relaxation - Temperature", "1"),
                     ("Under-relaxation - Turbulent Kinetic Energy", "0.8"),
                     ("Under-relaxation - Turbulent Dissipation Rate", "0.8"),
                     ("Under-relaxation - Specific Dissipation Rate", "0.8"),
                     ("Discretization Scheme - Pressure", "Standard"),
                     ("Discretization Scheme - Momentum", "First"),
                     ("Discretization Scheme - Temperature", "First"), ("Secondary Gradient", False),
                     ("Discretization Scheme - Turbulent Kinetic Energy", "First"),
                     ("Discretization Scheme - Turbulent Dissipation Rate", "First"),
                     ("Discretization Scheme - Specific Dissipation Rate", "First"),
                     ("Discretization Scheme - Discrete Ordinates", "First"),
                     ("Linear Solver Type - Pressure", "V"), ("Linear Solver Type - Momentum", "flex"),
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
                     ("Frozen Flow Simulation", False), ("Start Time:=", "0s"), ("Stop Time:=", "20s"),
                     ("Time Step:=", "1s"), ("Iterations per Time Step", 20), ("Import Start Time", False),
                     ("Copy Fields From Source", False), ("SaveFieldsType", "Every N Steps"),
                     ("N Steps:=", "10s"), ("Enable Control Program", False), ("Control Program Name", "")]


def HFSS3DLayout_AdaptiveFrequencyData(freq):
    """Update HFSS 3D adaptive frequency data.

    Parameters
    ----------
    freq : float
        Value for adaptive frequency.
        

    Returns
    -------
    list
        Frequency parameters.

    """
    value = [
        ("AdaptiveFrequency", freq),
        ("MaxDelta", "0.02"),
        ("MaxPasses", 10),
        ("Expressions", [], None)]
    return value


HFSS3DLayout_SingleFrequencyDataList = [
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("5GHz"))]
HFSS3DLayout_BroadbandFrequencyDataList = [
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("5GHz")),
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("10GHz"))]
HFSS3DLayout_MultiFrequencyDataList = [
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("2.5GHz")),
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("5GHz")),
    ("AdaptiveFrequencyData", HFSS3DLayout_AdaptiveFrequencyData("10GHz"))]
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
    ("MultiFrequencyDataList", HFSS3DLayout_MultiFrequencyDataList)]
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
    ("DefeatureRatio", 1E-06),
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
    ("SmallVoidArea", -2E-09),
    ("HealingOption", 1),
    ("InclBBoxOption", 1),
    ("AuxBlock", []),
    ("DoAdaptive", True),
    ("Color", ["R:=", 0, "G:=", 0, "B:=", 0], None),  # TODO: create something smart for color arrays, like a class
    ("AdvancedSettings", HFSS3DLayout_AdvancedSettings),
    ("CurveApproximation", HFSS3DLayout_CurveApproximation),
    ("Q3D_DCSettings", HFSS3DLayout_Q3D_DCSettings),
    ("AdaptiveSettings", HFSS3DLayout_AdaptiveSettings)]

MechTerm = [("Enabled", True), ("MeshLink", meshlink),
            ("Solver", "Program Controlled"), ("Stepping", "Program Controlled")]
MechModal = [("Enabled", True), ("MeshLink", meshlink),
             ("Max Modes", 6), ("Limit Search", True), ("Range Max", "100MHz"), ("Range Min", "0Hz"),
             ("Solver", "Program Controlled")]

MechStructural = [("Enabled", True), ("MeshLink", meshlink), ("Solver", "Program Controlled"),
                  ("Stepping", "Program Controlled")]

# TODO complete the list of templates for other Solvers

GRM = [("Enabled", True), ("MeshLink", meshlink),
       ("RatedOutputPower", "1W"), ("RatedVoltage", "208V"), ("RatedSpeed", "3600rpm"),
       ("OperatingTemperature", "75cel"),
       ("OperationType", "Motor"), ("LoadType", "ConstPower"), ("RatedPowerFactor", "0.8"), ("Frequency", "60Hz"),
       ("CapacitivePowerFactor", False)]

TR = []


class SweepHFSS(object):
    """SweepHFSS class.
    
    Parameters
    ----------
    oanalysis :
    
    setupname : str
        Name of the setup.
    sweeptype : str, optional
        Type of the sweep. The default is ``"Interpolating"``.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which case
        the default properties are retrieved.
    
    """

    def __init__(self, oanalysis, setupname, sweepname, sweeptype="Interpolating", props=None):
        self.oanalysis = oanalysis
        self.props = {}
        self.setupname = setupname
        self.name = sweepname
        if props:
            self.props = props
        else:
            self.setupname = setupname
            self.name = sweepname
            self.props["Type"] = sweeptype
            self.props["isenabled"] = True
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
            self.props["SweepRanges"] = []

    @aedt_exception_handler
    def add_subrange(self, rangetype, start, end, count):
        """Add a subrange to the sweep.

        Parameters
        ----------
        rangetype :
            Type of subrange.
        start : float
            Starting frequency.
        end : float
            Stopping frequency.
        count : int or float
            Frequency count or frequency step.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        range = {}
        range["RangeType"] = rangetype
        range["RangeStart"] = start
        range["RangeEnd"] = end
        if rangetype == "LinearCount":
            range["RangeCount"] = count
        elif rangetype == "LinearStep":
            range["RangeStep"] = count
        elif rangetype == "LogScale":
            range["RangeCount"] = self.props["RangeCount"]
            range["RangeSamples"] = count
        elif rangetype == "SinglePoints":
            range["SaveSingleField"] = False
        self.props["SweepRanges"].append(range)

    @aedt_exception_handler
    def create(self):
        """Create a sweep.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        self.oanalysis.InsertFrequencySweep(self.setupname, self._get_args())
        return True

    @aedt_exception_handler
    def update(self):
        """Update a sweep.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        self.oanalysis.EditFrequencySweep(self.setupname, self.name, self._get_args())
        return True

    @aedt_exception_handler
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
        dict2arg(props, arg)
        return arg


class SweepHFSS3DLayout(object):
    """SweepHFSS3DLayout class.

    Parameters
    ----------
    oanaysis :
    
    setupname : str
        Name of the setup.
    sweepname : str
        Name of the sweep.
    sweeptype : str, optional
        Type of the sweep. The default is ``"Interpolating"``.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which
        case the default properties are retrieved.
    
    """
    def __init__(self, oanalysis, setupname, sweepname, sweeptype="Interpolating", props=None):
        self.oanalysis = oanalysis
        self.props = {}
        self.setupname = setupname
        self.name = sweepname
        if props:
            self.props = props
        else:
            self.setupname = setupname
            self.name = sweepname

            self.props["Properties"] = OrderedDict({"Enable":True})
            self.props["Sweeps"] = OrderedDict(
                {"Variable": "Sweep 1", "Data": "LIN 1Hz 20GHz 0.05GHz", "OffsetF1": False, "Synchronize": 0})
            self.props["GenerateSurfaceCurrent"] = False
            self.props["SaveRadFieldsOnly"] = False
            if sweeptype == "Interpolating":
                self.props["FastSweep"] = True
            else:
                self.props["FastSweep"] = True

            self.props["SaveSingleField"] = False
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


    @aedt_exception_handler
    def add_subrange(self, rangetype, start, end, count):
        """Add a subrange to the sweep.

        Parameters
        ----------
        rangetype : str
            Type of the subrange. Options are:
            
            * ``"LinearCount"``
            * ``"LinearStep"``
            * ``"LogScale"``
            
        start : float
            Starting frequency.
        end : float
            Stopping frequency.
        count :
            Frequency count or frequency step.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        range = ""
        if rangetype == "LinearCount":
            range = " LINC "+str(start)+" "+str(end) + " "+str(count)
        elif rangetype == "LinearStep":
            range = " LIN "+str(start)+" "+str(end) + " "+str(count)
        elif rangetype == "LogScale":
            range = " DEC "+str(start)+" "+str(end) + " "+str(count)
        self.props["Sweeps"]["Data"] += range
        return self.update()

    @aedt_exception_handler
    def change_range(self, rangetype, start, end, count):
        """Update the range of the sweep.

        Parameters
        ----------
        rangetype : str
            Type of the subrange. Options are:
            
            * ``"LinearCount"``
            * ``"LinearStep"``
            * ``"LogScale"``
            
        start : float
            Starting frequency.
        end : float
            Stopping frequency.
        count :
            Frequency count or frequency step.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        range = ""
        if rangetype == "LinearCount":
            range = "LINC "+str(start)+" "+str(end) + " "+str(count)
        elif rangetype == "LinearStep":
            range = "LIN "+str(start)+" "+str(end) + " "+str(count)
        elif rangetype == "LogScale":
            range = "DEC "+str(start)+" "+str(end) + " "+str(count)
        self.props["Sweeps"]["Data"] = range
        return self.update()

    @aedt_exception_handler
    def create(self):
        """Create a sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        self.oanalysis.AddSweep(self.setupname, self._get_args())
        return True

    @aedt_exception_handler
    def update(self):
        """Update the sweep.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        self.oanalysis.EditSweep(self.setupname, self.name, self._get_args())
        return True

    @aedt_exception_handler
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
        dict2arg(props, arg)
        return arg


class SweepQ3D(object):
    """SweepQ3D class.

    Parameters
    ----------
    oanaysis :
    
    setupname :str
        Name of the setup.
    sweepname: str
        Name of the sweep.
    sweeptype : str, optional
        Type of the sweep. The default is ``"Interpolating"``.
    props : dict
        Dictionary of the properties.  The default is ``None``, in which case
        the default properties are retrieved.
        
    """
    def __init__(self, oanalysis, setupname, sweepname, sweeptype="Interpolating", props=None):
        self.oanalysis = oanalysis
        self.setupname = setupname
        self.name = sweepname
        self.props = {}
        if props:
            self.props = props
        else:
            self.props["Type"] = sweeptype
            self.props["isenabled"] = True
            self.props["RangeType"] = "LinearCount"
            self.props["RangeStart"] = "2.5GHz"
            self.props["RangeStep"] = "1GHz"
            self.props["RangeEnd"] = "7.5GHz"
            self.props["SaveSingleField"] = False

            self.props["RangeSamples"] = 3
            self.props["RangeCount"] = 401
            self.props["SaveFields"] = True
            self.props["SaveRadFields"] = True
            self.props["SweepRanges"] = []

    @aedt_exception_handler
    def add_subrange(self, type, start, end, count):
        """Add a subrange to the sweep.

        Parameters
        ----------
        type :
            Type of the subrange. Options are:
            
            * ``"LinearCount"``
            * ``"LinearStep"``
            * ``"LogScale"``
            
        start : float
            Starting frequency.
        end : float
            Stopping frequency.
        count :
            Frequency count or frequency step.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
            
        """
        range = {}
        range["RangeType"] = type
        range["RangeStart"] = start
        range["RangeEnd"] = end
        if type == "LinearCount":
            range["RangeCount"] = count
        elif type == "LinearStep":
            range["RangeStep"] = count
        elif type == "LogScale":
            range["RangeCount"] = self.props["RangeCount"]
            range["RangeSamples"] = count
        self.props["SweepRanges"].append(range)
        return True

    @aedt_exception_handler
    def create(self):
        """Create a sweep.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """
        self.oanalysis.InsertSweep(self.setupname, self._get_args())
        return True

    @aedt_exception_handler
    def update(self):
        """Update the sweep.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """
        self.oanalysis.EditSweep(self.setupname, self.name, self._get_args())

        return True

    @aedt_exception_handler
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
        dict2arg(props, arg)
        return arg


class SetupKeys(object):
    """SetupKeys class."""
    defaultSetups = {"DrivenModal": 1, "DrivenTerminal": 1, "Eigenmode": 2,
                     "Transient Network": 3, "SBR+": 4, "Transient": 5, "Magnetostatic": 6, "EddyCurrent": 7,
                     "Electrostatic": 8, "ElectroDCConduction": 9,
                     "ElectricTransient": 10, "SteadyTemperatureAndFlow": 11, "SteadyTemperatureOnly": 12,
                     "SteadyFlowOnly": 13,
                     "SteadyState": 11,
                     "Matrix": 14, "NexximLNA": 15, "NexximDC": 16, "NexximTransient": 17, "NexximQuickEye": 18,
                     "NexximVerifEye": 19, "NexximAMI": 20, "NexximOscillatorRSF": 21, "NexximOscillator1T": 22,
                     "NexximOscillatorNT": 23, "NexximHarmonicBalance1T": 24, "NexximHarmonicBalanceNT": 25,
                     "NexximSystem": 26, "NexximTVNoise": 27, "HSPICE": 28, "HFSS3DLayout": 29, "Open": 30, "Close": 31,
                     "Thermal": 32, "Modal": 33, "IRIM": 34, "ORIM": 34, "SRIM": 34, "WRIM": 34,
                     "DFIG": 34, "AFIM": 34, "HM": 34, "RFSM": 34, "RASM": 34, "RSM": 34,
                     "ISM": 34, "APSM": 34, "IBDM": 34,
                     "ABDM": 34, "TPIM": 34, "SPIM": 34, "TPSM": 34, "BLDC": 34, "ASSM": 34,
                     "PMDC": 34, "SRM": 34, "LSSM": 34, "UNIM": 34, "DCM": 34, "CPSM": 34, "NSSM": 34, "TR": 35,
                     "TransientTemperatureAndFlow": 36, "TransientTemperatureOnly": 37, "TransientFlowOnly": 38,
                     "Structural": 39}

    SetupTemplates = {0: HFSSDrivenAuto, 1: HFSSDrivenDefault, 2: HFSSEigen, 3: HFSSTransient, 4: HFSSSBR,
                      5: MaxwellTransient, 6: Magnetostatic, 7: EddyCurrent, 8: Electrostatic, 9: Electrostatic,
                      10: ElectricTransient, 11: SteadyTemperatureAndFlow, 12: SteadyTemperatureOnly,
                      13: SteadyFlowOnly, 14: Matrix, 15: NexximLNA, 16: NexximDC, 17: NexximTransient,
                      18: NexximQuickEye,
                      19: NexximVerifEye, 20: NexximAMI, 21: NexximOscillatorRSF, 22: NexximOscillator1T,
                      23: NexximOscillatorNT, 24: NexximHarmonicBalance1T, 25: NexximHarmonicBalanceNT,
                      26: NexximSystem, 27: NexximTVNoise, 28: HSPICE, 29: HFSS3DLayout, 30: Open, 31: Close,
                      32: MechTerm, 33: MechModal, 34: GRM, 35: TR, 36: TransientTemperatureAndFlow,
                      37: TransientTemperatureOnly, 38: TransientFlowOnly, 39: MechStructural}

    SetupNames = ["HFSSDrivenAuto", "HFSSDriven", "HFSSEigen", "HFSSTransient", "HFSSDriven",
                  "Transient", "Magnetostatic", "EddyCurrent", "Electrostatic", "ElectroDCConduction",
                  "ElectroDCConduction", "IcepakSteadyState", "IcepakSteadyState",
                  "IcepakSteadyState", "Matrix", "NexximLNA", "NexximDC", "NexximTransient", "NexximQuickEye",
                  "NexximVerifEye", "NexximAMI", "NexximOscillatorRSF", "NexximOscillator1T",
                  "NexximOscillatorNT", "NexximHarmonicBalance1T", "NexximHarmonicBalanceNT",
                  "NexximSystem", "NexximTVNoise", "HSPICE", "HFSS3DLayout", "2DMatrix", "2DMatrix", "MechThermal",
                  "MechModal", "GRM", "TR", "IcepakTransient", "IcepakTransient", "IcepakTransient", "MechStructural"]

    defaultAdaptive = {"DrivenModal": "LastAdaptive", "DrivenTerminal": "LastAdaptive", "Eigenmode": "LastAdaptive",
                       "Transient Network": "Transient", "SBR+": None, "Transient": "Transient",
                       "Magnetostatic": "LastAdaptive", "EddyCurrent": "LastAdaptive",
                       "Electrostatic": "LastAdaptive", "ElectroDCConduction": "LastAdaptive",
                       "ElectricTransient": "Transient", "SteadyTemperatureAndFlow": "SteadyState",
                       "SteadyTemperatureOnly": "SteadyState", "SteadyFlowOnly": "SteadyState",
                       "SteadyState": "SteadyState",
                       "Matrix": "LastAdaptive", "NexximLNA": None, "NexximDC": None, "NexximTransient": None,
                       "NexximQuickEye": None,
                       "NexximVerifEye": None, "NexximAMI": None, "NexximOscillatorRSF": None,
                       "NexximOscillator1T": None,
                       "NexximOscillatorNT": None, "NexximHarmonicBalance1T": None, "NexximHarmonicBalanceNT": None,
                       "NexximSystem": None, "NexximTVNoise": None, "HSPICE": None, "HFSS3DLayout": None,
                       "2DMatrix": "LastAdaptive", "MechThermal": "Solution", "MechModal": "Solution",
                       "GRM": "LastAdaptive", "TR": None, "TransientTemperatureAndFlow": "SteadyState",
                       "TransientTemperatureOnly": "Transient", "TransientFlowOnly": "Transient",
                       "Structural": "Solution"}
