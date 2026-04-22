import os
from pathlib import Path
from cocotb_tools.runner import get_runner

# 项目根目录
PROJ_ROOT = Path(__file__).resolve().parent.parent
RTL_DIR = PROJ_ROOT / "rtl"
TB_DIR = PROJ_ROOT / "tb"

# Icarus Verilog 所在目录（MSYS2 UCRT64）
MSYS_BIN = r"D:\msys64\ucrt64\bin"

# Anaconda Python 根目录
PYTHON_ROOT = Path(r"C:\Users\lzy\anaconda3")
LIBPYTHON = PYTHON_ROOT / "python311.dll"

# 把 iverilog / vvp 加到 PATH
os.environ["PATH"] = MSYS_BIN + os.pathsep + os.environ["PATH"]

# 告诉 cocotb 去哪里找 python311.dll
os.environ["LIBPYTHON_LOC"] = str(LIBPYTHON)

# 关键：把 tb 目录加入 Python 搜索路径
old_pythonpath = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = str(TB_DIR) + os.pathsep + old_pythonpath if old_pythonpath else str(TB_DIR)

sources = [
    RTL_DIR / "axi_lite_to_apb_bridge.v",
    TB_DIR / "tb_axi_lite_to_apb_bridge.sv",
]

runner = get_runner("icarus")

runner.build(
    sources=sources,
    hdl_toplevel="tb_axi_lite_to_apb_bridge",
    always=True,
    waves=True,
)

runner.test(
    hdl_toplevel="tb_axi_lite_to_apb_bridge",
    test_module="test_axi2apb_basic",
)