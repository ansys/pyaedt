"""
Icepak 3d Layout Class
----------------------------------------------------------------


Description
==================================================

This class contains all the Icepak AEDT Functionalities. It inherites all the objects that belongs to Icepak


:Example:

app = Icepak()     creates and Icepak object and connect to existing hfss design (create a new hfss design if not present)


app = Icepak(projectname)     creates and Icepak object and link to projectname project. If project doesn't exists, it creates a new one and rename it


app = Icepak(projectname,designame)     creates and Icepak object and link to designname design in projectname project


app = Icepak("myfile.aedt")     creates and Icepak object and open specified project


========================================================

"""

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
    """Icepak Object

    Parameters
    ----------
    projectname :
        name of the project to be selected or full path to the project to be opened  or to the AEDTZ
        archive. if None try to get active project and, if nothing present to create an empty one
    designname :
        name of the design to be selected. if None, try to get active design and, if nothing present to create an empty one
    solution_type :
        solution type to be applied to design. if None default is taken
    setup_name :
        setup_name to be used as nominal. if none active setup is taken or nothing

    Returns
    -------

    """
    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):
        FieldAnalysisIcepak.__init__(self, "Icepak", projectname, designname, solution_type, setup_name)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        ''' Push exit up to parent object Design '''
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    @property
    def existing_analysis_sweeps(self):
        """Existing Analysis Setup List
        
        
        :return: Return a list of all defined analysis setup names in the maxwell design.

        Parameters
        ----------

        Returns
        -------

        """
        setup_list = self.existing_analysis_setups
        sweep_list=[]
        for el in setup_list:
                sweep_list.append(el + " : " + self.solution_type)
        return sweep_list

    @aedt_exception_handler
    def assign_openings(self, air_faces):
        """Assign Opening to a list of faces

        Parameters
        ----------
        air_faces :
            list of face name

        Returns
        -------
        type
            bound object or None

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
            self.messenger.add_info_message("Opening Assigned")
            return bound
        return None

    @aedt_exception_handler
    def assign_2way_coupling(self,setup_name=None, number_of_iterations=2, continue_ipk_iterations=True, ipk_iterations_per_coupling=20):
        """Assign 2Way Coupling to a specific setup

        Parameters
        ----------
        setup_name :
            str optional setup name (Default value = None)
        number_of_iterations :
            int optional number of iterations (Default value = 2)
        continue_ipk_iterations :
            bool, optional continue Icepak Iteration (Default value = True)
        ipk_iterations_per_coupling :
            int, optional additional iterations per coupling (Default value = 20)

        Returns
        -------
        type
            Bool

        """

        if not setup_name:
            if self.setups:
                setup_name =self.setups[0].name
            else:
                self.messenger.add_error_message("No Setup Defined")
                return False
        self.oanalysis_setup.AddTwoWayCoupling(setup_name, ["NAME:Options", "NumCouplingIters:=", number_of_iterations,
                                                            "ContinueIcepakIterations:=", continue_ipk_iterations,
                                                            "IcepakIterationsPerCoupling:=",
                                                            ipk_iterations_per_coupling])
        return True

    @aedt_exception_handler
    def create_source_blocks_from_list(self, list_powers, assign_material=True, default_material="Ceramic_material"):
        """Assign to Box in Icepak Sources coming from CSV file. assignment is made by name

        Parameters
        ----------
        list_powers :
            list of input powers. its a list of list like in the examples [["Obj1", 1], ["Obj2", 3]]. it can contain multiple column for power inputs
        assign_material :
            bool (Default value = True)
        default_material :
            default material

        Returns
        -------
        type
            list of boundaries inserted

        """
        oObjects = self.modeler.primitives.get_all_solids_names()
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
        """Create Source Block for an object

        Parameters
        ----------
        object_name :
            name of the object
        input_power :
            input power. can be a string or a variable
        assign_material :
            bool (Default value = True)
        material_name :
            material name to assign in case assign_material is True (Default value = "Ceramic_material")
        use_object_for_name :
             (Default value = True)

        Returns
        -------
        type
            bound object or None

        """
        if assign_material:
            self.assignmaterial(object_name, material_name)
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
    def create_network_block(self, object_name, power, rjc, rjb, gravity_dir, top, assign_material=True,
                             default_material="Ceramic_material", use_object_for_name=True):
        """Create Network Block

        Parameters
        ----------
        object_name :
            name of the object for which block has to be created
        power :
            input power, can be a value or variable
        rjc :
            rjc value
        rjb :
            rjb value
        gravity_dir :
            0...5 gravity direction from -X to +Z
        top :
            is the board bounding value in mm of the top face
        assign_material :
            bool (Default value = True)
        default_material :
            default material
        use_object_for_name :
             (Default value = True)

        Returns
        -------
        type
            bounding object if created

        """
        if object_name in self.modeler.primitives.get_all_objects_names():
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
                self.assignmaterial(object_name, default_material)
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
                self.modeler.oeditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object_name], ["NAME:ChangedProps", ["NAME:Solve Inside", "Value:=", False]]]])
                return bound
            return None

    @aedt_exception_handler
    def create_network_blocks(self, input_list, gravity_dir, top, assign_material=True,
                             default_material="Ceramic_material"):
        """createNetworkBlocs(listfromCsv,gravityDir,top) create network objects form csv files

        Parameters
        ----------
        assign_material :
            param default_material:
        input_list :
            list of sources with input  rjc,  rjb, power. [[Objname1, rjc, rjb, power1,power2....],[Objname2, rjc2, rbj2, power1, power2...]]
        gravity_dir :
            0...5 gravity direction from -X to +Z
        top :
            is the board bounding value in mm of the top face
        default_material :
             (Default value = "Ceramic_material")

        Returns
        -------
        type
            networks boundary objects

        """
        objs = self.modeler.primitives.get_all_solids_names()
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
    def assign_block_from_sherlock_file(self, csv_name):
        """Assign block power to components based on sherlock file

        Parameters
        ----------
        csv_name :
            csf file from sherlock

        Returns
        -------
        type
            total power applied

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
        all_objects = self.modeler.primitives.get_all_objects_names()
        for power in component_data["Applied Power (W)"]:
            try:
                float(power)
                if "COMP_" + component_data["Ref Des"][i] in all_objects:
                    status = self.create_source_block("COMP_" + component_data["Ref Des"][i], str(power)+"W",assign_material=False)
                    if not status:
                        self.messenger.add_warning_message(
                            "Warning. Block {} skipped with {}W power".format(component_data["Ref Des"][i], power))
                    else:
                        total_power += float(power)
                        # print("Block {} created with {}W power".format(component_data["Ref Des"][i], power))
                elif component_data["Ref Des"][i] in all_objects:
                    status = self.create_source_block(component_data["Ref Des"][i], str(power)+"W",assign_material=False)
                    if not status:
                        self.messenger.add_warning_message(
                            "Warning. Block {} skipped with {}W power".format(component_data["Ref Des"][i], power))
                    else:
                        total_power += float(power)
                        # print("Block {} created with {}W power".format(component_data["Ref Des"][i], power))
            except:
                pass
            i += 1
        self.messenger.add_info_message("Blocks inserted with total power {}W".format(total_power))
        return total_power

    @aedt_exception_handler
    def assign_priority_on_intersections(self, component_prefix="COMP_"):
        """This methods validate an icepak design and, in case of intersections automatically apply priorities to overcome simulation issue

        Parameters
        ----------
        component_prefix :
            components prefix on which to search (Default value = "COMP_")

        Returns
        -------
        type
            Bool

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
        """TO BE CHECKED. Find the top location of the layout given the gravity

        Parameters
        ----------
        gravityDir :
            0...5 gravity direction from -X to +Z

        Returns
        -------
        type
            top position  (float)

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
        """Create a Heat Sink fully parametric.

        Parameters
        ----------
        hs_height :
            param hs_width: (Default value = 100)
        hs_basethick :
            param pitch: (Default value = 10)
        thick :
            param length: (Default value = 10)
        height :
            param draftangle: (Default value = 40)
        patternangle :
            param separation: (Default value = 10)
        symmetric :
            param symmetric_separation: (Default value = True)
        numcolumn_perside :
            param vertical_separation: (Default value = 2)
        matname :
            param center: (Default value = "Al-Extruded")
        plane_enum :
            param rotation: (Default value = 0)
        tolerance :
            return: (Default value = 1e-3)
        hs_width :
             (Default value = 100)
        pitch :
             (Default value = 20)
        length :
             (Default value = 40)
        draftangle :
             (Default value = 0)
        separation :
             (Default value = 5)
        symmetric_separation :
             (Default value = 20)
        vertical_separation :
             (Default value = 10)
        center :
             (Default value = [0)
        0 :
            
        0] :
            
        rotation :
             (Default value = 0)

        Returns
        -------

        """
        all_objs = self.modeler.primitives.get_all_objects_names()
        self['FinPitch'] = self.modeler.primitives.arg_with_dim(pitch)
        self['FinThickness'] = self.modeler.primitives.arg_with_dim(thick)
        self['FinLength'] = self.modeler.primitives.arg_with_dim(length)
        self['FinHeight'] = self.modeler.primitives.arg_with_dim(height)
        self['DraftAngle'] = draftangle
        self['PatternAngle'] = patternangle
        self['FinSeparation'] = self.modeler.primitives.arg_with_dim(separation)
        self['VerticalSeparation'] = self.modeler.primitives.arg_with_dim(vertical_separation)
        self['HSHeight'] = self.modeler.primitives.arg_with_dim(hs_height)
        self['HSWidth'] = self.modeler.primitives.arg_with_dim(hs_width)
        self['HSBaseThick'] = self.modeler.primitives.arg_with_dim(hs_basethick)
        if numcolumn_perside>1:
            self['NumColumnsPerSide'] = numcolumn_perside
        if symmetric:
            self['SymSeparation'] = self.modeler.primitives.arg_with_dim(symmetric_separation)
        # ipk['PatternDirection'] = 'Y'
        # ipk['LengthDirection'] = 'X'
        # ipk['HeightDirection'] = 'Z'
        self['Tolerance'] = self.modeler.primitives.arg_with_dim(tolerance)

        #self.modeler.primitives.create_box([0, 0, '-HSBaseThick'], ['HSWidth', 'HSHeight', 'FinHeight+HSBaseThick'], "Outline")
        self.modeler.primitives.create_box(['-HSWidth/200', '-HSHeight/200', '-HSBaseThick'], ['HSWidth*1.01', 'HSHeight*1.01', 'HSBaseThick+Tolerance'], "HSBase", matname)
        Fin_Line = []
        Fin_Line.append(self.Position(0, 0, 0))
        Fin_Line.append(self.Position(0, 'FinThickness', 0))
        Fin_Line.append(self.Position('FinLength', 'FinThickness + FinLength*sin(PatternAngle*3.14/180)', 0))
        Fin_Line.append(self.Position('FinLength', 'FinLength*sin(PatternAngle*3.14/180)', 0))
        Fin_Line.append(self.Position(0, 0, 0))
        self.modeler.primitives.create_polyline(Fin_Line, True, "Fin")
        Fin_Line2 = []
        Fin_Line2.append(self.Position(0, 'sin(DraftAngle*3.14/180)*FinThickness', 'FinHeight'))
        Fin_Line2.append(self.Position(0, 'FinThickness-sin(DraftAngle*3.14/180)*FinThickness', 'FinHeight'))
        Fin_Line2.append(
            self.Position('FinLength', 'FinThickness + FinLength*sin(PatternAngle*3.14/180)-sin(DraftAngle*3.14/180)*FinThickness',
                         'FinHeight'))
        Fin_Line2.append(
            self.Position('FinLength', 'FinLength*sin(PatternAngle*3.14/180)+sin(DraftAngle*3.14/180)*FinThickness', 'FinHeight'))
        Fin_Line2.append(self.Position(0, 'sin(DraftAngle*3.14/180)*FinThickness', 'FinHeight'))
        self.modeler.primitives.create_polyline(Fin_Line2, True, "Fin_top")
        self.modeler.connect(["Fin", "Fin_top"])
        self.assignmaterial("Fin", matname)
        # self.modeler.thicken_sheet("Fin",'-FinHeight')
        num = int((hs_width / (separation+thick))/(max(1-math.sin(patternangle*3.14/180),0.1)))
        self.modeler.duplicate_along_line("Fin", self.Position(0, 'FinSeparation+FinThickness', 0), num,True)
        self.modeler.duplicate_along_line("Fin", self.Position(0, '-FinSeparation-FinThickness', 0), num/4, True)

        all_names = self.modeler.primitives.get_all_objects_names()
        list = [i for i in all_names if "Fin" in i]
        if numcolumn_perside>0:
            self.modeler.duplicate_along_line(list,
                                             self.Position('FinLength+VerticalSeparation', 'FinLength*sin(PatternAngle*3.14/180)',
                                                          0),
                                             'NumColumnsPerSide', True)

        all_names = self.modeler.primitives.get_all_objects_names()
        list = [i for i in all_names if "Fin" in i]
        self.modeler.split(list, self.CoordinateSystemPlane.ZXPlane, "PositiveOnly")
        all_names = self.modeler.primitives.get_all_objects_names()
        list = [i for i in all_names if "Fin" in i]
        self.modeler.coordinate_system.create(self.Position(0, 'HSHeight', 0), view="XY", name="TopRight")
        self.modeler.split(list, self.CoordinateSystemPlane.ZXPlane, "NegativeOnly")

        if symmetric:

            self.modeler.coordinate_system.create(self.Position('(HSWidth-SymSeparation)/2', 0, 0), view="XY",
                                                  name="CenterRightSep")
            self.modeler.split(list, self.CoordinateSystemPlane.YZPlane, "NegativeOnly")
            self.modeler.coordinate_system.create(self.Position('SymSeparation/2', 0, 0), view="XY", name="CenterRight")
            self.modeler.duplicate_and_mirror(list, self.Position(0, 0, 0), self.Position(1, 0, 0))
            Center_Line = []
            Center_Line.append(self.Position('-SymSeparation', 'Tolerance','-Tolerance'))
            Center_Line.append(self.Position('SymSeparation', 'Tolerance', '-Tolerance'))
            Center_Line.append(self.Position('VerticalSeparation', '-HSHeight-Tolerance', '-Tolerance'))
            Center_Line.append(self.Position('-VerticalSeparation', '-HSHeight-Tolerance', '-Tolerance'))
            Center_Line.append(self.Position('-SymSeparation', 'Tolerance', '-Tolerance'))
            self.modeler.primitives.create_polyline(Center_Line, True, "Center")
            self.modeler.thicken_sheet("Center", '-FinHeight-2*Tolerance')
            all_names = self.modeler.primitives.get_all_objects_names()
            list = [i for i in all_names if "Fin" in i]
            self.modeler.subtract(list, "Center", False)
        else:
            self.modeler.coordinate_system.create(self.Position('HSWidth', 0, 0), view="XY",
                                                  name="BottomRight")
            self.modeler.split(list, self.CoordinateSystemPlane.YZPlane, "NegativeOnly")
        all_objs2 = self.modeler.primitives.get_all_objects_names()
        list_to_move=[i for i in all_objs2 if i not in all_objs]
        center[0] -= hs_width/2
        center[1] -= hs_height/2
        center[2] += hs_basethick
        self.modeler.coordinate_system.setWorkingCoordinateSystem("Global")
        self.modeler.translate(list_to_move,center)
        if plane_enum == self.CoordinateSystemPlane.XYPlane:
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.XAxis, rotation)
        elif plane_enum == self.CoordinateSystemPlane.ZXPlane:
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.XAxis, 90)
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.YAxis, rotation)
        elif plane_enum == self.CoordinateSystemPlane.YZPlane:
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.YAxis, 90)
            self.modeler.rotate(list_to_move, self.CoordinateSystemAxis.ZAxis, rotation)
        self.modeler.unite(list_to_move)
        self.modeler.primitives["HSBase"].set_name("HeatSink1")
        return True

    @aedt_exception_handler
    def edit_design_settings(self, gravityDir=0, ambtemp=22, performvalidation=False, CheckLevel="None",
                             defaultfluid="air", defaultsolid="Al-Extruded"):
        """Edit Design Main settings

        Parameters
        ----------
        gravityDir :
            0...5 gravity direction from -X to +Z (Default value = 0)
        ambtemp :
            Ambient Temperature (Default value = 22)
        performvalidation : bool
            Enable validation (Default value = False)
        CheckLevel :
            Level of check in validation. Default "None"
        defaultfluid :
            default fluid material. "air"
        defaultsolid :
            default soldi material. "Al-Extruded"

        Returns
        -------

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
        """Map EM losses to Icepak Design

        Parameters
        ----------
        designname :
            name of design of the source mapping (Default value = "HFSSDesign1")
        map_frequency :
            string containing Frequency to be mapped. It must be None for eigen mode analysis (Default value = None)
        setupname :
            Name of EM Setup (Default value = "Setup1")
        sweepname :
            Name of EM Sweep to be used for mapping. Default no sweep and LastAdaptive to be used
        surface_objects :
            list of objects in the source that are metals (Default value = [])
        source_project_name :
            Name of the source project: None to use source from the same project (Default value = None)
        paramlist :
            list of all params in EM to be mapped (Default value = [])
        object_list :
             (Default value = [])

        Returns
        -------

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
            allObjects = self.modeler.primitives.get_all_objects_names(refresh_list=True)
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
        """Creates the export of the Field Surface output. It will export 1 csv file for the specified variation variation

        Parameters
        ----------
        faces_list :
            list of faces to apply
        quantity_name :
            quantity to export (Default value = "HeatTransCoeff")
        savedir :
            directory where to save htc file (Default value = None)
        filename :
            name of htc file (Default value = None)
        sweep_name :
            name of the setup + sweep "IcepakSetup1 : SteatyState" (Default value = None)
        parameter_dict_with_values :
            dictionary of parameters defined for the specific setup with value (Default value = {})

        Returns
        -------
        type
            str filename

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
        """Creates the export of the Field Volume output. It will export 1 csv file for the specified variation variation

        Parameters
        ----------
        object_list :
            list of faces to apply
        quantity_name :
            quantity to export (Default value = "HeatTransCoeff")
        savedir :
            directory where to save htc file (Default value = None)
        filename :
            name of htc file (Default value = None)
        sweep_name :
            name of the setup + sweep "IcepakSetup1 : SteatyState" (Default value = None)
        parameter_dict_with_values :
            dictionary of parameters defined for the specific setup with value (Default value = {})

        Returns
        -------
        type
            str filename

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
        """Unite the files created by Fields Summary for the various variations

        Parameters
        ----------
        savedir :
            
        proj_icepak :
            

        Returns
        -------

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
        """New method for exporting field summary of all the objercts

        Parameters
        ----------
        output_dir :
             (Default value = None)
        solution_name :
             (Default value = None)
        type :
             (Default value = "Object")
        geometryType :
             (Default value = "Volume")
        quantity :
             (Default value = "Temperature")
        variation :
             (Default value = "")
        variationlist :
             (Default value = [])

        Returns
        -------

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
                self.messenger.add_error_message("Object " + el + " not added")
                self.messenger.add_error_message(str(e))
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
        """

        Parameters
        ----------
        radiation :
            

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
        """linkData list format
        
        * Project Name, if None => Use Active Project
        * Design Name
        * HFSS Solution Name, e.g. "HFSS Setup 1 : Last Adaptive"
        * Force Source Design Simulation, True or False
        * Preserve Source Design Solution, True or False

        Parameters
        ----------
        linkData :
            list containing data in the link description

        Returns
        -------

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
                                   rad="Nothing", extenttype="Bounding Box", outlinepolygon="", powerin="0W"):
        """Create a PCB Component in Icepak linked to HFSS3DLayout object

        Parameters
        ----------
        compName :
            name of the new component
        setupLinkInfo :
            array of 5 elements [projectname, designname, solution name, forcesimulation (bool), preserve results (bool)
        solutionFreq :
            Freq of solution if cosimulation is requested
        resolution :
            resolution of the mapping (int)
        PCB_CS :
            coordinate System (Default value = "Global")
        rad :
            radiating faces (Default value = "Nothing")
        extenttype :
            extend type. Bounding Box or Polygon (Default value = "Bounding Box")
        outlinepolygon :
            in case of extentype is Polygon the name of the polygon (Default value = "")
        powerin :
            in case cosim is disabled, the power to dissipate (default 0W)

        Returns
        -------
        type
            Bool

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
        if solutionFreq:
            compDefinition += ["UseThermalLink:=", True,
                               "CustomResolution:=", False, "Frequency:=", solutionFreq, hfssLinkInfo]
        else:
            compDefinition += ["UseThermalLink:=", False,
                               "CustomResolution:=", False, "Power:=", powerin, hfssLinkInfo]

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
                                 extenttype="Bounding Box", outlinepolygon="", close_linked_project_after_import=True):
        """Create a PCB Component in Icepak linked to HFSS3DLayout object linking only the geometry file (no solution linked)

        Parameters
        ----------
        component_name :
            Name of the new component created in Icepak
        project_name :
            Project name or project full path
        design_name :
            design name
        resolution :
            resolution of the mapping. Default2
        extenttype :
            extent type. Polygon or Bounding Box (Default value = "Bounding Box")
        outlinepolygon :
            outline polygon in case Polygon extentyype is chosen (Default value = "")
        close_linked_project_after_import :
            close the aedb project after the import (Default value = True)

        Returns
        -------
        type
            Bool

        """
        link_data = [project_name, design_name,  "<--EDB Layout Data-->", False, False]
        status = self.create_ipk_3dcomponent_pcb(component_name, link_data, "", resolution, extenttype=extenttype,
                                                 outlinepolygon=outlinepolygon)

        if close_linked_project_after_import and ".aedt" in project_name:
                prjname = os.path.splitext(os.path.basename(project_name))[0]
                self.close_project(prjname, saveproject=False)
        self.messenger.add_info_message("PCB Component Correctly created in Icepak")
        return status

    @aedt_exception_handler
    def copyGroupFrom(self, groupName, sourceDesign, sourceProject = None, sourceProjectPath = None):
        """

        Parameters
        ----------
        groupName :
            
        sourceDesign :
            
        sourceProject :
             (Default value = None)
        sourceProjectPath :
             (Default value = None)

        Returns
        -------

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
        """

        Parameters
        ----------
        fileName :
            
        filePath :
            
        fileFormat :
             (Default value = ".step")
        object_list :
             (Default value = [])
        removed_objects :
             (Default value = [])

        Returns
        -------

        """

        if not object_list:
            allObjects = self.modeler.primitives.get_all_objects_names(refresh_list=True)
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
        """Create custom Mesh tailored on PCB Design

        Parameters
        ----------
        meshtype :
            1 coarse, 2 standard, 3 very accurate
        gap_min_elements :
            param noOgrids: (Default value = "1")
        MLM_en :
            param MLM_Type: (Default value = True)
        stairStep_en :
            param edge_min_elements: (Default value = False)
        object :
            return: (Default value = "Region")
        noOgrids :
             (Default value = False)
        MLM_Type :
             (Default value = "3D")
        edge_min_elements :
             (Default value = "1")

        Returns
        -------

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
        """

        Parameters
        ----------
        scale_factor :
             (Default value = 1.0)
        restore_padding_values :
             (Default value = [50)
        50 :
            
        50] :
            

        Returns
        -------

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


        self.modeler.primitives["Component_Region"].set_model(False)

        self.modeler.edit_region_dimensions(restore_padding_values)
        return dis_x, dis_y, dis_z

    @aedt_exception_handler
    def create_temp_point_monitor(self, point_name, point_coord = [0,0,0]):
        """Create a Temperature Monitor for simulation

        Parameters
        ----------
        point_name :
            Name of the temperature monitor
        point_coord :
            Coordinate of the point monitor (Default value = [0)
        0 :
            
        0] :
            

        Returns
        -------
        type
            Boolean

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
        """Delete EM Losses Boundaries

        Parameters
        ----------
        bound_name :
            Name of boundary to delete

        Returns
        -------
        type
            Boolean

        """

        self.oboundary.DeleteBoundaries([bound_name])
        return True

    @aedt_exception_handler
    def delete_pcb_component(self, comp_name):
        """Delete PCB Component

        Parameters
        ----------
        comp_name :
            PCB Name

        Returns
        -------
        type
            Boolean

        """
        arg = ["NAME:Selections",
               "Selections:="		, comp_name]

        self.modeler.oeditor.Delete(arg)
        return True
