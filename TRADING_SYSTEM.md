# Interactive Trading System - Implementation Guide

## 🎯 Overview

You now have a fully functional prediction market trading system with:
- **Automated Market Maker (AMM)** pricing
- **Interactive buy/sell buttons** showing real-time prices
- **Transaction recording** in the database
- **Dynamic price charts** showing market history
- **Real-time price updates**

## 🏗️ Architecture

### Backend Components

#### 1. **Market Maker Algorithm** (`backend/app/services/market_maker.py`)
- **Algorithm**: Constant Product Market Maker (CPMM)
- **Formula**: Similar to Uniswap's x * y = k
- **Features**:
  - Dynamic pricing based on supply/demand
  - Automatic slippage calculation
  - Market depth analysis
  - Initial liquidity: $1,000 per market

#### 2. **New API Endpoints** (`backend/app/routes/bets.py`)

**GET `/api/markets/<id>/prices`**
- Returns current buy/sell prices for all outcomes
- Includes liquidity information
- Auto-refreshes every 5 seconds

**POST `/api/markets/<id>/buy`**
```json
{
  "outcome": "Yes",
  "amount": 10
}
```
- Purchases shares at current market price
- Automatically records transaction
- Returns updated prices

**GET `/api/markets/<id>/price-history`**
- Returns complete price history
- Shows how prices changed over time
- Used for charting

#### 3. **Transaction Recording** (`backend/app/models/bet.py`)
- Every trade is recorded as a Bet
- Includes:
  - Outcome purchased
  - Amount of shares
  - Price paid (stake)
  - Timestamp
  - Rationale/notes

### Frontend Components

#### 1. **Trading Interface** (`frontend/src/pages/MarketDetail.tsx`)
- **Buy Buttons**: Interactive purchase buttons for each outcome
- **Price Display**: Shows price per share in dollars
- **Amount Selector**: Adjust number of shares to buy
- **Total Cost**: Real-time calculation of purchase cost
- **Liquidity Display**: Shows available liquidity

#### 2. **Price Chart**
- **Library**: Recharts
- **Features**:
  - Line chart for each outcome
  - Time-series price history
  - Interactive tooltips
  - Automatic color coding

#### 3. **Real-time Updates**
- Prices refresh every 5 seconds
- Chart updates after each trade
- Optimistic UI updates

## 💰 Pricing Mechanism

### How It Works

1. **Initial State**:
   - Each outcome starts with equal liquidity: $1,000 / n_outcomes
   - Initial price = 1/n (e.g., 50% for Yes/No market)

2. **After Buying**:
   - Buyer adds stake to their outcome's pool
   - Price increases for that outcome
   - Other outcomes' prices decrease proportionally

3. **Price Formula**:
   ```
   Price(outcome) = Pool(outcome) / Total_All_Pools
   ```

4. **Buy Cost Formula**:
   ```
   Cost = (k / new_outcome_pool - current_other_pools) * 1.005
   where k = outcome_pool * other_pools_total (constant product)
   ```

### Example

**Market**: "Will GPT-5 be released in 2026?"
- **Outcomes**: Yes, No
- **Initial**: Yes = 50%, No = 50%
- **Initial Liquidity**: $500 each

**After buying 10 YES shares for $52.50**:
- YES pool: $552.50
- NO pool: $500
- New prices: YES = 52.5%, NO = 47.5%

## 📊 Features

### 1. Dynamic Pricing
- Prices move based on supply/demand
- More trades = more price movement
- Includes 0.5% fee

### 2. Market Depth
- Shows liquidity available
- Prevents manipulation
- Transparent pricing

### 3. Price Charts
- Historical price tracking
- Multiple outcomes on one chart
- Hover for details

### 4. Transaction Book
- All trades recorded in `bets` table
- Includes timestamp, outcome, amount
- Can track individual user portfolios

## 🎮 How to Use

### For Users

1. **Navigate to a Market**
   - Go to http://localhost:3000
   - Click on any market

2. **View Prices**
   - See current probability percentages
   - Check buy price per share
   - Review liquidity

3. **Buy Shares**
   - Select number of shares (1-100)
   - See total cost calculation
   - Click "Buy [Outcome]"
   - Transaction recorded instantly

4. **Watch Price Changes**
   - Price chart updates automatically
   - See your impact on the market
   - Track price trends

### For Developers

**Testing the API**:
```bash
# Get current prices
curl http://localhost:5001/api/markets/1/prices

# Buy 10 YES shares
curl -X POST http://localhost:5001/api/markets/1/buy \
  -H "Content-Type: application/json" \
  -d '{"outcome": "Yes", "amount": 10}'

# Get price history
curl http://localhost:5001/api/markets/1/price-history
```

**Database Queries**:
```python
# Get all transactions for a market
from app.models import Bet
bets = Bet.query.filter_by(market_id=1).all()

# Calculate total volume
total_volume = sum(bet.stake for bet in bets)
```

## 🔧 Configuration

### Adjust Initial Liquidity
```python
# backend/app/services/market_maker.py
market_maker = MarketMaker(initial_liquidity=2000.0)  # Default: 1000.0
```

### Change Fee Rate
```python
# In calculate_buy_price()
cost_with_fee = cost * 1.01  # Change from 1.005 (0.5%) to 1.01 (1%)
```

### Adjust Auto-Refresh Rate
```typescript
// frontend/src/pages/MarketDetail.tsx
refetchInterval: 10000,  // Change from 5000 (5s) to 10000 (10s)
```

## 📈 Future Enhancements

### Short-term
- [ ] Sell functionality (currently buy-only)
- [ ] User portfolio tracking
- [ ] Order history per user
- [ ] Market statistics (volume, trades count)

### Medium-term
- [ ] Limit orders
- [ ] Order book visualization
- [ ] Market depth chart
- [ ] User authentication
- [ ] Wallet balance system

### Long-term
- [ ] Multiple market makers (competition)
- [ ] Arbitrage detection
- [ ] Flash loan protection
- [ ] Advanced charting (candlesticks, volume)
- [ ] Mobile app

## 🐛 Troubleshooting

### Prices Not Updating
- Check browser console for errors
- Verify backend is running: `curl http://localhost:5001/health`
- Check network tab in DevTools

### Buy Button Not Working
- Verify market status is "active"
- Check console for error messages
- Ensure amount is between 1-100

### Chart Not Showing
- Need at least 2 trades for chart to appear
- Check if price history API returns data
- Verify Recharts is installed: `npm list recharts`

### Backend Errors
```bash
# View logs
tail -f backend/backend.log

# Restart backend
./stop.sh && ./start.sh
```

## 📚 API Reference

### Market Prices
```
GET /api/markets/{market_id}/prices

Response:
{
  "market_id": 1,
  "prices": {
    "Yes": {
      "current_price": 0.52,
      "buy_price": 1.0527,
      "sell_price": 0.9973,
      "liquidity": 552.50
    },
    "No": {
      "current_price": 0.48,
      "buy_price": 0.9973,
      "sell_price": 1.0027,
      "liquidity": 500.00
    }
  },
  "total_volume": 52.50
}
```

### Buy Shares
```
POST /api/markets/{market_id}/buy
Content-Type: application/json

Request:
{
  "outcome": "Yes",
  "amount": 10,
  "user_id": 1  # Optional
}

Response:
{
  "success": true,
  "bet": {
    "id": 123,
    "market_id": 1,
    "outcome": "Yes",
    "stake": 52.50,
    "shares": 10,
    "created_at": "2025-10-25T13:30:00"
  },
  "cost": 52.50,
  "shares": 10,
  "avg_price": 5.25,
  "new_prices": {
    "Yes": 0.525,
    "No": 0.475
  }
}
```

### Price History
```
GET /api/markets/{market_id}/price-history

Response:
{
  "market_id": 1,
  "history": [
    {
      "timestamp": "2025-10-25T13:00:00",
      "prices": {"Yes": 0.50, "No": 0.50},
      "volume": 0
    },
    {
      "timestamp": "2025-10-25T13:30:00",
      "prices": {"Yes": 0.525, "No": 0.475},
      "volume": 52.50,
      "bet_id": 123,
      "outcome": "Yes"
    }
  ]
}
```

## ✅ What Was Implemented

✅ Automated Market Maker pricing algorithm
✅ Real-time price calculation
✅ Interactive buy buttons with custom amounts
✅ Transaction recording in database
✅ Price history tracking
✅ Dynamic price chart with Recharts
✅ Auto-refreshing prices (5 second intervals)
✅ Liquidity display
✅ Total cost calculator
✅ Beautiful UI with animations
✅ Error handling and validation
✅ API documentation

## 🎉 Try It Now!

1. Open http://localhost:3000
2. Click on any market
3. Scroll to "Trade Shares"
4. See the price chart and trading interface
5. Adjust shares and click "Buy [Outcome]"
6. Watch prices and chart update!

---

**Built with**: Flask, React, TypeScript, Recharts, SQLite
**Algorithm**: Constant Product Market Maker (CPMM)
**Status**: Fully Functional ✅

