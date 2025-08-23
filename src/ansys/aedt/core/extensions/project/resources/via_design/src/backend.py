import json
from pathlib import Path
import tempfile

from pyedb import Edb
from pyedb.extensions.via_design_backend import Board


class ViaDesignBackend:
    _OUTPUT_DIR = None

    @property
    def output_dir(self):
        if self._OUTPUT_DIR is None:
            output_dir = self.cfg["general"]["output_dir"]
            if output_dir == "":
                self._OUTPUT_DIR = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
            else:
                self._OUTPUT_DIR = Path(output_dir)
        return self._OUTPUT_DIR

    def __init__(self, cfg):
        cfg_json = {
            "stackup": {"layers": [], "materials": []},
            "variables": [],
            "ports": [],
            "modeler": {"traces": [], "planes": [], "padstack_definitions": [], "padstack_instances": []},
        }

        self.cfg = cfg
        self.version = self.cfg["general"]["version"]
        outline_extent = self.cfg["placement"]["outline_extent"]
        pitch = self.cfg["placement"]["pitch"]

        board = Board(
            stackup=self.cfg["stackup"] if isinstance(self.cfg["stackup"], list) else self.cfg["stackup"]["layers"],
            padstack_defs=self.cfg["padstack_defs"],
            outline_extent=outline_extent,
            pitch=pitch,
            pin_map=self.cfg["placement"]["pin_map"],
            signals=self.cfg["signals"],
            differential_signals=self.cfg["differential_signals"],
        )
        board.populate_config(cfg_json)

        self.cfg_json = cfg_json

    def create_edb(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_dir / "config.json", "w") as f:
            json.dump(self.cfg_json, f, indent=4)
        app = Edb(
            edbpath=str((Path(self.output_dir) / self.cfg["title"]).with_suffix(".aedb")), version=self.version
        )
        app.configuration.load(self.cfg_json, apply_file=True)
        app.save()
        app.close()
        return app.edbpath
