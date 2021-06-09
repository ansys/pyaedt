import csv
import re
import os
import shutil
from ..generic.general_methods import aedt_exception_handler, generate_unique_name


@aedt_exception_handler
def read_info_fromcsv(projdir, name):
    """Read information from CSV file and return a list

    Parameters
    ----------
    projdir : str
        project directory
    name : str
        File name

    Returns
    -------
    list

    """

    filename = projdir + "//" + name
    listmcad = []
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            listmcad.append(row)
    return listmcad


@aedt_exception_handler
def clean_proj_folder(dir, name):
    """Delete all project name related folder

    Parameters
    ----------
    dir :
        project directory
    name :
        project name

    Returns
    -------

    """
    if os.path.exists(dir):
        shutil.rmtree(dir, True)
    os.mkdir(dir)
    return True


@aedt_exception_handler
def create_output_folder(ProjectDir):
    """Create the Output folders starting from the project dir

    Parameters
    ----------
    ProjectDir :
        project directory

    Returns
    -------
    type
        PicturePath, ResultsPath

    """
    npath = os.path.normpath(ProjectDir)

    # set pathname for the Output
    OutputPath = os.path.join(npath, os.path.basename(npath))
    # set pathname for the images
    PicturePath = os.path.join(npath, os.path.basename(npath), "Pictures")
    # set pathname for the files
    ResultsPath = os.path.join(npath, os.path.basename(npath), "Results")

    # Add foldes for outputs
    if not os.path.exists(OutputPath):
        os.mkdir(OutputPath)
    if not os.path.exists(PicturePath):
        os.mkdir(PicturePath)
    if not os.path.exists(ResultsPath):
        os.mkdir(ResultsPath)
    return PicturePath, ResultsPath


@aedt_exception_handler
def change_objects_visibility(origfile, solid_list):
    """Edit the project file (extension .aedt) to make only the specified solids visible

    Parameters
    ----------
    origfile :
        str) = full path of the project file
    SolidList :
        list) = list of the solid names to make visible (hide all the others)
    solid_list :
        

    Returns
    -------

    """
    path, filename = os.path.split(origfile)
    newfile = os.path.join(path, "aedttmp.tmp")

    if not os.path.isfile(origfile + ".lock"):  # check if the project is closed


        with open(origfile, "rb") as f, open(newfile, "wb") as n:

            # Reading file content
            content = f.read()

            # Searching file content for pattern
            pattern = re.compile(r"(\$begin 'EditorWindow'\n.+)(Drawings\[.+\])(.+\n\s*\$end 'EditorWindow')",
                                 re.UNICODE)
            # Replacing string
            ViewStr = u"Drawings[" + unicode(str(len(solid_list))) + u": " + unicode(str(solid_list).strip("["))
            s = pattern.sub(r"\1" + ViewStr + r"\3", content)

            # writing file content
            n.write(str(s))


        # renaming files and deleting temp

        os.remove(origfile)
        os.rename(newfile, origfile)


    else:  # project is locked
        print("change_objects_visibility: Project %s is still locked." % origfile)


@aedt_exception_handler
def change_model_orientation(origfile, bottom_dir):
    """Edit the project file (extension .aedt) to change the model orientation

    Parameters
    ----------
    origfile :
        str) = full path of the project file
    BottomDir :
        str) = bottom direction as specified in the properties file
    bottom_dir :
        

    Returns
    -------

    """
    path, filename = os.path.split(origfile)
    newfile = os.path.join(path, "aedttmp.tmp")

    # directory of u, v vectors for view orientation
    orientation = {
        '+X': 'OrientationMatrix(0, -0.816496610641479, -0.577350318431854, 0, 0.70710676908493, -0.40824830532074, '
              '0.577350318431854, 0, -0.70710676908493, -0.40824830532074, 0.577350318431854, 0, 0, 0, 0, 1, 0, -100, '
              '100, -100, 100, -100, 100)',
        '+Y': 'OrientationMatrix(-0.70710688829422, -0.408248245716095, 0.577350199222565, 0, 1.04308128356934e-07, '
              '-0.816496670246124, -0.577350199222565, 0, 0.707106709480286, -0.408248245716095, 0.577350437641144, '
              '0, 0, 0, 0, 1, 0, -100, 100, -100, 100, -100, 100)',
        '+Z': 'OrientationMatrix(0.70710676908493, -0.408248394727707, 0.577350199222565, 0, -0.70710676908493, '
              '-0.408248394727707, 0.577350199222565, 0, 0, -0.81649649143219, -0.577350437641144, 0, 0, 0, 0, 1, 0, '
              '-100, 100, -100, 100, -100, 100)',
        '-X': 'OrientationMatrix(0, 0.816496610641479, 0.577350318431854, 0, -0.70710676908493, -0.40824830532074, '
              '0.577350318431854, 0, 0.70710676908493, -0.40824830532074, 0.577350318431854, 0, 0, 0, -0, 1, 0, -100, '
              '100, -100, 100, -100, 100)',
        '-Y': 'OrientationMatrix(0.70710688829422, -0.408248245716095, 0.577350199222565, 0, 1.04308128356934e-07, '
              '0.816496670246124, 0.577350199222565, 0, -0.707106709480286, -0.408248245716095, 0.577350437641144, 0, '
              '0, 0, -0, 1, 0, -100, 100, -100, 100, -100, 100)',
        '-Z': 'OrientationMatrix(-0.70710676908493, -0.408248394727707, 0.577350199222565, 0, 0.70710676908493, '
              '-0.408248394727707, 0.577350199222565, 0, 0, 0.81649649143219, 0.577350437641144, 0, 0, 0, -0, 1, 0, '
              '-100, 100, -100, 100, -100, 100) '
    }

    if not os.path.isfile(origfile + ".lock"):  # check if the project is closed

        # opening files
        with open(origfile, "rb") as f, open(newfile, "wb") as n:

            # Reading file content
            content = f.read()

            # Searching file content for pattern
            pattern = re.compile(
                r"(\$begin 'EditorWindow'\n.+?)(OrientationMatrix\(.+?\))(.+\n\s*\$end 'EditorWindow')",
                re.UNICODE)
            # Replacing string
            OrientStr = unicode(orientation[bottom_dir])
            # ViewStr = u"Drawings[" + unicode(str(len(SolidList))) +
            # u": " + unicode(str(SolidList).strip("["))
            s = pattern.sub(r"\1" + OrientStr + r"\3", content)

            # writing file content
            n.write(str(s))


        # renaming files and deleting temp
        os.remove(origfile)
        os.rename(newfile, origfile)


    else:  # project is locked
        print("change_model_orientation: Project %s is still locked." % origfile)

