
# ////////////////////////////////////////////////////////////////

class kSIwaveProperties(object):
    """ """
    # General attributes ----------------------------------------
    PIN_GROUP = 1
    PART_NAME = 2
    REF_DES_NAME = 3
    PIN_NAME = 4
    INTER_COMPONENT_PIN_GROUP = 5

    # DC IR simulation attributes -------------------------------
    DCIR_SIM_NAME = 100
    DCIR_INIT_MESH_MAX_EDGE_LEN = 101
    DCIR_MESH_BWS = 102
    DCIR_MESH_VIAS = 103
    DCIR_NUM_BW_FACETS = 104
    DCIR_NUM_VIA_FACETS = 105
    DCIR_ADAPTIVE_SOLVE = 106
    DCIR_MIN_NUM_PASSES = 107
    DCIR_MAX_NUM_PASSES = 108
    DCIR_LOCAL_REFINEMENT = 109
    DCIR_ENERGY_ERROR = 110
    DCIR_REFINE_BWS = 111
    DCIR_REFINE_VIAS = 112
    DCIR_PLOT_JV = 113
    DCIR_CKT_ELEM_CONTACT_R = 114
    DCIR_ICEPAK_TEMP_FILE_PATH = 115
    SOURCE_NEG_TERMINALS_TO_GROUND = 116
    SOURCE_POS_TERMINALS_TO_GROUND = 117
    DCIR_MIN_DC_PLANE_AREA_TO_MESH = 118
    DCIR_MIN_DC_VOID_AREA_TO_MESH = 119
    DCIR_COMPUTE_L = 120

    # General simulation attributes -------------------------------
    NUM_CPUS_TO_USE = 200
    USE_HPC_LICENSE = 201

    # SYZ simulation attributes -------------------------------
    SYZ_COUPLING_COPLANE = 300
    SYZ_COUPLING_INTRA_PLANE = 301
    SYZ_COUPLING_SPLIT_PLANE = 302
    SYZ_COUPLING_CAVITY = 303
    SYZ_COUPLING_TRACE = 304
    SYZ_COUPLING_XTALK_THRESH = 305
    SYZ_MIN_VOID_MESH = 306
    SYZ_MESH_REFINEMENT = 307
    SYZ_TRACE_RETURN_CURRENT = 308
    SYZ_INCLUDE_SOURCE_PARASITICS = 309
    SYZ_USE_INF_GROUND_PLANE = 310
    SYZ_INF_GROUND_PLANE_DIST = 311
    SYZ_PERFORM_ERC = 312
    SYZ_EXCLUDE_NON_FUNCTIONAL_PADS = 313

    # Icepak simulation attributes -------------------------------

    ICEPAK_SIM_NAME = 400
    ICEPAK_DC_SIM_NAME = 401
    ICEPAK_MESH_FIDELITY = 402
    ICEPAK_CAB_ABOVE_PERCENT = 403
    ICEPAK_CAB_BELOW_PERCENT = 404
    ICEPAK_CAB_HORIZ_PERCENT = 405
    ICEPAK_FLOW_STYLE = 406

    ICEPAK_FLOW_SPEED = 407
    ICEPAK_FLOW_DIR = 408
    ICEPAK_FLOW_TEMP = 409

    ICEPAK_COND_FLOW_SPEED_TOP = 410
    ICEPAK_COND_FLOW_SPEED_BOTTOM = 411
    ICEPAK_COND_FLOW_DIR_TOP = 412
    ICEPAK_COND_FLOW_DIR_BOTTOM = 413
    ICEPAK_COND_TEMP_TOP = 414
    ICEPAK_COND_TEMP_BOTTOM = 415

    ICEPAK_GRAV_X = 416
    ICEPAK_GRAV_Y = 417
    ICEPAK_GRAV_Z = 418
    ICEPAK_AMBIENT_TEMP = 419

    ICEPAK_COMPONENT_FILE = 420
    ICEPAK_BRD_OUTLINE_FIDELITY_MM = 421
    ICEPAK_USE_MINIMAL_COMP_DEFAULTS = 422

    # PSI simulation attributes -------------------------------

    PSI_AC_SIM_NAME = 500
    PSI_AC_SWEEP_STR = 501

    PSI_SYZ_SIM_NAME = 502
    PSI_SYZ_SWEEP_STR = 503
    PSI_SYZ_INTERPOLATING = 504
    PSI_SYZ_FAST_SWP = 505
    PSI_SYZ_ADAPTIVE_SAMPLING = 506
    PSI_SYZ_ENFORCE_DC = 507
    PSI_SYZ_PORT_TYPE = 508

    PSI_DISTRIBUTED = 509
    PSI_NUM_CPUS = 510
    PSI_USE_HPC = 511
    PSI_HPC_LICENSE_TYPE = 512
    PSI_SIM_SERVER_NAME = 513
    PSI_SIM_SERVER_PORT = 514
    PSI_SIMULATION_PREFERENCE = 515
    PSI_MODEL_TYPE = 516
    PSI_ENHANCED_BW_MODELING = 517
    PSI_SURFACE_ROUGHNESS_MODEL = 518
    PSI_RMS_ROUGHNESS = 519
    PSI_TEMP_WORKING_DIR = 520
    PSI_IGNORE_DUMMY_NETS = 521
    PSI_PERFORM_ERC = 522
    PSI_EXCLUDE_NONFUNCTIONAL_PADS = 523
    PSI_AUTO_NET_SELECT = 524
    PSI_IMPROVED_LOW_FREQ_RESIST = 525
    PSI_SMALL_HOLE_SIZE = 526
    PSI_SIGNAL_NET_ERROR_TOL = 527
    PSI_CONDUCTOR_MODELING = 528
    PSI_IMPROVED_METAL_LOSS = 529
    PSI_IMPROVED_DIELECTRIC_FILL = 530
    PSI_TOP_FILL_MATERIAL = 531
    PSI_BOTTOM_FILL_MATERIAL = 532
    PSI_PCB_MATERIAL = 533
    PSI_INCLUDE_METAL_PLANE1 = 534
    PSI_INCLUDE_METAL_PLANE2 = 535
    PSI_FLOAT_METAL_PLANE1 = 536
    PSI_FLOAT_METAL_PLANE2 = 537
    PSI_H1 = 538
    PSI_H2 = 539

    # CPA simulation attributes -------------------------------

    CPA_SIM_NAME = 600
    CPA_CHANNEL_SETUP = 601  # channel = 1, individual source/sink = 0
    CPA_ESD_R_MODEL = 602  # ESD R model = 1, RLCG model = 0
    CPA_USE_Q3D_SOLVER = 603
    CPA_NET_PROCESSING_MODE = 604
    CPA_NETS_TO_PROCESS = 605
    CPA_CHANNEL_DIE_NAME = 610
    CPA_CHANNEL_PIN_GROUPING_MODE = 611  # per-pin = -1, die pin grouping = 1, PLOC = 0
    CPA_CHANNEL_COMPONENT_EXPOSURE_CONFIG = 612
    CPA_CHANNEL_VRM_SETUP = 613
    CPA_REPORT_EXPORT_PATH = 614
    CPA_RLCG_TABLE_EXPORT_PATH = 615

    CPA_EXTRACTION_MODE = 616  # 0 => optimal PI, 1 => optimal SI
    CPA_CUSTOM_REFINEMENT = 617
    CPA_EXTRACTION_FREQUENCY = 618
    CPA_COMPUTE_CAPACITANCE = 619
    CPA_COMPUTE_DC_PARAMS = 620
    CPA_DC_PARAMS_COMPUTE_RL = 621
    CPA_DC_PARAMS_COMPUTE_CG = 622
    CPA_AC_PARAMS_COMPUTE_RL = 623
    CPA_GROUND_PG_NETS_FOR_SI = 624
    CPA_AUTO_DETECT_SMALL_HOLES = 625
    CPA_SMALL_HOLE_DIAMETER = 626
    CPA_MODEL_TYPE = 627
    CPA_ADAPTIVE_REFINEMENT_CG_MAX_PASSES = 628
    CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_ERROR = 629
    CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_REFINEMENT_PER_PASS = 630
    CPA_ADAPTIVE_REFINEMENT_RL_MAX_PASSES = 631
    CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_ERROR = 632
    CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_REFINEMENT_PER_PASS = 633
    CPA_MIN_PLANE_AREA_TO_MESH = 634
    CPA_MIN_VOID_AREA_TO_MESH = 635
    CPA_VERTEX_SNAP_THRESHOLD = 636

    CPA_TERMINAL_TYPE = 640


# ////////////////////////////////////////////////////////////////

class kAttribIndex(object):
    """ """
    FROM_GROUP_NAME = 0
    FROM_NET_NAME = 1
    FROM_PIN_NAME = 2
    FROM_PINS_ON_NET_NAME = 3
    FROM_REFDES_NAME = 4
    TO_GROUP_NAME = 5
    TO_NET_NAME = 6
    TO_PIN_NAME = 7
    TO_PINS_ON_NET_NAME = 8
    TO_REFDES_NAME = 9
    TO_SOURCE_TYPE = 10
    TO_SOURCE_MAG = 11
    TO_RLC_TYPE = 12
    TO_RLC_MAG = 13
    REF_DES_NAME = 14
    PIN_NAME = 15
    PINS_ON_NET_NAME = 16
    TERM_TYPE = 17
    PIN_REGEX = 18
    PART_REGEX = 19
    REFDES_REGEX = 20
    NET_REGEX = 21
    FROM_PIN_ON_NET_NAME = 22
    TO_PIN_ON_NET_NAME = 23
    NUM_ATTRIBS = 24


class CSIwaveDCIRConfig(object):
    """ """

    def __init__(self, \
                 simName, \
                 initMeshMaxEdgeLen='2.5mm', \
                 meshBws=False, \
                 numBwFacets=8, \
                 meshVias=False, \
                 numViaFacets=8, \
                 adapt=True, \
                 minAdaptPasses=1, \
                 maxAdaptPasses=5, \
                 localRefinement=20.0, \
                 energyError=3.0, \
                 refineBws=True, \
                 refineVias=True, \
                 plotJV=True, \
                 cktElemContactR='0.1mm', \
                 icepakTempFile='', \
                 sourceTermsToGround=dict(),
                 exportDcThermalData='0',
                 fullDCReportPath='',
                 powerTreePath='',
                 powerTreeConfigPath='',
                 viaReportPath='',
                 perPinResPath='',
                 dcReportConfigFile='',
                 dcReportShowActiveDevices=False,
                 perPinUsePinFormat=False,
                 useLoopResForPerPin=True,
                 useTerminalsForPerPinRes=True,
                 icepakYRes='',
                 computeL=0,
                 temperature=20.0,
                 temperatureCoefficientOfResistance=0.004041,
                 dcReportImageBackgroundColor='white'):

        self.m_simName = simName
        self.m_initMeshMaxEdgeLen = initMeshMaxEdgeLen
        self.m_meshBws = meshBws
        self.m_numBwFacets = numBwFacets
        self.m_meshVias = meshVias
        self.m_numViaFacets = numViaFacets
        self.m_adapt = adapt
        self.m_minAdaptPasses = minAdaptPasses
        self.m_maxAdaptPasses = maxAdaptPasses
        self.m_localRefinement = localRefinement
        self.m_energyError = energyError
        self.m_refineBws = refineBws
        self.m_refineVias = refineVias
        self.m_plotJV = plotJV
        self.m_cktElemContactR = cktElemContactR
        self.m_icepakTempFile = icepakTempFile
        self.m_posSourceTermsToGround = list()
        self.m_negSourceTermsToGround = list()
        self.m_exportDcThermalData = exportDcThermalData
        self.m_fullDCReportPath = fullDCReportPath
        self.m_powerTreePath = powerTreePath
        self.m_powerTreeConfigPath = powerTreeConfigPath
        self.m_viaReportPath = viaReportPath
        self.m_perPinResPath = perPinResPath
        self.m_useLoopResForPerPinRes = useLoopResForPerPin
        self.m_perPinUsePinFormat = perPinUsePinFormat
        self.m_dcReportConfigFile = dcReportConfigFile
        self.m_dcReportShowActiveDevices = dcReportShowActiveDevices
        self.m_useTerminalsForPerPinRes = useTerminalsForPerPinRes
        self.m_icepakYRes = icepakYRes
        self.m_computeL = computeL
        self.m_temperature = temperature
        self.m_temperatureCoefficientOfResistance = temperatureCoefficientOfResistance
        self.m_dcReportImageBackgroundColor = dcReportImageBackgroundColor

        for sourceName in sourceTermsToGround:
            termToGround = sourceTermsToGround[sourceName]
            if termToGround.lower() == 'negativeterminal':
                self.m_negSourceTermsToGround.append(sourceName)
            elif termToGround.lower() == 'positiveterminal':
                self.m_posSourceTermsToGround.append(sourceName)

    # ----------------------------------------------------------------

    def SetNodeToGround(self, sourceName, groundNeg=True):
        """

        Parameters
        ----------
        sourceName :
            
        groundNeg :
             (Default value = True)

        Returns
        -------

        """
        if self.m_nodesToGround is None:
            self.m_nodesToGround = dict()
        if groundNeg is True:
            self.m_nodesToGround[sourceName] = '-'
        else:
            self.m_nodesToGround[sourceName] = '+'

    # ----------------------------------------------------------------

    def GetInitMeshMaxEdgeLen(self):
        """Returns a real number in meters representing the
        maximum value of the initial mesh edge length

        Parameters
        ----------

        Returns
        -------

        """
        return edb.Utility.Value(self.m_initMeshMaxEdgeLen)

    # ----------------------------------------------------------------

    def GetCktElemContactRadius(self):
        """Returns a real number in meters representing the circuit
        element contact radius

        Parameters
        ----------

        Returns
        -------

        """
        return edb.Utility.Value(self.m_cktElemContactR)
