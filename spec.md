# AXI4-Full to APB4 Multi-Slave Bridge Spec

## Version
v2.0 (Ultimate Edition)

## Overview
This project implements a high-performance, synchronous Full AXI4 to APB4 bridge with advanced features:
- **AXI4 Burst Support**: Handles multi-beat transactions (INCR mode).
- **Multi-Slave Decoding**: 1-to-4 APB device address mapping.
- **Robust Error Handling**: Deadlock-free "Data Sink" mechanism for illegal bursts.
- **Protocol Compliance**: Embedded SystemVerilog Assertions (SVA) for AXI/APB rules.

## Clock and Reset
- Shared clock: `clk`
- Active-low reset: `rst_n`

## Address Map & Decoding
The bridge decodes AXI addresses and routes to 4 different APB slaves via a 4-bit `psel` bus. The routing is based on `addr[13:12]`:
- **Device 0** (`psel[0]`): `0x0000_0000 ~ 0x0000_0FFF` 
- **Device 1** (`psel[1]`): `0x0000_1000 ~ 0x0000_1FFF` 
- **Device 2** (`psel[2]`): `0x0000_2000 ~ 0x0000_2FFF` 
- **Device 3** (`psel[3]`): `0x0000_3000 ~ 0x0000_3FFF` 

**Hardware boundaries check:**
- Valid address range is `0x0000 ~ 0x3FFF`.
- Rule: `s_axi_awaddr[31:14] == 18'h00000` (Area-optimized logic).

## Burst Handling Rule
- Translates a single AXI Burst transaction into multiple consecutive APB single transactions.
- Address automatically increments based on shift logic: `paddr <= paddr + (1 << awsize)`.
- Write acceptance strictly requires `s_axi_awvalid == 1` && `s_axi_wvalid == 1` to prevent deadlock.

## Advanced Error Handling
- **Out-of-range Access (Black-Hole Sink)**: If an illegal address is targeted during a burst, the bridge enters `ST_ERR_SINK_W` state to absorb all remaining `WDATA` beats safely, preventing AXI bus deadlock, and returns `SLVERR` at the end.
- **PSLVERR Propagation**: APB `pslverr` is latched (`err_latch`) during burst beats and evaluated at the final `RESP` phase to return `SLVERR`.
- **Timeout Protection**: `TIMEOUT_CYCLES = 16`. If APB `pready` is stuck, the bridge forces a timeout, enters the sink state to clear AXI buffers, and returns `SLVERR`.

## Verification Features (cocotb)
- Full Python-based coroutine testbench.
- Mock APB slaves with variable characteristics (0-delay, wait-states, read-only errors).
- Functional coverage collection for transactions, burst types, and error intersections.



# AXI4-Full 到 APB4 多节点桥接器规格说明书 (Spec)

## 版本号
v2.0 (终极版)

## 1. 总体概述 (Overview)
本项目实现了一个高性能的、纯同步的 Full AXI4 到 APB4 桥接器，包含以下高级特性：
- **完整 AXI4 突发传输 (Burst) 支持**：能够处理连续多拍的数据传输（支持 INCR 递增模式）。
- **多从设备译码 (Multi-Slave Decoding)**：支持 1 根 AXI 总线路由到 4 个不同的 APB 从设备。
- **高鲁棒性错误处理 (Robust Error Handling)**：独创“数据排空黑洞”机制，彻底杜绝非法突发传输导致的总线死锁。
- **底层协议合规 (Protocol Compliance)**：内嵌 SVA（SystemVerilog Assertions）断言防线，24小时监控 AXI/APB 协议规则。

## 2. 时钟与复位 (Clock and Reset)
- **共享时钟**：`clk`（全同步设计，无跨时钟域处理）
- **复位信号**：`rst_n`（低电平有效异步复位）

## 3. 地址映射与智能译码 (Address Map & Decoding)
桥接器通过解析 AXI 传来的地址，将请求通过 4-bit 的 `psel`（片选）总线路由给 4 个不同的 APB 外设。
路由规则基于地址的第 `[13:12]` 位：
- **设备 0** (`psel[0]`): `0x0000_0000 ~ 0x0000_0FFF` (常用于 UART等极速设备)
- **设备 1** (`psel[1]`): `0x0000_1000 ~ 0x0000_1FFF` (常用于 SPI等慢速设备)
- **设备 2** (`psel[2]`): `0x0000_2000 ~ 0x0000_2FFF` (常用于 GPIO只读设备)
- **设备 3** (`psel[3]`): `0x0000_3000 ~ 0x0000_3FFF` (常用于 Timer定时器)

**硬件边界安全检查：**
- 合法的整体地址范围必须在 `0x0000 ~ 0x3FFF` 之间。
- **硬件判断逻辑**：`s_axi_awaddr[31:14] == 18'h00000` 
> *【导师批注】：这里没有使用 > 或 < 符号，而是直接判断高 18 位是否全为 0，这在芯片综合时极大地节省了电路面积。*

## 4. 突发传输规则 (Burst Handling Rule)
- 桥接器负责将 AXI 的 1 次长突发（如连续 4 拍），拆解为 APB 的 4 次独立单拍传输。
- **地址递增逻辑**：`paddr <= paddr + (1 << awsize)`。
> *【导师批注】：利用硬件移位操作 `(1 << awsize)` 替代乘法器来实现地址累加，是高级 IC 设计中的经典面积优化手段。*
- **防死锁写握手**：严格要求 `s_axi_awvalid == 1` 且 `s_axi_wvalid == 1` 同时到达时，桥接器才接单。

## 5. 高阶异常处理机制 (Advanced Error Handling)
- **越界访问 (黑洞拦截)**：如果 AXI 发起了一次 8 拍的写突发，但地址超出了 `0x3FFF`。桥接器不会立刻报错阻断，而是进入 `ST_ERR_SINK_W` (数据排空状态)，把剩下的 WDATA 全部安全吸收掉，防止 AXI 总线瘫痪，最后统一返回 `SLVERR` 错误响应。
- **PSLVERR 错误传递**：如果 APB 从设备报错 (`pslverr = 1`)，桥接器会用锁存器 (`err_latch`) 记下错误，在突发传输的最后阶段将错误传递给 AXI 的 `BRESP / RRESP`。
- **超时保护 (Timeout)**：设定 `TIMEOUT_CYCLES = 16`。如果 APB 从设备死机（长时间不拉高 `pready`），桥接器会强制掐断连接，清理缓存，并向主机返回 `SLVERR`。

## 6. 验证特性 (Verification Features)
- 抛弃传统 Verilog Testbench，采用 **cocotb + Python 协程** 驱动的现代验证平台。
- 编写了 **Mock APB Slaves (虚拟自动机)**，实现了对不同设备的 0 延迟、多拍等待（Wait-states）、只读报错等复杂场景的精准模拟。