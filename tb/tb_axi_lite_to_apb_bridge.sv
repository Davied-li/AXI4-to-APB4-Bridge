`timescale 1ns / 1ps

module tb_axi_lite_to_apb_bridge;

    // ==========================================
    // 时钟和复位
    // ==========================================
    logic clk;
    logic rst_n;

    // ==========================================
    // AXI 侧信号 (加入所有的 Burst 信号)
    // ==========================================
    logic [31:0] s_axi_awaddr;
    logic [2:0]  s_axi_awprot;
    logic [7:0]  s_axi_awlen;    // 新增
    logic [2:0]  s_axi_awsize;   // 新增
    logic [1:0]  s_axi_awburst;  // 新增
    logic        s_axi_awvalid;
    logic        s_axi_awready;

    logic [31:0] s_axi_wdata;
    logic [3:0]  s_axi_wstrb;
    logic        s_axi_wlast;    // 新增
    logic        s_axi_wvalid;
    logic        s_axi_wready;

    logic [1:0]  s_axi_bresp;
    logic        s_axi_bvalid;
    logic        s_axi_bready;

    logic [31:0] s_axi_araddr;
    logic [2:0]  s_axi_arprot;
    logic [7:0]  s_axi_arlen;    // 新增
    logic [2:0]  s_axi_arsize;   // 新增
    logic [1:0]  s_axi_arburst;  // 新增
    logic        s_axi_arvalid;
    logic        s_axi_arready;

    logic [31:0] s_axi_rdata;
    logic [1:0]  s_axi_rresp;
    logic        s_axi_rlast;    // 新增
    logic        s_axi_rvalid;
    logic        s_axi_rready;

    // ==========================================
    // APB 侧信号
    // ==========================================
    logic [31:0] paddr;
    logic [2:0]  pprot;
    logic [3:0]  psel;
    logic        penable;
    logic        pwrite;
    logic [31:0] pwdata;
    logic [3:0]  pstrb;
    logic [31:0] prdata;
    logic        pready;
    logic        pslverr;

    // ==========================================
    // 实例化真正的 DUT (你刚才写的 RTL)
    // ==========================================
    axi_lite_to_apb_bridge #(
        .ADDR_WIDTH(32),
        .DATA_WIDTH(32)
    ) dut (
        .clk            (clk),
        .rst_n          (rst_n),
        
        .s_axi_awaddr   (s_axi_awaddr),
        .s_axi_awprot   (s_axi_awprot),
        .s_axi_awlen    (s_axi_awlen),    // 连线
        .s_axi_awsize   (s_axi_awsize),   // 连线
        .s_axi_awburst  (s_axi_awburst),  // 连线
        .s_axi_awvalid  (s_axi_awvalid),
        .s_axi_awready  (s_axi_awready),

        .s_axi_wdata    (s_axi_wdata),
        .s_axi_wstrb    (s_axi_wstrb),
        .s_axi_wlast    (s_axi_wlast),    // 连线
        .s_axi_wvalid   (s_axi_wvalid),
        .s_axi_wready   (s_axi_wready),

        .s_axi_bresp    (s_axi_bresp),
        .s_axi_bvalid   (s_axi_bvalid),
        .s_axi_bready   (s_axi_bready),

        .s_axi_araddr   (s_axi_araddr),
        .s_axi_arprot   (s_axi_arprot),
        .s_axi_arlen    (s_axi_arlen),    // 连线
        .s_axi_arsize   (s_axi_arsize),   // 连线
        .s_axi_arburst  (s_axi_arburst),  // 连线
        .s_axi_arvalid  (s_axi_arvalid),
        .s_axi_arready  (s_axi_arready),

        .s_axi_rdata    (s_axi_rdata),
        .s_axi_rresp    (s_axi_rresp),
        .s_axi_rlast    (s_axi_rlast),    // 连线
        .s_axi_rvalid   (s_axi_rvalid),
        .s_axi_rready   (s_axi_rready),

        .paddr          (paddr),
        .pprot          (pprot),
        .psel           (psel),
        .penable        (penable),
        .pwrite         (pwrite),
        .pwdata         (pwdata),
        .pstrb          (pstrb),
        .prdata         (prdata),
        .pready         (pready),
        .pslverr        (pslverr)
    );

    // 自动生成波形文件 (用于后续查错)
    initial begin
        $dumpfile("bridge_burst.vcd");
        $dumpvars(0, tb_axi_lite_to_apb_bridge);
    end

endmodule