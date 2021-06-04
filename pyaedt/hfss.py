"""
Hfss Class
----------------------------------------------------------------


Description
==================================================

This class contains all the HFSS Functionalities. It inherites all the objects that belongs to HFSS


:Example:

hfss = Hfss()     creates and hfss object and connect to existing hfss design (create a new hfss design if not present)


hfss = Hfss(projectname)     creates and hfss object and link to projectname project. If project doesn't exists, it creates a new one and rename it


hfss = Hfss(projectname,designame)     creates and hfss object and link to designname design in projectname project


hfss = Hfss("myfile.aedt")     creates and hfss object and open specified project


========================================================

"""
from __future__ import absolute_import
import os
from .application.Analysis3D import FieldAnalysis3D
from .desktop import exception_to_desktop
from .modeler.GeometryOperators import GeometryOperators
from .modules.Boundary import BoundaryObject
from .generic.general_methods import generate_unique_name, aedt_exception_handler
from collections import OrderedDict
from .application.DataHandlers import random_string


class Hfss(FieldAnalysis3D, object):
    """HFSS object"""
    def __repr__(self):
        try:
            return "HFSS {} {}. ProjectName:{} DesignName:{} ".format(self._aedt_version, self.solution_type, self.project_name, self.design_name)
        except:
            return "HFSS Module"

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):
        """HFSS Object

            Parameters
            ----------
            projectname :
                name of the project to be selected or full path to the project to be opened  or to the AEDTZ archive. if None try to get active project and, if nothing present to create an empty one
            designname :
                name of the design to be selected. if None, try to get active design and, if nothing present to create an empty one
            solution_type :
                solution type to be applied to design. if None default is taken
            setup_name :
                setup_name to be used as nominal. if none active setup is taken or nothing

            Returns
            -------

        """
        FieldAnalysis3D.__init__(self, "HFSS", projectname, designname, solution_type, setup_name)
    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    class BoundaryType(object):
        """ """
        (PerfectE, PerfectH, Aperture, Radiation, Impedance, LayeredImp, LumpedRLC, FiniteCond) = range(0, 8)

    @aedt_exception_handler
    def _create_lumped_driven(self, objectname, int_line_start, int_line_stop, impedance, portname,renorm, deemb):
        start = [str(i)+self.modeler.primitives.model_units for i in int_line_start]
        stop = [str(i)+self.modeler.primitives.model_units for i in int_line_stop]
        props = OrderedDict({"Objects": [objectname], "DoDeembed": deemb, "RenormalizeAllTerminals": renorm,
                             "Modes": OrderedDict({"Mode1": OrderedDict({"ModeNum": 1, "UseIntLine": True,
                                                                         "IntLine": OrderedDict(
                                                                             {"Start": start, "End": stop}),
                                                                         "AlignmentGroup": 0, "CharImp": "Zpi",
                                                                         "RenormImp": str(impedance) + "ohm"})}),
                             "ShowReporterFilter": False,
                             "ReporterFilter": [True],
                             "Impedance"	:  str(impedance)+"ohm"})
        bound = BoundaryObject(self, portname,props, "LumpedPort")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def _create_port_terminal(self, objectname, int_line_stop, portname, iswaveport=False):
        ref_conductors=self.modeler.convert_to_selections(int_line_stop,False)
        props = OrderedDict({})
        props["Faces"]=int(objectname)
        props["IsWavePort"]=iswaveport
        props["ReferenceConductors"]=ref_conductors
        props["RenormalizeModes"]=True
        bound = BoundaryObject(self, portname, props, "AutoIdentify")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return True

    @aedt_exception_handler
    def _create_circuit_port(self, edgelist, impedance, name, renorm, deemb, renorm_impedance=""):
        edgelist = self.modeler._convert_list_to_ids(edgelist,False)
        props = OrderedDict({"Edges": edgelist, "Impedance": str(impedance) + "ohm", "DoDeembed": deemb,
                             "RenormalizeAllTerminals": renorm})

        if self.solution_type == "DrivenModal":

            if renorm:
                if type(renorm_impedance) is int or type(renorm_impedance) is float or 'i' not in renorm_impedance:
                    renorm_imp = str(renorm_impedance) + 'ohm'
                else:
                    renorm_imp = '(' + renorm_impedance + ') ohm'
            else:
                renorm_imp = '0ohm'
            props["RenormImp"] = renorm_imp
        else:
            props["TerminalIDList"] = []
        bound = BoundaryObject(self,name,props, "CircuitPort")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def _create_waveport_driven(self, objectname, int_line_start=None, int_line_stop=None, impedance=50, portname="",
                                renorm=True, nummodes=1, deemb_distance=0):
        start = None
        stop = None
        if int_line_start and int_line_stop:
            start = [str(i)+self.modeler.primitives.model_units for i in int_line_start]
            stop = [str(i)+self.modeler.primitives.model_units for i in int_line_stop]
            useintline = True
        else:
            useintline=False

        props = OrderedDict({})
        props["Objects"] = [objectname]
        props["NumModes"] = nummodes
        props["UseLineModeAlignment"] = False

        if deemb_distance!=0:
            props["DoDeembed"] = True
            props["DeembedDist"] = str(deemb_distance)+self.modeler.model_units

        else:
            props["DoDeembed"] = False
        props["RenormalizeAllTerminals"] = renorm
        modes = OrderedDict({})
        arg2 = []
        arg2.append("NAME:Modes")
        i=1
        report_filter=[]
        while i<=nummodes:
            if i == 1:
                mode = OrderedDict({})
                mode["ModeNum"] = i
                mode["UseIntLine"] = useintline
                if useintline:
                    mode["IntLine"] = OrderedDict({"Start": start, "End": stop})
                mode["AlignmentGroup"] = 0
                mode["CharImp"] = "Zpi"
                mode["RenormImp"] = str(impedance)+"ohm"
                modes["Mode1"] = mode
            else:
                mode = OrderedDict({})

                mode["ModeNum"] = i
                mode["UseIntLine"] = False
                mode["AlignmentGroup"] = 0
                mode["CharImp"] = "Zpi"
                mode["RenormImp"] = str(impedance)+"ohm"
                modes["Mode"+str(i)] = mode
            report_filter.append(True)
            i += 1
        props["Modes"] = modes
        props["ShowReporterFilter"] = False
        props["ReporterFilter"] = report_filter
        props["UseAnalyticAlignment"] = False
        bound = BoundaryObject(self, portname, props, "WavePort")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assigncoating(self, obj, mat=None,
                      cond=58000000, perm=1, usethickness=False, thickness="0.1mm", roughness="0um",
                      isinfgnd=False, istwoside=False, isInternal=True, issheelElement=False, usehuray=False,
                      radius="0.5um", ratio="2.9"):
        """The function assigns Finite Conductivity to object obj with material mat

        Parameters
        ----------
        obj : list or str
            object list
        mat : str
            material name to use, optional (Default value = None)
        cond : float
            if not material is provided user has to provide conductivity (Default value = 58000000)
        perm : float
            if not material is provided user has to provide permittivity (Default value = 1)
        usethickness : bool
            boolean (Default value = False)
        thickness : str
            thickness value in case usethickness=True (Default value = "0.1mm")
        roughness : str
            optional roughness value (Default value = "0um")
        isinfgnd : bool
            Boolean (Default value = False)
        istwoside : bool
            Boolean (Default value = False)
        isInternal : bool
            Boolean (Default value = True)
        issheelElement : bool
            Boolena (Default value = False)
        usehuray : bool
            Boolean (Default value = False)
        radius : str
            Huray Coefficient (Default value = "0.5um")
        ratio : str
            Huray Coefficient (Default value = "2.9")

        Returns
        -------
        :class: BoundaryObject
            Boundary Object

        Examples
        --------
        >>> id1 = aedtapp.modeler.primitives.get_obj_id("inner")
        >>> coat = aedtapp.assigncoating([id1], "copper",usethickness=True, thickness="0.2mm")
        """

        mat = mat.lower()
        listobj = self.modeler.convert_to_selections(obj, True)
        listobjname = "_".join(listobj)
        props = {"Objects" : listobj}
        if mat:
            if mat in self.materials.material_keys:
                Mat = self.materials.material_keys[mat]
                Mat.update()
                props['UseMaterial'] = True
                props['Material'] = mat
                self.materials._aedmattolibrary(mat)
            elif self.materials.checkifmaterialexists(mat):
                props['UseMaterial'] = True
                props['Material'] = mat
            else:
                return False
        else:
            props['UseMaterial'] = False
            props['Conductivity'] = str(cond)
            props['Permeability'] = str(str(perm))
        props['UseThickness'] = usethickness
        if usethickness:
            props['Thickness'] = thickness
        if usehuray:
            props['Radius'] = str(radius)
            props['Ratio'] = str(ratio)
            props['InfGroundPlane'] = False
        else:
            props['Roughness'] = roughness
            props['InfGroundPlane'] = isinfgnd
        props['IsTwoSided'] = istwoside

        if istwoside:
            props['IsShellElement'] = issheelElement
        else:
            props['IsInternal'] = isInternal
        bound = BoundaryObject(self, "Coating_" + listobjname[:32], props, "FiniteCond")
        if bound.create():
            self._messenger.add_debug_message('Assigned Coating ' + mat + ' to object ' + listobjname)
            self.boundaries.append(bound)
            return bound
        return True

    @aedt_exception_handler
    def create_frequency_sweep(self, setupname, unit="GHz", freqstart=1e-3, freqstop=10, sweepname=None,
                               num_of_freq_points=451, sweeptype="Interpolating",
                               interpolation_tol=0.5, interpolation_max_solutions=250):
        """Create a Frequency Sweep

        Parameters
        ----------
        setupname : str
            name of the setup to which is attached the sweep
        unit :
            Units ("MHz", "GHz"....) (Default value = "GHz")
        freqstart :
            Starting Frequency of sweep (Default value = 1e-3)
        freqstop :
            Stop Frequency of Sweep (Default value = 10)
        sweepname :
            name of the Sweep (Default value = None)
        num_of_freq_points :
            Number of frequency point in the range (Default value = 451)
        sweeptype :
            Fast"|"Interpolating"|"Discrete" (default)
        interpolation_max_solutions :
            max number of solutions evaluated for the interpolation process (Default value = 250)
        interpolation_tol :
            error tolerance threshold for the interpolation process (Default value = 0.5)

        Returns
        -------
        type
            True if operation succeeded

        """

        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self.messenger.add_warning_message("Sweep {} already present. Please rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, sweeptype)
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeCount"] = num_of_freq_points
                sweepdata.props["Type"] = sweeptype
                if sweeptype == "Interpolating":
                    sweepdata.props["InterpTolerance"] = interpolation_tol
                    sweepdata.props["InterpMaxSolns"] = interpolation_max_solutions
                    sweepdata.props["InterpMinSolns"] = 0
                    sweepdata.props["InterpMinSubranges"] = 1

                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.update()
                return sweepname


    @aedt_exception_handler
    def create_linear_count_sweep(self, setupname, unit, freqstart, freqstop, num_of_freq_points,
                                  sweepname=None, save_fields=True, save_rad_fields=False):
        """Create a Discrete Sweep with specified the number of points

        Parameters
        ----------
        setupname : str
            Setup name
        freqstart : float
            Starting Frequency of sweep (eg. 1)
        freqstop : float
            Stop Frequency of Sweep
        sweepname : str
            name of the Sweep (Default value = None)
        unit : str
            Units ("MHz", "GHz"....)
        num_of_freq_points : int
            Number of frequency point in the range
        save_fields : bool
            bool (Default value = True)
        save_rad_fields :
            bool (Default value = False)

        Returns
        -------
        :class: SweepHFSS
            sweepname

        """
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self.messenger.add_warning_message("Sweep {} already present. Please rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = str(freqstart) + unit,
                sweepdata.props["RangeEnd"] = str(freqstop) + unit,
                sweepdata.props["RangeCount"] = num_of_freq_points,
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "LinearCount"
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.update()
                return sweepname

    @aedt_exception_handler
    def create_linear_step_sweep(self, setupname, unit, freqstart, freqstop, step_size,
                                 sweepname=None, save_fields=True, save_rad_fields=False):
        """Create a Discrete Sweep with specified the number of points

        Parameters
        ----------
        freqstart : float
            Starting Frequency of sweep
        freqstop : float
            Stop Frequency of Sweep
        sweepname : str
            name of the Sweep (Default value = None)
        unit : str
            Units ("MHz", "GHz"....)
        step_size : float
            Frequency size of the step
        setupname : str
            Setup name
        save_fields : bool
            bool (Default value = True)
        save_rad_fields : bool
            bool (Default value = False)

        Returns
        -------
        :class: SweepHFSS
            sweepname

        """
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self.messenger.add_warning_message("Sweep {} already present. Please rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeStep"] = str(step_size) + unit
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.update()
                return sweepname


    @aedt_exception_handler
    def create_discrete_sweep(self, setupname, sweepname="SinglePoint", freq="1GHz", save_field=True, save_radiating_field=False):
        """Create a Discrete Sweep with a single frequency value

        Parameters
        ----------
        setupname : str
            Setup name
        freq : str
            sweep freq (including Units) as string (Default value = "1GHz")
        sweepname : str
            name of the sweep (Default value = "SinglePoint")
        save_field : bool
            bool (Default value = True)
        save_radiating_field : bool
            bool (Default value = False)

        Returns
        -------
        :class: SweepHFSS
            sweepname

        """
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self.messenger.add_warning_message("Sweep {} already present. Please rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = freq
                sweepdata.props["RangeEnd"] = freq
                sweepdata.props["SaveSingleField"] = save_field
                sweepdata.props["SaveFields"] = save_field
                sweepdata.props["SaveRadFields"] = save_radiating_field
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "SinglePoints"
                sweepdata.update()
                self._messenger.add_info_message("Sweep Created Correctly")
                return sweepname


    @aedt_exception_handler
    def create_circuit_port_between_objects(self, startobj, endobject, axisdir="XYNeg", impedance=50, portname=None,
                                            renorm=True, renorm_impedance=50, deemb=False):
        """Function that Creates a Circuit port taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = "XYNeg")
        impedance :
            Port Impedance (Default value = 50)
        portname :
            Port Name. (Default value = None)
        renorm :
            Boolean, Renormalize Mode (Default value = True)
        renorm_impedance :
            Float or str, Renormalize Impedance (Default value = 50)
        deemb :
            Boolean DEembed Port (Default value = False)

        Returns
        -------
        type
            portname

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            out, parallel = self.modeler.primitives.find_closest_edges(startobj, endobject, axisdir)
            port_edges = []
            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self._create_circuit_port(out, impedance,portname, renorm, deemb,renorm_impedance=renorm_impedance):
                return portname
        return False

    @aedt_exception_handler
    def create_lumped_port_between_objects(self, startobj, endobject, axisdir=0, impedance=50, portname=None,
                                           renorm=True, deemb=False,port_on_plane=True):
        """Function that Creates a Lumped taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        impedance :
            Port Impedance (Default value = 50)
        portname :
            Port Name. (Default value = None)
        renorm :
            Boolean, Renormalize Mode (Default value = True)
        deemb :
            Boolean DEembed Port (Default value = False)
        port_on_plane :
            Boolean. If True Source will be created on the Plane ortogonal to AxisDir (Default value = True)

        Returns
        -------
        type
            portname

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, port_on_plane)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                self._create_lumped_driven(sheet_name, point0, point1, impedance, portname,renorm, deemb)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                self._create_port_terminal(faces[0], endobject, portname, iswaveport=False)
            return portname
        return False

    @aedt_exception_handler
    def create_voltage_source_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, source_on_plane=True):
        """Function that Creates a Voltage Source taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of VS. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            Optional Source Name (Default value = None)
        source_on_plane :
            Boolean. If True Source will be created on the Plane ortogonal to AxisDir (Default value = True)

        Returns
        -------
        type
            sourcename

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, source_on_plane)
            if not sourcename:
                sourcename = generate_unique_name("Voltage")
            elif sourcename+":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Voltage")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def create_current_source_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, source_on_plane=True):
        """Function that Creates a Voltage Source taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of VS. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            Optional Source Name (Default value = None)
        source_on_plane :
            Boolean. If True Source will be created on the Plane ortogonal to AxisDir (Default value = True)

        Returns
        -------
        type
            sourcename

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, source_on_plane)
            if not sourcename:
                sourcename = generate_unique_name("Current")
            elif sourcename+":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Current")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def create_source_excitation(self, sheet_name, point1, point2, sourcename, sourcetype="Voltage"):
        """

        Parameters
        ----------
        sheet_name :
            
        point1 :
            
        point2 :
            
        sourcename :
            
        sourcetype :
             (Default value = "Voltage")

        Returns
        -------

        """

        props = OrderedDict({"Objects": [sheet_name],
               "Direction":OrderedDict({"Start": point1, "End": point2})})

        bound = BoundaryObject(self, sourcename, props, sourcetype)
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def create_wave_port_between_objects(self, startobj, endobject, axisdir=0, impedance=50, nummodes=1, portname=None,
                                         renorm=True, deembed_dist=0, port_on_plane=True, add_pec_cap=False):
        """Function that Creates a Waveport taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        impedance :
            Port Impedance (Default value = 50)
        nummodes :
            Number of Modes (Default value = 1)
        portname :
            Port Name. (Default value = None)
        renorm :
            Boolean, Renormalize Mode (Default value = True)
        deembed_dist :
            Deembed Distance. Float in model units (default mm). if 0 Deembed is disabled
        port_on_plane :
            Boolean. If True Port will be created on the Plane ortogonal to AxisDir (Default value = True)
        add_pec_cap :
             (Default value = False)

        Returns
        -------
        :class: BoundaryObject
            Port Name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, port_on_plane)
            if add_pec_cap:
                dist = GeometryOperators.points_distance(point0, point1)
                self._create_pec_cap(sheet_name, axisdir, dist/10)
            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                return self._create_waveport_driven(sheet_name, point0, point1, impedance, portname, renorm, nummodes, deembed_dist)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                return self._create_port_terminal(faces[0], endobject, portname, iswaveport=True)
        return False

    @aedt_exception_handler
    def _create_pec_cap(self, sheet_name, axisdir, pecthick):
        vector = [0, 0, 0]
        if axisdir < 3:
            vector[divmod(axisdir, 3)[1]] = -pecthick / 2
        else:
            vector[divmod(axisdir, 3)[1]] = pecthick / 2

        status, pecobj = self.modeler.duplicate_along_line(sheet_name, vector)
        self.modeler.thicken_sheet(pecobj[0], pecthick, True)
        self.assignmaterial(pecobj[0], "pec")
        return True

    @aedt_exception_handler
    def create_wave_port_microstrip_between_objects(self, startobj, endobject, axisdir=0, impedance=50, nummodes=1, portname=None,
                                         renorm=True, deembed_dist=0, vfactor=3, hfactor=5):
        """Function that Creates a Waveport taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        impedance :
            Port Impedance (Default value = 50)
        nummodes :
            Number of Modes (Default value = 1)
        portname :
            Port Name. (Default value = None)
        renorm :
            Boolean, Renormalize Mode (Default value = True)
        deembed_dist :
            Deembed Distance. Float in model units (default mm). if 0 Deembed is disabled
        vfactor :
            Port Vertical Factor (Default value = 3)
        hfactor :
            Port HorizontalFactor (Default value = 5)

        Returns
        -------
        :class: BoundaryObject
            Port Name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_microstrip_sheet_from_object_closest_edge(startobj,endobject,axisdir, vfactor, hfactor)
            dist = GeometryOperators.points_distance(point0, point1)
            self._create_pec_cap(sheet_name, axisdir,dist/10)
            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                return self._create_waveport_driven(sheet_name, point0, point1, impedance, portname, renorm, nummodes, deembed_dist)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                return self._create_port_terminal(faces[0], endobject, portname, iswaveport=True)
        return False

    @aedt_exception_handler
    def create_perfecte_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, is_infinite_gnd=False, bound_on_plane=True ):
        """Function that Creates a Perfect E  taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            Perfect E Name. (Default value = None)
        bound_on_plane :
            Boolean. If True PerfectE will be created on the Plane ortogonal to AxisDir (Default value = True)
        is_infinite_gnd :
             (Default value = False)

        Returns
        -------
        :class: BoundaryObject
            boundary object

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("PerfE")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectE, sheet_name, sourcename, is_infinite_gnd)
        return False

    @aedt_exception_handler
    def create_perfecth_from_objects(self, startobj, endobject, axisdir=0, sourcename=None,bound_on_plane=True):
        """Function that Creates a Perfect H  taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            Perfect H Name. (Default value = None)
        bound_on_plane :
            Boolean. If True PerfectH will be created on the Plane ortogonal to AxisDir (Default value = True)

        Returns
        -------
        :class: BoundaryObject
            Boundary Object

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("PerfH")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectH, sheet_name, sourcename)
        return None

    @aedt_exception_handler
    def SARSetup(self,Tissue_object_List_ID, TissueMass=1, MaterialDensity=1,  voxel_size=1, Average_SAR_method=0):
        """Set SAR Settings

        Parameters
        ----------
        Tissue_object_List_ID :
            33
        TissueMass :
            param MaterialDensity: (Default value = 1)
        voxel_size :
            param Average_SAR_method: (Default value = 1)
        MaterialDensity :
             (Default value = 1)
        Average_SAR_method :
             (Default value = 0)

        Returns
        -------
        bool
        """
        self.odesign.SARSetup(TissueMass, MaterialDensity, Tissue_object_List_ID, voxel_size, Average_SAR_method)
        return True

    @aedt_exception_handler
    def create_open_region(self, Frequency="1GHz", Boundary="Radiation", ApplyInfiniteGP=False, GPAXis="-z"):
        """Create an open region on the active Editor

        Parameters
        ----------
        Frequency :
            Frequency with Units (Default value = "1GHz")
        Boundary :
            Boundary Type. Default "Radition"
        ApplyInfiniteGP :
            Bool to apply infinite Ground Plane (Default value = False)
        GPAXis :
             (Default value = "-z")

        Returns
        -------
        bool
        """
        vars= [
                "NAME:Settings",
                "OpFreq:="	, Frequency,
                "Boundary:="		, Boundary,
                "ApplyInfiniteGP:="	, ApplyInfiniteGP
            ]
        if ApplyInfiniteGP:
            vars.append("Direction:=")
            vars.append(GPAXis)

        self.omodelsetup.CreateOpenRegion(vars)
        return True

    @aedt_exception_handler
    def create_lumped_rlc_between_objects(self, startobj, endobject, axisdir=0, sourcename=None, rlctype="Parallel",
                                          Rvalue=None, Lvalue=None, Cvalue=None, bound_on_plane=True):
        """Function that Creates a Perfect H  taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            Perfect H Name. (Default value = None)
        Cvalue :
            Capacitance Value in F. None to disable (Default value = None)
        Lvalue :
            Inductacnce Value in H. None to disable (Default value = None)
        rlctype :
            Parallel" or "Series" (Default value = "Parallel")
        Rvalue :
            Resistance Value in Ohm. None to disable (Default value = None)
        bound_on_plane :
            Boolean. If True Boundary will be created on the Plane ortogonal to AxisDir (Default value = True)

        Returns
        -------
        :class: BoundaryObject
            Boundary Name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] and (Rvalue or Lvalue or Cvalue):
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj,endobject,axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("Lump")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            start = [str(i) + self.modeler.primitives.model_units for i in point0]
            stop = [str(i) + self.modeler.primitives.model_units for i in point1]

            props = OrderedDict()
            props["Objects"] = [sheet_name]
            props["CurrentLine"] = OrderedDict({"Start":start, "End": stop})
            props["RLC Type"] = [rlctype]
            if Rvalue:
                props["UseResist"] = True
                props["Resistance"] = str(Rvalue)+"ohm"
            if Lvalue:
                props["UseInduct"] = True
                props["Inductance"] = str(Lvalue)+"H"
            if Cvalue:
                props["UseCap"] = True
                props["Capacitance"] = str(Cvalue)+"F"
            bound = BoundaryObject(self, sourcename, props, "LumpedRLC")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def create_impedance_between_objects(self, startobj, endobject, axisdir=0, sourcename=None, resistance=50, reactance=0, is_infground=False, bound_on_plane=True):
        """Function that Creates an impedance taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir :
            Position of impedance. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            impedance Name. (Default value = None)
        resistance :
            Resistance Value in Ohm. None to disable (Default value = 50)
        reactance :
            Reactance Value in Ohm. None to disable (Default value = 0)
        bound_on_plane :
            Boolean. If True Impdedance will be created on the Plane ortogonal to AxisDir (Default value = True)
        is_infground :
             (Default value = False)

        Returns
        -------
        :class: BoundaryObject
            Boundary Name

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(endobject):
            self.messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] :
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject, axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("Imped")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            props = OrderedDict({"Objects": [sheet_name], "Resistance": str(resistance), "Reactance": str(reactance),
                                 "InfGroundPlane": is_infground})
            bound = BoundaryObject(self, sourcename, props, 'Impedance')
            if bound.create():
                self.boundaries.append(bound)
                return bound

        return False

    @aedt_exception_handler
    def create_boundary(self, boundary_type=BoundaryType.PerfectE, sheet_name=None, boundary_name="", is_infinite_gnd=False):
        """Create a Boundary given specific inputs

        Parameters
        ----------
        boundary_type :
            BoundaryType object (PerfectE, PerfectH, Aperture, Radiation) (Default value = BoundaryType.PerfectE)
        sheet_name :
            Sheet Name. It can be an integer (facesID), a string (sheet) or a list of previous (Default value = None)
        boundary_name :
            Boundary Name (Default value = "")
        is_infinite_gnd :
            Boolean (Default value = False)

        Returns
        -------
        :class: BoundaryObject
            Boundary Object if successful

        """

        props = {}
        sheet_name = self.modeler._convert_list_to_ids(sheet_name)
        if type(sheet_name) is list:
            if type(sheet_name[0]) is str:
                props["Objects"] = sheet_name
            else:
                props["Faces"] = sheet_name

        if boundary_type == self.BoundaryType.PerfectE:
            props['InfGroundPlane'] = is_infinite_gnd
            bound = BoundaryObject(self, boundary_name, props, 'PerfectE')
        elif boundary_type == self.BoundaryType.PerfectH:
            bound = BoundaryObject(self, boundary_name, props, 'PerfectH')
        elif boundary_type == self.BoundaryType.Aperture:
            bound = BoundaryObject(self, boundary_name, props, 'Aperture')
        elif boundary_type == self.BoundaryType.Radiation:
            props['IsFssReference'] = False
            props['IsForPML'] = False
            bound = BoundaryObject(self, boundary_name, props, 'Radiation')
        else:
            return None
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def _get_reference_and_integration_points(self, sheet, axisdir):
        objID = self.modeler.oeditor.GetFaceIDs(sheet)
        face_edges = self.modeler.primitives.get_face_edges(objID[0])
        mid_points = [self.modeler.primitives.get_edge_midpoint(i) for i in face_edges]
        if axisdir < 3:
            min_point = [1e6, 1e6, 1e6]
            max_point = [-1e6, -1e6, -1e6]
            for el in mid_points:
                if el[axisdir] < min_point[axisdir]:
                    min_point = el
                if el[axisdir] > max_point[axisdir]:
                    max_point = el
        else:
            min_point = [-1e6, -1e6, -1e6]
            max_point = [1e6, 1e6, 1e6]
            for el in mid_points:
                if el[axisdir - 3] > min_point[axisdir - 3]:
                    min_point = el
                if el[axisdir-3] < max_point[axisdir-3]:
                    max_point = el

        refid = self.modeler.primitives.get_bodynames_from_position(min_point)
        refid.remove(sheet)
        diels = self.get_all_dielectrics_names()
        for el in refid:
            if el in diels:
                refid.remove(el)

        int_start=None
        int_stop = None
        if min_point != max_point:
            int_start = min_point
            int_stop = max_point
        return refid, int_start, int_stop

    @aedt_exception_handler
    def create_wave_port_from_sheets(self, sheet, deemb=0, axisdir=0, impedance=50, nummodes=1, portname=None,
                                     renorm=True):
        """create WavePort on sheet objects created starting from sheets

        Parameters
        ----------
        sheet :
            list of input sheets from where ports will be created
        deemb :
            deembedding value distance. Float in model_units (Default value = 0)
        axisdir :
            Position of reference object. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        impedance :
            Port Impedance (Default value = 50)
        nummodes :
            Number of Modes (Default value = 1)
        portname :
            Port Name. (Default value = None)
        renorm :
            Boolean, Renormalize Mode (Default value = True)
        deembed_dist :
            Deembed Distance. Float in model units (default mm). if 0 Deembed is disabled

        Returns
        -------
        list
            list of objects created
        """
        sheet = self.modeler.convert_to_selections(sheet, True)
        portnames = []
        for obj in sheet:
            refid, int_start, int_stop = self._get_reference_and_integration_points(obj, axisdir)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname+":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                b = self._create_waveport_driven(obj, int_start, int_stop, impedance, portname, renorm, nummodes, deemb)
                if b:
                    portnames.append(b)
            else:
                faces = self.modeler.primitives.get_object_faces(obj)
                if len(refid)>0:
                    b = self._create_port_terminal(faces[0], refid, portname, iswaveport=True)
                    if b:
                        portnames.append(b)

                else:
                    return False
        return portnames

    @aedt_exception_handler
    def assign_lumped_port_to_sheet(self, sheet_name, axisdir=0, impedance=50, portname=None,
                                    renorm=True, deemb=False, reference_object_list=[]):
        """Function that Creates a Lumped taking one sheet

        Parameters
        ----------
        sheet_name :
            Sheet Name object
        axisdir :
            Integration Line direction of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        impedance :
            Port Impedance (Default value = 50)
        portname :
            Port Name. (Default value = None)
        renorm :
            bool) Renormalize Mode (Default value = True)
        deemb :
            bool) Deembed Port (Default value = False)
        reference_object_list :
            for Driven Terminal Solutions only. list of reference conductors (Default value = [])

        Returns
        -------
        type
            Object Name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)

            cond = self.get_all_conductors_names()
            touching = self.modeler.primitives.get_bodynames_from_position(point0)
            listcond = []
            for el in touching:
                if el in cond:
                    listcond.append(el)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                self._create_lumped_driven(sheet_name, point0, point1, impedance, portname, renorm, deemb)
            else:
                if not reference_object_list:
                    cond = self.get_all_conductors_names()
                    touching = self.modeler.primitives.get_bodynames_from_position(point0)
                    reference_object_list = []
                    for el in touching:
                        if el in cond:
                            reference_object_list.append(el)
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                self._create_port_terminal(faces[0], reference_object_list, portname, iswaveport=False)
            return portname
        return False

    @aedt_exception_handler
    def assig_voltage_source_to_sheet(self, sheet_name, axisdir=0, sourcename=None):
        """Function that Creates a Voltage Source taking one sheet.

        Parameters
        ----------
        sheet_name :
            Sheet name on which apply the boundary
        axisdir :
            Position of VS. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            Optional Source Name (Default value = None)

        Returns
        -------
        type
            Object Name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)
            if not sourcename:
                sourcename = generate_unique_name("Voltage")
            elif sourcename+":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Voltage")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def assign_current_source_to_sheet(self, sheet_name,  axisdir=0, sourcename=None):
        """Function that Creates a Voltage Source taking one sheet.

        Parameters
        ----------
        sheet_name :
            Sheet name on which apply the boundary
        axisdir :
            Position of VS. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            Optional Source Name (Default value = None)

        Returns
        -------
        type
            Object Name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)
            if not sourcename:
                sourcename = generate_unique_name("Current")
            elif sourcename+":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Current")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def assign_perfecte_to_sheets(self, sheet_list, sourcename=None, is_infinite_gnd=False ):
        """Function that Creates a Perfect E  taking one sheet.

        Parameters
        ----------
        sheet_list :
            Sheet name or list on which apply the boundary
        sourcename :
            Perfect E Name. (Default value = None)
        is_infinite_gnd :
            Boolean to determine if Perfect E is an Infinite Ground (Default value = False)

        Returns
        -------
        type
            Boundary Object

        """
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            if not sourcename:
                sourcename = generate_unique_name("PerfE")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectE, sheet_list, sourcename, is_infinite_gnd)
        return None

    @aedt_exception_handler
    def assign_perfecth_to_sheets(self, sheet_list, sourcename=None):
        """Function that Creates a Perfect H  taking one sheet.

        Parameters
        ----------
        sheet_list :
            list of sheets on which apply the boundary
        sourcename :
            Perfect H Name. (Default value = None)

        Returns
        -------
        type
            Boundary Object

        """
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:

            if not sourcename:
                sourcename = generate_unique_name("PerfH")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectH, sheet_list, sourcename)
        return None

    @aedt_exception_handler
    def assign_lumped_rlc_to_sheet(self, sheet_name, axisdir=0, sourcename=None, rlctype="Parallel",
                                          Rvalue=None, Lvalue=None, Cvalue=None):
        """Function that Creates a Perfect H  taking one sheet.

        Parameters
        ----------
        sheet_name :
            Name of the sheet on which apply the boundary
        axisdir :
            Position of port. it should be one of Application.AxisDir [XNeg, YNeg, ZNeg, XPos,YPos,ZPos] (Default value = 0)
        sourcename :
            Perfect H Name. (Default value = None)
        Cvalue :
            Capacitance Value in F. None to disable (Default value = None)
        Lvalue :
            Inductacnce Value in H. None to disable (Default value = None)
        rlctype :
            Parallel" or "Series" (Default value = "Parallel")
        Rvalue :
            Resistance Value in Ohm. None to disable (Default value = None)

        Returns
        -------
        type
            Object Name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] and (Rvalue or Lvalue or Cvalue):
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)

            if not sourcename:
                sourcename = generate_unique_name("Lump")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            start = [str(i) + self.modeler.primitives.model_units for i in point0]
            stop = [str(i) + self.modeler.primitives.model_units for i in point1]
            props = OrderedDict()
            props["Objects"] = [sheet_name]
            props["CurrentLine"] = OrderedDict({"Start":start, "End": stop})
            props["RLC Type"] = [rlctype]
            if Rvalue:
                props["UseResist"] = True
                props["Resistance"] = str(Rvalue)+"ohm"
            if Lvalue:
                props["UseInduct"] = True
                props["Inductance"] = str(Lvalue)+"H"
            if Cvalue:
                props["UseCap"] = True
                props["Capacitance"] = str(Cvalue)+"F"
            bound = BoundaryObject(self, sourcename, props, "LumpedRLC")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def assign_impedance_to_sheet(self, sheet_name, sourcename=None, resistance=50, reactance=0, is_infground=False):
        """Function that Creates an impedance taking one sheet.

        Parameters
        ----------
        sheet_name :
            Name of the sheet on which apply the boundary
        sourcename :
            impedance Name. (Default value = None)
        resistance :
            Resistance Value in Ohm. None to disable (Default value = 50)
        reactance :
            Reactance Value in Ohm. None to disable (Default value = 0)
        is_infground :
             (Default value = False)

        Returns
        -------
        type
            Object Name

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] :

            if not sourcename:
                sourcename = generate_unique_name("Imped")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            props = OrderedDict({"Objects": [sheet_name], "Resistance": str(resistance), "Reactance": str(reactance),
                                 "InfGroundPlane": is_infground})
            bound = BoundaryObject(self, sourcename, props, "Impedance")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def create_circuit_port_from_edges(self, edge_signal, edge_gnd, port_name="",
                                       port_impedance="50",
                                       renormalize=False, renorm_impedance="50",
                                       deembed=False):
        """Create circuit port. Integration line from edge2 to edge1
        
        renormalize impedance is ignored in driven terminal
        impedance format: - int, float, str:"50", str: "50+1i*55"

        Parameters
        ----------
        edge_signal :
            edge id
        edge_gnd :
            edge id
        port_name :
            name of the port (Default value = "")
        port_impedance :
            str impedance (Default value = "50")
        renormalize :
            bool (Default value = False)
        renorm_impedance :
            str impedance (Default value = "50")
        deembed :
            bool (Default value = False)

        Returns
        -------
        type
            bool

        """
        edge_list = [edge_signal, edge_gnd]
        if not port_name:
            port_name = generate_unique_name("Port")
        elif port_name + ":1" in self.modeler.get_excitations_name():
            port_name = generate_unique_name(port_name)

        result = self._create_circuit_port(edge_list, port_impedance, port_name, renormalize,
                                           deembed, renorm_impedance=renorm_impedance)
        if result:
            return port_name
        else:
            return False

    @aedt_exception_handler
    def edit_source(self, portandmode, powerin, phase="0deg"):
        """Setup the Power Loaded to the Filter. this is needed for thermal Analysis

        Parameters
        ----------
        powerin :
            Power (in Watt) or project variable to be put as stored energy into the the project
        portandmode :
            Portname and mode. Example Port1:1
        phase :
             (Default value = "0deg")

        Returns
        -------

        """
        self._messenger.add_info_message("Setting Up Power to Eigemode " + powerin + "Watt")
        if self.solution_type != "Eigenmode":
            self.osolution.EditSources([["IncludePortPostProcessing:=", True, "SpecifySystemPower:=", False],
                                        ["Name:=", portandmode, "Magnitude:=", powerin, "Phase:=", phase]])
        else:
            self.osolution.EditSources(
                [["FieldType:=", "EigenStoredEnergy"], ["Name:=", "Modes", "Magnitudes:=", [powerin]]])
        return True

    @aedt_exception_handler
    def thicken_port_sheets(self, inputlist, value, internalExtr=True, internalvalue=1):
        """thicken_port_sheets: create thicken sheets of value "mm" over the full list of input port faces inputlist
        inputlist: list of faces to thicken
        value: value in mm to thicken
        internalExtr: define if the sheet must also be extruded internally
        internalvalue: define the value in mm to thicken internally the sheet (vgoing into the model)

        Parameters
        ----------
        inputlist :
            
        value :
            
        internalExtr :
             (Default value = True)
        internalvalue :
             (Default value = 1)

        Returns
        -------

        """
        tol = 1e-6
        ports_ID={}
        aedt_bounding_box = self.modeler.primitives.get_model_bounding_box()
        directions = {}
        for el in inputlist:
            objID = self.modeler.oeditor.GetFaceIDs(el)
            faceCenter = self.modeler.oeditor.GetFaceCenter(int(objID[0]))
            directionfound = False
            l = 10
            while not directionfound:
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", str(l) + "mm",
                        "BothSides:=", False
                    ])
                # aedt_bounding_box2 = self._oeditor.GetModelBoundingBox()
                aedt_bounding_box2 = self.modeler.primitives.get_model_bounding_box()
                self._odesign.Undo()
                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "External"
                    directionfound = True
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", "-" + str(l) + "mm",
                        "BothSides:=", False
                    ])
                # aedt_bounding_box2 = self._oeditor.GetModelBoundingBox()
                aedt_bounding_box2 = self.modeler.primitives.get_model_bounding_box()

                self._odesign.Undo()

                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "Internal"
                    directionfound = True
                else:
                    l = l + 10
        for el in inputlist:
            objID = self.modeler.oeditor.GetFaceIDs(el)
            maxarea = 0
            for f in objID:
                faceArea = self.modeler.primitives.get_face_area(int(f))
                if faceArea > maxarea:
                    maxarea = faceArea
                    faceCenter = self.modeler.oeditor.GetFaceCenter(int(f))
            if directions[el] == "Internal":
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", "-" + str(value) + "mm",
                        "BothSides:=", False
                    ])
            else:
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", str(value) + "mm",
                        "BothSides:=", False
                    ])
            if "Vacuum" in el:
                newfaces = self.modeler.oeditor.GetFaceIDs(el)
                for f in newfaces:
                    try:
                        fc2 = self.modeler.oeditor.GetFaceCenter(f)
                        fc2 = [float(i) for i in fc2]
                        fa2 = self.modeler.primitives.get_face_area(int(f))
                        faceoriginal = [float(i) for i in faceCenter]
                        #dist = mat.sqrt(sum([(a*a-b*b) for a,b in zip(faceCenter, fc2)]))
                        if abs(fa2 - maxarea) < tol**2 and (abs(faceoriginal[2] - fc2[2]) > tol or abs(
                                faceoriginal[1] - fc2[1]) > tol or abs(faceoriginal[0] - fc2[0]) > tol):
                            ports_ID[el] = int(f)

                        # if (abs(faceoriginal[0] - fc2[0]) < tol and abs(faceoriginal[1] - fc2[1]) < tol and abs(
                        #         faceoriginal[2] - fc2[2]) > tol) or (
                        #         abs(faceoriginal[0] - fc2[0]) < tol and abs(faceoriginal[1] - fc2[1]) > tol and abs(
                        #         faceoriginal[2] - fc2[2]) < tol) or (
                        #         abs(faceoriginal[0] - fc2[0]) > tol and abs(faceoriginal[1] - fc2[1]) < tol and abs(
                        #         faceoriginal[2] - fc2[2]) < tol):
                        #     ports_ID[el] = int(f)
                    except:
                        pass
            if internalExtr:
                objID2 = self.modeler.oeditor.GetFaceIDs(el)
                for fid in objID2:
                    try:
                        faceCenter2 = self.modeler.oeditor.GetFaceCenter(int(fid))
                        if faceCenter2 == faceCenter:
                            self.modeler.oeditor.MoveFaces(
                                [
                                    "NAME:Selections",
                                    "Selections:=", el,
                                    "NewPartsModelFlag:=", "Model"
                                ],
                                [
                                    "NAME:Parameters",
                                    [
                                        "NAME:MoveFacesParameters",
                                        "MoveAlongNormalFlag:=", True,
                                        "OffsetDistance:=", str(internalvalue) + "mm",
                                        "MoveVectorX:=", "0mm",
                                        "MoveVectorY:=", "0mm",
                                        "MoveVectorZ:=", "0mm",
                                        "FacesToMove:=", [int(fid)]
                                    ]
                                ])
                    except:
                        self.messenger.add_debug_message("done")
                        # self.modeler_oproject.ClearMessages()
        return ports_ID

    @aedt_exception_handler
    def validate_full_design(self, dname=None, outputdir=None, ports=None):
        """Validate the design based on expected value and save infos on log file
        and also returns the validation info in a list

        Parameters
        ----------
        dname :
            optional, name of design to validate (Default value = None)
        outputdir :
            optional, output dir where to save the log file (Default value = None)
        ports :
            number of excitations (sum of modes) expected (Default value = None)

        Returns
        -------
        type
            all the info in a list for use later

        """
        self._messenger.add_debug_message("Design Validation Checks")
        validation_ok = True
        val_list = []
        if not dname:
            dname = self.design_name
        if not outputdir:
            outputdir = self.project_path
        pname = self.project_name
        validation_log_file = os.path.join(outputdir, pname + "_" + dname + "_validation.log")

        # Desktop Messages
        msg = "Desktop Messages:"
        val_list.append(msg)
        temp_msg = list(self._desktop.GetMessages(pname, dname, 0))
        if temp_msg:
            temp2_msg = [i.strip('Project: ' + pname + ', Design: ' + dname + ', ').strip('\r\n') for i in temp_msg]
            val_list.extend(temp2_msg)

        # Run Design Validation and write out the lines to the logger
        temp_val_file = os.path.join(os.environ['TEMP'], "\\val_temp.log")
        simple_val_return = self.validate_simple(temp_val_file)
        if simple_val_return == 1:
            msg = "Design validation check PASSED!"
        elif simple_val_return == 0:
            msg = "Design validation check ERROR!"
            validation_ok = False
        val_list.append(msg)
        msg = "Design Validation Messages:"
        val_list.append(msg)
        if os.path.isfile(temp_val_file):
            with open(temp_val_file, 'r') as df:
                temp = df.read().splitlines()
                val_list.extend(temp)
            os.remove(temp_val_file)
        else:
            msg = "** No Design Validation File found **"
            self._messenger.add_debug_message(msg)
            val_list.append(msg)
        msg = "-- End of Design Validation Messages"
        val_list.append(msg)

        # Find the Excitations and check or list them out
        msg = "Excitations Check:"
        val_list.append(msg)
        if self.solution_type != 'Eigenmode':
            detected_excitations = self.modeler.get_excitations_name()
            if ports:
                if self.solution_type == 'DrivenTerminal':
                    ports_t = ports * 2  # for each port we have terminal and reference excitation
                else:
                    ports_t = ports
                if ports_t != len(detected_excitations):
                    msg = "** Port Number Error! - Please check model **"
                    self._messenger.add_error_message(msg)
                    val_list.append(msg)
                    validation_ok = False
                else:
                    msg1 = "Solution type: " + str(self.solution_type)
                    msg2 = "Ports Requested: " + str(ports)
                    msg3 = "Defined excitations number: " + str(len(detected_excitations))
                    msg4 = "Defined excitations names: " + str(detected_excitations)
                    val_list.append(msg1)
                    val_list.append(msg2)
                    val_list.append(msg3)
                    val_list.append(msg4)
        else:
            msg = "Eigen Model Detected - no excitatons defined"
            self._messenger.add_debug_message(msg)
            val_list.append(msg)

        # Find the number of analysis setups and output the info
        msg = "Analysis Setup Messages:"
        val_list.append(msg)
        setups = list(self.oanalysis.GetSetups())
        if setups:
            msg = "Detected setup and sweep: "
            val_list.append(msg)
            for setup in setups:
                msg = str(setup)
                val_list.append(msg)
                if self.solution_type != 'EigenMode':
                    sweepsname = self.oanalysis.GetSweeps(setup)
                    if sweepsname:
                        for sw in sweepsname:
                            msg = ' |__ ' + sw
                            val_list.append(msg)
        else:
            msg = 'No setup detected!'
            val_list.append(msg)

        with open(validation_log_file, "w") as f:
            for item in val_list:
                f.write("%s\n" % item)
        return val_list, validation_ok  # return all the info in a list for use later


    @aedt_exception_handler
    def create_scattering(self, PlotName="S Parameter Plot Nominal", sweep_name=None, PortNames=None, PortExcited=None, variations=None ):
        """Create Scattering Report
        
        
        sweeps = design eXploration variations (list of str)
        PortNames = (list of str)
        PortExcited = (str)
        :return:

        Parameters
        ----------
        PlotName :
             (Default value = "S Parameter Plot Nominal")
        sweep_name :
             (Default value = None)
        PortNames :
             (Default value = None)
        PortExcited :
             (Default value = None)
        variations :
             (Default value = None)

        Returns
        -------

        """
        # set plot name
        # Setup arguments list for CreateReport function
        Families = ["Freq:=", ["All"]]
        if variations:
            Families += variations
        else:
            Families += self.get_nominal_variation()
        if not sweep_name:
            sweep_name = self.existing_analysis_sweeps[1]
        elif sweep_name not in self.existing_analysis_sweeps:
            self.messenger.add_error_message("Setup {} doesn't exist in Setup list".format(sweep_name))
            return False
        if not PortNames:
            PortNames = self.modeler.get_excitations_name()
        full_matrix = False
        if not PortExcited:
            PortExcited = PortNames
            full_matrix = True
        if type(PortNames) is str:
            PortNames = [PortNames]
        if type(PortExcited) is str:
            PortExcited = [PortExcited]
        list_y = []
        for p in list(PortNames):
            for q in list(PortExcited):
                if not full_matrix:
                    list_y.append("dB(S(" + p + "," + q + "))")
                elif PortExcited.index(q) >= PortNames.index(p):
                    list_y.append("dB(S(" + p + "," + q + "))")

        Trace = ["X Component:=", "Freq", "Y Component:=", list_y]
        solution_data = ""
        if self.solution_type == "DrivenModal":
            solution_data = "Modal Solution Data"
        elif self.solution_type == "DrivenTerminal":
            solution_data = "Terminal Solution Data"
        if solution_data != "":
            # run CreateReport function

            self.post.oreportsetup.CreateReport(
                PlotName,
                solution_data,
                "Rectangular Plot",
                sweep_name,
                ["Domain:=", "Sweep"],
                Families,
                Trace,
                [])
            return True
        return False

        # export the image

    @aedt_exception_handler
    def create_qfactor_report(self, project_dir, outputlist, setupname, plotname, Xaxis="X"):
        """Function that export CSV of eigenQ Plot

        Parameters
        ----------
        project_dir :
            Output dir
        outputlist :
            output quantity, in this case, Q-factor
        setupname :
            Name of the setup from which generate the report
        plotname :
            name of the plot
        Xaxis :
            Xasis value (default "X")

        Returns
        -------

        """
        npath = os.path.normpath(project_dir)

        # Setup arguments list for createReport function
        args = [Xaxis + ":=", ["All"]]
        args2 = ["X Component:=", Xaxis, "Y Component:=", outputlist]

        self.post.post_oreport_setup.CreateReport(plotname, "Eigenmode Parameters", "Rectangular Plot",
                                                  setupname + " : LastAdaptive", [], args, args2, [])
        return True

    @aedt_exception_handler
    def export_touchstone(self, solutionname, sweepname, filename=None, variation=[], variations_value=[]):
        """Synopsis: Export Touchston file to local folder
        
        
        solutionname = name of the solution solved
        sweepname = name of the sweep solved
        FileName = full path of output file
        Variations = list (list of all parameters variations e.g. ["$AmbientTemp", "$PowerIn"] )
        VariationsValue = list (list of all parameters variations value) e.g. ["22cel", "100"] )

        Parameters
        ----------
        solutionname :
            
        sweepname :
            
        filename :
             (Default value = None)
        variation :
             (Default value = [])
        variations_value :
             (Default value = [])

        Returns
        -------

        """

        # normalize the save path
        if not filename:
            appendix = ""
            for v, vv in zip(variation,variations_value):
                appendix += "_"+ v + vv.replace("\'","")
            ext = ".S" + str(self.oboundary.GetNumExcitations())+"p"
            filename = os.path.join(self.project_path, solutionname +"_"+ sweepname + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        print("Exporting Touchstone " + filename)
        DesignVariations = ""
        i=0
        for el in variation:
            DesignVariations += str(variation[i]) + "=\'" + str(variations_value[i].replace("\'", "")) + "\' "
            i+=1
            # DesignVariations = "$AmbientTemp=\'22cel\' $PowerIn=\'100\'"
        # array containing "SetupName:SolutionName" pairs (note that setup and solution are separated by a colon)
        SolutionSelectionArray = [solutionname + ":" + sweepname]
        # 2=tab delimited spreadsheet (.tab), 3= touchstone (.sNp), 4= CitiFile (.cit),
        # 7=Matlab (.m), 8=Terminal Z0 spreadsheet
        FileFormat = 3
        OutFile = filename  # full path of output file
        FreqsArray = ["all"]  # array containin the frequencies to export, use ["all"] for all frequencies
        DoRenorm = True  # perform renormalization before export
        RenormImped = 50  # Real impedance value in ohm, for renormalization
        DataType = "S"  # Type: "S", "Y", or "Z" matrix to export
        Pass = -1  # The pass to export. -1 = export all passes.
        ComplexFormat = 0  # 0=Magnitude/Phase, 1=Real/Immaginary, 2=dB/Phase
        DigitsPrecision = 15  # Touchstone number of digits precision
        IncludeGammaImpedance = True  # Include Gamma and Impedance in comments
        NonStandardExtensions = False  # Support for non-standard Touchstone extensions

        self.osolution.ExportNetworkData(DesignVariations, SolutionSelectionArray, FileFormat,
                                         OutFile, FreqsArray, DoRenorm, RenormImped, DataType, Pass,
                                         ComplexFormat, DigitsPrecision, False, IncludeGammaImpedance,
                                         NonStandardExtensions)
        return True


    @aedt_exception_handler
    def set_export_touchstone(self, activate):
        """Set Automatic export of touchstone after simulation to True

        Parameters
        ----------
        activate : bool
            Export after simulation

        Returns
        -------
        type
            True if operation succeeded

        """

        settings = []
        if activate:
            settings.append("NAME:Design Settings Data")
            settings.append("Export After Simulation:=")
            settings.append(True)
            settings.append("Export Dir:=")
            settings.append("")
        elif not activate:
            settings.append("NAME:Design Settings Data")
            settings.append("Export After Simulation:=")
            settings.append(False)
        self.odesign.SetDesignSettings(settings)
        return True

    @aedt_exception_handler
    def assign_radiation_boundary_to_objects(self, obj_names, boundary_name=""):
        """

        Parameters
        ----------
        obj_names :
            
        boundary_name :
             (Default value = "")

        Returns
        -------

        """
        #TODO: to be tested

        """
        Assign radiation boundary to one or more objects (usually airbox object)

        :param obj_names: objects name or id to which the boundary condition is assigned
        :param boundary_name: optional, name of the boundary
        :return: True if correctly assigned
        """
        object_list = self.modeler.convert_to_selections(obj_names, return_list=True)
        if boundary_name:
            rad_name = boundary_name
        else:
            rad_name = generate_unique_name("Rad_")
        return self.create_boundary(self.BoundaryType.Radiation, object_list,rad_name)

    @aedt_exception_handler
    def assign_radiation_boundary_to_faces(self, faces_id, boundary_name=""):
        """Assign radiation boundary to one or more objects (usually airbox object)

        Parameters
        ----------
        faces_id :
            face id to which the boundary condition is assigned
        boundary_name :
            optional, name of the boundary (Default value = "")

        Returns
        -------
        type
            True if correctly assigned

        """
        if type(faces_id) is not list:
            faces_list = [int(faces_id)]
        else:
            faces_list = [int(i) for i in faces_id]
        if boundary_name:
            rad_name = boundary_name
        else:
            rad_name = generate_unique_name("Rad_")
        return self.create_boundary(self.BoundaryType.Radiation, faces_list, rad_name)

