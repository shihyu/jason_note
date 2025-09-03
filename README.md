# Jason's Trading & Quantitative Analysis Platform

A comprehensive financial trading ecosystem for Taiwan stock market, futures, options, and cryptocurrency trading.

## 🚀 Features

- **Multi-Asset Trading**: Stocks, futures, options, and cryptocurrencies
- **Multiple Broker Integration**: SinoPac (Shioaji), Fubon Securities
- **Crypto Exchange Support**: BitoPro for Taiwan market
- **Advanced Strategies**: Momentum, mean reversion, market making, arbitrage
- **Backtesting Framework**: Historical analysis with walk-forward optimization
- **Real-time Data**: WebSocket connections for live market data
- **Risk Management**: Stop-loss, position sizing, MAE/MFE analysis
- **Automated Execution**: Paper trading and live trading modes
- **Notifications**: Telegram bot and LINE Notify integration

## 📁 Project Structure

```
├── Jlab/                    # Main trading research laboratory
│   ├── finlab/             # FinLab quantitative strategies
│   ├── shioaji/            # SinoPac broker integration
│   ├── fubon/              # Fubon Securities platform
│   ├── market-maker/       # Crypto market making system
│   ├── Options/            # Taiwan Index Options trading
│   ├── Future/             # Futures trading (TXF, stock futures)
│   ├── Strategy/           # Trading strategy implementations
│   └── Tools/              # Utility scripts and analysis
├── atm_strategy/           # Automated Trading Module
├── bitopro/               # BitoPro exchange integration
├── fubon-neo-api/         # Fubon Neo API tools
└── Stock_News_Sentiment/  # News sentiment analysis
```

## 🛠 Installation

### Prerequisites

- Python 3.8+
- Redis (for data caching)
- Trading account with supported brokers

### Setup

1. Clone the repository:
```bash
git clone https://github.com/shihyu/jason_note.git
cd jason_note
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API credentials:
```bash
cp config.example.ini config.ini
# Edit config.ini with your API keys
```

4. Install broker certificates:
```bash
# Place your .pfx certificate files in the appropriate directories
# Shioaji: Jlab/shioaji/
# Fubon: Jlab/fubon/
```

## 🎯 Key Strategies

### 藏獒策略 (Tibetan Mastiff)
High momentum stock screening strategy with strict entry/exit rules.
```bash
cd Jlab/finlab
python backtest_戰獒.py
```

### 威廉當沖 (William Day Trading)
Intraday trading system with technical indicators.
```bash
cd atm_strategy/當沖
python 威廉當沖.py
```

### Market Making
Grid trading and liquidity provision for cryptocurrency.
```bash
cd Jlab/market-maker
python main.py
```

## 📊 Backtesting

Run backtests with historical data:
```bash
# Example: Backtest a strategy
python backtest_strategy.py --strategy=momentum --start=2023-01-01 --end=2023-12-31
```

## 🤖 Live Trading

### Paper Trading Mode
```bash
python main.py --paper --strategy=your_strategy
```

### Live Trading (Use with caution!)
```bash
python main.py --live --strategy=your_strategy --capital=100000
```

## 📈 Performance Metrics

The system tracks:
- Sharpe Ratio
- Maximum Drawdown (MDD)
- Win Rate
- Profit Factor
- Risk-Reward Ratio
- MAE/MFE Analysis

## 🔔 Notifications

### Telegram Bot Setup
1. Create bot with BotFather
2. Add token to config.ini
3. Enable notifications in strategy

### LINE Notify Setup
1. Get token from LINE Notify
2. Add to config.ini
3. Configure alert thresholds

## 🧪 Testing

Run tests:
```bash
# Unit tests
pytest tests/

# Integration tests
python test_shioaji_connection.py
python test_market_maker.py
```

## 🔒 Security

- Never commit API keys or certificates
- Use environment variables for sensitive data
- Enable 2FA on broker accounts
- Monitor positions and orders regularly
- Set maximum position limits
- Use paper trading for testing

## 📝 Development Workflow

1. **Research**: Develop ideas in Jupyter notebooks
2. **Implement**: Code strategy with unit tests
3. **Backtest**: Validate with historical data
4. **Paper Trade**: Test in simulated environment
5. **Deploy**: Go live with risk controls
6. **Monitor**: Track performance and iterate

## ⚠️ Risk Disclaimer

**IMPORTANT**: Trading involves substantial risk of loss. This software is for educational purposes. Always:
- Start with paper trading
- Use proper risk management
- Never trade with money you cannot afford to lose
- Understand the strategies before deployment
- Monitor automated systems continuously

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📖 Documentation

- [Strategy Documentation](docs/strategies.md)
- [API Reference](docs/api.md)
- [Backtesting Guide](docs/backtesting.md)
- [Risk Management](docs/risk.md)

## 🛠 Troubleshooting

### Common Issues

**Certificate Error**: Ensure .pfx file is in correct location
**API Rate Limit**: Implement exponential backoff
**Connection Timeout**: Check network and firewall settings
**Data Quality**: Validate tick data before aggregation

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review example scripts in each module

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FinLab for quantitative analysis tools
- Shioaji API for broker integration
- All contributors and testers

---

**Remember**: Past performance does not guarantee future results. Always do your own research and trade responsibly.