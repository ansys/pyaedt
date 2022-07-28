from __future__ import absolute_import  # noreorder

import datetime
import warnings

from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.Modeler import GeometryModeler
from pyaedt.modeler.Primitives3D import Primitives3D


class Modeler3D(GeometryModeler, Primitives3D, object):
    """Provides the Modeler 3D application interface.

    This class is inherited in the caller application and is accessible through the modeler variable
    object. For example, ``hfss.modeler``.

    Parameters
    ----------
    application : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
    Examples
    --------
    >>> from pyaedt import Hfss
    >>> hfss = Hfss()
    >>> my_modeler = hfss.modeler
    """

    def __init__(self, application):
        GeometryModeler.__init__(self, application, is3d=True)
        Primitives3D.__init__(self)

    def __get__(self, instance, owner):
        self._app = instance
        return self

    @property
    def primitives(self):
        """Primitives.

        .. deprecated:: 0.4.15
            No need to use primitives anymore. You can instantiate primitives methods directly from modeler instead.

        Returns
        -------
        :class:`pyaedt.modeler.Primitives3D.Primitives3D`

        """
        mess = "The property `primitives` is deprecated.\n"
        mess += " Use `app.modeler` directly to instantiate primitives methods."
        warnings.warn(mess, DeprecationWarning)
        return self

    @pyaedt_function_handler()
    def create_3dcomponent(
        self,
        component_file,
        component_name=None,
        variables_to_include=[],
        exclude_region=False,
        object_list=None,
        boundaries_list=None,
        excitation_list=None,
        included_cs=None,
    ):
        """Create a 3D component file.

        Parameters
        ----------
        component_file : str
            Full path to the A3DCOMP file.
        component_name : str, optional
            Name of the component. The default is ``None``.
        variables_to_include : list, optional
             List of variables to include. The default is ``[]``.
        exclude_region : bool, optional
             Whether to exclude the region. The default is ``False``.
        object_list : list, optional
            List of Objects names to export. The default is all objects
        boundaries_list : list, optional
            List of Boundaries names to export. The default is all boundaries
        excitation_list : list, optional
            List of Excitation names to export. The default is all excitations
        included_cs : list, optional
            List of Coordinate Systems to export. The default is all coordinate systems

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Create3DComponent
        """
        if self._app.design_type == "Icepak":
            exclude_region = True
        if not component_name:
            component_name = self._app.design_name
        dt_string = datetime.datetime.now().strftime("%H:%M:%S %p %b %d, %Y")
        arg = [
            "NAME:CreateData",
            "ComponentName:=",
            component_name,
            "Company:=",
            "",
            "Company URL:=",
            "",
            "Model Number:=",
            "",
            "Help URL:=",
            "",
            "Version:=",
            "1.0",
            "Notes:=",
            "",
            "IconType:=",
            "",
            "Owner:=",
            "pyaedt",
            "Email:=",
            "",
            "Date:=",
            dt_string,
            "HasLabel:=",
            False,
            "IsEncrypted:=",
            False,
            "AllowEdit:=",
            False,
            "SecurityMessage:=",
            "",
            "Password:=",
            "",
            "EditPassword:=",
            "",
            "PasswordType:=",
            "UnknownPassword",
            "HideContents:=",
            True,
            "ReplaceNames:=",
            True,
            "ComponentOutline:=",
            "None",
        ]
        if object_list:
            objs = object_list
        else:
            objs = self.object_names
        for el in objs:
            if "Region" in el and exclude_region:
                objs.remove(el)
        arg.append("IncludedParts:="), arg.append(objs)
        arg.append("HiddenParts:="), arg.append([])
        activecs = self.oeditor.GetActiveCoordinateSystem()
        if included_cs:
            allcs = included_cs
        else:
            allcs = self.oeditor.GetCoordinateSystems()
        arg.append("IncludedCS:="), arg.append(allcs)
        arg.append("ReferenceCS:="), arg.append(activecs)
        par_description = []
        if variables_to_include:
            variables = variables_to_include
        else:
            variables = self._app._variable_manager.independent_variable_names
        for el in variables:
            par_description.append(el + ":=")
            par_description.append("")
        arg.append("IncludedParameters:="), arg.append(variables)
        variables = self._app._variable_manager.dependent_variable_names
        arg.append("IncludedDependentParameters:="), arg.append(variables)
        for el in variables:
            par_description.append(el + ":=")
            par_description.append("")
        arg.append("ParameterDescription:="), arg.append(par_description)
        arg.append("IsLicensed:="), arg.append(False)
        arg.append("LicensingDllName:="), arg.append("")
        arg.append("VendorComponentIdentifier:="), arg.append("")
        arg.append("PublicKeyFile:="), arg.append("")
        arg2 = ["NAME:DesignData"]
        if boundaries_list:
            boundaries = boundaries_list
        else:
            boundaries = self.get_boundaries_name()
        if boundaries:
            arg2.append("Boundaries:="), arg2.append(boundaries)
        if self._app.design_type == "Icepak":
            meshregions = [name for name in self._app.mesh.meshregions.name]
            try:
                meshregions.remove("Global")
            except:
                pass
            if meshregions:
                arg2.append("MeshRegions:="), arg2.append(meshregions)
        else:
            if excitation_list:
                excitations = excitation_list
            else:
                excitations = self._app.excitations
                if self._app.design_type == "HFSS":
                    exc = self._app.get_oo_name(self._app.odesign, "Excitations")
                    if exc and exc[0] not in self._app.excitations:
                        excitations.extend(exc)
            excitations = list(set([i.split(":")[0] for i in excitations]))
            if excitations:
                arg2.append("Excitations:="), arg2.append(excitations)
        meshops = [el.name for el in self._app.mesh.meshoperations]
        arg2.append("MeshOperations:="), arg2.append(meshops)
        arg3 = ["NAME:ImageFile", "ImageFile:=", ""]

        return _retry_ntimes(3, self.oeditor.Create3DComponent, arg, arg2, component_file, arg3)

    @pyaedt_function_handler()
    def create_coaxial(
        self,
        startingposition,
        axis,
        innerradius=1,
        outerradius=2,
        dielradius=1.8,
        length=10,
        matinner="copper",
        matouter="copper",
        matdiel="teflon_based",
    ):
        """Create a coaxial.

        Parameters
        ----------
        startingposition : list
            List of ``[x, y, z]`` coordinates for the starting position.
        axis : int
            Coordinate system AXIS (integer ``0`` for X, ``1`` for Y, ``2`` for Z) or
            the :class:`Application.CoordinateSystemAxis` enumerator.
        innerradius : float, optional
            Inner coax radius. The default is ``1``.
        outerradius : float, optional
            Outer coax radius. The default is ``2``.
        dielradius : float, optional
            Dielectric coax radius. The default is ``1.8``.
        length : float, optional
            Coaxial length. The default is ``10``.
        matinner : str, optional
            Material for the inner coaxial. The default is ``"copper"``.
        matouter : str, optional
            Material for the outer coaxial. The default is ``"copper"``.
        matdiel : str, optional
            Material for the dielectric. The default is ``"teflon_based"``.

        Returns
        -------
        tuple
            Contains the inner, outer, and dielectric coax as
            :class:`pyaedt.modeler.Object3d.Object3d` objects.

        References
        ----------

        >>> oEditor.CreateCylinder
        >>> oEditor.AssignMaterial


        Examples
        --------

        This example shows how to create a Coaxial Along X Axis waveguide.

        >>> from pyaedt import Hfss
        >>> app = Hfss()
        >>> position = [0,0,0]
        >>> coax = app.modeler.create_coaxial(
        ...    position, app.AXIS.X, innerradius=0.5, outerradius=0.8, dielradius=0.78, length=50
        ... )

        """
        if not (outerradius > dielradius and dielradius > innerradius):
            raise ValueError("Error in coaxial radius.")
        inner = self.create_cylinder(axis, startingposition, innerradius, length, 0)
        outer = self.create_cylinder(axis, startingposition, outerradius, length, 0)
        diel = self.create_cylinder(axis, startingposition, dielradius, length, 0)
        self.subtract(outer, inner)
        self.subtract(outer, diel)
        inner.material_name = matinner
        outer.material_name = matouter
        diel.material_name = matdiel

        return inner, outer, diel

    @pyaedt_function_handler()
    def create_waveguide(
        self,
        origin,
        wg_direction_axis,
        wgmodel="WG0",
        wg_length=100,
        wg_thickness=None,
        wg_material="aluminum",
        parametrize_w=False,
        parametrize_h=False,
        create_sheets_on_openings=False,
        name=None,
    ):
        """Create a standard waveguide and optionally parametrize `W` and `H`.

        Available models are WG0.0, WG0, WG1, WG2, WG3, WG4, WG5, WG6,
        WG7, WG8, WG9, WG9A, WG10, WG11, WG11A, WG12, WG13, WG14,
        WG15, WR102, WG16, WG17, WG18, WG19, WG20, WG21, WG22, WG24,
        WG25, WG26, WG27, WG28, WG29, WG29, WG30, WG31, and WG32.

        Parameters
        ----------
        origin : list
            List of ``[x, y, z]`` coordinates for the original position.
        wg_direction_axis : int
            Coordinate system axis (integer ``0`` for X, ``1`` for Y, ``2`` for Z) or
            the :class:`Application.CoordinateSystemAxis` enumerator.
        wgmodel : str, optional
            Waveguide model. The default is ``"WG0"``.
        wg_length : float, optional
            Waveguide length. The default is ``100``.
        wg_thickness : float, optional
            Waveguide thickness. The default is ``None``, in which case the
            thickness is `wg_height/20`.
        wg_material : str, optional
            Waveguide material. The default is ``"aluminum"``.
        parametrize_w : bool, optional
            Whether to parametrize `W`. The default is ``False``.
        parametrize_h : bool, optional
            Whether to parametrize `H`. The default is ``False``.
        create_sheets_on_openings : bool, optional
            Whether to create sheets on both openings. The default is ``False``.
        name : str, optional
            Name of the waveguide. The default is ``None``.

        Returns
        -------
        tuple
            Tuple of :class:`Object3d <pyaedt.modeler.Object3d.Object3d>`
            objects created by the waveguide.

        References
        ----------

        >>> oEditor.CreateBox
        >>> oEditor.AssignMaterial


        Examples
        --------

        This example shows how to create a WG9 waveguide.

        >>> from pyaedt import Hfss
        >>> app = Hfss()
        >>> position = [0, 0, 0]
        >>> wg1 = app.modeler.create_waveguide(position, app.AXIS.,
        ...                                    wgmodel="WG9", wg_length=2000)


        """
        p1 = -1
        p2 = -1
        WG = {
            "WG0.0": [584.2, 292.1],
            "WG0": [533.4, 266.7],
            "WG1": [457.2, 228.6],
            "WG2": [381, 190.5],
            "WG3": [292.1, 146.05],
            "WG4": [247.65, 123.825],
            "WG5": [195.58, 97.79],
            "WG6": [165.1, 82.55],
            "WG7": [129.54, 64.77],
            "WG8": [109.22, 54.61],
            "WG9": [88.9, 44.45],
            "WG9A": [86.36, 43.18],
            "WG10": [72.136, 34.036],
            "WG11": [60.2488, 28.4988],
            "WG11A": [58.166, 29.083],
            "WG12": [47.5488, 22.1488],
            "WG13": [40.386, 20.193],
            "WG14": [34.8488, 15.7988],
            "WG15": [28.4988, 12.6238],
            "WR102": [25.908, 12.954],
            "WG16": [22.86, 10.16],
            "WG17": [19.05, 9.525],
            "WG18": [15.7988, 7.8994],
            "WG19": [12.954, 6.477],
            "WG20": [0.668, 4.318],
            "WG21": [8.636, 4.318],
            "WG22": [7.112, 3.556],
            "WG23": [5.6896, 2.8448],
            "WG24": [4.7752, 2.3876],
            "WG25": [3.7592, 1.8796],
            "WG26": [3.0988, 1.5494],
            "WG27": [2.54, 1.27],
            "WG28": [2.032, 1.016],
            "WG29": [1.651, 0.8255],
            "WG30": [1.2954, 0.6477],
            "WG31": [1.0922, 0.5461],
            "WG32": [0.8636, 0.4318],
        }

        if wgmodel in WG:
            wgwidth = WG[wgmodel][0]
            wgheight = WG[wgmodel][1]
            if not wg_thickness:
                wg_thickness = wgheight / 20
            if parametrize_h:
                self._app[wgmodel + "_H"] = self._arg_with_dim(wgheight)
                h = wgmodel + "_H"
                hb = wgmodel + "_H + 2*" + self._arg_with_dim(wg_thickness)
            else:
                h = self._arg_with_dim(wgheight)
                hb = self._arg_with_dim(wgheight) + " + 2*" + self._arg_with_dim(wg_thickness)

            if parametrize_w:
                self._app[wgmodel + "_W"] = self._arg_with_dim(wgwidth)
                w = wgmodel + "_W"
                wb = wgmodel + "_W + " + self._arg_with_dim(2 * wg_thickness)
            else:
                w = self._arg_with_dim(wgwidth)
                wb = self._arg_with_dim(wgwidth) + " + 2*" + self._arg_with_dim(wg_thickness)
            if wg_direction_axis == self._app.AXIS.Z:
                airbox = self.create_box(origin, [w, h, wg_length])

                if type(wg_thickness) is str:
                    origin[0] = str(origin[0]) + "-" + wg_thickness
                    origin[1] = str(origin[1]) + "-" + wg_thickness
                else:
                    origin[0] -= wg_thickness
                    origin[1] -= wg_thickness

            elif wg_direction_axis == self._app.AXIS.Y:
                airbox = self.create_box(origin, [w, wg_length, h])

                if type(wg_thickness) is str:
                    origin[0] = str(origin[0]) + "-" + wg_thickness
                    origin[2] = str(origin[2]) + "-" + wg_thickness
                else:
                    origin[0] -= wg_thickness
                    origin[2] -= wg_thickness
            else:
                airbox = self.create_box(origin, [wg_length, w, h])

                if type(wg_thickness) is str:
                    origin[2] = str(origin[2]) + "-" + wg_thickness
                    origin[1] = str(origin[1]) + "-" + wg_thickness
                else:
                    origin[2] -= wg_thickness
                    origin[1] -= wg_thickness
            centers = [f.center for f in airbox.faces]
            xpos = [i[wg_direction_axis] for i in centers]
            mini = xpos.index(min(xpos))
            maxi = xpos.index(max(xpos))
            if create_sheets_on_openings:
                p1 = self.create_object_from_face(airbox.faces[mini].id)
                p2 = self.create_object_from_face(airbox.faces[maxi].id)
            if not name:
                name = generate_unique_name(wgmodel)
            if wg_direction_axis == self._app.AXIS.Z:
                wgbox = self.create_box(origin, [wb, hb, wg_length], name=name)
            elif wg_direction_axis == self._app.AXIS.Y:
                wgbox = self.create_box(origin, [wb, wg_length, hb], name=name)
            else:
                wgbox = self.create_box(origin, [wg_length, wb, hb], name=name)
            self.subtract(wgbox, airbox, False)
            wgbox.material_name = wg_material

            return wgbox, p1, p2
        else:
            return None

    @pyaedt_function_handler()
    def objects_in_bounding_box(self, bounding_box, check_solids=True, check_lines=True, check_sheets=True):
        """Given a bounding box checks if objects, sheets and lines are inside it.

        Parameters
        ----------
        bounding_box : list.
            List of coordinates of bounding box vertices.
        check_solids : bool, optional.
            Check solid objects.
        check_lines : bool, optional.
            Check line objects.
        check_sheets : bool, optional.
            Check sheet objects.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d`
        """

        if len(bounding_box) != 6:
            raise ValueError("Bounding box list must have dimension 6.")

        objects = []

        if check_solids:
            for obj in self.solid_objects:
                if (
                    bounding_box[3] <= obj.bounding_box[0] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[1] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[2] <= bounding_box[2]
                    and bounding_box[3] <= obj.bounding_box[3] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[4] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[5] <= bounding_box[2]
                ):
                    objects.append(obj)

        if check_lines:
            for obj in self.line_objects:
                if (
                    bounding_box[3] <= obj.bounding_box[0] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[1] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[2] <= bounding_box[2]
                    and bounding_box[3] <= obj.bounding_box[3] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[4] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[5] <= bounding_box[2]
                ):
                    objects.append(obj)

        if check_sheets:
            for obj in self.sheet_objects:
                if (
                    bounding_box[3] <= obj.bounding_box[0] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[1] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[2] <= bounding_box[2]
                    and bounding_box[3] <= obj.bounding_box[3] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[4] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[5] <= bounding_box[2]
                ):
                    objects.append(obj)

        return objects
