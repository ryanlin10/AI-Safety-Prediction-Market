# Migration Notes: Bid/Ask Price Storage

## Summary
Fixed the issue where market percentages on the dashboard didn't add up to 100%. The system now stores and uses the bid/ask prices from `markets.json` directly instead of only calculating from bets.

## Changes Made

### Backend Changes

1. **Market Model** (`backend/app/models/market.py`)
   - Added `bid_price` and `ask_price` columns
   - Updated `get_current_odds()` to prioritize stored bid/ask prices over calculated odds from bets
   - For binary markets with stored prices: YES = (bid + ask) / 2, NO = 1 - YES

2. **Market Routes** (`backend/app/routes/markets.py`)
   - Updated `get_markets()` to include `current_odds` in the response
   - Updated `generate_market_from_keyword()` to store bid/ask prices when creating markets

3. **Load Markets Script** (`backend/load_markets_from_json.py`)
   - Updated to store bid/ask prices from JSON when creating markets

4. **Database Migration**
   - Created `migrate_add_prices.py` to add new columns to existing databases
   - Updated `migrations/init_db.sql` for fresh PostgreSQL installations

### Frontend Changes

1. **Dashboard** (`frontend/src/pages/Dashboard.tsx`)
   - Removed separate price fetching queries
   - Now uses `market.current_odds` directly from the markets list API
   - Displays percentages that always add up to 100%

## Migration Steps Completed

1. ✅ Added new columns to database
2. ✅ Reloaded all markets with correct bid/ask prices
3. ✅ Verified percentages add up to 100%

## Next Steps

**To see the changes:**
1. Restart the backend server if it's running
2. Refresh the frontend dashboard

The dashboard will now display the correct percentages from the JSON file, and they will always add up to 100%.

## Example Output

Before: Markets showed 50/50 or incorrect percentages
After:
- Market 1: YES: 77.5%, NO: 22.5% (bid: 0.75, ask: 0.8)
- Market 2: YES: 67.5%, NO: 32.5% (bid: 0.65, ask: 0.7)
- Market 3: YES: 78.5%, NO: 21.5% (bid: 0.75, ask: 0.82)

All percentages now correctly sum to 100% ✅

