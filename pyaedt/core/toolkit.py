"""
Toolkit Module
----------------

Disclaimer
==========

**Copyright (c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited**

**This tool release is unofficial and not covered by standard Ansys Support license.**


Description
==========

This module contains a number of classes designed to support development of WPF GUI-based toolkits for AEDT
applications. The primary classes are:

    AEDTToolkit             : Base Class to support UI Toolkit development
    AEDTToolkitSettings     : Class to support UI settings for testing purposes
    ToolkitBuilder          : Class to support generation of a zip package wth all needed dependencies

:Example:

**Example 1**
A toolkit is built by deriving a class called ApplicationWindow from AEDTToolkit. Parallel to this file, an xaml file
should be present in the same directory.

from pyaedt.Maxwell import Maxwell2D
from pyaedt.Toolkit import AEDTToolkit, launch, select_directory

class ApplicationWindow(AEDTToolkit):

    def custom_callback(self):
        pass

    def __init__(self):
        AEDTToolkit.__init__(self, toolkit_file=__file__, aedt_design=Maxwell2D(), parent_design_name=None)

        # Setup Callbacks
        # Textbox inputs with validation callbacks
        self.set_callback('_input1', 'LostFocus', self.validate_positive_float)
        self.set_callback('_input2', 'LostFocus', self.validate_positive_float_variable)

        # Button click callback to toolkit-specific method self.custom_callback
        self.set_callback('run_method', 'Click', self.custom_callback)

        # Toolkit Function from here
        value1 = self.ui.float_value("_input1")
        value2 = self.ui.text_value("_input2")

# Launch the toolkit
if __name__ == '__main__':
    launch(__file__, version="2019.3", autosave=False)

================

"""
from __future__ import absolute_import
from __future__ import print_function
import os
import json
import sys
import clr
import subprocess
import shutil
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED

from .desktop import Desktop, get_version_env_variable, get_version_key, force_close_desktop
if sys.implementation.name == 'ironpython':
    clr.AddReference("PresentationFramework")
    clr.AddReference("PresentationCore")
    clr.AddReference("System.Windows")
    clr.AddReference("System.Windows.Forms")
    clr.AddReference("System.Drawing")
else:
    clr.AddReference("System.Xml")
    clr.AddReference("PresentationFramework, Version=3.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35")
    clr.AddReference("PresentationCore, Version=3.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35")
    clr.AddReference('System.Windows.Forms')
    clr.AddReference('System')
    from System.IO import StreamReader
    from System.Windows.Markup import XamlReader

from System.Windows import LogicalTreeHelper
from System.Windows import Window, Application, Controls, Visibility, Input, Thickness
from System.Windows.Forms import Form, ListBox, DockStyle, Button, MessageBox, MessageBoxIcon, MessageBoxButtons
from System.Windows.Forms import FormBorderStyle, StatusBar, SelectionMode, DialogResult, FolderBrowserDialog, OpenFileDialog
from System.Windows.Media import Brushes
from System.Drawing import Size, Point, Bitmap

from System.Windows.Media.Imaging import BitmapImage, BitmapCacheOption, BitmapCreateOptions
from System import Uri, UriKind, Environment


def select_file(initial_dir=None, filter=None):
    '''

    from pyaedt.Toolkit import select_file
    load_profile = select_file(filter="csv files (*.csv)|*.csv")

    :param initial_dir:
    :param filter:
    :return:
    '''
    browser = OpenFileDialog()
    browser.Title = "Select a file with optional filter and directory"
    if initial_dir:
        browser.InitialDirectory = initial_dir
    if filter:
        browser.Filter = filter
    ret_val = browser.ShowDialog()
    if ret_val == DialogResult.OK:
        return browser.FileName
    else:
        return None

def select_directory(initial_dir=None, description=None):
        browser = FolderBrowserDialog()

        if initial_dir:
            browser.RootFolder = Environment.SpecialFolder.Desktop
            browser.SelectedPath = initial_dir
        if description:
            browser.Description = description
        else:
            browser.Description = "Select an empty folder to create the toolkit"

        test = browser.ShowDialog()
        if test == DialogResult.OK:
            return browser.SelectedPath
        else:
            return None

def copy_files_mkdir(root, files_in_subdir):
    if not os.path.exists(root):
        os.mkdir(root)
    for src_file, dest_file in files_in_subdir.items():
        shutil.copyfile(src_file, dest_file)


def print_timelog(str):
    time_value = datetime.now().time()
    print("{0}: {1}".format(time_value, str))


#def launch(workflow_module, version=None, autosave=False, close_desktop_on_exit=False):
def launch(workflow_module, version=None, autosave=False, close_desktop_on_exit=False):
    ''' Launches the ApplicationWindow class for the given module name which must lie within the path scope of
        the calling toolkit. Optionally the version can be specified in the form 20xx.y, e.g. 2019.3

        IronPython calls the run_application function of the ApplicationThread class. For CPython, a Thread with
        Apartment State is generated to adhere to requirements of System.Windows
    '''
    app = ApplicationThread(workflow_module, version, autosave, close_desktop_on_exit)

    if sys.implementation.name != 'ironpython':
        import clr
        clr.AddReference('System.Windows')
        from System.Threading import Thread, ThreadStart, ApartmentState

        print(close_desktop_on_exit)
        thread = Thread(ThreadStart(app.run_application))
        thread.SetApartmentState(ApartmentState.STA)
        thread.Start()
        thread.Join()
    else:
        if version:
            app.run_application()
        else:
            app.open_form()


launch_script='''
import os
import sys

# Ensure that this launch directory is included to the search path (needed for IronPython under AEDT)
toolkit_directory = os.path.abspath(os.path.dirname(__file__))
toolkit_lib_directory = os.path.join(toolkit_directory, 'lib')
sys.path.append(toolkit_directory)
sys.path.append(toolkit_lib_directory)

from lib.pyaedt.Toolkit import launch
launch('{}', version="2019.3")
'''

def message_box(text, caption=None, buttons=None, icon=None):
    '''
    :param text:        Main text of the message
    :param caption:     Caption of the window
    :param buttons:     Button type string (OK, OKCancel, YesNoCancel, YesNo)
    :param icon:        Valid icon type string (see below)
    :return:

    Valid types for the icon argument are :
        Asterisk
        Error
        Exclamation
        Hand
        Information
        None
        Question
        Stop
        Warning
    '''

    if not icon:
        icon_object = getattr(MessageBoxIcon, 'Information')
    else:
        icon_object = getattr(MessageBoxIcon, 'Information')

    if not caption:
        caption = ""

    if not buttons:
        buttons_object = MessageBoxButtons.OK
    else:
        buttons_object = getattr(MessageBoxButtons, buttons)

    result = MessageBox.Show(text, caption, buttons_object, icon_object)
    return result


class ToolkitBuilder():
    """
    **Class ToolkitBuilder**

    Class to help create a deployable zip file of the application and any dependencies that are not available via pip.

    Example: Build file placed in the Toolkit directory

        from pyaedt.Toolkit import ToolkitBuilder
        bld = ToolkitBuilder(__file__)
        bld.copy_from_local(extension=['py', 'xaml'])
        bld.copy_from_repo(sub_dir='pyaedt')
        bld.zip_archive()

    """

    def __init__(self, local_path, app_name=None):
        """ Instantiates a ToolkitBuilder object. This object manages the packaging of the WPF GUI to ensure
            that any dependencies not available via pip are stored with the toolkit deployable asset

        :param local_path:  path of the top-level toolkit files containing the *.py and *.xaml files. Optionally a file
                            located in the toolkit directory (typically __file__) tcan also be given

        :param app_name:    string name of the toolkit (optional) If not defined, tehn the name of the
                            parent directory is used
        """

        # if the local_path is defined as a file, take the path of that file
        if os.path.isfile(local_path):
            self.local_path = os.path.dirname(os.path.realpath(local_path))
        else:
            self.local_path = local_path

        if app_name:
            self.py_name = app_name
        else:
            self.py_name = os.path.basename(os.path.dirname(os.path.realpath(local_path)))

        self.toolkit_path = os.path.join(self.local_path, "..")

        # Extract the commit ID from the global repository
        self.global_lib_path = os.path.abspath(os.path.join(self.local_path, "..", "..", ".."))
        os.chdir(self.global_lib_path)
        command = [ 'git', 'rev-parse', 'HEAD']
        sh = False
        res = subprocess.check_output(command, shell=sh).rstrip()

        # Create a directory called 'build' in the xml directory
        self.build_path = os.path.join(self.local_path, '.build')
        if not os.path.isdir(self.build_path):
            os.mkdir(self.build_path)

        # Create a drectory named by the datetime (remove contents if already exists)
        self.build_name = '{0}-{date:%Y%m%d_%H%M}'.format( self.py_name, date=datetime.now() )
        self.commit_path = os.path.join(self.build_path, self.build_name)
        self.commit_lib_path = os.path.join(self.commit_path, 'lib')
        if os.path.isdir(self.commit_path):
            shutil.rmtree(self.commit_path)
        os.mkdir(self.commit_path)
        os.mkdir(self.commit_lib_path)

        # Add the commit hash to the module __init__.py files
        init_files =[]
        init_files.append(os.path.join(self.commit_lib_path, '__init__.py'))
        for file in init_files:
            with open(file, 'w') as f:
                f.write('#{0}\n'.format(res))

        # Create a launch file
        script_file = os.path.join(self.commit_path, "launch.py")
        with open(script_file, 'w') as f:
            f.write(launch_script.format(self.py_name))

    def copy_from_local(self, extension=None, ignore_dir=None):
        """ copy recursively all files in the local directory and all subdirectories of a given list of
            extensions

        :param extension: list of extensions to be copied, e.g. ['py', 'xaml']
        :param ignore_dir: boolean: ignore directories starting with "." or "_"
        """
        self.copy_from_repo(self.local_path, extension=extension, ignore_dir=ignore_dir)

    def copy_from_repo(self, root_dir=None, sub_dir=None, extension=None, ignore_dir=None):
        """ copy recursively all files from a specfied root directory and all subdirectories of a given list of
            extensions

        :param root_dir: optional root directory to copy from, default is the AnsysAutomation repository
        :param sub_dir: optional specific sub-directory within the root directory
        :param extension: list of extensions to be copied, e.g. ['py', 'xaml']
        :param ignore_dir: boolean: ignore directories starting with "." or "_"
        """
        if not extension:
            extension = ['py']
        elif isinstance(extension, str):
            extension = [extension]
        assert isinstance(extension, list), "Extension input parameter must be a string or a list"

        if not ignore_dir:
            ignore_dir = ['.', '_']
        elif isinstance(ignore_dir, str):
            extension = [ignore_dir]
        assert isinstance(ignore_dir, list), "Extension input parameter must be a string or a list"

        if not root_dir:
            root_dir = self.global_lib_path
        walk_dir = root_dir
        if sub_dir:
            if isinstance(sub_dir, str):
                sub_dir = [sub_dir]
            assert isinstance(sub_dir, list), "sub_dir must be a list or a string"
            for x in sub_dir:
                walk_dir = os.path.join(walk_dir, x)

        ignored_paths = []
        for root, dir, files in os.walk(walk_dir):
            ignore_path = False
            if ignore_dir:
                for x in ignore_dir:
                    if os.path.basename(root).startswith(x):
                        ignored_paths.append(root)
                        ignore_path = True
                        break
                for x in ignored_paths:
                    if root.startswith(x):
                        ignore_path = True
                        break
            if not ignore_path:
                files_in_subdir={}
                dest_dir = root.replace(root_dir, self.commit_lib_path)
                for name in files:
                    for ext in extension:
                        if name.endswith((ext)):
                            src_file = os.path.join(root, name)
                            dst_file = src_file.replace(root_dir, self.commit_lib_path)
                            files_in_subdir[src_file] = dst_file
                            break
                copy_files_mkdir(dest_dir, files_in_subdir)

    def zip_archive(self):
        """ Zip the collected data in the buld path """

        zip_archive = os.path.join(self.build_path, self.build_name + '.zip')
        with ZipFile(zip_archive, 'w', ZIP_DEFLATED) as myzip:
            for root, dirs, files in os.walk(self.commit_path):
                for filename in files:
                    abs_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(abs_path, self.commit_path)
                    myzip.write(abs_path, arcname=rel_path)

        # remove the commit directory
        shutil.rmtree(self.commit_path)


class ApplicationThread(object):
    """
    **Class ApplicationThread**

    Class to allow data to be passed to the run_application member function in a new thread.
        The run_application function connects to Desktop and instantiates an ApplicationWindow object of
        the calling module
    """
    def __init__(self, workflow_module, version, autosave=False, close_desktop_on_exit=False):
    #def __init__(self, workflow_module, version, autosave=False):
        self.workflow_module = os.path.basename(workflow_module).replace('.py', '')
        self.version = version
        self.autosave = autosave
        self.close_desktop_on_exit = close_desktop_on_exit

    def run_application(self):
        with Desktop(self.version, AlwaysNew=False) as d:
            if self.autosave:
                d.enable_autosave()
            else:
                d.disable_autosave()
            form_object = __import__(self.workflow_module)
            with form_object.ApplicationWindow() as form:
                form.display()
                print(self.close_desktop_on_exit)
                if self.close_desktop_on_exit:
                    force_close_desktop()

    def open_form(self):
        form_object = __import__(self.workflow_module)
        with form_object.ApplicationWindow() as form:
            form.display()


# Manages the settings data for the toolkit
class AEDTToolkitSettings:
    """ **AEDTToolkitSettings**

        This class provides a minimal implementation of the Toolkit providing assess to the settings file and
        allowing to call the toolkit_functionality without the GUI to speed up debugging (or potentially to
        deploy the function in batch mode. Typical usage looks like this:

               with Desktop(version="2019.3") as d:
                    app = AEDTToolkitTester(toolkit_file=__file__, aedt_app=Maxwell2D())
                    # if the settings file (app.settings_file) is present, the data is read automatically, otherwise
                    # GUI data can be generated by hand, e.g.
                    app.settings_data = {'param 1': 3, 'param 2': 'house' }
                    toolkit_function(app)
    """

    @property
    def settings_file(self):
        return os.path.join(self.settings_path, self.toolkit_name + "_Settings.json")

    @property
    def results_path(self):
        return os.path.join(self._parent.working_directory, "_results")

    @property
    def data_path(self):
        return os.path.join(self._working, "_data")

    @property
    def local_path(self):
        if self._working:
            return self._working
        else:
            return self._parent.working_directory

    @property
    def settings_path(self):
        '''
            Returns the working directory of the parent design - checks the current design settings
            file for the key "parent" to find teh name of the parent design
        '''
        my_path = self.local_path
        my_settings_file = os.path.join(self.local_path, self.toolkit_name + "_Settings.json")
        if os.path.exists(my_settings_file):
            settings_data = self.read_settings_file(my_settings_file)
            if "parent" in settings_data:
                if settings_data["parent"]:
                    my_dir = os.path.basename(my_path)
                    my_path =  my_path.replace(my_dir, settings_data["parent"])
        return my_path

    def read_settings_file(self, filename):
        with open(filename, 'r') as f:
            try:
                settings_data = json.load(f)
            except ValueError:
                if self._parent:
                    msg_string = "Invalid json file {0} will be overwritten.".format(filename)
                    self._parent._messenger.add_warning_message(msg_string)
                return None
        return settings_data

    @property
    def settings_data(self):
        settings_file = self.settings_file
        if os.path.exists(settings_file):
            return self.read_settings_file(self.settings_file)
        else:
            return {"parent": None}

    def __init__(self, aedtdesign=None, working_directory=None, toolkit_name=None):
        if aedtdesign:
            self._parent = aedtdesign
            self._working = None
        elif working_directory:
            assert os.path.exists(working_directory), "Working Directory {} does not exist"
            self._working = working_directory
        else:
            self._parent = None
            self._working = None
            #raise Exception("Toolkit name/file not defined")

        self.toolkit_name = toolkit_name

    def append_toolkit_dir(self):
        assert os.path.exists(self.settings_file), "Settings File not defined!"
        try:
            toolkit_dir = self.settings_data["_toolkit_dir"]
            sys.path.append(toolkit_dir)
        except KeyError:
            pass


class ListBoxForm(Form):

    @property
    def ResultOK(self):
        if self.DialogResult == DialogResult.OK:
            return True
        else:
            return False

    def __init__(self, list_items, default_item=None):

        self.MinimizeBox = False
        self.MaximizeBox = False
        self.Text = "Select Export Objects"

        self.lb = ListBox()
        self.lb.Parent = self
        for item in list_items:
            self.lb.Items.Add(item)
        self.lb.Location = Point(10, 10)
        self.lb.Size = Size(200, 250)
        self.lb.SelectedIndexChanged += self.OnChanged
        self.lb.SelectionMode = SelectionMode.MultiExtended
        self.sb = StatusBar()
        self.sb.Parent = self
        self.Size = Size(300, 350)
        self.CenterToScreen()

        # Define the border style of the form to a dialog box.
        self.FormBorderStyle = FormBorderStyle.FixedDialog;
        button1 = Button()
        button2 = Button()

        # Set the text of button1 to "OK".
        button1.Text = "OK"
        button2.Text = "Cancel"

        button1.Location = Point(10, self.lb.Bottom + 5)
        button2.Location  = Point(button1.Left + button1.Width + 10, button1.Top)

        button1.DialogResult = DialogResult.OK
        button2.DialogResult = DialogResult.Cancel

        self.AcceptButton = button1
        self.CancelButton = button2

        # Add buttons to the form.
        self.Controls.Add(button1)
        self.Controls.Add(button2)

        if default_item:
            if default_item in self.lb.Items:
                index_of_default_item = self.lb.Items.IndexOf(default_item)
                self.lb.SelectedIndex = index_of_default_item

    def OnChanged(self, sender, event):
        self.sb.Text = ";".join(sender.SelectedItems)


class UIObjectGetter:
    ''' Child class of a parent supplying a get_ui_object function returning a WPF GUI object.
        The class implementa a __getitem__ method to allow for accessing the GUI objects from the parent class
        through the syntax:
        parent.UIObjectGetter[ui_object_name]

        Additionally methods are provided to extraxt specific data types from the GUI object:
        float_value
        text_value
        '''
    def __init__(self, parent):
        self.parent = parent

    def __getitem__(self, ui_object_name):
        return self.parent.get_ui_object(ui_object_name)

    def float_value(self, ui_object_name):
        ''' Convert the text entry toa float and return teh value. If teh string is empty, return 0'''
        text_value = self[ui_object_name].Text
        if not text_value:
            return 0
        else:
            return float(text_value)

    def text_value(self, ui_object_name):
        return self[ui_object_name].Text

class AEDTToolkit(Window):
    """ **Class AEDTToolkit**

        This class provides a base class allowing the creation of a WPF-GUI-Based toolkit for AEDT. This class provides
        functionality for launching the GUI, reading and writing to settings files, path handling and error handling.
        Data validation functions are also provided as callbacks from the WPF GUI

    """
    @property
    def aedt_version_id(self):
        return self.aedtdesign.aedt_version_id

    @property
    def aedt_version_key(self):
        version = self.aedtdesign.odesktop.GetVersion()
        return get_version_key(version)

    @property
    def results_path(self):
        return os.path.join(self.aedtdesign.working_directory, '_results')

    @property
    def data_path(self):
        return os.path.join(self.aedtdesign.working_directory, '_data')

    @property
    def local_path(self):
        return self.settings_manager.local_path

    @property
    def settings_file(self):
        return self.settings_manager.settings_file

    @property
    def settings_data(self):
        return self.settings_manager.settings_data

    @property
    def local_settings_file(self):
        return self.settings_manager.settings_file

    @property
    def settings_path(self):
        return self.settings_manager.settings_path

    @property
    def xaml_file(self):
        return os.path.join(self.toolkit_directory, self.toolkit_name + '.xaml')

    def validate_object_name_prefix(self, sender, e):
        valid = False
        try:
            object_list = self.aedtdesign.modeler.get_matched_object_name(sender.Text + "*")
            assert object_list
            valid = True
        except AssertionError:
            pass
        self.update_textbox_status(sender, valid)

    def validate_string_no_spaces(self, sender, e):
        valid = False
        if sender.Text.find(" ") < 0:
            valid = True
        self.update_textbox_status(sender, valid)


    def validate_integer(self, sender, e):
        valid = False
        try:
            value = int(sender.Text)
            valid = True
        except ValueError:
            pass
        if not valid:
            value = None
        self.update_textbox_status(sender, valid)
        return value

    def validate_positive_odd_integer(self, sender, e):
        valid = False
        try:
            value = int(sender.Text)
            if value > 0 and value % 2 != 0:
                sender.Text = str(value)
                valid = True
        except ValueError:
            pass
        if not valid:
            value = None
        self.update_textbox_status(sender, valid)
        return value

    def validate_positive_integer(self, sender, e):
        valid = False
        try:
            value = int(sender.Text)
            if  value > 0:
                sender.Text = str(value)
                valid = True
        except ValueError:
            pass
        if not valid:
            value = None
        self.update_textbox_status(sender, valid)
        return value

    def validate_non_negative_integer(self, sender, e):
        valid = False
        try:
            value = int(sender.Text)
            if  value >= 0:
                sender.Text = str(value)
                valid = True
        except ValueError:
            pass
        if not valid:
            value = None
        self.update_textbox_status(sender, valid)
        return value

    def validate_negative_integer(self, sender, e):
        valid = False
        try:
            value = int(sender.Text)
            if value < 0:
                valid = True
        except ValueError:
            pass
        if not valid:
            value = None
        self.update_textbox_status(sender, valid)
        return value

    def validate_float(self, sender, e):
        valid = False
        try:
            value = float(sender.Text)
            sender.Text = str(value)
            valid = True
        except ValueError:
            value = None
        self.update_textbox_status(sender, valid)
        return value

    def validate_float_variable(self, sender, e):
        proj_and_des_variables = self.aedtdesign.variable_manager.variable_names
        if sender.Text in proj_and_des_variables:
            self.update_textbox_status(sender, True)
        else:
            self.validate_float(sender, e)

    def validate_positive_float_variable(self, sender, e):
        proj_and_des_variables = self.aedtdesign.variable_manager.variable_names
        if sender.Text in proj_and_des_variables:
            self.update_textbox_status(sender, True)
        else:
            self.validate_positive_float(sender, e)

    def validate_positive_integer_variable(self, sender, e):
        proj_and_des_variables = self.aedtdesign.variable_manager.variable_names
        if sender.Text in proj_and_des_variables:
            self.update_textbox_status(sender, True)
        else:
            self.validate_positive_integer(sender, e)

    def validate_positive_integer_global(self, sender, e):
        proj_variables = self.aedtdesign.variable_manager.project_variable_names
        if sender.Text in proj_variables:
            self.update_textbox_status(sender, True)
        else:
            self.validate_positive_integer(sender, e)

    def validate_positive_float_global(self, sender, e):
        proj_variables = self.aedtdesign.variable_manager.project_variable_names
        if sender.Text in proj_variables:
            self.update_textbox_status(sender, True)
        else:
            self.validate_positive_float(sender, e)

    def validate_positive_float(self, sender, e):
        valid = False
        try:
            value = float(sender.Text)
            if  value > 0:
                valid = True
        except ValueError:
            pass
        if not valid:
            value = None
        self.update_textbox_status(sender, valid)
        return value

    def validate_non_negative_float(self, sender, e):
        valid = False
        try:
            value = float(sender.Text)
            if  value >= 0.0:
                valid = True
        except ValueError:
            pass
        if not valid:
            value = None
        self.update_textbox_status(sender, valid)
        return value

    def update_textbox_status_with_default_text(self, sender, valid, default_text):
        if not valid:
            sender.Text = default_text
            sender.BorderBrush = Brushes.Red
        else:
            sender.BorderBrush = Brushes.Green

    def update_textbox_status(self, sender, valid):
        if not valid:
            sender.Text = ""
            sender.BorderBrush = Brushes.Red
        else:
            sender.BorderBrush = Brushes.Green

    def __init__(self, toolkit_file, aedt_design=None, parent_design_name=None, launch_gui=True):

        my_path = os.path.abspath(os.path.dirname(__file__))
        self.aedtdesign = aedt_design
        self.toolkit_name = os.path.basename(toolkit_file).replace(".py", "")

        if self.aedtdesign:
            self.settings_manager = AEDTToolkitSettings(aedtdesign=self.aedtdesign, toolkit_name=self.toolkit_name)
        else:
            self.settings_manager = AEDTToolkitSettings(working_directory=my_path, toolkit_name=self.toolkit_name)

        self.window = None

        self.ui = UIObjectGetter(self)
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.toolkit_directory = os.path.abspath(os.path.dirname(toolkit_file))
        self.pyaedt_directory = os.path.abspath(os.path.join(my_path, '..'))
        sys.path.append(self.toolkit_directory)
        sys.path.append(self.pyaedt_directory)


        if parent_design_name:
            self.parent_design_name = parent_design_name
            if not parent_design_name in self.aedtdesign.design_list:
                orig_design_name = self.aedtdesign.design_name
                if self.parent_design_name != orig_design_name:
                    self._write_parent_link()
                    self.aedtdesign.duplicate_design(self.parent_design_name)
                    self.aedtdesign.save_project()
            else:
                self.aedtdesign.set_active_design(parent_design_name)
        else:
            self.parent_design_name = self.aedtdesign.design_name

        self.dsoconfigfile = os.path.join(self.toolkit_directory, "dso.cfg")

        # Read existing settings and update the library path
        self._read_and_synch_settings_file()

        #LOCAL_INSTALL = self.aedtdesign.odesktop.GetExeDir()
        #self.desktopjob = os.path.join(LOCAL_INSTALL, "desktopjob.exe")

        if launch_gui:
            if sys.implementation.name == 'ironpython':
                clr.AddReference('IronPython.wpf')
                import wpf
                wpf.LoadComponent(self, self.xaml_file)
                self.window = self
            else:
                stream = StreamReader(self.xaml_file)
                self.window = XamlReader.Load(stream.BaseStream)

            workarea = __import__("System.Windows").Windows.SystemParameters.WorkArea
            desktopWorkingArea = workarea
            self.window.Left = desktopWorkingArea.Right - self.window.Width
            self.window.Top = desktopWorkingArea.Top

            self.SetText = self._get_objects_from_xaml_of_type('TextBox')
            self.SetCombo = self._get_objects_from_xaml_of_type('ComboBox')
            self.SetBool = self._get_objects_from_xaml_of_type(['RadioButton', 'CheckBox'])
            self.read_settings()

    def create_child_design(self, design_name):
        ''' Duplicates a design and makes a link to the parent design in teh settings file '''
        self.aedtdesign.duplicate_design(design_name)
        self._write_parent_link()

    def _read_and_synch_settings_file(self):
        ''' reads in existing settings data and updates the path of the library directory in case the project was
            moved to a new location, file system or operating system '''
        settings_file = self.settings_file
        if os.path.exists(settings_file):
            settings_data = self.settings_data
            with open(settings_file, 'w') as f:
                settings_data["_lib_dir"] = self.pyaedt_directory
                settings_data["_toolkit_dir"] = self.toolkit_directory
                json.dump(settings_data, f, indent=4)

    def _write_parent_link(self):
        with open(self.local_settings_file, 'w') as f:
            settings_data = {"parent": self.parent_design_name}
            json.dump(settings_data, f, indent=4)

    def dummy_callback(self, sender, e):
        pass

    def display(self):
        ''' Display the wpf application as a Dialoq (IronPython) or an Application (CPython)'''
        if sys.implementation.name == 'ironpython':
            Window.ShowDialog(self)
        else:
            Application().Run(self.window)

    def open_explorer(self, sender, e):
        """
        Open a windows explorer window pointing to the selected path in the sender control

        :param      sender: sender object from the wpf GUI
                    e: error object from teh wpf GUI
        :return:    None
        """
        from platform import system

        os_type = os.name
        if os_type == 'nt':
            selected_path = os.path.normpath(sender.Text)
            if os.path.exists(selected_path):
                os_command_string = r'explorer "{}"'.format(selected_path)
                subprocess.Popen(os_command_string)
            pass


    def set_callback(self, control, callback, function):
        '''
        Sets up the callback functions from the xaml GUI
        :param control: name of the control (Button, TextBox, etc) as a string
        :param callback: Name of teh callback function, e.g. "Click", "LostFocus", etc
        :param function: reference to the callback function (requires 2 arguments: sender, e)
        '''
        test_control = LogicalTreeHelper.FindLogicalNode(self.window, control)
        a = getattr(test_control, callback)
        a += function

    def set_margin(self, object_name, margin):
        ''' Sets the outer dimensions of the GUI window.
        :param margin: vector of floats [left, top, bottom, right]
        '''
        myThickness = Thickness()
        myThickness.Bottom = margin[2]
        myThickness.Left = margin[0]
        myThickness.Right = margin[3]
        myThickness.Top = margin[1]
        self.get_ui_object(object_name).Margin = myThickness

    def assign_image(self, ui_object_name, image_file):
        print_timelog("Assign image {}".format(image_file))
        bi = BitmapImage()
        bi.BeginInit()
        bi.CacheOption = BitmapCacheOption.OnLoad
        bi.CreateOptions = BitmapCreateOptions.IgnoreImageCache
        bi.UriSource = Uri(image_file, UriKind.RelativeOrAbsolute)
        bi.EndInit()
        self.ui[ui_object_name].Source = bi

    def set_visible(self, object_list):
        ''' Defines one or more GUI objects to be visible'''
        if isinstance(object_list, str):
            object_list = [ object_list ]
        for object_name in object_list:
            self.get_ui_object(object_name).Visibility = Visibility.Visible

    def set_hidden(self, object_list):
        ''' Defines one or more GUI objects to be hidden'''
        if isinstance(object_list, str):
            object_list = [ object_list ]
        for object_name in object_list:
            self.get_ui_object(object_name).Visibility = Visibility.Hidden

    def wait_cursor(self):
        ''' Turns on the "Wait" cursor and stores the current cursor'''
        self.previous_cursor = self.Cursor
        self.Cursor = Input.Cursors.Wait

    def standard_cursor(self):
        ''' Restores the current cursor'''
        self.Cursor = self.previous_cursor

    def _get_objects_from_xaml_of_type(self, type_list):
        if isinstance(type_list, str):
            type_list = [type_list]
        text_list = []
        with open(self.xaml_file, 'r') as f:
            for line in f:
                rstrip_line = line.lstrip()[1:]
                pp = rstrip_line.find(" ")
                object_type = rstrip_line[0:pp]
                if object_type in type_list:
                    attribute_list = rstrip_line.split(' ')
                    name = attribute_list[1].split('"')[1]
                    text_list.append(name)
        return text_list

    def message_box(self, text, caption=None, buttons=None, icon=None):
        return message_box(text, caption, buttons, icon)

    def ok_cancel_message_box(self, text, caption=None, icon=None):
        response = message_box(text, caption, "OKCancel", icon)
        if response == DialogResult.OK:
            return True
        else:
            return False

    def add_combo_items(self, combo_box_name, options, default=None):
        ''' Fills a combo box with a list of options and sets the selected value if nothing is present already
        :param combo_box_name: name of the combo box object in xaml
        :param options: list of entries to be set to the combobox
        :param default: default value to be used if there is no selected value present
        :return: None
        '''
        if not isinstance(options, list):
            options = [ options ]
        control = self.get_ui_object(combo_box_name)
        for each_option in options:
            control.Items.Add(each_option)
        if default and not control.SelectedValue:
            control.SelectedValue = default

    def get_ui_object(self, control_name):
        wpf_control = LogicalTreeHelper.FindLogicalNode(self.window, control_name)
        assert wpf_control, "WPF GUI object name {0} dies not exist !".format(control_name)
        return wpf_control

    def read_settings(self):
        """ Reads the setting data from the toolkit settings file in the parent design

        :return: Dictionary of settings data
        """
        settings_data = self.settings_data

        if settings_data:
            for text_control in self.SetText:
                wpf_control = self.get_ui_object(text_control)
                try:
                    txt_line = settings_data[text_control]
                    wpf_control.Text = txt_line
                    if txt_line:
                        wpf_control.BorderBrush = Brushes.Green
                except KeyError:
                    if wpf_control.IsEnabled:
                        wpf_control.BorderBrush = Brushes.Red

            for combo_control in self.SetCombo:
                wpf_control = self.get_ui_object(combo_control)
                try:
                    txt_line = settings_data[wpf_control.Name]
                    wpf_control.SelectedValue = txt_line
                    self.aedtdesign.messenger.add_info_message("Trying to set: " + txt_line)
                    if txt_line:
                        wpf_control.BorderBrush = Brushes.Green
                except KeyError:
                    if wpf_control.IsEnabled:
                        wpf_control.BorderBrush = Brushes.Red


            for bool_control in self.SetBool:
                wpf_control = self.get_ui_object(bool_control)
                try:
                    txt_line = int(settings_data[wpf_control.Name])
                except KeyError:
                    txt_line = 0
                except ValueError:
                    txt_line = 0
                wpf_control.IsChecked = bool(txt_line)
                if txt_line:
                    wpf_control.BorderBrush = Brushes.Green

        return settings_data

    def write_settings(self, user_defined_data=None):
        """ Write UI settings Textbox, Checkbox, Combobox only at present
            also write any user defined data from a json-serializable dictionary

        :param user_defined_data: dictionary with arbitrary user data (needs to be json serializable)
        :return: None
        """
        settings_data = self.settings_data
        with open(self.settings_file, 'w') as f:

            for text_control in self.SetText:
                wpf_control = self.get_ui_object(text_control)
                settings_data[wpf_control.Name] = wpf_control.Text

            for bool_control in self.SetBool:
                wpf_control = self.get_ui_object(bool_control)
                if wpf_control.IsChecked:
                    settings_data[wpf_control.Name] = '1'
                else:
                    settings_data[wpf_control.Name] = '0'

            for combo_control in self.SetCombo:
                wpf_control = self.get_ui_object(combo_control)
                settings_data[wpf_control.Name] = wpf_control.Text

            if isinstance(user_defined_data, dict):
                for key, entry in user_defined_data.items():
                    settings_data[key] = entry

            json.dump(settings_data, f, indent=4)


    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):

        # write the UI data to json
        self.write_settings()

        # If an error occured in the context of this object, close the window to avoid AEDT crashing
        if ex_type and self.window:
            self.Close()



