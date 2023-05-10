class kBar():
    open = 0
    hign = 0
    low = 0
    close = 0
    volum = 0
    vwap = 0
    timestamp = ""

    def setKBar(self, o, h, l, c, volume, vwap):
        self.open = o
        self.high = h
        self.low = l
        self.close = c
        self.volum = volume
        self.vwap = vwap

    def printKBar(self):
        print(f"Timestamp: {self.timestamp},"
              f"Open: {self.open},"
              f"High: {self.high},"
              f"Low: {self.low},"
              f"Close: {self.close},"
              f"Volum: {self.volum},"
              f"Vwap: {self.vwap}")
