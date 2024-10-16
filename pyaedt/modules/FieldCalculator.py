from typing import Callable, List, Literal, Protocol, Union, cast

FieldNumber = Union[int, float]


class StackBasedCalculator(Protocol):

    def AddNamedExpression(self, expression_name : str, field_type: str) -> None:
        ...

    def CopyNamedExprToStack(self, name: str) -> None:
        ...

    def CalcOp(self, op : str) -> None:
        ...

    def ClcMaterial(self, material: str, op : Union[Literal["mult"], Literal["div"]])-> None:
        ...

    def EnterComplex(self, complex: str)-> None:
        ...

    def EnterComplexVector(self, complex_vector: List[str])-> None:
        ...

    def EnterLine(self, name : str)-> None:
        ...

    def EnterPoint(self, name: str)-> None:
        ...

    def EnterQty(self, name: str)-> None:
        ...

    def EnterScalar(self, num: float)-> None:
        ...

    def EnterScalarFunc(self, name: str)-> None:
        ...

    def EnterSurface(self, name: str)-> None:
        ...

    def EnterVector(self, vector: List[float])-> None:
        ...

    def EnterVectorFunc(self, vector: List[str])-> None:
        ...

    def EnterVol(self, name: str)-> None:
        ...

class StackBasedCalculatorNotImplemented(StackBasedCalculator):

    def AddNamedExpression(self, expression_name : str, field_type: str) -> None:
        raise NotImplementedError()

    def CopyNamedExprToStack(self, name: str) -> None:
        raise NotImplementedError()

    def CalcOp(self, op : str) -> None:
        raise NotImplementedError()

    def ClcMaterial(self, material: str, op : Union[Literal["mult"], Literal["div"]])-> None:
        raise NotImplementedError()

    def EnterComplex(self, complex: str)-> None:
        raise NotImplementedError()

    def EnterComplexVector(self, complex_vector: List[str])-> None:
        raise NotImplementedError()

    def EnterLine(self, name : str)-> None:
        raise NotImplementedError()

    def EnterPoint(self, name: str)-> None:
        raise NotImplementedError()

    def EnterQty(self, name: str)-> None:
        raise NotImplementedError()

    def EnterScalar(self, num: float)-> None:
        raise NotImplementedError()

    def EnterScalarFunc(self, name: str)-> None:
        raise NotImplementedError()

    def EnterSurface(self, name: str)-> None:
        raise NotImplementedError()

    def EnterVector(self, vector: List[float])-> None:
        raise NotImplementedError()

    def EnterVectorFunc(self, vector: List[str])-> None:
        raise NotImplementedError()

    def EnterVol(self, name: str)-> None:
        raise NotImplementedError()
    
class ExtractScalarFuncName(StackBasedCalculatorNotImplemented):
    
        def __init__(self):
            self._name = None
    
        def EnterScalarFunc(self, name: str)-> None:
            self._name = name

        @property
        def name(self) -> str:
            if self._name is None:
                raise RuntimeError("No scalar function has been entered")
            return self._name

StackOperation = Callable[[StackBasedCalculator], None]

FieldExpressionArgument = Union[
    int, float , complex , "FieldExpressionNode"]

class FieldExpressionNode():

    def __init__(self, op : StackOperation):
        self._op = op

    @classmethod
    def _convert_complex_to_string(cls, arg : complex) -> str:
        return f"{arg.real} + {arg.imag}j"

    def extract_scalar_func_name(self) -> str:
        extractor = ExtractScalarFuncName()
        self.implement_on_stack(extractor)
        return extractor.name

    @classmethod
    def create(cls, arg : FieldExpressionArgument) -> "FieldExpressionNode":
        if isinstance(arg, FieldExpressionNode):
            return arg
        if isinstance(arg, (float, int)):
            return FieldExpressionNode(lambda c: c.EnterScalar(arg) )
        if isinstance(arg, complex):  # type: ignore
            return FieldExpressionNode(lambda c: c.EnterComplex(cls._convert_complex_to_string(arg)))
        raise RuntimeError(f"{arg} of {type(arg)} is not a valid component of the expression")
    
    def implement_on_stack(self, calculator : StackBasedCalculator):
        self._op(calculator)

    @classmethod
    def calc_op(cls, f : str, args: List[FieldExpressionArgument]) -> "FieldExpressionNode":
        def op(c : StackBasedCalculator):
            for arg in args:
                cls.create(arg).implement_on_stack(c)
            c.CalcOp(f)
        return FieldExpressionNode(op)

    def __add__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("+", [self, other])
    
    def __radd__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("+", [other, self])

    def __sub__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("-", [self, other])
    
    def __rsub__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("-", [other, self])
    
    def __mul__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("*", [self, other])
    
    def __rmul__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("*", [other, self])

    def __truediv__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("/", [self, other])
    
    def __rtruediv__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        if other in [1, 1.0]:
            return self.calc_op("1/", [self])
        return self.calc_op("/", [other, self])
    
    def __neg__(self) -> "FieldExpressionNode":
        return self.calc_op("Neg", [self])
    
    def __pow__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("Pow", [self, other])
    
    def __rpow__(self, other : FieldExpressionArgument) -> "FieldExpressionNode":
        return self.calc_op("Pow", [other, self])

class ScalarFactory:

    def __getattr__(self, name: str) -> FieldExpressionNode:
        return FieldExpressionNode(lambda c: c.EnterScalarFunc(name))
    
scalar = ScalarFactory()

class QuantityFactory:

    def __getattr__(self, name: str) -> FieldExpressionNode:
        return FieldExpressionNode(lambda c: c.EnterQty(name))
    
quantity = QuantityFactory()

class LineFactory:

    def __getattr__(self, name: str) -> FieldExpressionNode:
        return FieldExpressionNode(lambda c: c.EnterLine(name))
    
line = LineFactory()

class PointFactory:

    def __getattr__(self, name: str) -> FieldExpressionNode:
        return FieldExpressionNode(lambda c: c.EnterPoint(name))
    
point = PointFactory()

class SurfaceFactory:

    def __getattr__(self, name: str) -> FieldExpressionNode:
        return FieldExpressionNode(lambda c: c.EnterSurface(name))
    
surface = SurfaceFactory()

class VolumeFactory:

    def __getattr__(self, name: str) -> FieldExpressionNode:
        return FieldExpressionNode(lambda c: c.EnterVol(name))
    
volume = VolumeFactory()

class NamedExpressionFactory:

    def __getattr__(self, name: str) -> FieldExpressionNode:
        return FieldExpressionNode(lambda c: c.CopyNamedExprToStack(name))
    
expression = NamedExpressionFactory()

def Vector(
        x : Union[FieldNumber,complex,FieldExpressionNode],
        y : Union[FieldNumber,complex,FieldExpressionNode] ,
        z : Union[FieldNumber,complex,FieldExpressionNode]) -> FieldExpressionNode:
    if all(isinstance(i, (int, float)) for i in [x, y, z]):
        float_args : List[float] = [float(x), float(y), float(z)]  # type: ignore
        return FieldExpressionNode((lambda c: c.EnterVector(float_args)))
    if all(isinstance(i, complex) for i in [x, y, z]):
        args : List[str] = [
            FieldExpressionNode._convert_complex_to_string(x),  # type: ignore
            FieldExpressionNode._convert_complex_to_string(y),  # type: ignore
            FieldExpressionNode._convert_complex_to_string(z)]  # type: ignore
        return FieldExpressionNode((lambda c: c.EnterComplexVector(args)))
    if all(isinstance(i, FieldExpressionNode) for i in [x, y, z]):
        args : List[str] = [
            x.extract_scalar_func_name(),  # type: ignore
            y.extract_scalar_func_name(),  # type: ignore
            z.extract_scalar_func_name()]  # type: ignore
        return FieldExpressionNode((lambda c: c.EnterVectorFunc(args)))
    raise RuntimeError("All arguments must be of the same type and int, float, complex or scalar field")

def Abs(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Abs", [arg])
        
def Smooth(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Smooth", [arg])

def Real(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Real", [arg])

def Imag(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Imag", [arg])

def Domain(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Domain", [arg])

def Phase(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Phase", [arg])

def CmplxMag(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("CmplxMag", [arg])
        
def Conj(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Conj", [arg])

def AtPhase(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("AtPhase", [arg])

def CmplxReal(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("CmplxR", [arg])

def CmplxImag(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("CmplxI", [arg]) 

def CmplxPeak(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("CmplxPeak", [arg])

def VecX(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("VecX", [arg])

def VecY(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("VecY", [arg])   

def VecZ(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("VecZ", [arg])   

def Fraction(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("1/", [arg])

def Pow(arg1 : FieldExpressionArgument, arg2 : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Pow", [arg1, arg2])

def Sqrt(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Sqrt", [arg])       

def Sin(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Sin", [arg])    

def Cos(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Cos", [arg])

def Tan(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Tan", [arg])

def Asin(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Asin", [arg])

def Acos(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Acos", [arg])

def Atan(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Atan", [arg])

def Atan2(arg1 : FieldExpressionArgument, arg2 : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Atan2", [arg1, arg2])   

def DerivativeX(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("d/dx", [arg])

def DerivativeY(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("d/dy", [arg])

def DerivativeZ(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("d/dz", [arg])

def Integrate(arg1 : FieldExpressionArgument, arg2 : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Integrate", [arg1, arg2])

def Grad(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("Grad", [arg])

def ln(arg : FieldExpressionArgument) -> FieldExpressionNode:   
    return FieldExpressionNode.calc_op("ln", [arg])

def log(arg : FieldExpressionArgument) -> FieldExpressionNode:
    return FieldExpressionNode.calc_op("log", [arg])    


# Missing functions include:
# the max and min function set and
# Mean and Std functions
# ScalarX, ScalarY, ScalarZ
# Mag, Dot, Cross, Divg, Curl, TangentComponent, NormalComponent,
# 2D_Normal, UnitVecCSX, UnitVecCSY, UnitVecCSZ


# Missing stack operations are:
# ClcMaterial, ClcMaterialValue, XForm

    
class FieldCalculator():

    def __init__(self, calculator : StackBasedCalculator):
        self._calculator = calculator

    def add_named_expression(self, expression_name : str, arg : FieldExpressionArgument, field_type: str = "Fields"):
        node = FieldExpressionNode.create(arg)
        node.implement_on_stack(self._calculator)
        self._calculator.AddNamedExpression(expression_name, field_type)