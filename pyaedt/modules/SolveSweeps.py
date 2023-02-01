import copy
import json
import sys
import warnings
from collections import OrderedDict
from difflib import SequenceMatcher

from pyaedt import pyaedt_function_handler
from pyaedt.generic.DataHandlers import _dict2arg
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file
from pyaedt.modules.SetupTemplates import ASSM
from pyaedt.modules.SetupTemplates import BLDC
from pyaedt.modules.SetupTemplates import CPSM
from pyaedt.modules.SetupTemplates import DCM
from pyaedt.modules.SetupTemplates import DFIG
from pyaedt.modules.SetupTemplates import GRM
from pyaedt.modules.SetupTemplates import HFSSSBR
from pyaedt.modules.SetupTemplates import HSPICE
from pyaedt.modules.SetupTemplates import LSSM
from pyaedt.modules.SetupTemplates import NSSM
from pyaedt.modules.SetupTemplates import PMDC
from pyaedt.modules.SetupTemplates import SPIM
from pyaedt.modules.SetupTemplates import SRM
from pyaedt.modules.SetupTemplates import TPIM
from pyaedt.modules.SetupTemplates import TPSM
from pyaedt.modules.SetupTemplates import TR
from pyaedt.modules.SetupTemplates import UNIM
from pyaedt.modules.SetupTemplates import Close
from pyaedt.modules.SetupTemplates import EddyCurrent
from pyaedt.modules.SetupTemplates import ElectricTransient
from pyaedt.modules.SetupTemplates import Electrostatic
from pyaedt.modules.SetupTemplates import HFSS3DLayout
from pyaedt.modules.SetupTemplates import HFSSDrivenAuto
from pyaedt.modules.SetupTemplates import HFSSDrivenDefault
from pyaedt.modules.SetupTemplates import HFSSEigen
from pyaedt.modules.SetupTemplates import HFSSTransient
from pyaedt.modules.SetupTemplates import LNA3DLayout
from pyaedt.modules.SetupTemplates import Magnetostatic
from pyaedt.modules.SetupTemplates import Matrix
from pyaedt.modules.SetupTemplates import MaxwellTransient
from pyaedt.modules.SetupTemplates import MechModal
from pyaedt.modules.SetupTemplates import MechStructural
from pyaedt.modules.SetupTemplates import MechTerm
from pyaedt.modules.SetupTemplates import NexximAMI
from pyaedt.modules.SetupTemplates import NexximDC
from pyaedt.modules.SetupTemplates import NexximHarmonicBalance1T
from pyaedt.modules.SetupTemplates import NexximHarmonicBalanceNT
from pyaedt.modules.SetupTemplates import NexximLNA
from pyaedt.modules.SetupTemplates import NexximOscillator1T
from pyaedt.modules.SetupTemplates import NexximOscillatorNT
from pyaedt.modules.SetupTemplates import NexximOscillatorRSF
from pyaedt.modules.SetupTemplates import NexximQuickEye
from pyaedt.modules.SetupTemplates import NexximSystem
from pyaedt.modules.SetupTemplates import NexximTransient
from pyaedt.modules.SetupTemplates import NexximTVNoise
from pyaedt.modules.SetupTemplates import NexximVerifEye
from pyaedt.modules.SetupTemplates import Open
from pyaedt.modules.SetupTemplates import SiwaveAC3DLayout
from pyaedt.modules.SetupTemplates import SiwaveDC3DLayout
from pyaedt.modules.SetupTemplates import SteadyFlowOnly
from pyaedt.modules.SetupTemplates import SteadyTemperatureAndFlow
from pyaedt.modules.SetupTemplates import SteadyTemperatureOnly
from pyaedt.modules.SetupTemplates import Sweep3DLayout
from pyaedt.modules.SetupTemplates import SweepHfss3D
from pyaedt.modules.SetupTemplates import SweepSiwave
from pyaedt.modules.SetupTemplates import TransientFlowOnly
from pyaedt.modules.SetupTemplates import TransientTemperatureAndFlow
from pyaedt.modules.SetupTemplates import TransientTemperatureOnly

open3 = open
if sys.version_info < (3, 0):
    import io

    open3 = io.open


@pyaedt_function_handler()
def identify_setup(props):
    """Identify if a setup props is time or frequency domain.

    Parameters
    ----------
    props : dict

    Returns
    -------
    bool
        `True` if domain is Time. `False` for Frequency and Sweeps.
    """
    keys = [
        "Transient",
        "TimeStep",
        "Data/InitialStep",
        "TransientData",
        "QuickEyeAnalysis",
        "VerifEyeAnalysis",
        "AMIAnalysis",
        "HSPICETransientData",
        "SystemFDAnalysis",
        "Start Time:=",
    ]
    for key in keys:
        if "/" in key:
            if key.split("/")[0] in props and key.split("/")[1] in props[key.split("/")[0]]:
                return True
        elif key in props:
            return True
    return False


class SweepHFSS(object):
    """Initializes, creates, and updates sweeps in HFSS.

    Parameters
    ----------
    app : :class 'pyaedt.modules.SolveSetup.Setup'
        Setup used for the analysis.
    setupname : str
        Name of the setup.
    sweepname : str
        Name of the sweep.
    sweeptype : str, optional
        Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
        and ``"Discrete"``. The default is ``"Interpolating"``.
    props : dict, optional
        Dictionary of the properties. The default is ``None``, in which case
        the default properties are retrieved.

    Examples
    --------
    >>> hfss = Hfss(specified_version=version, projectname=proj, designname=gtemDesign, solution_type=solutiontype,
                    setup_name=setupname, new_desktop_session=False, close_on_exit=False)
    >>> hfss_setup = hfss.setups[0]
    >>> hfss_sweep = SweepHFSS(hfss_setup, 'Sweep', sweeptype ='Interpolating', props=None)

    """

    def __init__(self, setup, sweepname, sweeptype="Interpolating", props=None, **kwargs):
        if "app" in kwargs:
            warnings.warn(
                "`app` is deprecated since v0.6.22. Use `setup` instead.",
                DeprecationWarning,
            )
            setup = kwargs["app"]
        if "setupname" in kwargs:
            warnings.warn(
                "`setupname` is deprecated since v0.6.22 and not required anymore.",
                DeprecationWarning,
            )

        self._app = setup
        self.oanalysis = setup.omodule
        self.props = {}
        self.setupname = setup.name
        self.name = sweepname
        if props:
            self.props = props
        else:
            self.props = copy.deepcopy(SweepHfss3D)
            # for t in SweepHfss3D:
            #    _tuple2dict(t, self.props)
            if SequenceMatcher(None, sweeptype.lower(), "interpolating").ratio() > 0.8:
                sweeptype = "Interpolating"
            elif SequenceMatcher(None, sweeptype.lower(), "discrete").ratio() > 0.8:
                sweeptype = "Discrete"
            elif SequenceMatcher(None, sweeptype.lower(), "fast").ratio() > 0.8:
                sweeptype = "Fast"
            else:
                warnings.warn("Invalid sweep type. `Interpolating` will be set as default.")
                sweeptype = "Interpolating"
            self.props["Type"] = sweeptype

    @property
    def is_solved(self):
        """Verify if solutions are available for given sweep.

        Returns
        -------
        bool
            `True` if solutions are available.
        """
        sol = self._app.p_app.post.reports_by_category.standard(setup_name="{} : {}".format(self.setupname, self.name))
        if identify_setup(self.props):
            sol.domain = "Time"
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
        """Add a range to the sweep.

        Parameters
        ----------
        rangetype : str
            Type of the range. Options are ``"LinearCount"``,
            ``"LinearStep"``, ``"LogScale"``, and ``"SinglePoints"``.
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

        interval = {"RangeType": rangetype, "RangeStart": str(start) + unit}
        if rangetype == "LinearCount":
            interval["RangeEnd"] = str(end) + unit
            interval["RangeCount"] = count
        elif rangetype == "LinearStep":
            interval["RangeEnd"] = str(end) + unit
            interval["RangeStep"] = str(count) + unit
        elif rangetype == "LogScale":
            interval["RangeEnd"] = str(end) + unit
            interval["RangeCount"] = self.props["RangeCount"]
            interval["RangeSamples"] = count
        elif rangetype == "SinglePoints":
            interval["RangeEnd"] = str(start) + unit
            interval["SaveSingleField"] = save_single_fields
        if not self.props.get("SweepRanges", None):
            self.props["SweepRanges"] = {"Subrange": []}

        if not isinstance(self.props["SweepRanges"]["Subrange"], list):
            self.props["SweepRanges"]["Subrange"] = [self.props["SweepRanges"]["Subrange"]]
        self.props["SweepRanges"]["Subrange"].append(interval)

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
    app : :class 'pyaedt.modules.SolveSetup.Setup'
        Setup used for the analysis.
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

    def __init__(self, setup, sweepname, sweeptype="Interpolating", save_fields=True, props=None, **kwargs):

        if "app" in kwargs:
            warnings.warn(
                "`app` is deprecated since v0.6.22. Use `setup` instead.",
                DeprecationWarning,
            )
            setup = kwargs["app"]
        if "setupname" in kwargs:
            warnings.warn(
                "`setupname` is deprecated since v0.6.22 and not required anymore.",
                DeprecationWarning,
            )

        self._app = setup
        self.oanalysis = setup.omodule
        self.props = {}
        self.setupname = setup.name
        self.name = sweepname
        if props:
            self.props = props
        else:
            if setup.setuptype in [40, 41]:
                self.props = copy.deepcopy(SweepSiwave)
            else:
                self.props = copy.deepcopy(Sweep3DLayout)
            # for t in props:
            #    _tuple2dict(t, self.props)
            if SequenceMatcher(None, sweeptype.lower(), "kinterpolating").ratio() > 0.8:
                sweeptype = "kInterpolating"
            elif SequenceMatcher(None, sweeptype.lower(), "kdiscrete").ratio() > 0.8:
                sweeptype = "kDiscrete"
            else:
                warnings.warn("Invalid sweep type. `kInterpolating` will be set as default.")
                sweeptype = "kInterpolating"
            self.props["FreqSweepType"] = sweeptype
            self.props["GenerateSurfaceCurrent"] = save_fields

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
        expressions = [i for i in self.p_app.post.available_report_quantities(solution=self.combined_name)]
        sol = self._app._app.post.reports_by_category.standard(
            setup_name=self.combined_name, expressions=expressions[0]
        )
        if identify_setup(self.props):
            sol.domain = "Time"
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
        try:
            if rangetype == "SinglePoint" and self.props["FreqSweepType"] == "kInterpolating":
                raise AttributeError("'SinglePoint is allowed only when sweeptype is 'Discrete'.'")
            if rangetype == "LinearCount" or rangetype == "LinearStep" or rangetype == "LogScale":
                if not end or not count:
                    raise AttributeError("Parameters 'end' and 'count' must be present.")

            if rangetype == "LinearCount":
                sweep_range = " LINC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
            elif rangetype == "LinearStep":
                sweep_range = " LIN " + str(start) + unit + " " + str(end) + unit + " " + str(count) + unit
            elif rangetype == "LogScale":
                sweep_range = " DEC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
            elif rangetype == "SinglePoint":
                sweep_range = " " + str(start) + unit
            else:
                raise AttributeError(
                    'Allowed rangetype are "LinearCount", "SinglePoint", "LinearStep", and "LogScale".'
                )
            self.props["Sweeps"]["Data"] += sweep_range
            return self.update()
        except:
            return False

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
            sweep_range = "DEC " + str(start) + unit + " " + str(end) + unit + " " + str(count)
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


class SweepMatrix(object):
    """Initializes, creates, and updates sweeps in Q3D.

    Parameters
    ----------
    app : :class 'pyaedt.modules.SolveSetup.Setup'
        Setup used for the analysis.
    setupname : str
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

    def __init__(self, setup, sweepname, sweeptype="Interpolating", props=None, **kwargs):
        if "app" in kwargs:
            warnings.warn(
                "`app` is deprecated since v0.6.22. Use `setup` instead.",
                DeprecationWarning,
            )
            setup = kwargs["app"]
        if "setupname" in kwargs:
            warnings.warn(
                "`setupname` is deprecated since v0.6.22 and not required anymore.",
                DeprecationWarning,
            )
        self._app = setup
        self.oanalysis = setup.omodule
        self.setupname = setup.name
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

    @property
    def frequencies(self):
        """Get the list of all frequencies of the active sweep.
        The project has to be saved and solved to see values.

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
        """Get the list of all frequencies that have fields available.
        The project has to be saved and solved to see values.

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
    def add_subrange(self, rangetype, start, end=None, count=None, unit="GHz", clear=False, **kwargs):
        """Add a subrange to the sweep.

        Parameters
        ----------
        rangetype : str
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
        if "type" in kwargs:
            warnings.warn("type has been deprecated. use rangetype.", DeprecationWarning)
            rangetype = kwargs["type"]
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
            self.props["SweepRanges"] = {"Subrange": []}
            return self.update()
        sweep_range = {"RangeType": rangetype, "RangeStart": str(start) + unit}
        if rangetype == "LinearCount":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = count
        elif rangetype == "LinearStep":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeStep"] = str(count) + unit
        elif rangetype == "LogScale":
            sweep_range["RangeEnd"] = str(end) + unit
            sweep_range["RangeCount"] = self.props["RangeCount"]
            sweep_range["RangeSamples"] = count
        if not self.props.get("SweepRanges") or not self.props["SweepRanges"].get("Subrange"):
            self.props["SweepRanges"] = {"Subrange": []}
        self.props["SweepRanges"]["Subrange"].append(sweep_range)
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

    SetupNames = [  # TODO: HFSSDriven appears twice. Is this correct?
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

    def _export_properties_to_json(self, file_path):
        """Export all setup properties into a json file.

        Parameters
        ----------
        file_path : str
            File path of the json file.
        """
        if not file_path.endswith(".json"):
            file_path = file_path + ".json"
        with open3(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self, indent=4, ensure_ascii=False))
        return True

    def _import_properties_from_json(self, file_path):
        """Import setup properties from a json file.

        Parameters
        ----------
        file_path : str
            File path of the json file.
        """

        def set_props(target, source):
            for k, v in source.items():
                if k not in target:
                    raise Exception("{} is not a valid property name.".format(k))
                if not isinstance(v, dict):
                    target[k] = v
                else:
                    set_props(target[k], v)

        with open3(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            set_props(self, data)
        return True

    def delete_all(self):
        for item in list(self.keys()):
            if item != "_pyaedt_setup":
                OrderedDict.__delitem__(self, item)
