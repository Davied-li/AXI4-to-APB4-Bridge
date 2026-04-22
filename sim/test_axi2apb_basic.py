import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

# ==============================================================================
# 核心验证组件：模拟 4 个不同特性的 APB 从设备
# ==============================================================================
async def mock_multi_apb_slaves(dut):
    """在后台静默运行，根据 PSEL 的不同位，模拟不同设备的响应"""
    dut.pready.value = 0
    dut.pslverr.value = 0
    dut.prdata.value = 0
    
    timer_val = 0 # 用于 Device 3 的自增计数器

    while True:
        await RisingEdge(dut.clk)
        
        # 只有进入 APB ACCESS 阶段 (PENABLE=1) 时才响应
        if dut.penable.value == 1:
            psel_val = int(dut.psel.value)
            
            if psel_val == 1:  
                # Device 0 (UART @ 0x0xxx): 极速设备，瞬间 Ready
                dut.pready.value = 1
                dut.prdata.value = 0xAAAA0000
                await RisingEdge(dut.clk)
                dut.pready.value = 0
                
            elif psel_val == 2:  
                # Device 1 (SPI @ 0x1xxx): 慢速设备，硬生生拖延 3 拍
                for _ in range(3):
                    await RisingEdge(dut.clk)
                dut.pready.value = 1
                dut.prdata.value = 0xBBBB0000
                await RisingEdge(dut.clk)
                dut.pready.value = 0
                
            elif psel_val == 4:  
                # Device 2 (GPIO @ 0x2xxx): 只读设备，硬写会报错 (PSLVERR)
                dut.pready.value = 1
                dut.prdata.value = 0xCCCC0000
                if dut.pwrite.value == 1: 
                    dut.pslverr.value = 1 # 触发异常注入
                await RisingEdge(dut.clk)
                dut.pready.value = 0
                dut.pslverr.value = 0
                
            elif psel_val == 8:  
                # Device 3 (Timer @ 0x3xxx): 智能设备，数据每次自增
                dut.pready.value = 1
                dut.prdata.value = timer_val
                timer_val += 1
                await RisingEdge(dut.clk)
                dut.pready.value = 0

# ==============================================================================
# 基础操作：复位与信号初始化
# ==============================================================================
async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.s_axi_awvalid.value = 0
    dut.s_axi_wvalid.value = 0
    dut.s_axi_bready.value = 0
    dut.s_axi_arvalid.value = 0
    dut.s_axi_rready.value = 0
    
    dut.s_axi_awlen.value = 0
    dut.s_axi_awsize.value = 2   
    dut.s_axi_awburst.value = 1  
    dut.s_axi_wlast.value = 0
    
    dut.s_axi_arlen.value = 0
    dut.s_axi_arsize.value = 2
    dut.s_axi_arburst.value = 1

    await Timer(25, units="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

# 封装一个辅助写函数，让主测试代码更清爽
async def axi_write_single(dut, addr, data):
    dut.s_axi_awaddr.value = addr
    dut.s_axi_awvalid.value = 1
    dut.s_axi_wdata.value = data
    dut.s_axi_wstrb.value = 0xF
    dut.s_axi_wvalid.value = 1
    dut.s_axi_wlast.value = 1
    dut.s_axi_bready.value = 1
    
    while True:
        await RisingEdge(dut.clk)
        if dut.s_axi_awready.value == 1 and dut.s_axi_wready.value == 1:
            break
            
    dut.s_axi_awvalid.value = 0
    dut.s_axi_wvalid.value = 0
    dut.s_axi_wlast.value = 0
    
    while dut.s_axi_bvalid.value == 0:
        await RisingEdge(dut.clk)
    
    resp = int(dut.s_axi_bresp.value)
    await RisingEdge(dut.clk)
    return resp

# 封装一个辅助读函数
async def axi_read_single(dut, addr):
    dut.s_axi_araddr.value = addr
    dut.s_axi_arvalid.value = 1
    dut.s_axi_rready.value = 1
    
    while True:
        await RisingEdge(dut.clk)
        if dut.s_axi_arready.value == 1:
            break
            
    dut.s_axi_arvalid.value = 0
    
    while dut.s_axi_rvalid.value == 0:
        await RisingEdge(dut.clk)
    
    data = int(dut.s_axi_rdata.value)
    resp = int(dut.s_axi_rresp.value)
    await RisingEdge(dut.clk)
    return data, resp

# ==============================================================================
# 测试主入口：遍历 4 个设备及越界场景
# ==============================================================================
@cocotb.test()
async def test_multi_slave_mapping(dut):
    """测试 1 拖 4 多设备地址映射及高级异常注入"""
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    cocotb.start_soon(mock_multi_apb_slaves(dut))
    
    await reset_dut(dut)
    
    dut._log.info("========== 场景 1: 访问 Device 0 (UART, 极速响应) @ 0x00000100 ==========")
    resp = await axi_write_single(dut, 0x00000100, 0x11112222)
    assert resp == 0, "Device 0 写入失败"
    
    dut._log.info("========== 场景 2: 访问 Device 1 (SPI, 延迟 3 拍) @ 0x00001200 ==========")
    data, resp = await axi_read_single(dut, 0x00001200)
    assert resp == 0
    assert data == 0xBBBB0000, f"SPI 返回数据错误, 得到: {hex(data)}"

    dut._log.info("========== 场景 3: 访问 Device 2 (GPIO, 故意引发报错) @ 0x00002300 ==========")
    resp = await axi_write_single(dut, 0x00002300, 0x99999999)
    assert resp == 2, "GPIO 是只读的，写入必须返回 SLVERR (2)！"
    
    dut._log.info("========== 场景 4: 访问 Device 3 (Timer, 验证自增逻辑) @ 0x00003400 ==========")
    data1, _ = await axi_read_single(dut, 0x00003400)
    data2, _ = await axi_read_single(dut, 0x00003400)
    assert data1 == 0, "Timer 初始值应为 0"
    assert data2 == 1, "Timer 第二次读取应自增为 1"
    
    dut._log.info("========== 场景 5: 越界访问 (黑洞拦截) @ 0x00004500 ==========")
    resp = await axi_write_single(dut, 0x00004500, 0xDEADBEEF)
    assert resp == 2, "越界地址 (大于 0x3FFF) 必须被拦截并返回 SLVERR (2)！"

    dut._log.info("========== 全局通关：多设备地址映射与异常注入测试全部 PASS！ ==========")