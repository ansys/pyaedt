from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.toolkits.antennas.patch import Patch


class Antennas(object):
    def __init__(self, app):
        self._app = app

    def rectangular_patch_w_probe(
        self,
        frequency=10.0,
        frequency_unit="GHz",
        material="FR4_epoxy",
        outer_boundary=None,
        huygens_box=False,
        substrate_height=0.1575,
        length_unit="cm",
        coordinate_system="Global",
        antenna_name=None,
        position=None,
    ):
        if not position:
            position = [0, 0, 0]

        if not antenna_name:
            antenna_name = generate_unique_name("Patch")

        rect_patch = Patch(
            self._app,
            frequency=frequency,
            frequency_unit=frequency_unit,
            material=material,
            outer_boundary=outer_boundary,
            huygens_box=huygens_box,
            length_unit=length_unit,
            substrate_height=substrate_height,
            coordinate_system=coordinate_system,
            antenna_name=antenna_name,
            position=position,
        )
        rect_patch._draw()
        return rect_patch
