class SolutionType(object):
    """Default Solution Type Name"""
    class Hfss(object):
        """ """
        (DrivenModal, DrivenTerminal, EigenMode, Transient, SBR) = (
            "DrivenModal", "DrivenTerminal", "EigenMode", "Transient Network", "SBR+")

    class Maxwell3d(object):
        """ """
        (Transient, Magnetostatic, EddyCurrent, ElectroStatic, ElectroDCConduction, ElectroDCTransient) = \
            ("Transient", "Magnetostatic", "EddyCurrent", "Electrostatic", "ElectroDCConduction",
             "ElectricTransient")

    class Maxwell2d(object):
        """ """
        (TransientXY, TransientZ, MagnetostaticXY, MagnetostaticZ, EddyCurrentXY, EddyCurrentZ, ElectroStaticXY,
         ElectroStaticZ, ElectroDCConductionX, ElectroDCConductionZ, ElectroDCTransientXY, ElectroDCTransientZ) = \
            ("TransientXY", "TransientZ", "MagnetostaticXY", "MagnetostaticZ", "EddyCurrentXY", "EddyCurrentZ",
             "ElectrostaticXY", "ElectrostaticZ", "ElectroDCConductionXY","ElectroDCConductionZ",
             "ElectricTransientXY", "ElectricTransientZ")

    class Icepak(object):
        """ """
        (SteadyTemperatureAndFlow, SteadyTemperatureOnly, SteadyFlowOnly, TransientTemperatureAndFlow,
         TransientTemperatureOnly, TransientFlowOnly,) = (
            "SteadyTemperatureAndFlow", "SteadyTemperatureOnly", "SteadyFlowOnly", "TransientTemperatureAndFlow",
            "TransientTemperatureOnly", "TransientFlowOnly")

    class Circuit(object):
        """ """
        (NexximLNA, NexximDC, NexximTransient, NexximQuickEye, NexximVerifEye, NexximAMI, NexximOscillatorRSF,
         NexximOscillator1T, NexximOscillatorNT, NexximHarmonicBalance1T, NexximHarmonicBalanceNT, NexximSystem,
         NexximTVNoise, HSPICE, TR) = ("NexximLNA", "NexximDC", "NexximTransient",
                                       "NexximQuickEye", "NexximVerifEye", "NexximAMI", "NexximOscillatorRSF",
                                       "NexximOscillator1T",
                                       "NexximOscillatorNT", "NexximHarmonicBalance1T", "NexximHarmonicBalanceNT",
                                       "NexximSystem", "NexximTVNoise", "HSPICE", "TR")

    class Mechanical(object):
        """ """
        (Thermal, Structural, Modal) = ("Thermal", "Structural", "Modal")
class SetupTypes(object):
    """Default Setup Constants"""
    (HFSSDrivenAuto, HFSSDrivenDefault, HFSSEigen, HFSSTransient, HFSSSBR, MaxwellTransient, Magnetostatic, EddyCurrent,
     Electrostatic, ElectrostaticDC, ElectricTransient, SteadyTemperatureAndFlow, SteadyTemperatureOnly, SteadyFlowOnly,
     Matrix, NexximLNA, NexximDC, NexximTransient, NexximQuickEye, NexximVerifEye, NexximAMI, NexximOscillatorRSF,
     NexximOscillator1T, NexximOscillatorNT, NexximHarmonicBalance1T, NexximHarmonicBalanceNT, NexximSystem,
     NexximTVNoise, HSPICE, HFSS3DLayout, Open, Close, MechTerm, MechModal, GRM, TR, TransientTemperatureAndFlow,
     TransientTemperatureOnly, TransientFlowOnly,) = range(0, 39)


