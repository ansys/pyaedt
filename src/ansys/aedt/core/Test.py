import ansys.aedt.core
import tempfile

from emit_core.emit_constants import EmiCategoryFilter

AEDT_VERSION = "2025.1"
NG_MODE = False

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

project_name = ansys.aedt.core.generate_unique_project_name(
    root_name=temp_folder.name, project_name="antenna_cosite")
d = ansys.aedt.core.launch_desktop(AEDT_VERSION, NG_MODE, new_desktop=True)

emit = ansys.aedt.core.Emit(project_name, version=AEDT_VERSION)

# add a couple quick radios
radio = emit.modeler.components.create_component("New Radio")
radio = emit.modeler.components.create_component("New Radio")

rev = emit.results.analyze()
cats = rev.get_emi_category_filter_enabled(EmiCategoryFilter.IN_CHANNEL_TX_INTERMOD)
#n1limit = rev.n_to_1_limit
#receivers = rev.get_receiver_names()
pass

emit.save_project()
emit.release_desktop()