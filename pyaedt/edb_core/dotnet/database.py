"""Database."""
import os
import sys

from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import env_path
from pyaedt.generic.general_methods import env_path_student
from pyaedt.generic.general_methods import env_value
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import is_linux
from pyaedt.generic.general_methods import settings


class HierarchyDotNet:
    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except:
            try:
                return getattr(self._hierarchy, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, hier):
        self._hierarchy = hier

    @property
    def component(self):
        """Edb Dotnet Api Database `Edb.Cell.Hierarchy.Component`."""
        return self._hierarchy.Component

    @property
    def cell_instance(self):
        """Edb Dotnet Api Database `Edb.Cell.Hierarchy.CellInstance`."""
        return self._hierarchy.CellInstance

    @property
    def pin_group(self):
        """Edb Dotnet Api Database `Edb.Cell.Hierarchy.PinGroup`."""
        return self._hierarchy.PinGroup


class PolygonDataDotNet:
    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except:
            try:
                return getattr(self.dotnetobj, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, pdata):
        self.dotnetobj = pdata

    def get_bbox_of_boxes(self, points):
        if isinstance(points, list):
            points = convert_py_list_to_net_list(points)
        return self.dotnetobj.GetBBoxOfBoxes(points)

    def get_bbox_of_polygons(self, polygons):
        if isinstance(polygons, list):
            polygons = convert_py_list_to_net_list(polygons)
        return self.dotnetobj.GetBBoxOfPolygons(polygons)

    def create_from_bbox(self, points):
        if isinstance(points, list):
            points = convert_py_list_to_net_list(points)
        return self.dotnetobj.CreateFromBBox(points)

    def create_from_arcs(self, arcs, flag):
        if isinstance(arcs, list):
            arcs = convert_py_list_to_net_list(arcs)
        return self.dotnetobj.CreateFromArcs(arcs, flag)

    def unite(self, pdata):
        if isinstance(pdata, list):
            pdata = convert_py_list_to_net_list(pdata)
        return self.dotnetobj.Unite(pdata)

    def get_convex_hull_of_polygons(self, pdata):
        if isinstance(pdata, list):
            pdata = convert_py_list_to_net_list(pdata)
        return self.dotnetobj.GetConvexHullOfPolygons(pdata)


class NetDotNet:
    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except:
            try:
                return getattr(self.net, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, net):
        self.net = net

    def find_by_name(self, layout, net):
        return self.net.FindByName(layout, net)

    def create(self, layout, name):
        return self.net.Create(layout, name)


class CellClassDotNet:
    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except:
            try:
                return getattr(self._cell, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, cell):
        self._cell = cell

    @property
    def terminal(self):
        """Edb Dotnet Api Database `Edb.Cell.Terminal`."""
        return self._cell.Terminal

    @property
    def hierarchy(self):
        """Edb Dotnet Api Database `Edb.Cell.Hierarchy`."""
        return HierarchyDotNet(self._cell.Hierarchy)

    @property
    def cell(self):
        """Edb Dotnet Api Database `Edb.Cell`."""
        return self._cell.Cell

    @property
    def net(self):
        return NetDotNet(self._cell.Net)

    @property
    def layer_type(self):
        return self._cell.LayerType

    @property
    def layer_type_set(self):
        return self._cell.LayerTypeSet

    @property
    def layer(self):
        return self._cell.Layer

    @property
    def layout_object_type(self):
        return self._cell.LayoutObjType

    @property
    def primitive(self):
        """Edb Dotnet Api Database `Edb.Cell.Primitive`."""
        return self._cell.Primitive


class UtilityDotNet:
    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except:
            try:
                return getattr(self.utility, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, utility):
        self.utility = utility

    def value(self, value, varserver=None):
        if varserver:
            return self.utility.Value(value, varserver)
        else:
            return self.utility.Value(value)


class GeometryDotNet:
    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except:
            try:
                return getattr(self.geometry, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, geometry, utility):
        self.geometry = geometry
        self.utility = utility

    def point_data(self, p1, p2):
        if isinstance(p1, (int, float, str, list)):
            p1 = UtilityDotNet(self.utility).value(p1)
        if isinstance(p2, (int, float, str, list)):
            p2 = UtilityDotNet(self.utility).value(p2)
        return self.geometry.PointData(p1, p2)

    def point3d_data(self, p1, p2, p3):
        if isinstance(p1, (int, float, str, list)):
            p1 = UtilityDotNet(self.utility).value(p1)
        if isinstance(p2, (int, float, str, list)):
            p2 = UtilityDotNet(self.utility).value(p2)
        if isinstance(p3, (int, float, str, list)):
            p3 = UtilityDotNet(self.utility).value(p3)
        return self.geometry.Point3DData(p1, p2, p3)

    @property
    def extent_type(self):
        return self.geometry.ExtentType

    @property
    def polygon_data(self):
        return PolygonDataDotNet(self.geometry.PolygonData)

    def arc_data(self, point1, point2, rotation=None, height=None):
        if isinstance(point1, (list, tuple)):
            point1 = self.point_data(point1[0], point1[1])
        if isinstance(point2, (list, tuple)):
            point2 = self.point_data(point2[0], point2[1])
        if height and isinstance(height, (list, tuple)):
            height = self.point_data(height[0], height[1])
        if rotation and height:
            return self.geometry.ArcData(point1, point2, rotation, height)
        else:
            return self.geometry.ArcData(point1, point2)


class CellDotNet:
    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except:
            try:
                return getattr(self.edb, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, edb):
        self.edb = edb

    @property
    def definition(self):
        return self.edb.Definition

    @property
    def database(self):
        """Edb Dotnet Api Database."""
        return self.edb.Database

    @property
    def cell(self):
        """Edb Dotnet Api Database `Edb.Cell`."""
        return CellClassDotNet(self.edb.Cell)

    @property
    def utility(self):
        return UtilityDotNet(self.edb.Utility)

    @property
    def geometry(self):
        return GeometryDotNet(self.edb.Geometry, self.edb.Utility)


class EdbDotNet:
    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except:
            try:
                return getattr(self._edb, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, edbversion, student_version=False):
        self.edbversion = edbversion
        self.student_version = student_version
        """Initialize DLLs."""
        from pyaedt.generic.clr_module import _clr

        if is_linux:
            if env_value(self.edbversion) in os.environ or settings.edb_dll_path:
                if settings.edb_dll_path:
                    self.base_path = settings.edb_dll_path
                else:
                    self.base_path = env_path(self.edbversion)
                sys.path.append(self.base_path)
            else:
                main = sys.modules["__main__"]
                if "oDesktop" in dir(main):
                    self.base_path = main.oDesktop.GetExeDir()
                    sys.path.append(main.oDesktop.GetExeDir())
                    os.environ[env_value(self.edbversion)] = self.base_path
                else:
                    edb_path = os.getenv("PYAEDT_SERVER_AEDT_PATH")
                    if edb_path:
                        self.base_path = edb_path
                        sys.path.append(edb_path)
                        os.environ[env_value(self.edbversion)] = self.base_path
            if is_ironpython:
                _clr.AddReferenceToFile("Ansys.Ansoft.Edb.dll")
                _clr.AddReferenceToFile("Ansys.Ansoft.EdbBuilderUtils.dll")
                _clr.AddReferenceToFileAndPath(os.path.join(self.base_path, "Ansys.Ansoft.SimSetupData.dll"))
            else:
                _clr.AddReference("Ansys.Ansoft.Edb")
                _clr.AddReference("Ansys.Ansoft.EdbBuilderUtils")
                _clr.AddReference("Ansys.Ansoft.SimSetupData")
        else:
            if settings.edb_dll_path:
                self.base_path = settings.edb_dll_path
            elif self.student_version:
                self.base_path = env_path_student(self.edbversion)
            else:
                self.base_path = env_path(self.edbversion)
            sys.path.append(self.base_path)
            _clr.AddReference("Ansys.Ansoft.Edb")
            _clr.AddReference("Ansys.Ansoft.EdbBuilderUtils")
            _clr.AddReference("Ansys.Ansoft.SimSetupData")
        os.environ["ECAD_TRANSLATORS_INSTALL_DIR"] = self.base_path
        oaDirectory = os.path.join(self.base_path, "common", "oa")
        os.environ["ANSYS_OADIR"] = oaDirectory
        os.environ["PATH"] = "{};{}".format(os.environ["PATH"], self.base_path)
        edb = __import__("Ansys.Ansoft.Edb")
        self._edb = edb.Ansoft.Edb
        edbbuilder = __import__("Ansys.Ansoft.EdbBuilderUtils")
        self.edbutils = edbbuilder.Ansoft.EdbBuilderUtils
        self.simSetup = __import__("Ansys.Ansoft.SimSetupData")
        self.simsetupdata = self.simSetup.Ansoft.SimSetupData.Data

    @property
    def edb_api(self):
        """Edb Dotnet Api class."""
        return CellDotNet(self._edb)

    @property
    def database(self):
        """Edb Dotnet Api Database."""
        return self.edb_api.database

    @property
    def definition(self):
        """Edb Dotnet Api Database `Edb.Definition`."""
        return self.edb_api.Definition


class Database(EdbDotNet):
    """Class representing a database object."""

    def __init__(self, edbversion, student_version=False):
        """Initialize a new Database."""
        EdbDotNet.__init__(self, edbversion, student_version)
        self._db = None

    @property
    def db(self):
        """Active database object."""
        return self._db

    def run_as_standalone(self, flag):
        self.edb_api.database.SetRunAsStandAlone(flag)

    def create(self, db_path):
        """Create a Database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level database folder

        Returns
        -------
        Database
        """
        self._db = self.edb_api.database.Create(db_path)
        return self._db

    def open(self, db_path, read_only):
        """Open an existing Database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level Database folder.
        read_only : bool
            Obtain read-only access.

        Returns
        -------
        Database or None
            The opened Database object, or None if not found.
        """
        self._db = self.edb_api.database.Open(
            db_path,
            read_only,
        )
        return self._db

    def delete(self, db_path):
        """Delete a database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level database folder.
        """
        return self.edb_api.database.Delete(db_path)

    def save(self):
        """Save any changes into a file."""
        return self._db.Save()

    def close(self):
        """Close the database.

        .. note::
            Unsaved changes will be lost.
        """
        return self._db.Close()

    @property
    def top_circuit_cells(self):
        """Get top circuit cells.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return list(self._db.TopCircuitCells)

    @property
    def circuit_cells(self):
        """Get all circuit cells in the Database.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return list(self._db.CircuitCells)

    @property
    def footprint_cells(self):
        """Get all footprint cells in the Database.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return list(self._db.FootprintCells)

    @property
    def edb_uid(self):
        """Get ID of the database.

        Returns
        -------
        int
            The unique EDB id of the Database.
        """
        return self._db.GetId()

    @property
    def is_read_only(self):
        """Determine if the database is open in a read-only mode.

        Returns
        -------
        bool
            True if Database is open with read only access, otherwise False.
        """
        return self._db.IsReadOnly()

    def find_by_id(self, db_id):
        """Find a database by ID.

        Parameters
        ----------
        db_id : int
            The Database's unique EDB id.

        Returns
        -------
        Database
            The Database or Null on failure
        """
        self.edb_api.database.FindById(db_id)

    def save_as(self, path, version=""):
        """Save this Database to a new location and older EDB version.

        Parameters
        ----------
        path : str
            New Database file location.
        version : str
            EDB version to save to. Empty string means current version.
        """
        self._db.SaveAs(path, version)

    def get_version_by_release(self, release):
        """Get the EDB version corresponding to the given release name.

        Parameters
        ----------
        release : str
           Release name.

        Returns
        -------
        str
           EDB version.
        """
        self._db.GetVersionByRelease(release)

    @property
    def directory(self):
        """Get the directory of the Database.

        Returns
        -------
        str
            Directory of the Database.
        """
        return self._db.GetDirectory()

    def get_product_property(self, prod_id, attr_it):
        """Get the product-specific property value.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.
        attr_it : int
            Attribute ID.

        Returns
        -------
        str
            Property value returned.
        """
        return self._db.GetProductProperty(prod_id, attr_it)

    def set_product_property(self, prod_id, attr_it, prop_value):
        """Set the product property associated with the given product and attribute ids.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.
        attr_it : int
            Attribute ID.
        prop_value : str
            Product property's new value
        """
        self._db.SetProductProperty(prod_id, attr_it, prop_value)

    def get_product_property_ids(self, prod_id):
        """Get a list of attribute ids corresponding to a product property id.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.

        Returns
        -------
        list[int]
            The attribute ids associated with this product property.
        """
        return self._db.GetProductPropertyIds(prod_id)

    def import_material_from_control_file(self, control_file, schema_dir=None, append=True):
        """Import materials from the provided control file.

        Parameters
        ----------
        control_file : str
            Control file name with full path.
        schema_dir : str
            Schema file path.
        append : bool
            True if the existing materials in Database are kept. False to remove existing materials in database.
        """
        self._db.ImportMaterialFromControlFile(
            control_file,
            schema_dir,
            append,
        )

    @property
    def version(self):
        """Get version of the Database.

        Returns
        -------
        tuple(int, int)
            A tuple of the version numbers [major, minor]
        """
        major, minor = self._db.GetVersion()
        return major, minor

    def scale(self, scale_factor):
        """Uniformly scale all geometry and their locations by a positive factor.

        Parameters
        ----------
        scale_factor : float
            Amount that coordinates are multiplied by.
        """
        self._db.Scale(scale_factor)

    @property
    def source(self):
        """Get source name for this Database.

        This attribute is also used to set the source name.

        Returns
        -------
        str
            name of the source
        """
        return self._db.GetSource()

    @source.setter
    def source(self, source):
        """Set source name of the database."""
        self._db.SetSource(source)

    @property
    def source_version(self):
        """Get the source version for this Database.

        This attribute is also used to set the version.

        Returns
        -------
        str
            version string

        """
        return self._db.GetSourceVersion()

    @source_version.setter
    def source_version(self, source_version):
        """Set source version of the database."""
        self._db.SetSourceVersion(source_version)

    def copy_cells(self, cells_to_copy):
        """Copy Cells from other Databases or this Database into this Database.

        Parameters
        ----------
        cells_to_copy : list[:class:`Cell <ansys.edb.layout.Cell>`]
            Cells to copy.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
            New Cells created in this Database.
        """
        _dbCells = convert_py_list_to_net_list(cells_to_copy)
        return self._db.CopyCells(_dbCells)

    @property
    def apd_bondwire_defs(self):
        """Get all APD bondwire definitions in this Database.

        Returns
        -------
        list[:class:`ApdBondwireDef <ansys.edb.definition.ApdBondwireDef>`]
        """
        return list(self._db.APDBondwireDefs)

    @property
    def jedec4_bondwire_defs(self):
        """Get all JEDEC4 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec4BondwireDef <ansys.edb.definition.Jedec4BondwireDef>`]
        """
        return list(self._db.Jedec4BondwireDefs)

    @property
    def jedec5_bondwire_defs(self):
        """Get all JEDEC5 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec5BondwireDef <ansys.edb.definition.Jedec5BondwireDef>`]
        """
        return list(self._db.Jedec5BondwireDefs)

    @property
    def padstack_defs(self):
        """Get all Padstack definitions in this Database.

        Returns
        -------
        list[:class:`PadstackDef <ansys.edb.definition.PadstackDef>`]
        """
        return list(self._db.PadstackDefs)

    @property
    def package_defs(self):
        """Get all Package definitions in this Database.

        Returns
        -------
        list[:class:`PackageDef <ansys.edb.definition.PackageDef>`]
        """
        return list(self._db.PackageDefs)

    @property
    def component_defs(self):
        """Get all component definitions in the database.

        Returns
        -------
        list[:class:`ComponentDef <ansys.edb.definition.ComponentDef>`]
        """
        return list(self._db.ComponentDefs)

    @property
    def material_defs(self):
        """Get all material definitions in the database.

        Returns
        -------
        list[:class:`MaterialDef <ansys.edb.definition.MaterialDef>`]
        """
        return list(self._db.MaterialDefs)

    @property
    def dataset_defs(self):
        """Get all dataset definitions in the database.

        Returns
        -------
        list[:class:`DatasetDef <ansys.edb.definition.DatasetDef>`]
        """
        return list(self._db.DatasetDefs)

    def attach(self, hdb):
        """Attach the database to existing AEDT instance.

        Parameters
        ----------
        hdb

        Returns
        -------

        """
        from pyaedt.generic.clr_module import Convert

        hdl = Convert.ToUInt64(hdb)
        return self.edb_api.database.attach(hdl)
