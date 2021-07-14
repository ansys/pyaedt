class SolutionType(object):
    """SolutionType class.
    
    The class provides the name of the default solution type.
    """
    class Hfss(object):
        """Hfss class."""
        (DrivenModal, DrivenTerminal, EigenMode, Transient, SBR) = (
            "DrivenModal", "DrivenTerminal", "EigenMode", "Transient Network", "SBR+")

    class Maxwell3d(object):
        """Maxwell3d class."""
        (Transient, Magnetostatic, EddyCurrent, ElectroStatic, ElectroDCConduction, ElectroDCTransient) = \
            ("Transient", "Magnetostatic", "EddyCurrent", "Electrostatic", "ElectroDCConduction",
             "ElectricTransient")

    class Maxwell2d(object):
        """Maxwell 2D class."""
        (TransientXY, TransientZ, MagnetostaticXY, MagnetostaticZ, EddyCurrentXY, EddyCurrentZ, ElectroStaticXY,
         ElectroStaticZ, ElectroDCConductionX, ElectroDCConductionZ, ElectroDCTransientXY, ElectroDCTransientZ) = \
            ("TransientXY", "TransientZ", "MagnetostaticXY", "MagnetostaticZ", "EddyCurrentXY", "EddyCurrentZ",
             "ElectrostaticXY", "ElectrostaticZ", "ElectroDCConductionXY","ElectroDCConductionZ",
             "ElectricTransientXY", "ElectricTransientZ")

    class Icepak(object):
        """Icepak class."""
        (SteadyTemperatureAndFlow, SteadyTemperatureOnly, SteadyFlowOnly, TransientTemperatureAndFlow,
         TransientTemperatureOnly, TransientFlowOnly,) = (
            "SteadyTemperatureAndFlow", "SteadyTemperatureOnly", "SteadyFlowOnly", "TransientTemperatureAndFlow",
            "TransientTemperatureOnly", "TransientFlowOnly")

    class Circuit(object):
        """Circuit class."""
        (NexximLNA, NexximDC, NexximTransient, NexximQuickEye, NexximVerifEye, NexximAMI, NexximOscillatorRSF,
         NexximOscillator1T, NexximOscillatorNT, NexximHarmonicBalance1T, NexximHarmonicBalanceNT, NexximSystem,
         NexximTVNoise, HSPICE, TR) = ("NexximLNA", "NexximDC", "NexximTransient",
                                       "NexximQuickEye", "NexximVerifEye", "NexximAMI", "NexximOscillatorRSF",
                                       "NexximOscillator1T",
                                       "NexximOscillatorNT", "NexximHarmonicBalance1T", "NexximHarmonicBalanceNT",
                                       "NexximSystem", "NexximTVNoise", "HSPICE", "TR")

    class Mechanical(object):
        """Mechanical class."""
        (Thermal, Structural, Modal) = ("Thermal", "Structural", "Modal")
class SetupTypes(object):
    """SetupTypes class.
     This class provides constants for the default setup types."""
    (HFSSDrivenAuto, HFSSDrivenDefault, HFSSEigen, HFSSTransient, HFSSSBR, MaxwellTransient, Magnetostatic, EddyCurrent,
     Electrostatic, ElectrostaticDC, ElectricTransient, SteadyTemperatureAndFlow, SteadyTemperatureOnly, SteadyFlowOnly,
     Matrix, NexximLNA, NexximDC, NexximTransient, NexximQuickEye, NexximVerifEye, NexximAMI, NexximOscillatorRSF,
     NexximOscillator1T, NexximOscillatorNT, NexximHarmonicBalance1T, NexximHarmonicBalanceNT, NexximSystem,
     NexximTVNoise, HSPICE, HFSS3DLayout, Open, Close, MechTerm, MechModal, GRM, TR, TransientTemperatureAndFlow,
     TransientTemperatureOnly, TransientFlowOnly,) = range(0, 39)


