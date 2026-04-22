TOPLEVEL_LANG = verilog
SIM = icarus
PYTHON_BIN = C:/Users/lzy/anaconda3/python.exe
COCOTB_MAKEFILES = $(shell $(PYTHON_BIN) -m cocotb_tools.config --makefiles)
PWD = $(CURDIR)
VERILOG_SOURCES = $(PWD)/../rtl/axi_lite_to_apb_bridge.v $(PWD)/../tb/tb_axi_lite_to_apb_bridge.sv
TOPLEVEL = tb_axi_lite_to_apb_bridge
MODULE = test_axi2apb_basic
WAVES = 1
include $(COCOTB_MAKEFILES)/Makefile.sim