## pine語言學習指令碼


```sh
//@version=4
study("SMA Trend Strategy")

// 設置參數
fastLength = input(title="Fast Length", type=input.integer, defval=10)
slowLength = input(title="Slow Length", type=input.integer, defval=20)

// 計算指標
fastSMA = sma(close, fastLength)
slowSMA = sma(close, slowLength)

// 設置止盈止損
longStop = strategy.position_avg_price * (1 - 0.01)
shortStop = strategy.position_avg_price * (1 + 0.01)
longlimit = strategy.position_avg_price * (1 + 0.01)
shortlimit = strategy.position_avg_price * (1 - 0.01)

// 開倉條件
longCondition = crossover(fastSMA, slowSMA)
shortCondition = crossunder(fastSMA, slowSMA)

// 開倉
strategy.entry("Long", strategy.long, when=longCondition)
strategy.entry("Short", strategy.short, when=shortCondition)

// 止盈止損
strategy.exit("Long Stop", "Long", stop=longStop,limit=longlimit)
strategy.exit("Short Stop", "Short", stop=shortStop,limit=shortlimit)
```



#     [The Art of Trading](https://www.youtube.com/c/TheArtofTrading)  

https://courses.theartoftrading.com/pages/pine-script-mastery-code#strategy1

https://www.youtube.com/watch?v=h-erJbnBj6A&feature=youtu.be



## How To Create A Regime Filter

[Watch Lesson](https://youtu.be/MV61WcTkV54)

```python
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © ZenAndTheArtOfTrading / www.PineScriptMastery.com
// @version=5
indicator("Regime Filter")

// Get user input
res = input.timeframe(title="Timeframe", defval="D")
len = input.int(title="EMA Length", defval=20)
market = input.symbol(title="Market", defval="NASDAQ:NDX")

// Define custom security function
f_sec(_market, _res, _exp) => request.security(_market, _res, _exp[barstate.isconfirmed ? 0 : 1])

// Get EMA value
ema = ta.ema(close, len)
emaValue = f_sec(market, res, ema)

// Check if price is above or below EMA filter
marketPrice = f_sec(market, res, close)
regimeFilter = marketPrice > emaValue or marketPrice[1] > emaValue[1]

// Change background color
bgcolor(regimeFilter ? color.green : color.red)
```



## AUTO-FIBONACCI Tool

[Watch Lesson](https://youtu.be/SdYHqTlsDWo)

```python
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © ZenAndTheArtOfTrading / PineScriptMastery.com
// @version=5
indicator("Auto-Fib", overlay=true)

// Get user input
var devTooltip          = "Deviation is a multiplier that affects how much the price should deviate from the previous pivot in order for the bar to become a new pivot."
var depthTooltip        = "The minimum number of bars that will be taken into account when calculating the indicator."
threshold_multiplier    = input.float(title="Deviation", defval=3, minval=0, tooltip=devTooltip)
depth                   = input.int(title="Depth", defval=10, minval=1, tooltip=depthTooltip)
reverse                 = input.bool(title="Reverse", defval=false, tooltip="Flips the fibonacci levels around.")
extendLeft              = input.bool(title="Extend Left    |    Extend Right", defval=false, inline="Extend Lines")
extendRight             = input.bool(title="", defval=false, inline="Extend Lines")
prices                  = input.bool(title="Show Prices", defval=false)
deleteLastLine          = input.bool(title="Delete Last Line", defval=true)
levels                  = input.bool(title="Show Levels", defval=true, inline="Levels")
levelsFormat            = input.string(title="", defval="Values", options=["Values", "Percent"], inline="Levels")
labelsPosition          = input.string(title="Labels Position", defval="Left", options=["Left", "Right"])
backgroundTransparency  = input.int(title="Background Transparency", defval=85, minval=0, maxval=100)

// Check extending parameter
var extending = extend.none
if extendLeft and extendRight
    extending := extend.both
if extendLeft and not extendRight
    extending := extend.left
if not extendLeft and extendRight
    extending := extend.right

// Calculate deviation threshold for identifying major swings
dev_threshold = ta.atr(10) / close * 100 * threshold_multiplier

// Prepare pivot variables
var line lineLast = na
var int iLast = 0
var int iPrev = 0
var float pLast = 0
var isHighLast = false // Otherwise the last pivot is a low pivot

// Custom function for detecting pivot points
pivots(src, length, isHigh) =>
    l2 = length * 2
    c = nz(src[length])
    ok = true
    for i = 0 to l2
        if isHigh and src[i] > c
            ok := false
        if not isHigh and src[i] < c
            ok := false
    if ok
        [bar_index[length], c]
    else
        [int(na), float(na)]

// Get bar index & price high/low for current pivots
[iH, pH] = pivots(high, depth / 2, true)
[iL, pL] = pivots(low, depth / 2, false)

// Custom function for calculating price deviation
calc_dev(base_price, price) => 100 * (price - base_price) / price

// Custom function for detecting pivots that meet our deviation criteria
pivotFound(dev, isHigh, index, price) =>
    if isHighLast == isHigh and not na(lineLast)
        // New pivot in same direction as last, so update line (ie. trend-continuation)
        if isHighLast ? price > pLast : price < pLast
            line.set_xy2(lineLast, index, price)
            [lineLast, isHighLast]
        else
            [line(na), bool(na)] // No valid pivot detected, return nothing
    else // Reverse the trend/pivot direction (or create the very first line if lineLast is na)
        if math.abs(dev) > dev_threshold
            // Price move is significant - create a new line between the pivot points
            id = line.new(iLast, pLast, index, price, color=color.gray, width=1, style=line.style_dashed)
            [id, isHigh]
        else
            [line(na), bool(na)]

// If bar index for current pivot high is not NA (ie. we have a new pivot):
if not na(iH)
    dev = calc_dev(pLast, pH) // Calculate the deviation from last pivot
    [id, isHigh] = pivotFound(dev, true, iH, pH)
    if not na(id) // If the line has been updated, update price values and delete previous line
        if id != lineLast and deleteLastLine
            line.delete(lineLast)
        lineLast := id
        isHighLast := isHigh
        iPrev := iLast
        iLast := iH
        pLast := pH
else 
    if not na(iL) // If bar index for current pivot low is not NA (ie. we have a new pivot):
        dev = calc_dev(pLast, pL) // Calculate the deviation from last pivot
        [id, isHigh] = pivotFound(dev, false, iL, pL)
        if not na(id) // If the line has been updated, update price values and delete previous line
            if id != lineLast and deleteLastLine
                line.delete(lineLast)
            lineLast := id
            isHighLast := isHigh
            iPrev := iLast
            iLast := iL
            pLast := pL

// Draw fibonacci level as a line and return the line object ID
draw_fib_line(price, col) =>
    var id = line.new(iLast, price, bar_index, price, color=col, width=1, extend=extending)
    if not na(lineLast)
        line.set_xy1(id, line.get_x1(lineLast), price)
        line.set_xy2(id, line.get_x2(lineLast), price)  
	id  

// Draw fibonacci labels
draw_label(price, txt, txtColor) =>
    x = labelsPosition == "Left" ? line.get_x1(lineLast) : not extendRight ? line.get_x2(lineLast) : bar_index
    labelStyle = labelsPosition == "Left" ? label.style_label_right : label.style_label_left
    align = labelsPosition == "Left" ? text.align_right : text.align_left
    labelsAlignStrLeft = txt + '\n ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏ \n'
    labelsAlignStrRight = '       ' + txt + '\n ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏  ‏ \n'
    labelsAlignStr = labelsPosition == "Left" ? labelsAlignStrLeft : labelsAlignStrRight
    var id = label.new(x=x, y=price, text=labelsAlignStr, textcolor=txtColor, style=labelStyle, textalign=align, color=#00000000)
    label.set_xy(id, x, price)
    label.set_text(id, labelsAlignStr)
    label.set_textcolor(id, txtColor)

// Format the given string
format(txt) => " (" + str.tostring(txt, "#.####") + ")"

// Return the formatted label text for Fibonacci levels
label_txt(level, price) =>
    l = levelsFormat == "Values" ? str.tostring(level) : str.tostring(level * 100) + "%"
    (levels ? l : "") + (prices ? format(price) : "")

// Returns true if price is crossing the given fib level
crossing_level(price, fib) => (fib > price and fib < price[1]) or (fib < price and fib > price[1])

// Get starting and ending high/low price of the current pivot (for calculating fib levels)
startPrice = reverse ? line.get_y1(lineLast) : pLast
endPrice = reverse ? pLast : line.get_y1(lineLast)

// Calculate price difference between high and low
iHL = startPrice > endPrice
diff = (iHL ? -1 : 1) * math.abs(startPrice - endPrice)

// Process the given fib level (calculate fib, draw line & label, detect alerts, fill bgcolor between last fib)
processLevel(show, value, colorL, lineIdOther) =>
    if show
	    fibPrice = startPrice + diff * value
		lineId = draw_fib_line(fibPrice, colorL)
        draw_label(fibPrice, label_txt(value, fibPrice), colorL)
        if crossing_level(close, fibPrice) // Trigger alert if price is crossing this fib level
            alert("Autofib: " + syminfo.ticker + " crossing level " + str.tostring(value))
        if not na(lineIdOther) // Fill background color between each fib level
            linefill.new(lineId, lineIdOther, color=color.new(colorL, backgroundTransparency))
		lineId
    else
		lineIdOther

//{=============================================================================
var g_fibs = "Fibonacci Levels"
// Get Fibonacci level user inputs
show_0 = input(true, "", inline = "Level0", group=g_fibs)
value_0 = input(0, "", inline = "Level0", group=g_fibs)
color_0 = input(#787b86, "", inline = "Level0", group=g_fibs)
//------------------------------------------------------------------------------
show_0_236 = input(true, "", inline = "Level0", group=g_fibs)
value_0_236 = input(0.236, "", inline = "Level0", group=g_fibs)
color_0_236 = input(#f44336, "", inline = "Level0", group=g_fibs)
//------------------------------------------------------------------------------
show_0_382 = input(true, "", inline = "Level1", group=g_fibs)
value_0_382 = input(0.382, "", inline = "Level1", group=g_fibs)
color_0_382 = input(#81c784, "", inline = "Level1", group=g_fibs)
//------------------------------------------------------------------------------
show_0_5 = input(true, "", inline = "Level1", group=g_fibs)
value_0_5 = input(0.5, "", inline = "Level1", group=g_fibs)
color_0_5 = input(#4caf50, "", inline = "Level1", group=g_fibs)
//------------------------------------------------------------------------------
show_0_618 = input(true, "", inline = "Level2", group=g_fibs)
value_0_618 = input(0.618, "", inline = "Level2", group=g_fibs)
color_0_618 = input(#009688, "", inline = "Level2", group=g_fibs)
//------------------------------------------------------------------------------
show_0_65 = input(false, "", inline = "Level2", group=g_fibs)
value_0_65 = input(0.65, "", inline = "Level2", group=g_fibs)
color_0_65 = input(#009688, "", inline = "Level2", group=g_fibs)
//------------------------------------------------------------------------------
show_0_786 = input(true, "", inline = "Level3", group=g_fibs)
value_0_786 = input(0.786, "", inline = "Level3", group=g_fibs)
color_0_786 = input(#64b5f6, "", inline = "Level3", group=g_fibs)
//------------------------------------------------------------------------------
show_1 = input(true, "", inline = "Level3", group=g_fibs)
value_1 = input(1, "", inline = "Level3", group=g_fibs)
color_1 = input(#787b86, "", inline = "Level3", group=g_fibs)
//------------------------------------------------------------------------------
show_1_272 = input(false, "", inline = "Level4", group=g_fibs)
value_1_272 = input(1.272, "", inline = "Level4", group=g_fibs)
color_1_272 = input(#81c784, "", inline = "Level4", group=g_fibs)
//------------------------------------------------------------------------------
show_1_414 = input(false, "", inline = "Level4", group=g_fibs)
value_1_414 = input(1.414, "", inline = "Level4", group=g_fibs)
color_1_414 = input(#f44336, "", inline = "Level4", group=g_fibs)
//------------------------------------------------------------------------------
show_1_618 = input(false, "", inline = "Level5", group=g_fibs)
value_1_618 = input(1.618, "", inline = "Level5", group=g_fibs)
color_1_618 = input(#2196f3, "", inline = "Level5", group=g_fibs)
//------------------------------------------------------------------------------
show_1_65 = input(false, "", inline = "Level5", group=g_fibs)
value_1_65 = input(1.65, "", inline = "Level5", group=g_fibs)
color_1_65 = input(#2196f3, "", inline = "Level5", group=g_fibs)
//------------------------------------------------------------------------------
show_2_618 = input(false, "", inline = "Level6", group=g_fibs)
value_2_618 = input(2.618, "", inline = "Level6", group=g_fibs)
color_2_618 = input(#f44336, "", inline = "Level6", group=g_fibs)
//------------------------------------------------------------------------------
show_2_65 = input(false, "", inline = "Level6", group=g_fibs)
value_2_65 = input(2.65, "", inline = "Level6", group=g_fibs)
color_2_65 = input(#f44336, "", inline = "Level6", group=g_fibs)
//------------------------------------------------------------------------------
show_3_618 = input(false, "", inline = "Level7", group=g_fibs)
value_3_618 = input(3.618, "", inline = "Level7", group=g_fibs)
color_3_618 = input(#9c27b0, "", inline = "Level7", group=g_fibs)
//------------------------------------------------------------------------------
show_3_65 = input(false, "", inline = "Level7", group=g_fibs)
value_3_65 = input(3.65, "", inline = "Level7", group=g_fibs)
color_3_65 = input(#9c27b0, "", inline = "Level7", group=g_fibs)
//------------------------------------------------------------------------------
show_4_236 = input(false, "", inline = "Level8", group=g_fibs)
value_4_236 = input(4.236, "", inline = "Level8", group=g_fibs)
color_4_236 = input(#e91e63, "", inline = "Level8", group=g_fibs)
//------------------------------------------------------------------------------
show_4_618 = input(false, "", inline = "Level8", group=g_fibs)
value_4_618 = input(4.618, "", inline = "Level8", group=g_fibs)
color_4_618 = input(#81c784, "", inline = "Level8", group=g_fibs)
//------------------------------------------------------------------------------
show_neg_0_236 = input(false, "", inline = "Level9", group=g_fibs)
value_neg_0_236 = input(-0.236, "", inline = "Level9", group=g_fibs)
color_neg_0_236 = input(#f44336, "", inline = "Level9", group=g_fibs)
//------------------------------------------------------------------------------
show_neg_0_382 = input(false, "", inline = "Level9", group=g_fibs)
value_neg_0_382 = input(-0.382, "", inline = "Level9", group=g_fibs)
color_neg_0_382 = input(#81c784, "", inline = "Level9", group=g_fibs)
//------------------------------------------------------------------------------
show_neg_0_618 = input(false, "", inline = "Level10", group=g_fibs)
value_neg_0_618 = input(-0.618, "", inline = "Level10", group=g_fibs)
color_neg_0_618 = input(#009688, "", inline = "Level10", group=g_fibs)
//------------------------------------------------------------------------------
show_neg_0_65 = input(false, "", inline = "Level10", group=g_fibs)
value_neg_0_65 = input(-0.65, "", inline = "Level10", group=g_fibs)
color_neg_0_65 = input(#009688, "", inline = "Level10", group=g_fibs)
//-----------------------------------------------------------------------------}
//{=============================================================================
// Process each fibonacci level
//==============================================================================
lineId0  = processLevel(show_neg_0_65, value_neg_0_65, color_neg_0_65, line(na))
lineId1  = processLevel(show_neg_0_618, value_neg_0_618, color_neg_0_618, lineId0)
lineId2  = processLevel(show_neg_0_382, value_neg_0_382, color_neg_0_382, lineId1)
lineId3  = processLevel(show_neg_0_236, value_neg_0_236, color_neg_0_236, lineId2)
lineId4  = processLevel(show_0, value_0, color_0, lineId3)
lineId5  = processLevel(show_0_236, value_0_236, color_0_236, lineId4)
lineId6  = processLevel(show_0_382, value_0_382, color_0_382, lineId5)
lineId7  = processLevel(show_0_5, value_0_5, color_0_5, lineId6)
lineId8  = processLevel(show_0_618, value_0_618, color_0_618, lineId7)
lineId9  = processLevel(show_0_65, value_0_65, color_0_65, lineId8)
lineId10 = processLevel(show_0_786, value_0_786, color_0_786, lineId9)
lineId11 = processLevel(show_1, value_1, color_1, lineId10)
lineId12 = processLevel(show_1_272, value_1_272, color_1_272, lineId11)
lineId13 = processLevel(show_1_414, value_1_414, color_1_414, lineId12)
lineId14 = processLevel(show_1_618, value_1_618, color_1_618, lineId13)
lineId15 = processLevel(show_1_65, value_1_65, color_1_65, lineId14)
lineId16 = processLevel(show_2_618, value_2_618, color_2_618, lineId15)
lineId17 = processLevel(show_2_65, value_2_65, color_2_65, lineId16)
lineId18 = processLevel(show_3_618, value_3_618, color_3_618, lineId17)
lineId19 = processLevel(show_3_65, value_3_65, color_3_65, lineId18)
lineId20 = processLevel(show_4_236, value_4_236, color_4_236, lineId19)
lineId21 = processLevel(show_4_618, value_4_618, color_4_618, lineId20)
//-----------------------------------------------------------------------------}
```



## Pivots & Impulsive Moves

[Watch Lesson](https://youtu.be/5I8rLVvcbok)

```python
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © ZenAndTheArtOfTrading / PineScriptMastery.com
// @version=5
indicator("Pivot Points", overlay=true)

// Get user input
var devTooltip          = "Deviation is a multiplier that affects how much the price should deviate from the previous pivot in order for the bar to become a new pivot."
var depthTooltip        = "The minimum number of bars that will be taken into account when analyzing pivots."
threshold_multiplier    = input.float(title="Deviation", defval=2.5, minval=0, tooltip=devTooltip)
depth                   = input.int(title="Depth", defval=10, minval=1, tooltip=depthTooltip)
deleteLastLine          = input.bool(title="Delete Last Line", defval=false)
bgcolorChange           = input.bool(title="Change BgColor", defval=false)

// Calculate deviation threshold for identifying major swings
dev_threshold = ta.atr(10) / close * 100 * threshold_multiplier

// Prepare pivot variables
var line lineLast = na
var int iLast = 0 // Index last
var int iPrev = 0 // Index previous
var float pLast = 0 // Price last
var isHighLast = false // If false then the last pivot was a pivot low

// Custom function for detecting pivot points (and returning price + bar index)
pivots(src, length, isHigh) =>
    l2 = length * 2
    c = nz(src[length])
    ok = true
    for i = 0 to l2
        if isHigh and src[i] > c // If isHigh, validate pivot high
            ok := false
        if not isHigh and src[i] < c // If not isHigh, validate pivot low
            ok := false
    if ok // If pivot is valid, return bar index + high price value
        [bar_index[length], c]
    else // If pivot is invalid, return na
        [int(na), float(na)]

// Get bar index & price high/low for current pivots
[iH, pH] = pivots(high, depth / 2, true)
[iL, pL] = pivots(low, depth / 2, false)

// Custom function for calculating price deviation for validating large moves
calc_dev(base_price, price) => 100 * (price - base_price) / price

// Custom function for detecting pivots that meet our deviation criteria
pivotFound(dev, isHigh, index, price) =>
    if isHighLast == isHigh and not na(lineLast) // Check bull/bear direction of new pivot
        // New pivot in same direction as last (a pivot high), so update line upwards (ie. trend-continuation)
        if isHighLast ? price > pLast : price < pLast // If new pivot is above last pivot, update line
            line.set_xy2(lineLast, index, price)
            [lineLast, isHighLast]
        else
            [line(na), bool(na)] // New pivot is not above last pivot, so don't update the line
    else // Reverse the trend/pivot direction (or create the very first line if lineLast is na)
        if math.abs(dev) > dev_threshold
            // Price move is significant - create a new line between the pivot points
            id = line.new(iLast, pLast, index, price, color=color.gray, width=1, style=line.style_dashed)
            [id, isHigh]
        else
            [line(na), bool(na)]

// If bar index for current pivot high is not NA (ie. we have a new pivot):
if not na(iH)
    dev = calc_dev(pLast, pH) // Calculate the deviation from last pivot
    [id, isHigh] = pivotFound(dev, true, iH, pH) // Pass the current pivot high into pivotFound() for validation & line update
    if not na(id) // If the line has been updated, update price & index values and delete previous line
        if id != lineLast and deleteLastLine
            line.delete(lineLast)
        lineLast := id
        isHighLast := isHigh
        iPrev := iLast
        iLast := iH
        pLast := pH
else 
    if not na(iL) // If bar index for current pivot low is not NA (ie. we have a new pivot):
        dev = calc_dev(pLast, pL) // Calculate the deviation from last pivot
        [id, isHigh] = pivotFound(dev, false, iL, pL) // Pass the current pivot low into pivotFound() for validation & line update
        if not na(id) // If the line has been updated, update price values and delete previous line
            if id != lineLast and deleteLastLine
                line.delete(lineLast)
            lineLast := id
            isHighLast := isHigh
            iPrev := iLast
            iLast := iL
            pLast := pL

// Get starting and ending high/low price of the current pivot line
startIndex = line.get_x1(lineLast)
startPrice = line.get_y1(lineLast)
endIndex   = line.get_x2(lineLast)
endPrice   = line.get_y2(lineLast)

// Draw top & bottom of impulsive move
topLine    = line.new(startIndex, startPrice, endIndex, startPrice, extend=extend.right, color=color.red)
bottomline = line.new(startIndex, endPrice, endIndex, endPrice, extend=extend.right, color=color.green)
line.delete(topLine[1])
line.delete(bottomline[1])
//plot(startPrice, color=color.green)
//plot(endPrice, color=color.red)

// Do what you like with these pivot values :)
// Keep in mind there will be an X bar delay between pivot price values updating based on Depth setting
dist = math.abs(startPrice - endPrice)
plot(dist, color=color.new(color.purple,100))
bullish = endPrice > startPrice
offsetBG = -(depth / 2)
bgcolor(bgcolorChange ? bullish ? color.new(color.green,90) : color.new(color.red,90) : na, offset=offsetBG)
```



## Tracking Ichimoku Base Line

[Watch Lesson](https://youtu.be/yPiys6dJF4M)

```python
// PineScriptMastery.com
// @version=5
indicator(title="Ichimoku Cloud", shorttitle="Ichimoku", overlay=true)

// Get user input
conversionPeriods       = input.int(9, minval=1, title="Conversion Line Length")
basePeriods             = input.int(26, minval=1, title="Base Line Length")
laggingSpan2Periods     = input.int(52, minval=1, title="Leading Span B Length")
displacement            = input.int(26, minval=1, title="Lagging Span")
donchian(len)           => math.avg(ta.lowest(len), ta.highest(len))
conversionLine          = donchian(conversionPeriods)
baseLine                = donchian(basePeriods)
leadLine1               = math.avg(conversionLine, baseLine)
leadLine2               = donchian(laggingSpan2Periods)

// Draw cloud
plot(conversionLine, color=#2962FF, title="Conversion Line", display=display.none)
plot(baseLine, color=#B71C1C, title="Base Line", display=display.none)
plot(close, offset = -displacement + 1, color=#43A047, title="Lagging Span", display=display.none)
p1 = plot(leadLine1, offset = displacement - 1, color=#A5D6A7, title="Leading Span A", display=display.none)
p2 = plot(leadLine2, offset = displacement - 1, color=#EF9A9A, title="Leading Span B", display=display.none)
fill(p1, p2, color = leadLine1 > leadLine2 ? color.rgb(67, 160, 71, 90) : color.rgb(244, 67, 54, 90), display=display.none)

// Track horizontal baseline
var baseLineSaved = baseLine
if baseLine != baseLine[1]
    baseLineSaved := na
else
    baseLineSaved := baseLine

// Draw baseline
plot(baseLineSaved, color=color.purple, style=plot.style_linebr, title="Base Line Saved")

// Track price trading above/below baseline
isPriceAboveBaseLine = close > baseLineSaved
priceTradingAboveBL = isPriceAboveBaseLine and not na(baseLineSaved)
priceTradingBelowBL = not isPriceAboveBaseLine and not na(baseLineSaved)

// Draw condition
bgcolor(priceTradingAboveBL ? color.new(color.green,80) : na)
bgcolor(priceTradingBelowBL ? color.new(color.red,80) : na)

// Track candle pattern tests of baseline (example purposes - needs more conditions to be actually useful!)
candlePatternBull = priceTradingAboveBL and priceTradingAboveBL[1] and low[1] < baseLineSaved and close > baseLineSaved
candlePatternBear = priceTradingBelowBL and priceTradingBelowBL[1] and high[1] > baseLineSaved and close < baseLineSaved
plotshape(candlePatternBull, style=shape.triangleup, color=color.green, location=location.belowbar)
plotshape(candlePatternBear, style=shape.triangledown, color=color.red)
```



## A Simple Pullback Strategy

[Watch Lesson](https://youtu.be/h-erJbnBj6A)

```python
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © ZenAndTheArtOfTrading / www.PineScriptMastery.com
// @version=5
strategy("Simple Pullback Strategy", 
     overlay=true, 
     initial_capital=50000,
     default_qty_type=strategy.percent_of_equity, 
     default_qty_value=100, // 100% of balance invested on each trade
     commission_type=strategy.commission.percent, 
     commission_value=0.2)

// Get user input
i_ma1           = input.int(title="MA 1 Length", defval=120, step=10, group="Strategy Parameters", tooltip="Long-term MA")
i_ma2           = input.int(title="MA 2 Length", defval=10, step=10, group="Strategy Parameters", tooltip="Short-term MA")
i_stopPercent   = input.float(title="Stop Loss Percent", defval=0.10, step=0.1, group="Strategy Parameters", tooltip="Failsafe Stop Loss Percent Decline")
i_lowerClose    = input.bool(title="Exit On Lower Close", defval=false, group="Strategy Parameters", tooltip="Wait for a lower-close before exiting above MA2")
i_startTime     = input.time(title="Start Filter", defval=timestamp("01 Jan 1995 13:30 +0000"), group="Time Filter", tooltip="Start date & time to begin searching for setups")
i_endTime       = input.time(title="End Filter", defval=timestamp("1 Jan 2099 19:30 +0000"), group="Time Filter", tooltip="End date & time to stop searching for setups")

// Get indicator values
ma1 = ta.sma(close, i_ma1)
ma2 = ta.sma(close, i_ma2)

// Check filter(s)
f_dateFilter = time >= i_startTime and time <= i_endTime

// Check buy/sell conditions
var float buyPrice = 0
buyCondition    = close > ma1 and close < ma2 and strategy.position_size == 0 and f_dateFilter
sellCondition   = close > ma2 and strategy.position_size > 0 // (not i_lowerClose or close < low[1])
stopDistance    = strategy.position_size > 0 ? ((buyPrice - close) / close) : na
stopPrice       = strategy.position_size > 0 ? buyPrice - (buyPrice * i_stopPercent) : na
stopCondition   = strategy.position_size > 0 and stopDistance > i_stopPercent

// Enter positions
if buyCondition
    strategy.entry(id="Long", direction=strategy.long)

if buyCondition[1]
    buyPrice := open

// Exit positions
if sellCondition or stopCondition
    strategy.close(id="Long", comment="Exit" + (stopCondition ? "SL=true" : ""))
    buyPrice := na

// Draw pretty colors
plot(buyPrice, color=color.lime, style=plot.style_linebr)
plot(stopPrice, color=color.red, style=plot.style_linebr, offset=-1)
plot(ma1, color=color.blue)
plot(ma2, color=color.orange)
```



## MACD Strategy + 2 Profit Targets

[Watch Lesson](https://www.youtube.com/watch?v=P1Lol05qb5s)

```python
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © ZenAndTheArtOfTrading / www.PineScriptMastery.com
//
// System Rules:
// Indicators: MACD indicator (default values), ATR (14), EMA (200)
// 1. Price must be trading above/below the 200 EMA
// 2. Only 1 bar can close above/below the 200 EMA over the past 5 bars
// 3. We take the FIRST MACD cross and ignore subsequent signals until TP/SL is hit
// 4. Stop Loss = 0.5 ATR above/below the recent swing high/low (7 bars lookback)
// 5. First take profit = 1:1 (25%)
// 6. Second take profit = 2:1 (100%)
// 7. Move stop loss to break-even after 1st target is hit
//
// @version=5
strategy("[2022] MACD Cross Strategy", overlay=true,
     currency="USD",
     calc_on_order_fills=true,
     use_bar_magnifier=true,
     initial_capital=10000,
     default_qty_type=strategy.percent_of_equity,
     default_qty_value=100, // 100% of balance invested on each trade
     commission_type=strategy.commission.cash_per_contract)
     //commission_value=0.005) // Interactive Brokers rate

// Import ZenLibrary
import ZenAndTheArtOfTrading/ZenLibrary/5 as zen

// Get user input
var g_system    = "System Entry Settings"
i_ema_filter    = input.int(title="EMA Filter Length", defval=200, group=g_system)
i_ema_filter2   = input.int(title="EMA Max Bars Above/Below", defval=1, group=g_system)
i_stop_multi    = input.float(title="Stop Loss Multiplier", defval=0.5, step=0.5, group=g_system)
i_stop_lookback = input.int(title="Stop Loss Lookback", defval=7, group=g_system)
var g_risk      = "System Risk Settings"
i_rr1           = input.float(title="Risk:Reward Target 1", defval=1.0, group=g_risk)
i_rr2           = input.float(title="Risk:Reward Target 2", defval=2.0, group=g_risk)
i_target1       = input.float(title="Profit % Target 1", defval=25, group=g_risk)
i_riskPerTrade  = input.float(title="Forex Risk Per Trade %", defval=1.0)
var g_macd      = "MACD Settings"
i_price_src     = input.source(title="Price Source", defval=close, group=g_macd)
i_fast_length   = input.int(title="Fast Length", defval=12, group=g_macd)
i_slow_length   = input.int(title="Slow Length", defval=26, group=g_macd)
i_signal_length = input.int(title="Signal Smoothing", minval=1, maxval=50, defval=9, group=g_macd)
i_sma_source    = input.string(title="Oscillator MA Type", defval="EMA", options=["SMA", "EMA"], group=g_macd)
i_sma_signal    = input.string(title="Signal Line MA Type", defval="EMA", options=["SMA", "EMA"], group=g_macd)

//------------- DETERMINE CURRENCY CONVERSION RATE -------------//
// Check if our account currency is the same as the base or quote currency or neither (for risk $ conversion purposes)
accountSameAsCounterCurrency = strategy.account_currency == syminfo.currency
accountSameAsBaseCurrency = strategy.account_currency == syminfo.basecurrency
accountNeitherCurrency = not accountSameAsCounterCurrency and not accountSameAsBaseCurrency
// Get currency conversion rates if applicable
conversionCurrencyPair = accountSameAsCounterCurrency ? syminfo.tickerid : strategy.account_currency + syminfo.currency
conversionCurrencyRate = accountSameAsBaseCurrency or accountNeitherCurrency ? request.security(conversionCurrencyPair, "D", close, ignore_invalid_symbol=true) : 1.0
// Display the current conversion currency ticker (for debug purposes)
if barstate.islastconfirmedhistory
    table t = table.new(position.top_right, 1, 2, color.black)
    table.cell(t, 0, 0, "Conversion: " + conversionCurrencyPair + " (" + str.tostring(conversionCurrencyRate) + ")", text_color=color.white, text_size=size.small)
    table.cell(t, 0, 1, "Account: $" + str.tostring(zen.truncate(strategy.equity)), text_color=color.white, text_size=size.small)
//------------- END CURRENCY CONVERSION RATE CODE -------------//

// Calculate MACD
[macdLine, signalLine, histLine] = ta.macd(i_price_src, i_fast_length, i_slow_length, i_signal_length)

// Get indicator values
ema = ta.ema(close, i_ema_filter)
atr = ta.atr(14)

// Check for zero-point crosses
crossUp     = ta.crossover(signalLine, macdLine)
crossDown   = ta.crossunder(signalLine, macdLine)

// Check general system filters
tradeFilters = not na(ema) and not na(atr)

// Check trend conditions
upTrend     = close > ema
downTrend   = close < ema

// Check trade conditions
longConditions  = tradeFilters and macdLine[1] < 0 and signalLine[1] < 0
shortConditions = tradeFilters and macdLine[1] > 0 and signalLine[1] > 0

// Confirm long & short setups
longSignal   = longConditions and upTrend and crossDown
shortSignal  = shortConditions and downTrend and crossUp

// Calculate stop loss
longStop    = ta.lowest(low, i_stop_lookback) - (atr * i_stop_multi)
shortStop   = ta.highest(high, i_stop_lookback) + (atr * i_stop_multi)

// Save stops & targets
var float tradeStop = na
var float tradeTarget1 = na
var float tradeTarget2 = na
var float tradeSize = na

// Count bars above/below MA
int barsAboveMA = 0
int barsBelowMA = 0

for i = 1 to 5
    if close[i] < ema[i]
        barsBelowMA += 1
    if close[i] > ema[i]
        barsAboveMA += 1

// Combine signal filters
longTrade   = longSignal  and barsBelowMA <= i_ema_filter2 and strategy.position_size == 0
shortTrade  = shortSignal and barsAboveMA <= i_ema_filter2 and strategy.position_size == 0

// Handle long trade entry (enter position, reset stops & targets)
if longTrade
    if syminfo.type == "forex"
        tradeStop := longStop
        stopDistance = close - tradeStop
        tradeTarget1 := close + (stopDistance * i_rr1)
        tradeTarget2 := close + (stopDistance * i_rr2)
        tradeSize := na
        positionSize = zen.av_getPositionSize(strategy.equity, i_riskPerTrade, zen.toWhole(stopDistance) * 10, conversionCurrencyRate)
        strategy.entry(id="Long", direction=strategy.long, qty=positionSize)
    else
        strategy.entry(id="Long", direction=strategy.long)
        tradeStop := na
        tradeTarget1 := na
        tradeTarget2 := na

// Handle short trade entry (enter position, reset stops & targets)
if shortTrade
    if syminfo.type == "forex"
        tradeStop := shortStop
        stopDistance = tradeStop - close
        tradeTarget1 := close - (stopDistance * i_rr1)
        tradeTarget2 := close - (stopDistance * i_rr2)
        tradeSize := na
        positionSize = zen.av_getPositionSize(strategy.equity, i_riskPerTrade, zen.toWhole(shortStop - close) * 10, conversionCurrencyRate)
        strategy.entry(id="Short", direction=strategy.short, qty=positionSize)
    else
        strategy.entry(id="Short", direction=strategy.short)
        tradeStop := na
        tradeTarget1 := na
        tradeTarget2 := na
    
// Handle forex trade size tracking variable
if syminfo.type == "forex" and strategy.position_size != 0 and na(tradeSize)
    tradeSize := strategy.position_size

// Handle long stops & target calculation
if strategy.position_size > 0 and na(tradeStop) and syminfo.type != "forex"
    tradeStop := longStop
    stopDistance = strategy.position_avg_price - tradeStop
    tradeTarget1 := strategy.position_avg_price + (stopDistance * i_rr1)
    tradeTarget2 := strategy.position_avg_price + (stopDistance * i_rr2)
    tradeSize := strategy.position_size

// Handle short stops & target calculation
if strategy.position_size < 0 and na(tradeStop) and syminfo.type != "forex"
    tradeStop := shortStop
    stopDistance = tradeStop - strategy.position_avg_price
    tradeTarget1 := strategy.position_avg_price - (stopDistance * i_rr1)
    tradeTarget2 := strategy.position_avg_price - (stopDistance * i_rr2)
    tradeSize := strategy.position_size

// Handle trade exits
strategy.exit(id="Long Exit #1",  from_entry="Long",  limit=tradeTarget1, stop=tradeStop, qty_percent=i_target1)
strategy.exit(id="Long Exit #2",  from_entry="Long",  limit=tradeTarget2, stop=tradeStop, qty_percent=100)
strategy.exit(id="Short Exit #1", from_entry="Short", limit=tradeTarget1, stop=tradeStop, qty_percent=i_target1)
strategy.exit(id="Short Exit #2", from_entry="Short", limit=tradeTarget2, stop=tradeStop, qty_percent=100)

// Handle both long & short trade break-even stops (do this AFTER first position has exited above ^)
if strategy.position_size != tradeSize
    tradeStop := strategy.position_avg_price
    tradeTarget1 := na

// Draw conditional data
plot(ema, color=close > ema ? color.green : color.red, linewidth=2, title="EMA")
plotshape(longTrade,  style=shape.triangleup,   color=color.green, location=location.belowbar, title="Long Setup")
plotshape(shortTrade, style=shape.triangledown, color=color.red,   location=location.abovebar, title="Short Setup")

// Draw stops & targets
plot(strategy.position_size != 0 ? tradeStop : na,   color=color.red,   style=plot.style_linebr, title="Stop Loss")
plot(strategy.position_size != 0 ? tradeTarget1 : na, color=color.green, style=plot.style_linebr, title="Profit Target 1")
plot(strategy.position_size != 0 ? tradeTarget2 : na, color=color.green, style=plot.style_linebr, title="Profit Target 2")
```



## Calculating Forex LOT SIZES

[Watch Lesson](https://youtu.be/Dp1C3oHrq7g)

```python
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © ZenAndTheArtOfTrading / www.PineScriptMastery.com
//
// System Rules:
// Indicators: MACD indicator (default values), ATR (14), EMA (200)
// 1. Price must be trading above/below the 200 EMA
// 2. Only 1 bar can close above/below the 200 EMA over the past 5 bars
// 3. We take the FIRST MACD cross and ignore subsequent signals until TP/SL is hit
// 4. Stop Loss = 0.5 ATR above/below the recent swing high/low (7 bars lookback)
// 5. First take profit = 1:1 (25%)
// 6. Second take profit = 2:1 (100%)
// 7. Move stop loss to break-even after 1st target is hit
//
// @version=5
strategy("[2022] MACD Cross Strategy", overlay=true,
     currency="USD",
     calc_on_order_fills=true,
     use_bar_magnifier=true,
     initial_capital=10000,
     default_qty_type=strategy.percent_of_equity,
     default_qty_value=100, // 100% of balance invested on each trade
     commission_type=strategy.commission.cash_per_contract)
     //commission_value=0.005) // Interactive Brokers rate

// Get user input
var g_system    = "System Entry Settings"
i_ema_filter    = input.int(title="EMA Filter Length", defval=200, group=g_system)
i_ema_filter2   = input.int(title="EMA Max Bars Above/Below", defval=1, group=g_system)
i_stop_multi    = input.float(title="Stop Loss Multiplier", defval=0.5, step=0.5, group=g_system)
i_stop_lookback = input.int(title="Stop Loss Lookback", defval=7, group=g_system)
var g_risk      = "System Risk Settings"
i_rr1           = input.float(title="Risk:Reward Target 1", defval=1.0, group=g_risk)
i_rr2           = input.float(title="Risk:Reward Target 2", defval=2.0, group=g_risk)
i_target1       = input.float(title="Profit % Target 1", defval=25, group=g_risk)
i_riskPerTrade  = input.float(title="Forex Risk Per Trade %", defval=1.0)
i_useLots       = input.bool(title="Use Lots Instead Of Units", defval=false)
var g_macd      = "MACD Settings"
i_price_src     = input.source(title="Price Source", defval=close, group=g_macd)
i_fast_length   = input.int(title="Fast Length", defval=12, group=g_macd)
i_slow_length   = input.int(title="Slow Length", defval=26, group=g_macd)
i_signal_length = input.int(title="Signal Smoothing", minval=1, maxval=50, defval=9, group=g_macd)
i_sma_source    = input.string(title="Oscillator MA Type", defval="EMA", options=["SMA", "EMA"], group=g_macd)
i_sma_signal    = input.string(title="Signal Line MA Type", defval="EMA", options=["SMA", "EMA"], group=g_macd)

//------------- DETERMINE CURRENCY CONVERSION RATE ------------- { //
// Import ZenLibrary
import ZenAndTheArtOfTrading/ZenLibrary/5 as zen
// Custom function for converting units into lot sizes
unitsToLots(units) =>
    float lots = units / 100000
    lots := math.round(lots, 2)
    _return = lots * 100000
// Check if our account currency is the same as the base or quote currency or neither (for risk $ conversion purposes)
accountSameAsCounterCurrency = strategy.account_currency == syminfo.currency
accountSameAsBaseCurrency = strategy.account_currency == syminfo.basecurrency
accountNeitherCurrency = not accountSameAsCounterCurrency and not accountSameAsBaseCurrency
// Get currency conversion rates if applicable
conversionCurrencyPair = accountSameAsCounterCurrency ? syminfo.tickerid : strategy.account_currency + syminfo.currency
conversionCurrencyRate = accountSameAsBaseCurrency or accountNeitherCurrency ? request.security(conversionCurrencyPair, "D", close, ignore_invalid_symbol=true) : 1.0
// Display the current conversion currency ticker (for debug purposes)
if barstate.islastconfirmedhistory
    table t = table.new(position.top_right, 1, 2, color.black)
    table.cell(t, 0, 0, "Conversion: " + conversionCurrencyPair + " (" + str.tostring(conversionCurrencyRate) + ")", text_color=color.white, text_size=size.small)
    table.cell(t, 0, 1, "Account: $" + str.tostring(zen.truncate(strategy.equity)), text_color=color.white, text_size=size.small)
//------------- END CURRENCY CONVERSION RATE CODE ------------- }//

// Calculate MACD
[macdLine, signalLine, histLine] = ta.macd(i_price_src, i_fast_length, i_slow_length, i_signal_length)

// Get indicator values
ema = ta.ema(close, i_ema_filter)
atr = ta.atr(14)

// Check for zero-point crosses
crossUp     = ta.crossover(signalLine, macdLine)
crossDown   = ta.crossunder(signalLine, macdLine)

// Check general system filters
tradeFilters = not na(ema) and not na(atr)

// Check trend conditions
upTrend     = close > ema
downTrend   = close < ema

// Check trade conditions
longConditions  = tradeFilters and macdLine[1] < 0 and signalLine[1] < 0
shortConditions = tradeFilters and macdLine[1] > 0 and signalLine[1] > 0

// Confirm long & short setups
longSignal   = longConditions and upTrend and crossDown
shortSignal  = shortConditions and downTrend and crossUp

// Calculate stop loss
longStop    = ta.lowest(low, i_stop_lookback) - (atr * i_stop_multi)
shortStop   = ta.highest(high, i_stop_lookback) + (atr * i_stop_multi)

// Save stops & targets
var float tradeStop = na
var float tradeTarget1 = na
var float tradeTarget2 = na
var float tradeSize = na

// Count bars above/below MA
int barsAboveMA = 0
int barsBelowMA = 0

for i = 1 to 5
    if close[i] < ema[i]
        barsBelowMA += 1
    if close[i] > ema[i]
        barsAboveMA += 1

// Combine signal filters
longTrade   = longSignal  and barsBelowMA <= i_ema_filter2 and strategy.position_size == 0
shortTrade  = shortSignal and barsAboveMA <= i_ema_filter2 and strategy.position_size == 0

// Handle long trade entry (enter position, reset stops & targets)
if longTrade
    if syminfo.type == "forex"
        tradeStop := longStop
        stopDistance = close - tradeStop
        tradeTarget1 := close + (stopDistance * i_rr1)
        tradeTarget2 := close + (stopDistance * i_rr2)
        tradeSize := na
        positionSize = zen.av_getPositionSize(strategy.equity, i_riskPerTrade, zen.toWhole(stopDistance) * 10, conversionCurrencyRate)
        strategy.entry(id="Long", direction=strategy.long, qty=i_useLots ? unitsToLots(positionSize) : positionSize)
    else
        strategy.entry(id="Long", direction=strategy.long)
        tradeStop := na
        tradeTarget1 := na
        tradeTarget2 := na

// Handle short trade entry (enter position, reset stops & targets)
if shortTrade
    if syminfo.type == "forex"
        tradeStop := shortStop
        stopDistance = tradeStop - close
        tradeTarget1 := close - (stopDistance * i_rr1)
        tradeTarget2 := close - (stopDistance * i_rr2)
        tradeSize := na
        positionSize = zen.av_getPositionSize(strategy.equity, i_riskPerTrade, zen.toWhole(shortStop - close) * 10, conversionCurrencyRate)
        strategy.entry(id="Short", direction=strategy.short, qty=i_useLots ? unitsToLots(positionSize) : positionSize)
    else
        strategy.entry(id="Short", direction=strategy.short)
        tradeStop := na
        tradeTarget1 := na
        tradeTarget2 := na
    
// Handle forex trade size tracking variable
if syminfo.type == "forex" and strategy.position_size != 0 and na(tradeSize)
    tradeSize := strategy.position_size

// Handle long stops & target calculation
if strategy.position_size > 0 and na(tradeStop) and syminfo.type != "forex"
    tradeStop := longStop
    stopDistance = strategy.position_avg_price - tradeStop
    tradeTarget1 := strategy.position_avg_price + (stopDistance * i_rr1)
    tradeTarget2 := strategy.position_avg_price + (stopDistance * i_rr2)
    tradeSize := strategy.position_size

// Handle short stops & target calculation
if strategy.position_size < 0 and na(tradeStop) and syminfo.type != "forex"
    tradeStop := shortStop
    stopDistance = tradeStop - strategy.position_avg_price
    tradeTarget1 := strategy.position_avg_price - (stopDistance * i_rr1)
    tradeTarget2 := strategy.position_avg_price - (stopDistance * i_rr2)
    tradeSize := strategy.position_size

// Handle trade exits
float exitPartialUnits = math.abs(strategy.position_size / (100 / i_target1))
float exitPartialLots = unitsToLots(exitPartialUnits)
strategy.exit(id="Long Exit #1",  from_entry="Long",  limit=tradeTarget1, stop=tradeStop, qty=i_useLots ? exitPartialLots : exitPartialUnits)
strategy.exit(id="Long Exit #2",  from_entry="Long",  limit=tradeTarget2, stop=tradeStop, qty_percent=100)
strategy.exit(id="Short Exit #1", from_entry="Short", limit=tradeTarget1, stop=tradeStop, qty=i_useLots ? exitPartialLots : exitPartialUnits)
strategy.exit(id="Short Exit #2", from_entry="Short", limit=tradeTarget2, stop=tradeStop, qty_percent=100)

// Handle both long & short trade break-even stops (do this AFTER first position has exited above ^)
if strategy.position_size != tradeSize
    tradeStop := strategy.position_avg_price
    tradeTarget1 := na

// Draw conditional data
plot(ema, color=close > ema ? color.green : color.red, linewidth=2, title="EMA")
plotshape(longTrade,  style=shape.triangleup,   color=color.green, location=location.belowbar, title="Long Setup")
plotshape(shortTrade, style=shape.triangledown, color=color.red,   location=location.abovebar, title="Short Setup")

// Draw stops & targets
plot(strategy.position_size != 0 ? tradeStop : na,   color=color.red,   style=plot.style_linebr, title="Stop Loss")
plot(strategy.position_size != 0 ? tradeTarget1 : na, color=color.green, style=plot.style_linebr, title="Profit Target 1")
plot(strategy.position_size != 0 ? tradeTarget2 : na, color=color.green, style=plot.style_linebr, title="Profit Target 2")
```



## Mean Reversion Strategy

[Watch Lesson](https://youtu.be/yz_T1gpAw6Y)

```python
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © ZenAndTheArtOfTrading / www.PineScriptMastery.com
// @version=5
strategy("ATR Reversion System", 
     overlay=true, 
     currency=currency.USD,
     initial_capital=100000, 
     default_qty_type=strategy.percent_of_equity, 
     default_qty_value=100, 
     commission_type=strategy.commission.cash_per_order, 
     commission_value=9.95)

// Get user input
i_EmaLongLength     = input.int(title="Long-term EMA", defval=200)
i_EmaShortLength    = input.int(title="Short-term EMA Length", defval=20)
i_ATRPeriod         = input.int(title="ATR Period", defval=5)
i_ATRBand           = input.float(title="ATR Band Distance", defval=1)
i_ATRStretch        = input.float(title="ATR Buy Stretch", defval=1)
i_SellBand          = input.string(title="Sell At Band:", defval="Middle", options=["Top", "Middle", "Bottom"])
i_SellSrc           = input.source(title="Sell Price Source", defval=high)

// Get indicator values
emaLongTerm     = ta.ema(close, i_EmaLongLength)
emaShortTerm    = ta.ema(close, i_EmaShortLength)
atrValue        = ta.atr(i_ATRPeriod)

// Get ATR bands
atrBandTop = emaShortTerm + (atrValue * i_ATRBand)
atrBandBot = emaShortTerm - (atrValue * i_ATRBand)

// Define price stretch
float buyLimitPrice = na

// Check setup conditions = bar close is below ATR band, above long-term EMA
setupCondition = close < atrBandBot and low > emaLongTerm

// Clear any pending limit orders
strategy.cancel_all()

// Enter trades on next bar after setup condition is met
if setupCondition
    buyLimitPrice := low - (atrValue * i_ATRStretch)
    strategy.entry("Long", strategy.long, limit=buyLimitPrice)

// Get sell price
sellPrice = switch i_SellBand
    "Top"       => atrBandTop
    "Middle"    => emaShortTerm
    "Bottom"    => atrBandBot

// Exit trades
if i_SellSrc >= sellPrice or close < emaLongTerm
    strategy.close("Long", comment="Exit trade")

// Draw data to chart
plot(emaLongTerm, "EMA Filter", color.red, 2)
plot(emaShortTerm, "ATR Band Middle", color.blue)
plot(atrBandBot, "ATR Band Bottom", color=color.green)
plot(atrBandTop, "ATR Band Top", color=color.new(color.gray, 75))
plot(setupCondition ? buyLimitPrice : na, "Buy Limit", color.lime, 1, plot.style_cross)
```