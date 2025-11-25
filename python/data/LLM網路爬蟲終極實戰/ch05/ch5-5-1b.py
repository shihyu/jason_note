import csv

data = [
    ["姓名", "年齡", "城市"],
    ["王小明", 28, "台北"],
    ["陳美麗", 35, "高雄"],
    ["李大仁", 42, "新竹"]
]
# 使用 utf-8-sig 編碼儲存成 CSV 檔案
with open("Example3.csv", mode="w", encoding="utf-8-sig",
          newline="") as fp:
    writer = csv.writer(fp)
    writer.writerows(data)
