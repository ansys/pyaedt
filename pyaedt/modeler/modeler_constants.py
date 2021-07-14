

class BLNDChamferRangeLaw(object):
    """BLNDChamferRangeLaw class."""
    (BLNDConstantRange,
     BLNDVariableRange) = range(0, 2)


class BLNDFilletRadiusLaw(object):
    """BLNDFilletRadiusLaw class."""
    (BLNDConstantRadius,
     BLNDVariableRadius) = range(0, 2)


class BLNDFilletType(object):
    """BLNDFilletType class."""
    (BLNDRound,
     BLNDMitered) = range(0, 2)


class CoordinateSystemAxis(object):
    """CoordinateSystemAxis class."""
    (XAxis, YAxis, ZAxis) = range(0, 3)


class CoordinateSystemPlane(object):
    """CoordinateSystemPlane class."""
    (XYPlane, YZPlane, ZXPlane) = range(0, 3)


class Plane(object):
    """Plane class."""
    (XYPlane, YZPlane, ZXPlane, ISO) = ("XY", "YZ", "ZX", "iso")


class GravityDirection(object):
    """GravityDirection class."""
    (XNeg, YNeg, ZNeg, XPos, YPos, ZPos) = range(0, 6)


class MessageSeverity(object):
    """MessageSeverity class."""
    (InfoMessage,
     WarningMessage,
     ErrorMessage,
     FatalMessage,
     IncompleteMessage) = range(0, 5)


class ParamDataType(object):
    """ParamDataType class."""
    (Unknown,
     Int,
     Double,
     String,
     Bool,
     Position) = range(-1, 5)


class ParamPropFlag(object):
    """ParamPropFlag class."""
    (Unknown,
     NoFlag,
     ReadOnly,
     MustBeInt) = range(-1, 3)
    MustBeReal = 4
    Hidden = 8


class ParamPropType(object):
    """ParamPropTyp class."""
    (Unknown,
     Text,
     Menu,
     Number,
     Value,
     FileName,
     Checkbox,
     Position) = range(-1, 7)


class PartPropertyFlags(object):
    """PartPropertyFlags class."""
    PropNonModel = 1
    PropDisplayWireFrame = 2
    PropReadOnly = 4
    PostprocessingGeometry = 8
    PropInvisible = 16
    PropShowDirection = 32
    PropDummy = 33


class PolylineSegmentType(object):
    """PolylineSegmentType class."""
    (LineSegment,
     ArcSegment,
     SplineSegment,
     AngularArcSegment) = range(0, 4)


class PolylineXSegmentType(object):
    """PolylineXSegmentType class."""
    (NONE,
     Line,
     Circle,
     Rectangle,
     Trapezoid) = range(0, 5)


class SplitWhichSideToKeep(object):
    """SplitWhichSideToKeep class."""
    (SplitKeepBoth,
     SplitKeepPositiveOnly,
     SplitKeepNegativeOnly) = range(0, 3)


class SweepDraftType(object):
    """SweepDraftType class."""
    (ExtendedDraft,
     RoundDraft,
     NaturalDraft,
     MixedDraft) = range(0, 4)


class UnitType(object):
    """UnitType  class."""
    (NoUnit,
     LengthUnit,
     AngleUnit) = range(0, 3)
