from collections import OrderedDict
import math
import warnings

from pyaedt import is_ironpython
from pyaedt.edb_core.edb_data.edbvalue import EdbValue
from pyaedt.edb_core.edb_data.primitives_data import EDBPrimitives
from pyaedt.edb_core.general import PadGeometryTpe
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.edb_core.general import convert_pytuple_to_nettuple
from pyaedt.generic.clr_module import String
from pyaedt.generic.clr_module import _clr
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.geometry_operators import GeometryOperators


class HfssExtentInfo:
    """ """

    def __init__(self, pedb):
        self._pedb = pedb

        self._hfss_extent_info_type = {
            "BoundingBox": self._pedb.edb.Utility.HFSSExtentInfoType.BoundingBox,
            "Conforming": self._pedb.edb.Utility.HFSSExtentInfoType.Conforming,
            "ConvexHull": self._pedb.edb.Utility.HFSSExtentInfoType.ConvexHull,
            "Polygon": self._pedb.edb.Utility.HFSSExtentInfoType.Polygon,
        }
        self._open_region_type = {
            "Radiation": self._pedb.edb.Utility.OpenRegionType.Radiation,
            "PML": self._pedb.edb.Utility.OpenRegionType.PML,
        }
        pass

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

    @pyaedt_function_handler
    def _update_hfss_extent_info(self, hfss_extent_info):
        return self._pedb.active_cell.SetHFSSExtentInfo(hfss_extent_info)

    @property
    def _edb_hfss_extent_info(self):
        return self._pedb.active_cell.GetHFSSExtentInfo()

    @property
    def air_box_horizontal_extent_enabled(self):
        return self._edb_hfss_extent_info.AirBoxHorizontalExtent.Item2

    @air_box_horizontal_extent_enabled.setter
    def air_box_horizontal_extent_enabled(self, value):
        info = self._edb_hfss_extent_info
        info.AirBoxHorizontalExtent = convert_pytuple_to_nettuple((self.air_box_horizontal_extent, value))
        self._update_hfss_extent_info(info)

    @property
    def air_box_horizontal_extent(self):
        return self._edb_hfss_extent_info.AirBoxHorizontalExtent.Item1

    @air_box_horizontal_extent.setter
    def air_box_horizontal_extent(self, value):
        info = self._edb_hfss_extent_info
        info.AirBoxHorizontalExtent = convert_pytuple_to_nettuple((value, self.air_box_horizontal_extent_enabled))
        self._update_hfss_extent_info(info)

    @property
    def air_box_negative_vertical_extent_enabled(self):
        return self._edb_hfss_extent_info.AirBoxNegativeVerticalExtent.Item2

    @air_box_negative_vertical_extent_enabled.setter
    def air_box_negative_vertical_extent_enabled(self, value):
        info = self._edb_hfss_extent_info
        info.AirBoxNegativeVerticalExtent = convert_pytuple_to_nettuple((self.air_box_negative_vertical_extent, value))
        self._update_hfss_extent_info(info)

    @property
    def air_box_negative_vertical_extent(self):
        return self._edb_hfss_extent_info.AirBoxNegativeVerticalExtent.Item1

    @air_box_negative_vertical_extent.setter
    def air_box_negative_vertical_extent(self, value):
        info = self._edb_hfss_extent_info
        info.AirBoxNegativeVerticalExtent = convert_pytuple_to_nettuple(
            (value, self.air_box_negative_vertical_extent_enabled)
        )
        self._update_hfss_extent_info(info)

    @property
    def base_polygon(self):
        return EDBPrimitives(self._edb_hfss_extent_info.BasePolygon, self._pedb)

    @base_polygon.setter
    def base_polygon(self, value):
        info = self._edb_hfss_extent_info
        info.BasePolygon = value.primitive_object
        self._update_hfss_extent_info(info)

    @property
    def dielectric_base_polygon(self):
        return EDBPrimitives(self._edb_hfss_extent_info.DielectricBasePolygon, self._pedb)

    @dielectric_base_polygon.setter
    def dielectric_base_polygon(self, value):
        info = self._edb_hfss_extent_info
        info.DielectricBasePolygon = value.primitive_object
        self._update_hfss_extent_info(info)

    @property
    def dielectric_extent_size_enabled(self):
        return self._edb_hfss_extent_info.DielectricExtentSize.Item2

    @dielectric_extent_size_enabled.setter
    def dielectric_extent_size_enabled(self, value):
        info = self._edb_hfss_extent_info
        info.DielectricExtentSize = convert_pytuple_to_nettuple((self.dielectric_extent_size, value))
        self._update_hfss_extent_info(info)

    @property
    def dielectric_extent_size(self):
        return self._edb_hfss_extent_info.DielectricExtentSize.Item1

    @dielectric_extent_size.setter
    def dielectric_extent_size(self, value):
        info = self._edb_hfss_extent_info
        info.DielectricExtentSize = convert_pytuple_to_nettuple((value, self.dielectric_extent_size_enabled))
        self._update_hfss_extent_info(info)

    @property
    def dielectric_extent_type(self):
        return self._edb_hfss_extent_info.DielectricExtentType.ToString()

    @dielectric_extent_type.setter
    def dielectric_extent_type(self, value):
        info = self._edb_hfss_extent_info
        info.DielectricExtentType = self._hfss_extent_info_type[value]
        self._update_hfss_extent_info(info)

    @property
    def extent_type(self):
        return self._edb_hfss_extent_info.ExtentType.ToString()

    @extent_type.setter
    def extent_type(self, value):
        info = self._edb_hfss_extent_info
        info.ExtentType = self._hfss_extent_info_type[value]
        self._update_hfss_extent_info(info)

    @property
    def honor_user_dielectric(self):
        return self._edb_hfss_extent_info.HonorUserDielectric

    @honor_user_dielectric.setter
    def honor_user_dielectric(self, value):
        info = self._edb_hfss_extent_info
        info.HonorUserDielectric = value
        self._update_hfss_extent_info(info)

    @property
    def is_pml_visible(self):
        return self._edb_hfss_extent_info.IsPMLVisible

    @is_pml_visible.setter
    def is_pml_visible(self, value):
        info = self._edb_hfss_extent_info
        info.IsPMLVisible = value
        self._update_hfss_extent_info(info)

    @property
    def open_region_type(self):
        return self._edb_hfss_extent_info.OpenRegionType.ToString()

    @open_region_type.setter
    def open_region_type(self, value):
        info = self._edb_hfss_extent_info
        info.OpenRegionType = self._open_region_type[value]
        self._update_hfss_extent_info(info)

    @property
    def operating_freq(self):
        return EdbValue(self._edb_hfss_extent_info.OperatingFreq)

    @operating_freq.setter
    def operating_freq(self, value):
        if isinstance(value, EdbValue):
            value = value._edb_obj
        else:
            value = self._get_edb_value(value)
        info = self._edb_hfss_extent_info
        info.OperatingFreq = value
        self._update_hfss_extent_info(info)

    @property
    def radiation_level(self):
        return EdbValue(self._edb_hfss_extent_info.RadiationLevel)

    @radiation_level.setter
    def radiation_level(self, value):
        value = value._edb_obj if isinstance(value, EdbValue) else self._get_edb_value(value)
        info = self._edb_hfss_extent_info
        info.RadiationLevel = value
        self._update_hfss_extent_info(info)

    @property
    def sync_air_box_vertical_extent(self):
        return self._edb_hfss_extent_info.SyncAirBoxVerticalExtent

    @sync_air_box_vertical_extent.setter
    def sync_air_box_vertical_extent(self, value):
        info = self._edb_hfss_extent_info
        info.SyncAirBoxVerticalExtent = value
        self._update_hfss_extent_info(info)

    @property
    def truncate_air_box_at_ground(self):
        return self._edb_hfss_extent_info.TruncateAirBoxAtGround

    @truncate_air_box_at_ground.setter
    def truncate_air_box_at_ground(self, value):
        info = self._edb_hfss_extent_info
        info.TruncateAirBoxAtGround = value
        self._update_hfss_extent_info(info)

    @property
    def use_open_region(self):
        return self._edb_hfss_extent_info.UseOpenRegion

    @use_open_region.setter
    def use_open_region(self, value):
        info = self._edb_hfss_extent_info
        info.UseOpenRegion = value
        self._update_hfss_extent_info(info)

    @property
    def use_xy_data_extent_for_vertical_expansion(self):
        return self._edb_hfss_extent_info.UseXYDataExtentForVerticalExpansion

    @use_xy_data_extent_for_vertical_expansion.setter
    def use_xy_data_extent_for_vertical_expansion(self, value):
        info = self._edb_hfss_extent_info
        info.UseXYDataExtentForVerticalExpansion = value
        self._update_hfss_extent_info(info)

    @pyaedt_function_handler
    def load_config(self, config):
        for i, j in config.items():
            if hasattr(self, i):
                setattr(self, i, j)

    @pyaedt_function_handler
    def export_config(self):
        config = dict()
        for i in dir(self):
            if i.startswith("_"):
                continue
            elif i in ["load_config", "export_config"]:
                continue
            else:
                config[i] = getattr(self, i)
        return config
