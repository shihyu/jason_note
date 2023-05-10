## High Frequency Trading Framework with Machine/Deep Learning

In this project, we provide a framework/pipeline for high frequency trading using machine/deep learning techniques. More advanced feature engineering (with depth trade and quote data) and models (such as pre-trained models) can be applied in this framework.

### Target
- Extract trading signals from level-II orderbook data
- Predict orderbook dynamics using machine learning and deep learning techniques

### Data
The SGX FTSE CHINA A50 INDEX Futures (新加坡交易所FTSE中國A50指數期貨) tick depth data are used.

### Strategy Pipline
<img src="./Graph/pipline.png" width="650">
  
### Orderbook Signals
We use limit orderbook data to develop trading signals, including **Depth Ratio**, **Rise Ratio**, and **Orderbook Imbalance (OBI)**.

<img src="./Graph/depth.png" width="650"> 
  
### Price Series

<img src="./images/best_bid_ask.png" width="750">

### Feature Engineering & HFT Factors Design
- Simple average depth ratio and OBI:

<img src="./images/depth_0915_1130.png" width="750">
<img src="./images/depth_1300_1600.png" width="750">

- Weighted average depth ratio, OBI, and rise ratio:

<img src="./images/rise_1300_1600_w.png" width="750">
 
 ### Model Fitting
- Basic Models:
  *  RandomForestClassifier
  *  ExtraTreesClassifier
  *  AdaBoostClassifier
  *  GradientBoostingClassifier
  *  Support Vector Machines
  *  Other classifiers: Softmax, KNN, MLP, LSTM, etc.

- Hyperparameters:
  * Training window: 30min
  * Test window: 10sec
  * Prediction label: 15min forward
   
### Performance Metrics
- Prediction accuracy:

<img src="./images/prediction.png" width="750">

- Prediction Accuracy Series:
<img src="./images/single_day_accuracy.png" width="800">

- Cross Validation Mean Accuracy:

<img src="./images/CV_result.png" width="800">

- Best Model:

<img src="./images/best_CV_result.png" width="800">

   
### PnL Visualization
<img src="./images/best_CV_result_all.png" width="800">
    
### Improvements

**Feature Engineering**

Other potentially useful signals:
- volume imbalance signal
- trade imbalance signal
- technical indicators of bid and ask series (RSI, MACD...)
- WAP/WPR, weighted average price, VWAP, TWAP
- .....

Signal generating techniques:
- consider different weights on different level of orderbook data for a particular signal
- consider moving average with period n (hyperparameter)
- consider weighted average of signals, such as weighted average of trade imbalance and orderbook imbalance
- Lasso regression, genetic programming
- .....
 
**Models**

This project only provides a baseline. More advanced models are welcomed:
- CNN
- GRU/LSTM
- XGBoost, AdaBoost, GBDT, LightGBM
- Attention, Auto-encoder
- TabNet
- Pre-trained models
- .....

**Performance Metrics**

The performance metrics are subject to amendment, including the PnL calculation, commission fee consideration, etc.

