from tkinter import ttk

def create_tab_load_config(tab_frame, master):
    row = 0
    ttk.Button(        tab_frame,        name="load_config_file",
        text="Load Config file",
        command=call_back_load,
        style="PyAEDT.TButton",
        width=30,
    ).grid(row=row, column=0)

    row = row + 1
    ttk.Button(
        tab_frame,
        name="generate_template",
        text="Generate Template",
        #command=call_back_export_template,
        style="PyAEDT.TButton",
        width=30,
    ).grid(row=row, column=0)

    row = row + 1
    ttk.Radiobutton(
        tab_frame,
        text="Active Design",
        value=True,
        #variable=tk_vars.load_active_design,
        style="PyAEDT.TRadiobutton",
        name="active_design",
    ).grid(row=row, column=0, sticky="w")
    row = row + 1
    ttk.Radiobutton(
        tab_frame,
        text="Configure File Specified Design",
        value=False,
        #variable=tk_vars.load_active_design,
        name="specified_design",
        style="PyAEDT.TRadiobutton",
    ).grid(row=row, column=0, sticky="w")

    row = row + 1
    ttk.Checkbutton(
        tab_frame,
        name="overwrite_design",
        text="Overwrite Design",
        #variable=self.tk_vars.load_overwrite,
        style="PyAEDT.TCheckbutton",
    ).grid(row=row, column=0, sticky="w")

def update(master):
    master.config.load


def call_back_load(self):
    file_path = filedialog.askopenfilename(
        title="Select Configuration",
        filetypes=(("toml", "*.toml"),),
        defaultextension=".toml",
    )

    if not file_path:  # pragma: no cover
        return

    config = CfgConfigureLayout.from_file(file_path)

    if self.tk_vars.load_active_design.get():
        aedb = get_active_edb()
        config.layout_file = aedb

    working_directory = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
    working_directory.mkdir()


    # Apply settings to Edb
    app = Edb(edbpath=str(config.layout_file), edbversion=config.version)
    if config.layout_validation.illegal_rlc_values:
        app.layout_validation.illegal_rlc_values(fix=True)

    cfg = config.get_edb_config_dict(app)

    if config.supplementary_json != "":
        app.configuration.load(config.supplementary_json)
    app.configuration.load(cfg)

    app.configuration.run()

    if self.tk_vars.load_overwrite.get():
        app.save()
        new_aedb = app.edbpath
        # Delete .aedt if it exists
        if Path(new_aedb).with_suffix(".aedt").exists():
            desktop = ansys.aedt.core.Desktop(
                new_desktop=False,
                version=VERSION,
                port=PORT,
                aedt_process_id=AEDT_PROCESS_ID,
                student_version=IS_STUDENT,
            )
            desktop.odesktop.DeleteProject(Path(new_aedb).stem)
            if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
                desktop.release_desktop(False, False)
    else:
        new_aedb = str(Path(working_directory) / Path(app.edbpath).name)
        app.save_as(new_aedb)
    app.close()
    settings.logger.info(f"New Edb is saved to {new_aedb}")

    # Open new Edb in AEDT
    app = ansys.aedt.core.Hfss3dLayout(
        project=str(new_aedb),
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)
    return True