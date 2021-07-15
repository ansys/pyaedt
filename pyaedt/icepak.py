"""This module contains the `Icepak` class."""

from __future__ import absolute_import
import csv
import math
import os
import re
from .application.AnalysisIcepak import FieldAnalysisIcepak
from .desktop import exception_to_desktop
from .generic.general_methods import generate_unique_name, aedt_exception_handler
from .modules.Boundary import BoundaryObject
from  collections import OrderedDict


class Icepak(FieldAnalysisIcepak):
    """Icepak application interface.

    This class allows you to connect to an existing Icepack design or create a
    new Icepak design if one does not exist.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
        case an attempt is made to get an active project. If no 
        projects are present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in 
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, which applies the default type.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or 
        nothing is used.
    specified_version: str, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is  used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default 
        is``False``, which launches AEDT in the graphical mode.  
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. 
    student_version : bool, optional
        Whether open AEDT Student Version. The default is ``False``.

    Examples
    --------
    Create an instance of `Icepak` and connect to an existing Icepak
    design or create a new Icepak design if one does not exist.

    >>> from pyaedt import Icepak
    >>> aedtapp = Icepak()

    Create an instance of `Icepak` and link to a project named
    ``projectname``. If this project does not exist, create one with
    this name.

    >>> aedtapp = Icepak(projectname)

    Create an instance of `Icepak` and link to a design named
    ``designname`` in a project named ``projectname``.

    >>> aedtapp = Icepak(projectname,designame)

    Create an instance of `Icepak` and open the specified project,
    which is ``myfile.aedt``.

    >>> aedtapp = Icepak("myfile.aedt")

    Create an instance of `Icepak` using the 2021 R1 release and
    open the specified project, which is ``myfile.aedt``.

    >>> aedtapp = Icepak(specified_version="2021.1", projectname="myfile.aedt")

    """
    
    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        FieldAnalysisIcepak.__init__(self, "Icepak", projectname, designname, solution_type, setup_name,
                                     specified_version, NG, AlwaysNew, release_on_exit, student_version)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        ''' Push exit up to parent object Design '''
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    @property
    def existing_analysis_sweeps(self):
        """List the existing analysis setups.       

        Returns
        -------
        list
            List of all defined analysis setup names in the Maxwell design.
            
        """
        setup_list = self.existing_analysis_setups
        sweep_list=[]
        s_type = self.solution_type
        for el in setup_list:
                sweep_list.append(el + " : " +s_type)
        return sweep_list

    @aedt_exception_handler
    def assign_openings(self, air_faces):
        """Assign openings to a list of faces.

        Parameters
        ----------
        air_faces : list
            List of face names.

        Returns
        -------
        type
            Bound object when successful or ``None`` when failed.

        """

        boundary_name = generate_unique_name("Opening")
        self.modeler.create_face_list(air_faces, "boundary_faces")
        props = {}
        air_faces = self.modeler._convert_list_to_ids(air_faces)

        props["Faces"] = air_faces
        props["Temperature"] = "AmbientTemp"
        props["External Rad. Temperature"] = "AmbientRadTemp"
        props["Inlet Type"] = "Pressure"
        props["Total Pressure"] = "AmbientPressure"
        bound = BoundaryObject(self, boundary_name, props, 'Opening')
        if bound.create():
            self.boundaries.append(bound)
            self._messenger.add_info_message("Opening Assigned")
            return bound
        return None

    @aedt_exception_handler
    def assign_2way_coupling(self,setup_name=None, number_of_iterations=2, continue_ipk_iterations=True, ipk_iterations_per_coupling=20):
        """Assign two-way coupling to a specific setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.
        number_of_iterations : int, optional
            Number of iterations. The default is ``2``.
        continue_ipk_iterations : bool, optional
           Whether to continue Icepak iterations. The default is ``True``.
        ipk_iterations_per_coupling : int, optional
            Additional iterations per coupling. The default is ``20``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        if not setup_name:
            if self.setups:
                setup_name =self.setups[0].name
            else:
                self._messenger.add_error_message("No Setup Defined")
                return False
        self.oanalysis_setup.AddTwoWayCoupling(setup_name, ["NAME:Options", "NumCouplingIters:=", number_of_iterations,
                                                            "ContinueIcepakIterations:=", continue_ipk_iterations,
                                                            "IcepakIterationsPerCoupling:=",
                                                            ipk_iterations_per_coupling])
        return True

    @aedt_exception_handler
    def create_source_blocks_from_list(self, list_powers, assign_material=True, default_material="Ceramic_material"):
        """Assign to a box in Icepak the sources that coming from the CSV file. 
        
        Assignment is made by name.

        Parameters
        ----------
        list_powers : list
            List of input powers. It is a list of list like in this examples: 
            ``[["Obj1", 1], ["Obj2", 3]]``. The list can contain multiple 
            columns for power inputs.
        assign_material : bool, optional
            Whether to assign a material. The default is ``True``.
        default_material : str, optional
            Default material. The default is ``"Ceramic_material"``.

        Returns
        -------
        type
            List of boundaries inserted.

        """
        oObjects = self.modeler.primitives.solid_names
        listmcad = []
        num_power = None
        for row in list_powers:
            if not num_power:
                num_power = len(row)-1
                self["P_index"] = 0
            if row[0] in oObjects:
                listmcad.append(row)
                if num_power>1:
                    self[row[0]+"_P"] = str(row[1:])
                    out = self.create_source_block(row[0], row[0]+"_P[P_index]", assign_material, default_material)

                else:
                    out = self.create_source_block(row[0], str(row[1]) + "W", assign_material, default_material)
                if out:
                    listmcad.append(out)

        return listmcad

    @aedt_exception_handler
    def create_source_block(self, object_name, input_power, assign_material=True, material_name="Ceramic_material", use_object_for_name=True):
        """Create a source block for an object.

        Parameters
        ----------
        object_name : str
            Name of the object.
        input_power : str or var
            Input power. 
        assign_material : bool, optional
            Whether to assign a material. The default is ``True``.
        material_name :
            Material to assign if ``assign_material=True``. The default is ``"Ceramic_material"``.
        use_object_for_name : bool, optional
             The default is ``True``.

        Returns
        -------
        type
            Bound object when successful or ``None`` when failed.

        """
        if assign_material:
            self.modeler.primitives[object_name].material_name = material_name
        props={}
        props["Objects"] = [object_name]
        props["Block Type"] = "Solid"
        props["Use External Conditions"] = False
        props["Total Power"] = input_power
        if use_object_for_name:
            boundary_name = object_name
        else:
            boundary_name = generate_unique_name("Block")

        bound = BoundaryObject(self, boundary_name, props, 'Block')
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return None

    @aedt_exception_handler
    def create_source_power(self, face_id, input_power="0W", thermal_condtion="Total Power",
                            surface_heat="0irrad_W_per_m2", temperature="AmbientTemp", 
                            radiate=False, source_name=None):
        """Create a source power for a face.

        Parameters
        ----------
        face_id : int
            Face ID.
        input_power : str, float, or int, optional
            Input power.
        surface_heat : str, optional
            Surface heat.  The default is ``"0irrad_W_per_m2"``.
        temperature : str, optional
            Type of the temperature. The default is ``"AmbientTemp"``.
        radiate : bool
            Whether to enable radiation. The default is ``False``.
        source_name : str, optional
            Name of the source. The default is ``None``.
        Returns
        -------
        BoundaryObject
            Boundary object when successful or ``None`` when failed.
        """
        if not source_name:
            source_name = generate_unique_name("Source")
        props={}
        props["Faces"] = [face_id]
        props["Thermal Condition"] = thermal_condtion
        props["Total Power"] = input_power
        props["Surface Heat"] = surface_heat
        props["Temperature"] = temperature
        props["Radiation"] = OrderedDict({"Radiate" : radiate})
        bound = BoundaryObject(self, source_name, props, 'SourceIcepak')
        if bound.create():
            self.boundaries.append(bound)
            return bound

    @aedt_exception_handler
    def create_network_block(self, object_name, power, rjc, rjb, gravity_dir, top, assign_material=True,
                             default_material="Ceramic_material", use_object_for_name=True):
        """Create a network block.

        Parameters
        ----------
        object_name : str
            Name of the object to create the block for.
        power : str or var
            Input power.
        rjc :
            RJC value.
        rjb :
            RJB value.
        gravity_dir :
            Gravity direction from -X to +Z. Options are ``0`` through ``5``. 
        top :
            Board bounding value in mm of the top face.
        assign_material : bool, optional
            Whether to assign a material. The default is ``True``.
        default_material : str, optional
            Default material if ``assign_material=True``. The default is ``"Ceramic_material"``.
        use_object_for_name : bool, optional
             The default is ``True``.

        Returns
        -------
        type
            Bounding object when successful.
        """
        if object_name in self.modeler.primitives.object_names:
            faces = self.modeler.primitives.get_object_faces(object_name)
            k = 0
            faceCenter = {}
            for f in faces:
                faceCenter[f] = self.modeler.oeditor.GetFaceCenter(int(f))
                faceCenter[f] = [round(float(i), 1) for i in faceCenter[f]]
                k = k + 1
            fcmax = -1e9
            fcmin = 1e9
            fcrjc = None
            fcrjb = None
            for fc in faceCenter:
                fc1 = faceCenter[fc]
                if fc1[gravity_dir] < fcmin:
                    fcmin = fc1[gravity_dir]
                    fcrjc = int(fc)
                if fc1[gravity_dir] > fcmax:
                    fcmax = fc1[gravity_dir]
                    fcrjb = int(fc)
            if fcmax < float(top):
                app = fcrjc
                fcrjc = fcrjb
                fcrjb = app
            if assign_material:
                self.modeler.primitives[object_name].material_name = default_material
            props = {}
            if use_object_for_name:
                boundary_name = object_name
            else:
                boundary_name = generate_unique_name("Block")
            props["Faces"] = [fcrjc, fcrjb]
            props["Nodes"] = OrderedDict({"Face" + str(fcrjc): [fcrjc, "NoResistance"],
                              "Face" + str(fcrjb): [fcrjb, "NoResistance"], "Internal": [power]})
            props["Links"] = OrderedDict({"Link1": ["Face" + str(fcrjc), "Internal", "R", str(rjc) + "cel_per_w"],
                              "Link2": ["Face" + str(fcrjb), "Internal", "R", str(rjb) + "cel_per_w"]})
            props["SchematicData"] = OrderedDict({})
            bound = BoundaryObject(self, boundary_name, props, 'Network')
            if bound.create():
                self.boundaries.append(bound)
                self.modeler.primitives[object_name].solve_inside = False
                return bound
            return None

    @aedt_exception_handler
    def create_network_blocks(self, input_list, gravity_dir, top, assign_material=True,
                             default_material="Ceramic_material"):
        """Create network blocks from CSV files.

        Parameters
        ----------
        input_list : list
            List of sources with inputs  ``rjc``,  ``rjb``, and ``power``. 
            For example: ``[[Objname1, rjc, rjb, power1,power2....],[Objname2, rjc2, rbj2, power1, power2...]]``.
        gravity_dir : int
            Gravity direction from -X to +Z. Options are ``0`` to ``5``.
        top :
            Board bounding value in mm of the top face.
        assign_material : bool, optional
            Whether to assign a material. The default is ``True``.
        default_material : str, optional
            Default material if ``assign_material=True``. The default is ``"Ceramic_material"``.
       
        Returns
        -------
        type
            Networks boundary objects.
        """
        objs = self.modeler.primitives.solid_names
        countpow = len(input_list[0])-3
        networks = []
        for row in input_list:
            if row[0] in objs:
                if countpow>1:
                    self[row[0] + "_P"] = str(row[3:])
                    self["P_index"] = 0
                    out = self.create_network_block(row[0], row[0] + "_P[P_index]", row[1], row[2], gravity_dir, top,
                                                    assign_material, default_material)
                else:
                    if not row[3]:
                        pow="0W"
                    else:
                        pow=str(row[3])+"W"
                    out = self.create_network_block(row[0], pow, row[1], row[2], gravity_dir,
                                                    top, assign_material, default_material)
                if out:
                    networks.append(out)
        return networks

    @aedt_exception_handler
    def assign_surface_monitor(self, face_name, monitor_type="Temperature", monitor_name=None):
        """Assign a surface monitor.

        Parameters
        ----------
        face_name : str
            Name of the face.
        monitor_type : str, optional
            Type of the monitor.  The default ``"Temperature"``.
        monitor_name : str, optional
            Name of the monitor.  The default is ``None``, in which case
            a default name is assigned automatically.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not monitor_name:
            monitor_name = generate_unique_name("Monitor")
        oModule = self.odesign.GetModule("Monitor")
        oModule.AssignFaceMonitor(["NAME:" + monitor_name, "Quantities:=", [monitor_type], "Objects:=", [face_name]])
        return True

    @aedt_exception_handler
    def assign_point_monitor(self, point_position, monitor_type="Temperature", monitor_name=None):
        """Create and assign a point monitor.

        Parameters
        ----------
        point_position : str
            Name of the point.
        monitor_type : str, optional
            Type of the monitor. The default is ``"Temperature"``.
        monitor_name : str, optional
            Name of the monitor. The default is ``None``, in which case 
            a default name is assigned automatically.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        point_name = generate_unique_name("Point")
        self.modeler.oeditor.CreatePoint(
            ["NAME:PointParameters", "PointX:=", self.modeler.primitives._arg_with_dim(point_position[0]), "PointY:=",
             self.modeler.primitives._arg_with_dim(point_position[1]), "PointZ:=",
             self.modeler.primitives._arg_with_dim(point_position[2])],
            ["NAME:Attributes", "Name:=", point_name, "Color:=", "(143 175 143)"])
        if not monitor_name:
            monitor_name = generate_unique_name("Monitor")
        oModule = self.odesign.GetModule("Monitor")
        oModule.AssignPointMonitor(["NAME:" + monitor_name, "Quantities:=", [monitor_type], "Points:=", [point_name]])
        return True


    @aedt_exception_handler
    def assign_block_from_sherlock_file(self, csv_name):
        """Assign block power to components based on a CSV file from Sherlock.

        Parameters
        ----------
        csv_name : str
            Name of the CSV file.

        Returns
        -------
        type
            Total power applied.
        """
        with open(csv_name) as csvfile:
            csv_input = csv.reader(csvfile)
            component_header = next(csv_input)
            data = list(csv_input)
            k = 0
            component_data = {}
            for el in component_header:
                component_data[el] = [i[k] for i in data]
                k += 1
        total_power = 0
        i=0
        all_objects = self.modeler.primitives.object_names
        for power in component_data["Applied Power (W)"]:
            try:
                float(power)
                if "COMP_" + component_data["Ref Des"][i] in all_objects:
                    status = self.create_source_block("COMP_" + component_data["Ref Des"][i], str(power)+"W",assign_material=False)
                    if not status:
                        self._messenger.add_warning_message(
                            "Warning. Block {} skipped with {}W power".format(component_data["Ref Des"][i], power))
                    else:
                        total_power += float(power)
                        # print("Block {} created with {}W power".format(component_data["Ref Des"][i], power))
                elif component_data["Ref Des"][i] in all_objects:
                    status = self.create_source_block(component_data["Ref Des"][i], str(power)+"W",assign_material=False)
                    if not status:
                        self._messenger.add_warning_message(
                            "Warning. Block {} skipped with {}W power".format(component_data["Ref Des"][i], power))
                    else:
                        total_power += float(power)
                        # print("Block {} created with {}W power".format(component_data["Ref Des"][i], power))
            except:
                pass
            i += 1
        self._messenger.add_info_message("Blocks inserted with total power {}W".format(total_power))
        return total_power

    @aedt_exception_handler
    def assign_priority_on_intersections(self, component_prefix="COMP_"):
        """Validate an Icepak design.
        
        If there are intersections, priorities are automatically applied to overcome simulation issues.

        Parameters
        ----------
        component_prefix: str, optional
            Component prefix to search for. The default is ``"COMP_"``.

        Returns
        -------
        bool
             ``True`` when successful, ``False`` when failed.     
        """
        temp_log = os.path.join(self.project_path, "validation.log")
        validate = self.odesign.ValidateDesign(temp_log)
        self.save_project()
        i = 2
        if validate == 0:
            priority_list = []
            with open(temp_log, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if '[error]' in line and component_prefix in line and "intersect" in line:
                        id1 = line.find(component_prefix)
                        id2 = line[id1:].find("\"")
                        name = line[id1:id1 + id2]
                        if name not in priority_list:
                            priority_list.append(name)
            print("{} Intersections have been found. Applying Priorities".format(len(priority_list)))
            for objname in priority_list:
                self.mesh.add_priority(1, [objname], priority=i)
                i += 1
        return True

    @aedt_exception_handler
    def find_top(self, gravityDir):
        """Find the top location of the layout given a gravity.

        Parameters
        ----------
        gravityDir :
            Gravity direction from -X to +Z. Choices are ``0`` to ``5``

        Returns
        -------
        float
            Top position
        """
        dirs = ["-X", "+X", "-Y", "+Y", "-Z", "+Z"]
        for dir in dirs:
            argsval = ["NAME:" + dir + " Padding Data", "Value:=", "0"]
            args = ["NAME:AllTabs", ["NAME:Geometry3DCmdTab", ["NAME:PropServers", "Region:CreateRegion:1"],
                                     ["NAME:ChangedProps", argsval]]]
            self.modeler.oeditor.ChangeProperty(args)
        oBoundingBox = self.modeler.get_model_bounding_box()
        if gravityDir < 3:
            return oBoundingBox[gravityDir + 3]
        else:
            return oBoundingBox[gravityDir - 3]

    @aedt_exception_handler
    def create_parametric_fin_heat_sink(self, hs_height=100, hs_width=100, hs_basethick=10, pitch=20, thick=10, length=40, height=40,
                                        draftangle=0, patternangle=10, separation=5, symmetric=True, symmetric_separation=20,
                                        numcolumn_perside=2, vertical_separation=10, matname="Al-Extruded", center = [0,0,0],
                                        plane_enum=0, rotation=0, tolerance=1e-3):
        """Create a parametric heat sink.

        Parameters
        ----------
        hs_height : int, optional
            Height of the heat sink. The default is ``100``.
        hs_width: int, optional
            Width of the heat sink. The default is ``100``.
        hs_basethick : int, optional
            Thickness of the heat sink base. The default is ``100``.
        pitch: optional
            Pitch of the heat sink. The default is ``10``.
        thick : optional
            Thickness of the heatsink. The default is ``10``.
        length: optional
            The default is ``40``.
        height : optional
            Height of the heatsink.  The default is ``40``.
        draftangle : optional
            Draft angle.  The default is ``0``.
        patternangle : optional
            Pattern angle.  The default is ``10``.
        separation : optional
            The default is ``5``.
        symmetric : bool, optional
            Whether the heatsink is symmetric.  The default is ``True``.
        symmetric_separation: optional
            The default is ``20``.
        numcolumn_perside : int, optional
            Number of columns per side. The default is ``2``.
        vertical_separation: optional
            The default is ``10``.
        matname : str, optional
            Name of the material. The default is ``Al-Extruded``.
        center : list, optional
           Center of the heatsink.  The default is ``[0, 0, 0]``.
        plane_enum : optional
            The default is ``0``.
        rotation : optional
            The default is ``0``.
        tolerance : optional
            The default is ``1e-3``.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        all_objs = self.modeler.primitives.object_names
        self['FinPitch'] = self.modeler.primitives._arg_with_dim(pitch)
        self['FinThickness'] = self.modeler.primitives._arg_with_dim(thick)
        self['FinLength'] = self.modeler.primitives._arg_with_dim(length)
        self['FinHeight'] = self.modeler.primitives._arg_with_dim(height)
        self['DraftAngle'] = draftangle
        self['PatternAngle'] = patternangle
        self['FinSeparation'] = self.modeler.primitives._arg_with_dim(separation)
        self['VerticalSeparation'] = self.modeler.primitives._arg_with_dim(vertical_separation)
        self['HSHeight'] = self.modeler.primitives._arg_with_dim(hs_height)
        self['HSWidth'] = self.modeler.primitives._arg_with_dim(hs_width)
        self['HSBaseThick'] = self.modeler.primitives._arg_with_dim(hs_basethick)
        if numcolumn_perside>1:
            self['NumColumnsPerSide'] = numcolumn_perside
        if symmetric:
            self['SymSeparation'] = self.modeler.primitives._arg_with_dim(symmetric_separation)
        # ipk['PatternDirection'] = 'Y'
        # ipk['LengthDirection'] = 'X'
        # ipk['HeightDirection'] = 'Z'
        self['Tolerance'] = self.modeler.primitives._arg_with_dim(tolerance)

        #self.modeler.primitives.create_box([0, 0, '-HSBaseThick'], ['HSWidth', 'HSHeight', 'FinHeight+HSBaseThick'], "Outline")
        self.modeler.primitives.create_box(['-HSWidth/200', '-HSHeight/200', '-HSBaseThick'], ['HSWidth*1.01', 'HSHeight*1.01', 'HSBaseThick+Tolerance'], "HSBase", matname)
        Fin_Line = []
        Fin_Line.append(self.Position(0, 0, 0))
        Fin_Line.append(self.Position(0, 'FinThickness', 0))
        Fin_Line.append(self.Position('FinLength', 'FinThickness + FinLength*sin(PatternAngle*3.14/180)', 0))
        Fin_Line.append(self.Position('FinLength', 'FinLength*sin(PatternAngle*3.14/180)', 0))
        Fin_Line.append(self.Position(0, 0, 0))
        self.modeler.primitives.create_polyline(Fin_Line, cover_surface=True, name="Fin")
        Fin_Line2 = []
        Fin_Line2.append(self.Position(0, 'sin(DraftAngle*3.14/180)*FinThickness', 'FinHeight'))
        Fin_Line2.append(self.Position(0, 'FinThickness-sin(DraftAngle*3.14/180)*FinThickness', 'FinHeight'))
        Fin_Line2.append(
            self.Position('FinLength', 'FinThickness + FinLength*sin(PatternAngle*3.14/180)-sin(DraftAngle*3.14/180)*FinThickness',
                         'FinHeight'))
        Fin_Line2.append(
            self.Position('FinLength', 'FinLength*sin(PatternAngle*3.14/180)+sin(DraftAngle*3.14/180)*FinThickness', 'FinHeight'))
        Fin_Line2.append(self.Position(0, 'sin(DraftAngle*3.14/180)*FinThickness', 'FinHeight'))
        self.modeler.primitives.create_polyline(Fin_Line2, cover_surface=True, name="Fin_top")
        self.modeler.connect(["Fin", "Fin_top"])
        self.modeler.primitives["Fin"].material_name = matname
        # self.modeler.thicken_sheet("Fin",'-FinHeight')
        num = int((hs_width / (separation+thick))/(max(1-math.sin(patternangle*3.14/180),0.1)))
        self.modeler.duplicate_along_line("Fin", self.Position(0, 'FinSeparation+FinThickness', 0), num,True)
        self.modeler.duplicate_along_line("Fin", self.Position(0, '-FinSeparation-FinThickness', 0), num/4, True)

        all_names = self.modeler.primitives.object_names
        list = [i for i in all_names if "Fin" in i]
        if numcolumn_perside>0:
            self.modeler.duplicate_along_line(list,
                                             self.Position('FinLength+VerticalSeparation', 'FinLength*sin(PatternAngle*3.14/180)',
                                                          0),
                                             'NumColumnsPerSide', True)

        all_names = self.modeler.primitives.object_names
        list = [i for i in all_names if "Fin" in i]
        self.modeler.split(list, self.CoordinateSystemPlane.ZXPlane, "PositiveOnly")
        all_names = self.modeler.primitives.object_names
        list = [i for i in all_names if "Fin" in i]
        self.modeler.create_coordinate_system(self.Position(0, 'HSHeight', 0), mode="view", view="XY", name="TopRight")

        self.modeler.split(list, self.CoordinateSystemPlane.ZXPlane, "NegativeOnly")

        if symmetric:

            self.modeler.create_coordinate_system(self.Position('(HSWidth-SymSeparation)/2', 0, 0), mode="view",
                                                  view="XY", name="CenterRightSep",reference_cs="TopRight")

            self.modeler.split(list, self.CoordinateSystemPlane.YZPlane, "NegativeOnly")
            self.modeler.create_coordinate_system(self.Position('SymSeparation/2', 0, 0),
                                                  mode="view", view="XY", name="CenterRight",reference_cs="CenterRightSep")
            self.modeler.duplicate_and_mirror(list, self.Position(0, 0, 0), self.Position(1, 0, 0))
            Center_Line = []
            Center_Line.append(self.Position('-SymSeparation', 'Tolerance','-Tolerance'))
            Center_Line.append(self.Position('SymSeparation', 'Tolerance', '-Tolerance'))
            Center_Line.append(self.Position('VerticalSeparation', '-HSHeight-Tolerance', '-Tolerance'))
            Center_Line.append(self.Position('-VerticalSeparation', '-HSHeight-Tolerance', '-Tolerance'))
            Center_Line.append(self.Position('-SymSeparation', 'Tolerance', '-Tolerance'))
            self.modeler.primitives.create_polyline(Center_Line, cover_surface=True, name="Center")
            self.modeler.thicken_sheet("Center", '-FinHeight-2*Tolerance')
            all_names = self.modeler.primitives.object_names
            list = [i for i in all_names if "Fin" in i]
            self.modeler.subtract(list, "Center", False)
        else:
            self.modeler.create_coordinate_system(self.Position('HSWidth', 0, 0), mode="view", view="XY",
                                                  name="BottomRight",reference_cs="TopRight")
            self.modeler.split(list, self.CoordinateSystemPlane.YZPlane, "NegativeOnly")
        all_objs2 = self.modeler.primitives.object_names
        list_to_move=[i for i in all_objs2 if i not in all_objs]
        center[0] -= hs_width/2
        center[1] -= hs_height/2
        center[2] += hs_basethick
        self.modeler.set_working_coordinate_system("Global")
        self.modeler.translate(list_to_move, center)
        if plane_enum == self.CoordinateSystemPlane.XYPlane:
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.XAxis, rotation)
        elif plane_enum == self.CoordinateSystemPlane.ZXPlane:
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.XAxis, 90)
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.YAxis, rotation)
        elif plane_enum == self.CoordinateSystemPlane.YZPlane:
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.YAxis, 90)
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.ZAxis, rotation)
        self.modeler.unite(list_to_move)
        self.modeler.primitives[list_to_move[0]].name = "HeatSink1"
        return True

    @aedt_exception_handler
    def edit_design_settings(self, gravityDir=0, ambtemp=22, performvalidation=False, CheckLevel="None",
                             defaultfluid="air", defaultsolid="Al-Extruded"):
        """Update the main settings of the design.

        Parameters
        ----------
        gravityDir : int, optional
            Gravity direction from -X to +Z. Options are ``0`` through ``5``. 
            The default is ``0``.
        ambtemp : optional 
            Ambient temperature. The default is ``22``.
        performvalidation : bool, optional
            Whether to enable validation. The default is ``False``.
        CheckLevel : optional
            Level of check during validation. The default is ``None``.
        defaultfluid : str, optional
            Default fluid material. The default is ``"air"``.
        defaultsolid : str, optional
            Default solid material. The default is ``"Al-Extruded"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        AmbientTemp = str(ambtemp)+"cel"
        #
        # Configure design settings for gravity etc
        IceGravity = ["X", "Y", "Z"]
        GVPos = False
        if int(gravityDir) > 2:
            GVPos = True
        GVA = IceGravity[int(gravityDir) - 3]
        self._odesign.SetDesignSettings(
            ["NAME:Design Settings Data", "Perform Minimal validation:=", performvalidation, "Default Fluid Material:=",
             defaultfluid, "Default Solid Material:=", defaultsolid, "Default Surface Material:=",
             "Steel-oxidised-surface",
             "AmbientTemperature:=", AmbientTemp, "AmbientPressure:=", "0n_per_meter_sq",
             "AmbientRadiationTemperature:=", AmbientTemp,
             "Gravity Vector CS ID:=", 1, "Gravity Vector Axis:=", GVA, "Positive:=", GVPos],
            ["NAME:Model Validation Settings",
             "EntityCheckLevel:=", CheckLevel, "IgnoreUnclassifiedObjects:=", False, "SkipIntersectionChecks:=", False])
        return True

    @aedt_exception_handler
    def assign_em_losses(self, designname="HFSSDesign1", setupname="Setup1", sweepname="LastAdaptive", map_frequency=None,
                         surface_objects=[], source_project_name=None, paramlist=[], object_list=[]):
        """Map EM losses to an Icepak design.

        Parameters
        ----------
        designname : string, optional
            Name of the design of the source mapping. The default is ``"HFSSDesign1"``.
        setupname : str, optional
            Name of the EM setup. The default is ``"Setup1"``.
        sweepname : str, optional
            Name of the EM sweep to use for mapping. The default is ``"LastAdaptive"``.
        map_frequency : optional
            String containing the frequency to map. The default is ``None``. 
            The value must be ``None`` for Eigenmode analysis.
        surface_objects : list, optional
            List of objects in the source that are metals. The default is ``[]``.
        source_project_name : str, optional
            Name of the source project. The default is ``None``, in which case the 
            source from the same project is used.
        paramlist :list, optional
            List of all params in the EM to map. The default is ``[]``.
        object_list : list, optional
            List of objects. The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self._messenger.add_info_message("Mapping HFSS EM Lossess")
        oName = self.project_name
        if oName == source_project_name or source_project_name is None:
            projname = "This Project*"
        else:
            projname = source_project_name + ".aedt"
        #
        # Generate a list of model objects from the lists made previously and use to map the HFSS losses into Icepak
        #
        if not object_list:
            allObjects = self.modeler.primitives.object_names
            if "Region" in allObjects:
                allObjects.remove("Region")
        else:
            allObjects = object_list[:]

        surfaces = surface_objects
        if map_frequency:
            intr = [map_frequency]
        else:
            intr = []


        argparam = OrderedDict({})
        for el in self.available_variations.nominal_w_values_dict:
            argparam[el] = self.available_variations.nominal_w_values_dict[el]

        for el in paramlist:
            argparam[el]=el

        props = OrderedDict(
            {"Objects": allObjects, "Project": projname, "projname": "ElectronicsDesktop",
             "Design": designname, "Soln": setupname + " : " + sweepname, "Params": argparam,
             "ForceSourceToSolve": True, "PreservePartnerSoln": True, "PathRelativeTo": "TargetProject"})
        props["Intrinsics"]= intr
        props["SurfaceOnly"]= surfaces

        name = generate_unique_name("EMLoss")
        bound = BoundaryObject(self, name, props, "EMLoss")
        if bound.create():
            self.boundaries.append(bound)
            self._messenger.add_info_message('EM losses Mapped from design {}'.format(designname))
            return bound
        return False


    @aedt_exception_handler
    def eval_surface_quantity_from_field_summary(self, faces_list, quantity_name="HeatTransCoeff", savedir=None,
                                                 filename=None, sweep_name=None, parameter_dict_with_values={}):
        """Export the field surface output.
        
        This method exports one CSV file for the specified variation.

        Parameters
        ----------
        faces_list : list
            List of faces to apply.
        quantity_name : str, optional
            Name of the quantity to export. The default is ``"HeatTransCoeff"``.
        savedir : str, optional
            Directory to save the HTC file to. The default is ``None``.
        filename : str, optional
            Name of the HTC file. The default is ``None``.
        sweep_name : str, optional
            Name of the setup and name of the sweep. For example: ``"IcepakSetup1 : SteatyState"``. The default is ``None``.
        parameter_dict_with_values : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.

        Returns
        -------
        str
            Name of the file.
        """
        name=generate_unique_name(quantity_name)
        self.modeler.create_face_list(faces_list,name )
        if not savedir:
            savedir = self.project_path
        if not filename:
            filename = generate_unique_name(self.project_name+quantity_name)
        if not sweep_name:
            sweep_name=self.nominal_sweep
        self.osolution.EditFieldsSummarySetting(
            [
                "Calculation:=", ["Object", "Surface", name, quantity_name, "", "Default", "AmbientTemp"],
            ])
        string = ""
        for el in parameter_dict_with_values:
            string += el + "=\'" + parameter_dict_with_values[el] + "\' "
        filename = os.path.join(savedir, filename + ".csv")
        self.osolution.ExportFieldsSummary(
                [
                    "SolutionName:=", sweep_name,
                    "DesignVariationKey:=", string,
                    "ExportFileName:=", filename,
                    "IntrinsicValue:=", ""
                ])
        return filename

    def eval_volume_quantity_from_field_summary(self, object_list, quantity_name="HeatTransCoeff",  savedir=None,
                                                 filename=None, sweep_name=None, parameter_dict_with_values={}):
        """Export the field volume output.
        
        This method exports one CSV file for the specified variation.

        Parameters
        ----------
        object_list : list
            List of faces to apply.
        quantity_name : str, optional
            Name of the quantity to export. The default is ``"HeatTransCoeff"``.
        savedir : str, optional
            Directory to save the HTC file to. The default is ``None``.
        filename :  str, optional
            Name of the HTC file. The default is ``None``.
        sweep_name :
            Name of the setup and name of the sweep. For example: ``"IcepakSetup1 : SteatyState"``. The default is ``None``.
        parameter_dict_with_values : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``

        Returns
        -------
        str
           Name of the file.
        """
        if not savedir:
            savedir = self.project_path
        if not filename:
            filename = generate_unique_name(self.project_name+quantity_name)
        if not sweep_name:
            sweep_name=self.nominal_sweep
        self.osolution.EditFieldsSummarySetting(
            [
                "Calculation:=", ["Object", "Volume", ",".join(object_list), quantity_name, "", "Default", "AmbientTemp"],
            ])
        string = ""
        for el in parameter_dict_with_values:
            string += el + "=\'" + parameter_dict_with_values[el] + "\' "
        filename = os.path.join(savedir, filename + ".csv")
        self.osolution.ExportFieldsSummary(
                [
                    "SolutionName:=", sweep_name,
                    "DesignVariationKey:=", string,
                    "ExportFileName:=", filename,
                    "IntrinsicValue:=", ""
                ])
        return filename

    @aedt_exception_handler
    def UniteFieldsSummaryReports(self, savedir, proj_icepak):
        """Unite the files created by a fields summary for the variations.

        Parameters
        ----------
        savedir : str
           Directory path for saving the file.           
        proj_icepak : str
            Name of the Icepak project.  

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        newfilename = os.path.join(savedir, proj_icepak + "_HTCAndTemp.csv")
        newfilelines = []
        headerwriten = False
        filetoremove = []
        # first variation
        i = 0
        filename = os.path.join(savedir, proj_icepak + "_HTCAndTemp_var" + str(i) + ".csv")
        # iterate the variations
        while os.path.exists(filename):
            with open(filename, 'r') as f:
                lines = f.readlines()
                variation = lines[1]
                # Searching file content for temp and power
                pattern = re.compile(r"DesignVariation,\$AmbientTemp=('.+?')\s+\$PowerIn=('.+?')")
                m = pattern.match(variation)
                temp = m.group(1)
                power = m.group(2)
                if not headerwriten:
                    # write the new file header
                    newfilelines.append("$AmbientTemp,$PowerIn," + lines[4])
                    newfilelines.append("\n")
                    headerwriten = True

                # add the new lines
                newfilelines.append(temp + ',' + power + ',' + lines[5])
                newfilelines.append(temp + ',' + power + ',' + lines[6])

            # search for next variation
            filetoremove.append(filename)
            i += 1
            filename = os.path.join(savedir, proj_icepak + "_HTCAndTemp_var" + str(i) + ".csv")
        # write the new file
        with open(newfilename, 'w') as f:
            f.writelines(newfilelines)
        # remove the single files variation
        for fr in filetoremove:
            os.remove(fr)
        return True


    def export_summary(self, output_dir=None, solution_name=None, type="Object", geometryType="Volume", quantity="Temperature",
                       variation="", variationlist=[]):
        """Export a fields summary of all objects.

        Parameters
        ----------
        output_dir : str, optional
             Name of directory to export the fields summary to. The default is ``None``.
        solution_name : str, optional
             Name of the solution. The default is ``None``.
        type : string, optional
             The default is ``"Object"``.
        geometryType : str, optional
             Type of the geometry. The default is ``"Volume"``.
        quantity : str, optional
             The default is ``"Temperature"``.
        variation : str, optional
             The default is ``""``.
        variationlist : list, optional
             The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        all_objs = list(self.modeler.oeditor.GetObjectsInGroup("Solids"))
        all_objs_NonModeled = list(self.modeler.oeditor.GetObjectsInGroup("Non Model"))
        all_objs_model = [item for item in all_objs if item not in all_objs_NonModeled]
        arg = []
        self._messenger.add_info_message("Objects Lists " + str(all_objs_model))
        for el in all_objs_model:
            try:
                self.osolution.EditFieldsSummarySetting(
                    ["Calculation:=", [type, geometryType, el, quantity, "", "Default"]])
                arg.append("Calculation:=")
                arg.append([type, geometryType, el, quantity, "", "Default"])
            except Exception as e:
                self._messenger.add_error_message("Object " + el + " not added")
                self._messenger.add_error_message(str(e))
        if not output_dir:
            output_dir = self.project_path
        self.osolution.EditFieldsSummarySetting(arg)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        if not solution_name:
            solution_name = self.nominal_sweep
        if variation:
            for l in variationlist:
                self.osolution.ExportFieldsSummary(["SolutionName:=",solution_name ,
                                                          "DesignVariationKey:=", variation + "=\'" + str(l) + "\'",
                                                          "ExportFileName:=",
                                                         os.path.join(output_dir,
                                                                      "IPKsummaryReport" + quantity + "_" + str(
                                                                          l) + ".csv")])
        else:
            self.osolution.ExportFieldsSummary(["SolutionName:=", solution_name,
                                                      "DesignVariationKey:=", "",
                                                      "ExportFileName:=",
                                                      os.path.join(output_dir, "IPKsummaryReport" + quantity + ".csv")])
        return True

    @aedt_exception_handler
    def get_radiation_settings(self, radiation):
        """Retrieve radiation settings.

        Parameters
        ----------
        radiation : str
            One of the following:
            
            * ``"Nothing"``
            * ``"Low"``
            * ``"High"``
            * ``"Both"``
            

        Returns
        -------

        """
        if radiation == "Nothing":
            lowSideRad = False
            highSideRad = False
        elif radiation == "Low":
            lowSideRad = True
            highSideRad = False
        elif radiation == "High":
            lowSideRad = False
            highSideRad = True
        elif radiation == "Both":
            lowSideRad = True
            highSideRad = True
        return lowSideRad, highSideRad

    @aedt_exception_handler
    def get_link_data(self, linkData):
        """Retrieve a list of linked data.
                
        Parameters
        ----------
        linkData : list
            List of the data to retrieve for links. Options are:
            
            * Project name, if ``None`` use the active project.
            * Design name
            * HFSS solution name, such as ``"HFSS Setup 1 : Last Adaptive"``
            * Force source design simulation, ``True`` or ``False``.
            * Preserve source design solution, ``True`` or ``False``.

        Returns
        -------
        list
            List containing the requested link data.
        """
        if linkData[0] is None:
            project_name = "This Project*"
        else:
            project_name = linkData[0].replace("\\","/")

        designName = linkData[1]
        hfssSolutionName = linkData[2]
        forceSourceSimEnabler = linkData[3]
        preserveSrcResEnabler = linkData[4]

        arg = ["NAME:DefnLink",
            "Project:="	, project_name,
            "Product:="		, "ElectronicsDesktop",
            "Design:="		, designName,
            "Soln:="		, hfssSolutionName,
            ["NAME:Params"],
            "ForceSourceToSolve:="	, forceSourceSimEnabler,
            "PreservePartnerSoln:="	, preserveSrcResEnabler,
            "PathRelativeTo:="	, "TargetProject"]

        return arg

    @aedt_exception_handler
    def create_ipk_3dcomponent_pcb(self, compName, setupLinkInfo, solutionFreq, resolution, PCB_CS="Global",
                                   rad="Nothing", extenttype="Bounding Box", outlinepolygon="", powerin="0W",
                                   custom_x_resolution=None, custom_y_resolution=None):
        """Create a PCB component in Icepak that is linked to an HFSS 3D Layout object.

        Parameters
        ----------
        compName : str
            Name of the new PCB component.
        setupLinkInfo : list
            List of the five elements needed to set up the link: 
            ``[projectname, designname, solution name, forcesimulation (bool), preserve results (bool)``.
        solutionFreq :
            Frequency of the solution if cosimulation is requested.
        resolution : int
            Resolution of the mapping.
        PCB_CS : str, optional
            Coordinate system for the PCB. The default is ``"Global"``.
        rad : str, optional
            Radiating faces. The default is ``"Nothing"``.
        extenttype : str, optional
            Type of the extent. Options are ``"Bounding Box"`` or ``"Polygon"``.  
            The default is ``"Bounding Box"``.
        outlinepolygon : str, optional
            Name of the polygon if ``extentype="Polygon"``. The default is ``""``.
        powerin : str, optional
            Power to dissipate if cosimulation is disabled. The default is ``"0W"``.

        Returns
        -------
        bool
             ``True`` when successful, ``False`` when failed.
        """
        lowRad, highRad = self.get_radiation_settings(rad)
        hfssLinkInfo = self.get_link_data(setupLinkInfo)
        compInfo = ["NAME:BasicComponentInfo",
                    "ComponentName:=", compName,
                    "Company:=", "",
                    "Company URL:=", "",
                    "Model Number:=", "",
                    "Help URL:=", "",
                    "Version:=", "1.0",
                    "Notes:=", "",
                    "IconType:=", "PCB"]
        compDefinition = ["NAME:NativeComponentDefinitionProvider",
                          "Type:=", "PCB",
                          "Unit:="	, self.modeler.model_units,
                          "MovePlane:="		, "XY",
                          "Use3DLayoutExtents:="	, False,
                          "ExtentsType:="		, extenttype,
                          "OutlinePolygon:="	, outlinepolygon]

        compDefinition += ["CreateDevices:=", False,
                            "CreateTopSolderballs:=", False,
                            "CreateBottomSolderballs:=", False, ]
        compDefinition += ["Resolution:=", int(resolution),
                           ["NAME:LowSide", "Radiate:=", lowRad],
                           ["NAME:HighSide", "Radiate:=", highRad]]


        if custom_x_resolution and custom_y_resolution:
            compDefinition += ["UseThermalLink:=", solutionFreq!="",
                               "CustomResolution:=", True, "CustomResolutionRow:=", custom_x_resolution,
                               "CustomResolutionCol:=", 600]
        else:
            compDefinition += ["UseThermalLink:=", solutionFreq != "",
                               "CustomResolution:=", False]
        if solutionFreq:
                compDefinition += ["Frequency:=", solutionFreq, hfssLinkInfo]
        else:
            compDefinition += ["Power:=", powerin, hfssLinkInfo]

        compInstancePar = ["NAME:InstanceParameters",
                           "GeometryParameters:="	, "",
                           "MaterialParameters:="	, "",
                           "DesignParameters:="	, ""]

        compData = ["NAME:InsertNativeComponentData",
                    "TargetCS:=", PCB_CS,
                    "SubmodelDefinitionName:=", compName,
                    ["NAME:ComponentPriorityLists"],
                    "NextUniqueID:=", 0,
                    "MoveBackwards:=", False,
                    "DatasetType:=", "ComponentDatasetType",
                    ["NAME:DatasetDefinitions"],
                    compInfo,
                    ["NAME:GeometryDefinitionParameters" ,["NAME:VariableOrders"] ],
                    ["NAME:DesignDefinitionParameters",	["NAME:VariableOrders"]	],
                    ["NAME:MaterialDefinitionParameters", ["NAME:VariableOrders"] ],
                    "MapInstanceParameters:=", "DesignVariable",
                    "UniqueDefinitionIdentifier:=", "a731a7c3-f557-4ab7-ae80-6bf8520c6129",
                    "OriginFilePath:="	, "",
                    "IsLocal:="		, False,
                    "ChecksumString:="	, "",
                    "ChecksumHistory:="	, [],
                    "VersionHistory:="	, [],
                    compDefinition,
                    compInstancePar]

        self.modeler.oeditor.InsertNativeComponent(compData)
        self.modeler.primitives.refresh_all_ids()
        self.materials._load_from_project()
        return True

    @aedt_exception_handler
    def create_pcb_from_3dlayout(self, component_name, project_name, design_name, resolution=2,
                                 extenttype="Bounding Box", outlinepolygon="", close_linked_project_after_import=True,
                                 custom_x_resolution=None, custom_y_resolution=None):
        """Create a PCB component in Icepak that is linked to an HFSS 3D Layout object linking only to the geometry file (no solution linked)

        Parameters
        ----------
        component_name : str
            Name of the new PCB component created in Icepak.
        project_name : str
            Name of the oroject or the full path to the project.
        design_name : str
            Name of the design.
        resolution : optional
            Resolution of the mapping. The default is `2`.
        extenttype :
            Type of the extent. Options are ``"Polygon"`` or ``"Bounding Box"``. The default is ``"Bounding Box"``.
        outlinepolygon : str, optional
            Name of the outline polygon if ``extentyype="Polygon"``. The default is ``""``.
        close_linked_project_after_import : bool, optional
            Whether to close the linked AEDT project after the import. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if project_name == self.project_name:
            project_name = "This Project*"
        link_data = [project_name, design_name,  "<--EDB Layout Data-->", False, False]
        status = self.create_ipk_3dcomponent_pcb(component_name, link_data, "", resolution, extenttype=extenttype,
                                                 outlinepolygon=outlinepolygon, custom_x_resolution=custom_x_resolution,
                                                 custom_y_resolution=custom_y_resolution)

        if close_linked_project_after_import and ".aedt" in project_name:
                prjname = os.path.splitext(os.path.basename(project_name))[0]
                self.close_project(prjname, saveproject=False)
        self._messenger.add_info_message("PCB Component Correctly created in Icepak")
        return status

    @aedt_exception_handler
    def copyGroupFrom(self, groupName, sourceDesign, sourceProject = None, sourceProjectPath = None):
        """Copy a group from another design.

        Parameters
        ----------
        groupName : str
            Name of the group.
        sourceDesign : str
            Name of the source design.
        sourceProject : str, optional
            Name of the source project. The default is ``None``.
        sourceProjectPath : str, optional
            Path to the source project. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        oName = self.project_name
        if sourceProject == oName or sourceProject is None:
            oSrcProject = self._desktop.GetActiveProject()
        else:
            self._desktop.OpenProject(sourceProjectPath)
            oSrcProject = self._desktop.SetActiveProject(sourceProject)

        oDesign = oSrcProject.SetActiveDesign(sourceDesign)
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oEditor.Copy(["NAME:Selections", "Selections:=", groupName])

        self.modeler.oeditor.Paste()
        self.modeler.primitives.refresh_all_ids()
        self.materials._load_from_project()
        return True

    @aedt_exception_handler
    def export3DModel(self, fileName, filePath, fileFormat = ".step", object_list = [], removed_objects = []):
        """Export the 3D model.

        Parameters
        ----------
        fileName : str
            Name of the file.   
        filePath : str
            Path to the file.
        fileFormat : str, optional
             Format of the file. The default is ``".step"``.
        object_list : list, optional
             The default is ``[]``.
        removed_objects : list, optional
             The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not object_list:
            allObjects = self.modeler.primitives.object_names
            if removed_objects:
                for rem in removed_objects:
                    allObjects.remove(rem)
            else:
                if "Region" in allObjects:
                    allObjects.remove("Region")
        else:
            allObjects = object_list[:]

        print(allObjects)

        stringa = ','.join(allObjects)
        arg = ["NAME:ExportParameters",
               "AllowRegionDependentPartSelectionForPMLCreation:=", True,
               "AllowRegionSelectionForPMLCreation:=", True,
               "Selections:=", stringa,
               "File Name:=", str(filePath)+"/"+str(fileName)+str(fileFormat),
               "Major Version:=", -1,
               "Minor Version:=", -1]

        self.modeler.oeditor.Export(arg)
        return True


    @aedt_exception_handler
    def globalMeshSettings(self, meshtype, gap_min_elements="1", noOgrids=False, MLM_en=True, MLM_Type="3D",
                           stairStep_en=False, edge_min_elements="1", object="Region"):
        """Create a custom mesh tailored on a PCB design.

        Parameters
        ----------
        meshtype : 
            Type of mesh. Options are ``1``, ``2``, and ``3``, which represent 
            respectively a coarse, standard, or very accurate mesh.
        gap_min_elements : str, optional
            The default is ``"1"``.
        noOgrids : bool, optional
            The default is ``False``.
        MLM_en: bool, optional
            The default is ``True``.
        MLM_Type: str, optional
            The default is ``"3D"``.
        stairStep_en : bool, optional
            The default is ``False``.
        edge_min_elements: str, optional
            The default is ``"1"``.
        object : str, optional
            The default is ``"Region"``.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        oModule = self.odesign.GetModule("MeshRegion")

        oBoundingBox = self.modeler.oeditor.GetModelBoundingBox()
        xsize = abs(float(oBoundingBox[0]) - float(oBoundingBox[3])) / (15 * meshtype * meshtype)
        ysize = abs(float(oBoundingBox[1]) - float(oBoundingBox[4])) / (15 * meshtype * meshtype)
        zsize = abs(float(oBoundingBox[2]) - float(oBoundingBox[5])) / (10 * meshtype)
        MaxSizeRatio = (1 + (meshtype / 2))

        oModule.EditGlobalMeshRegion(
            [
                "NAME:Settings",
                "MeshMethod:="	, "MesherHD",
                "UserSpecifiedSettings:=", True,
                "ComputeGap:="		, True,
                "MaxElementSizeX:="	, str(xsize) + self.modeler.model_units,
                "MaxElementSizeY:="	, str(ysize) + self.modeler.model_units,
                "MaxElementSizeZ:="	, str(zsize) + self.modeler.model_units,
                "MinElementsInGap:="	, gap_min_elements,
                "MinElementsOnEdge:="	, edge_min_elements,
                "MaxSizeRatio:="	, str(MaxSizeRatio),
                "NoOGrids:="		, noOgrids,
                "EnableMLM:="		, MLM_en,
                "EnforeMLMType:="	, MLM_Type,
                "MaxLevels:="		, "0",
                "BufferLayers:="	, "0",
                "UniformMeshParametersType:=", "Average",
                "StairStepMeshing:="	, stairStep_en,
                "MinGapX:="		, str(xsize / 10) + self.modeler.model_units,
                "MinGapY:="		, str(xsize / 10) + self.modeler.model_units,
                "MinGapZ:="		, str(xsize / 10) + self.modeler.model_units,
                "Objects:="		, [object]
            ])
        return True

    @aedt_exception_handler
    def create_assign_region2PCBComponent(self, scale_factor = 1.0, restore_padding_values = [50,50,50,50,50,50]):
        """Create and assign a region to the PCB component.

        Parameters
        ----------
        scale_factor : float, optional
             The default is ``1.0``.
        restore_padding_values : list, optional
             The default is ``[50,50,50,50,50,50]``.  

        Returns
        -------
        tuple
            Tuple containing the ``(x, y, z)`` distances of the region.
        """
        self.modeler.edit_region_dimensions([0,0,0,0,0,0])

        verticesID = self.modeler.oeditor.GetVertexIDsFromObject("Region")

        x_values = []
        y_values = []
        z_values = []

        for id in verticesID:
            tmp = self.modeler.oeditor.GetVertexPosition(id)
            x_values.append(tmp[0])
            y_values.append(tmp[1])
            z_values.append(tmp[2])

        x_max = float(max(x_values)) * scale_factor
        x_min = float(min(x_values)) * scale_factor

        y_max = float(max(y_values)) * scale_factor
        y_min = float(min(y_values)) * scale_factor

        z_max = float(max(z_values)) * scale_factor
        z_min = float(min(z_values)) * scale_factor

        dis_x = str(float(x_max) - float(x_min))
        dis_y = str(float(y_max) - float(y_min))
        dis_z = str(float(z_max) - float(z_min))

        min_position = self.modeler.Position(str(x_min)+"mm", str(y_min)+"mm", str(z_min)+"mm")
        mesh_box = self.modeler.primitives.create_box(min_position,[dis_x+"mm",dis_y+"mm",dis_z+"mm"], "Component_Region")


        self.modeler.primitives["Component_Region"].model = False

        self.modeler.edit_region_dimensions(restore_padding_values)
        return dis_x, dis_y, dis_z

    @aedt_exception_handler
    def create_temp_point_monitor(self, point_name, point_coord = [0,0,0]):
        """Create a temperature monitor for the simulation.

        Parameters
        ----------
        point_name : str
            Name of the temperature monitor.
        point_coord : list, optional
            Point coordinates for the temperature monitor. The default is ``[0, 0, 0]``.
        
        Returns
        -------
        bool
             ``True`` when successful, ``False`` when failed.
        """
        arg1 = ["NAME:PointParameters",
               "PointX:="		, point_coord[0],
               "PointY:="		, point_coord[1],
               "PointZ:="		, point_coord[2]]

        arg2 = ["NAME:Attributes",
                "Name:="		, point_name,
                "Color:="		, "(143 175 143)"]

        self.modeler.oeditor.CreatePoint(arg1, arg2)
        monitor = self._odesign.GetModule("Monitor")

        arg = ["NAME:"+str(point_name),
               "Quantities:="		, ["Temperature"],
               "Points:="		, [str(point_name)]]

        monitor.AssignPointMonitor(arg)
        return True

    @aedt_exception_handler
    def delete_em_losses(self, bound_name):
        """Delete EM losses boundary.

        Parameters
        ----------
        bound_name : str
            Name of the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        self.oboundary.DeleteBoundaries([bound_name])
        return True

    @aedt_exception_handler
    def delete_pcb_component(self, comp_name):
        """Delete a PCB component.

        Parameters
        ----------
        comp_name : str
            Name of the PCB component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        arg = ["NAME:Selections",
               "Selections:="		, comp_name]

        self.modeler.oeditor.Delete(arg)
        return True
