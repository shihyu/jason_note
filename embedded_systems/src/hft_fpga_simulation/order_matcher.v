// 簡化的訂單匹配引擎
module order_matcher #(
    parameter PRICE_WIDTH = 32,
    parameter QTY_WIDTH = 16,
    parameter ID_WIDTH = 16
)(
    input wire clk,
    input wire rst,

    // 新訂單輸入
    input wire order_valid,
    input wire order_is_buy,  // 1=買單, 0=賣單
    input wire [PRICE_WIDTH-1:0] order_price,
    input wire [QTY_WIDTH-1:0] order_qty,
    input wire [ID_WIDTH-1:0] order_id,

    // 匹配輸出
    output reg match_valid,
    output reg [ID_WIDTH-1:0] match_buy_id,
    output reg [ID_WIDTH-1:0] match_sell_id,
    output reg [PRICE_WIDTH-1:0] match_price,
    output reg [QTY_WIDTH-1:0] match_qty,

    // 性能計數器
    output reg [31:0] total_orders,
    output reg [31:0] total_matches,
    output reg [31:0] cycle_counter
);

    // 簡化的訂單簿（實際應該用 CAM 或更複雜的結構）
    reg [PRICE_WIDTH-1:0] best_bid_price;
    reg [QTY_WIDTH-1:0] best_bid_qty;
    reg [ID_WIDTH-1:0] best_bid_id;
    reg bid_valid;

    reg [PRICE_WIDTH-1:0] best_ask_price;
    reg [QTY_WIDTH-1:0] best_ask_qty;
    reg [ID_WIDTH-1:0] best_ask_id;
    reg ask_valid;

    // 延遲計數（模擬處理延遲）
    reg [7:0] processing_cycles;

    always @(posedge clk) begin
        if (rst) begin
            match_valid <= 0;
            bid_valid <= 0;
            ask_valid <= 0;
            total_orders <= 0;
            total_matches <= 0;
            cycle_counter <= 0;
            processing_cycles <= 0;
        end else begin
            cycle_counter <= cycle_counter + 1;
            match_valid <= 0;

            if (order_valid) begin
                total_orders <= total_orders + 1;
                processing_cycles <= processing_cycles + 1;

                if (order_is_buy) begin
                    // 買單邏輯
                    if (ask_valid && order_price >= best_ask_price) begin
                        // 匹配成功
                        match_valid <= 1;
                        match_buy_id <= order_id;
                        match_sell_id <= best_ask_id;
                        match_price <= best_ask_price;
                        match_qty <= (order_qty < best_ask_qty) ? order_qty : best_ask_qty;
                        total_matches <= total_matches + 1;

                        // 更新訂單簿
                        if (order_qty >= best_ask_qty) begin
                            ask_valid <= 0;
                        end else begin
                            best_ask_qty <= best_ask_qty - order_qty;
                        end
                    end else begin
                        // 加入訂單簿
                        if (!bid_valid || order_price > best_bid_price) begin
                            best_bid_price <= order_price;
                            best_bid_qty <= order_qty;
                            best_bid_id <= order_id;
                            bid_valid <= 1;
                        end
                    end
                end else begin
                    // 賣單邏輯
                    if (bid_valid && order_price <= best_bid_price) begin
                        // 匹配成功
                        match_valid <= 1;
                        match_buy_id <= best_bid_id;
                        match_sell_id <= order_id;
                        match_price <= best_bid_price;
                        match_qty <= (order_qty < best_bid_qty) ? order_qty : best_bid_qty;
                        total_matches <= total_matches + 1;

                        // 更新訂單簿
                        if (order_qty >= best_bid_qty) begin
                            bid_valid <= 0;
                        end else begin
                            best_bid_qty <= best_bid_qty - order_qty;
                        end
                    end else begin
                        // 加入訂單簿
                        if (!ask_valid || order_price < best_ask_price) begin
                            best_ask_price <= order_price;
                            best_ask_qty <= order_qty;
                            best_ask_id <= order_id;
                            ask_valid <= 1;
                        end
                    end
                end
            end
        end
    end

endmodule