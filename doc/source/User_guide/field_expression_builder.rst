Field expression builder
========================

The AEDT Fields Calculator is driven by a stack of string operations in reverse
Polish notation. Assembling those strings by hand is error-prone and hides which
operations are valid for a given quantity. The **field expression builder** wraps
that operation grammar with four strongly-typed expression classes
(``ScalarReal``, ``ScalarComplex``, ``VectorReal``, ``VectorComplex``) so that an
editor or type checker guides you, and a readable Python chain replaces the raw
operation list.

It does not read any raw binary field data; it is purely a typed front end for
the calculator's own operation stack and reuses the existing
``FieldsCalculator`` to register, evaluate, and export expressions.

Getting started
---------------

Obtain the builder through ``hfss.post.fields_calculator.expressions``:

.. code:: python

    from ansys.aedt.core import Hfss
    from ansys.aedt.core.visualization.post.field_calculator_expressions import (
        Line,
        Surface,
        Volume,
        cross,
        dot,
    )

    hfss = Hfss()
    fx = hfss.post.fields_calculator.expressions

    e = fx.vector("E")  # VectorComplex
    mag_e = e.magnitude()  # ScalarReal
    peak = mag_e.maximum(Volume("MySolid"))  # ScalarReal over a volume
    value = peak.evaluate(setup="Setup1 : LastAdaptive")

Unary operations are ``.method()`` calls whose return type tells you what comes
next; binary operations are the Python operators (``+ - * /``) and the free
functions ``dot`` and ``cross``. Geometry is referenced with ``Line``,
``Surface``, and ``Volume``. Nothing is sent to AEDT until you call
``add()``, ``evaluate()``, or ``export()``.

Catalog cookbook
----------------

Every expression shipped in ``expression_catalog.toml`` can be written with the
builder, and each compiles to the **same** operation stack the catalog uses (the
unit tests assert this exactly). The examples below show the typed form next to
the previous operation list to highlight the difference. In the previous form,
``'assignment'`` is the object name filled in at registration time; with the
builder you pass the geometry directly to the reduction.

Power flow through a surface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field expression builder**

.. code:: python

    poynting = fx.named_expression("Poynting", is_vector=True)
    power = dot(poynting.real(), fx.normal()).integrate(Surface("MySheet"))

**Previous operation stack**

.. code:: python

    operations = [
        "NameOfExpression('Poynting')",
        "Operation('Real')",
        "Operation('Normal')",
        "Operation('Dot')",
        "EnterSurface('assignment')",
        "Operation('SurfaceValue')",
        "Operation('Integrate')",
    ]

``fx.normal()`` pushes the surface's unit normal vector so that ``dot`` projects
the field onto it.

Voltage drop along a line
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The complex line voltage integrates the real and imaginary tangential
projections separately and recombines them.

**Field expression builder**

.. code:: python

    e = fx.vector("E")
    line = Line("MyLine")
    real_part = dot(e.real(), fx.tangent()).integrate(line).as_complex_real()
    imag_part = dot(e.imaginary(), fx.tangent()).integrate(line).as_complex_imag()
    voltage = real_part + imag_part

**Previous operation stack**

.. code:: python

    operations = [
        "Fundamental_Quantity('E')",
        "Operation('Real')",
        "Operation('Tangent')",
        "Operation('Dot')",
        "EnterLine('assignment')",
        "Operation('LineValue')",
        "Operation('Integrate')",
        "Operation('CmplxR')",
        "Fundamental_Quantity('E')",
        "Operation('Imag')",
        "Operation('Tangent')",
        "Operation('Dot')",
        "EnterLine('assignment')",
        "Operation('LineValue')",
        "Operation('Integrate')",
        "Operation('CmplxI')",
        "Operation('+')",
    ]

Wave impedance along a line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field expression builder**

.. code:: python

    unit = fx.vector_constant(1, 0, 0)
    e = fx.vector("E").smooth().component_magnitude()
    h = fx.named_expression("<Hx,Hy,Hz>", is_vector=True).smooth().component_magnitude()
    impedance = cross(e, unit).magnitude() / cross(h, unit).magnitude()

**Previous operation stack**

.. code:: python

    operations = [
        "Fundamental_Quantity('E')",
        "Operation('Smooth')",
        "Operation('CmplxMag')",
        "Vector_Constant(1, 0, 0)",
        "Operation('Cross')",
        "Operation('Mag')",
        "NameOfExpression('<Hx,Hy,Hz>')",
        "Operation('Smooth')",
        "Operation('CmplxMag')",
        "Vector_Constant(1, 0, 0)",
        "Operation('Cross')",
        "Operation('Mag')",
        "Operation('/')",
    ]

H-field minimum position
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field expression builder**

.. code:: python

    h = fx.named_expression("<Hx,Hy,Hz>", is_vector=True)
    x_position = h.magnitude().min_position(Surface("MySheet")).scalar_x()

**Previous operation stack**

.. code:: python

    operations = [
        "NameOfExpression('<Hx,Hy,Hz>')",
        "Operation('Mag')",
        "EnterSurface('assignment')",
        "Operation('SurfaceValue')",
        "Operation('MinPos')",
        "Operation('ScalarX')",
    ]

Radial component of the magnetic field (Maxwell)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field expression builder**

.. code:: python

    b = fx.vector("B")
    phi = fx.function("PHI")  # a design variable
    b_radial = b.scalar_x() * phi.cos() + b.scalar_y() * phi.sin()

**Previous operation stack**

.. code:: python

    operations = [
        "Fundamental_Quantity('B')",
        "Operation('ScalarX')",
        "Scalar_Function(FuncValue='PHI')",
        "Operation('UMathFunc', 'Cos')",
        "Operation('*')",
        "Fundamental_Quantity('B')",
        "Operation('ScalarY')",
        "Scalar_Function(FuncValue='PHI')",
        "Operation('UMathFunc', 'Sin')",
        "Operation('*')",
        "Operation('+')",
    ]

Radial stress tensor (reusing named expressions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Field expression builder**

.. code:: python

    b_radial = fx.named_expression("b_radial")
    b_tangential = fx.named_expression("b_tangential")
    stress = (b_radial * b_radial + -(b_tangential * b_tangential)) / 1.25664e-06 / 2

**Previous operation stack**

.. code:: python

    operations = [
        "NameOfExpression('b_radial')",
        "NameOfExpression('b_radial')",
        "Operation('*')",
        "NameOfExpression('b_tangential')",
        "NameOfExpression('b_tangential')",
        "Operation('*')",
        "Operation('Neg')",
        "Operation('+')",
        "Scalar_Constant(1.25664e-06)",
        "Operation('/')",
        "Scalar_Constant(2)",
        "Operation('/')",
    ]

Python numbers are accepted as operands and are turned into the matching
``Scalar_Constant`` / ``Complex_Constant`` tokens, so ``/ 1.25664e-06 / 2`` reads
naturally.

Registering, evaluating, and exporting
---------------------------------------

A built expression is materialized through the underlying calculator:

.. code:: python

    power = dot(poynting.real(), fx.normal()).integrate(Surface("MySheet"))

    name = power.add("power_flow")  # register as a named expression
    result = power.evaluate(setup="Setup1 : LastAdaptive")  # register and evaluate
    power.export("power.fld", solution="Setup1 : LastAdaptive")  # register and export

Use ``verify()`` to check a chain locally before sending it to AEDT (a malformed
or unbalanced stack raises a clear error), and ``checkpoint()`` to keep very long
or heavily-reused expressions short by registering an intermediate named
expression and continuing from a single-token reference to it.

Coverage
--------

The builder reproduces all of the built-in catalog expressions exactly, including
the remaining ones not shown above: ``voltage_line_time``,
``voltage_line_maxwell``, ``voltage_drop``, ``voltage_drop_2025``,
``current_line``, ``current_line_time``, ``electric_charge``, ``e_line``,
``wave_impedance_y`` / ``wave_impedance_z``, ``h_field_minimum_y_position`` /
``h_field_minimum_z_position``, ``b_tangential``, and ``tangential_stress_tensor``.

For the full list of types and operations, and the operations that are not yet
wrapped, see the API reference for the ``field_calculator_expressions`` module.
