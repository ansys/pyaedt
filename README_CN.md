<!-- -->
<a name="readme-top"></a>
<!--
*** PyAEDT README
-->

# PyAEDT

<p style="text-align: center;">
    <br> <a href="README.md">English</a> | 中文
</p>

[![PyAnsys](https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC)](https://docs.pyansys.com/)[![pypi](https://img.shields.io/pypi/v/pyaedt.svg?logo=python&logoColor=white)](https://pypi.org/project/pyaedt/)[![PyPIact](https://pepy.tech/badge/pyaedt/month)](https://pypi.org/project/pyaedt/)[![PythonVersion](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)[![GH-CI](https://github.com/ansys/pyaedt/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/ansys/pyaedt/actions/workflows/unit_tests.yml)[![codecov](https://codecov.io/gh/ansys/pyaedt/branch/main/graph/badge.svg)](https://codecov.io/gh/ansys/pyaedt)[![MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/blog/license/mit)[![black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat)](https://github.com/psf/black)[![Anaconda](https://anaconda.org/conda-forge/pyaedt/badges/version.svg)](https://anaconda.org/conda-forge/pyaedt)[![pre-commit](https://results.pre-commit.ci/badge/github/ansys/pyaedt/main.svg)](https://results.pre-commit.ci/latest/github/ansys/pyaedt/main)

## PyAEDT 简介

`PyAEDT` 是一个直接与 `AEDT API` 交互的 `Python` 库。使最终用户的脚本编写更简易。它的框架可重复使用，适用于所有 AEDT 3D 产品（`HFSS`、`Icepak`、`Maxwell 3D` 和 `Q3D Extractor`）、`2D tools` 和 `Ansys Mechanical`。它支持像 `Nexxim` 这样的电路工具和 `Twin Builder` 这样的系统模拟工具。最后它为 `HFSS 3D Layout` 和 `EDB` 等 `Ansys` 布局工具提供脚本功能。它的类方法结构简化了最终用户的操作，同时尽可能在整个 API 中复用信息。

## 关于 PyAEDT 的安装

1. 您可以使用 `PyPI` 工具将 `PyAEDT` 安装在 `CPython 3.8-3.12` 版本上:

``` python
  pip install pyaedt
```

2. 当您同时需要其他数据处理时可以选择安装 `PyAEDT` 和以下对应的库（`matplotlib`,  `numpy`, `pandas`, `pyvista`）：

```sh
  pip install pyaedt[all]
  pip install matplotlib
  pip install numpy
  pip install pandas
  pip install pyvista
```

3. 您也可以从 `Conda-Forge` 安装 `PyAEDT` ：

```sh
  conda install -c conda-forge pyaedt
```

`PyAEDT` 与 `Ironpython` 兼容，仍然可以在 `AEDT` 框架中使用。

备注（2023年3月22日）：`PyAEDT`的主要贡献者决定减少默认包的内存占用。如果你运行 pip install pyaedt，以下安装是必须的(在拥有PyAEDT基础功能的情况下)：
```
"cffi == 1.15.0;platform_system=='Linux'",
"pywin32 >= 303;platform_system=='Windows'",
"pythonnet == 3.0.1",
"rpyc==5.3.0",
"psutil",
"dotnetcore2 ==3.1.23;platform_system=='Linux'"
```
4. 如果你需要其他库来做后期处理，可以使用以下方法来安装它们：
```sh
pip install pyaedt[all]
```

## 关于 PyAEDT

`PyAEDT` 是 [PyAnsys](https://docs.pyansys.com "PyAnsys") 的一部分，后者更庞大。努力促进直接从 `Python` 使用 `Ansys` 技术。

`PyAEDT` 旨在整合和扩展 `Ansys Electronics Desktop (AEDT)` 脚本的所有现有功能，以允许重用现有代码、共享最佳实践并加强协作。

 ## 关于 AEDT

`Ansys Electronics Desktop (AEDT)` 是一个真正支持电子系统设计的平台。[AEDT](https://www.ansys.com/products/electronics) 使用 `电气CAD(ECAD)` 和 `机械CAD(MCAD)` 工作流程提供对 Ansys gold-standard electro-magnetics 仿真解决方案的访问，例如 `Ansys HFSS`、`Ansys Maxwell`、`Ansys Q3D Extractor`、`Ansys SIwave` 和 `Ansys Icepak`。此外，它还包括与完整的 `Ansys热求解器(Thermal)`、`流体求解器(Fluid)` 和 `机械求解器(Mechanical)` 产品组合的直接连接，用于全面的多物理场分析。这些解决方案之间的紧密集成提供了前所未有的设置易用性，并更快地解决了用于设计和优化的复杂仿真。

 <p align="center">
  <img width="100%" src="https://images.ansys.com/is/image/ansys/ansys-electronics-technology-collage?wid=941&op_usm=0.9,1.0,20,0&fit=constrain,0" title="AEDT Applications" herf="https://www.ansys.com/products/electronics"
  />
</p>

`PyAEDT` 遵循 [MIT](https://github.com/ansys/pyaedt/blob/main/LICENSE "MIT") 许可证，并包括与 `AEDT tools` 和 `Ansys products` 交互的功能：

-  HFSS and HFSS 3D Layout
-  Icepak
-  Maxwell 2D, Maxwell 3D, and RMXprt
-  2D Extractor and Q3D Extractor
-  Mechanical
-  Nexxim
-  EDB
-  Twin Builder

## 文档与反馈

除了安装和使用信息外，`PyAEDT` 文档还提供了 [参考API](https://aedt.docs.pyansys.com/version/stable/API/index.html "API reference")，[示例](https://aedt.docs.pyansys.com/version/stable/examples/index.html "Examples")，和 [贡献](https://aedt.docs.pyansys.com/version/stable/Contributing.html "Contribute") 。


在 [PyAEDT Issues](https://github.com/ansys/pyaedt/issues) 页面，您可以提交所遇到的问题、反馈 bug、为新功能贡献您的想法与思路。如联系项目支持团队，请点击后面的链接发送电子邮件 [pyansys.support@ansys.com](pyansys.support@ansys.com).

## 适用范围

`PyAEDT` 支持 `AEDT 2022 R1` 或更高的版本。

`PyAEDT` 支持 `AEDT Student version 2022 R1` 或更高的版本。

关于学生版本的更多信息请查阅 [Student Version page](https://www.ansys.com/academic/students/ansys-electronics-desktop-student).

## 为什么选择 PyAEDT

在 AEDT UI 中使用记录和重用脚本自动执行是简化操作的一种快速又简便的办法。但是，此方法有以下缺陷：

-  记录的代码比较混乱，难以阅读与理解。
-  录制的脚本难以复用和二次编辑。
-  AEDT 多个全局用户会生成复杂庞大的代码。

`PyAEDT` 的主要优点是：

-  自动初始化所有AEDT项目，例如desktop项目中的编辑器、边界等等
-  清晰的错误管理
-  详细的日志管理
-  自由的变量管理
-  兼容 IronPython 和 CPython
-  使用数据对象简化复杂的 API 语法，同时保持 PEP8 合规性。
-  在不同求解器之间的可复用代码
-  在函数与API上拥有清晰的文档
-  代码单元测试，以提高不同 AEDT 版本的质量

## 工作流程示例

 1. 在所需的`AEDT`版本中初始化`desktop`类。
 2. 并初始化`AEDT`中所要使用的应用程序。

##  使用 Python IDE 连接 AEDT

`PyAEDT` 既可以在AEDT内部工作，也可以作为独立应用程序使用。此 Python 库会自动检测它是否正在运行在 IronPython 或 CPython 环境中并相应地初始化 AEDT。
`PyAEDT` 还提供高级错误管理。使用示例如下:

### 明确 AEDT 声明 [INFO] 并管理报错 [ERROR]

``` python
    # 以非图形模式启动 AEDT 2022 R2

    from ansys.aedt.core import Desktop, Circuit
    with Desktop(specified_version="2022.2",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False):
        circuit = Circuit()
        ...
        # 此处的任何错误都将被 Desktop 捕获。
        ...

    # Desktop 将在此处自动发布。
```

### Implicit AEDT declaration and error management

``` python
    # Launch the latest installed version of AEDT in graphical mode

    from ansys.aedt.core import Circuit
    with Circuit(specified_version="2022.2",
                 non_graphical=False) as circuit:
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.
```

## 远程应用程序调用

您可以在 CPython 服务器或任何 Windows 客户端计算机上进行远程应用程序调用。

CPython 服务器：

``` python
    # 在CPython上启动PyAEDT远程服务器

    from ansys.aedt.core.common_rpc import pyaedt_service_manager
    pyaedt_service_manager()
```

任意的 Windows 客户端：

``` python
    from ansys.aedt.core.common_rpc import create_session
    cl1 = create_session("server_name")
    cl1.aedt(port=50000, non_graphical=False)
    hfss = Hfss(machine="server_name", port=50000)
    # 在这里编辑您的代码
```

## 变量 Variables

``` python
    from ansys.aedt.core.HFSS import HFSS
    with HFSS as hfss:
         hfss["dim"] = "1mm"   # design variable
         hfss["$dim"] = "1mm"  # project variable
```

## 模型 Modeler

``` python
    # 创建BOX、分配变量和指定材料。

    from ansys.aedt.core.hfss import Hfss
    with Hfss as hfss:
         hfss.modeler.create_box([0, 0, 0], [10, "dim", 10],
                                 "mybox", "aluminum")
```

## 许可

要运行`PyAEDT`，您必须拥有`AEDT`的本地许可证。
`PyAEDT`在`MIT`许可下获得许可。这个模块对`Ansys`没有任何商业要求。`PyAEDT`通过向`AEDT`添加额外的Python接口扩展了`AEDT`的功能，而不改变原始软件的核心行为或许可。使用`PyAEDT`的交互式控件需要合法授权的`AEDT`本地license。有关`AEDT`的更多信息，请访问`Ansys`网站上的[AEDT页面](https://www.ansys.com/products/electronics)。

<p style="text-align: right;"> <a href="#readme-top">回到顶部</a> </p>

## 索引与目录

-  [Index](https://aedt.docs.pyansys.com/version/stable/genindex.html)
-  [Module Index](https://aedt.docs.pyansys.com/version/stable/py-modindex.html)
-  [Search Page](https://aedt.docs.pyansys.com/version/stable/search.html)
