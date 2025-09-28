// counter.v - 8-bit 計數器模組
module counter (
    input wire clk,
    input wire rst,
    output reg [7:0] count
);

    always @(posedge clk) begin
        if (rst)
            count <= 8'd0;
        else
            count <= count + 1;
    end

endmodule