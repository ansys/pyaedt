# Copyright (C) 2019 ANSYS, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


class BLNDChamferRangeLaw(object):
    """ """
    (BLNDConstantRange,
     BLNDVariableRange) = range(0, 2)


class BLNDFilletRadiusLaw(object):
    """ """
    (BLNDConstantRadius,
     BLNDVariableRadius) = range(0, 2)


class BLNDFilletType(object):
    """ """
    (BLNDRound,
     BLNDMitered) = range(0, 2)


class CoordinateSystemAxis(object):
    """ """
    (XAxis, YAxis, ZAxis) = range(0, 3)


class CoordinateSystemPlane(object):
    """ """
    (XYPlane, YZPlane, ZXPlane) = range(0, 3)


class Plane(object):
    """ """
    (XYPlane, YZPlane, ZXPlane, ISO) = ("XY", "YZ", "ZX", "iso")


class GravityDirection(object):
    """ """
    (XNeg, YNeg, ZNeg, XPos, YPos, ZPos) = range(0, 6)


class MessageSeverity(object):
    """ """
    (InfoMessage,
     WarningMessage,
     ErrorMessage,
     FatalMessage,
     IncompleteMessage) = range(0, 5)


class ParamDataType(object):
    """ """
    (Unknown,
     Int,
     Double,
     String,
     Bool,
     Position) = range(-1, 5)


class ParamPropFlag(object):
    """ """
    (Unknown,
     NoFlag,
     ReadOnly,
     MustBeInt) = range(-1, 3)
    MustBeReal = 4
    Hidden = 8


class ParamPropType(object):
    """ """
    (Unknown,
     Text,
     Menu,
     Number,
     Value,
     FileName,
     Checkbox,
     Position) = range(-1, 7)


class PartPropertyFlags(object):
    """ """
    PropNonModel = 1
    PropDisplayWireFrame = 2
    PropReadOnly = 4
    PostprocessingGeometry = 8
    PropInvisible = 16
    PropShowDirection = 32
    PropDummy = 33


class PolylineSegmentType(object):
    """ """
    (LineSegment,
     ArcSegment,
     SplineSegment,
     AngularArcSegment) = range(0, 4)


class PolylineXSegmentType(object):
    """ """
    (NONE,
     Line,
     Circle,
     Rectangle,
     Trapezoid) = range(0, 5)


class SplitWhichSideToKeep(object):
    """ """
    (SplitKeepBoth,
     SplitKeepPositiveOnly,
     SplitKeepNegativeOnly) = range(0, 3)


class SweepDraftType(object):
    """ """
    (ExtendedDraft,
     RoundDraft,
     NaturalDraft,
     MixedDraft) = range(0, 4)


class UnitType(object):
    """ """
    (NoUnit,
     LengthUnit,
     AngleUnit) = range(0, 3)
