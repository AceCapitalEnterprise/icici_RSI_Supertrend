from breeze_connect import BreezeConnect
import urllib
breeze = BreezeConnect(api_key="77%U3I71634^099gN232777%316Q~v4=")
breeze.generate_session(api_secret="9331K77(I8_52JG2K73$5438q95772j@",
                        session_token="47437327")


import numpy as np
import pandas as pd
import pandas_ta as ta
import time
from datetime import date, datetime, timedelta, time as t
import csv, re, time, math

time_1 = t(3, 45)  # 9:17 AM IST -> 3:47 AM UTC
time_2 = t(9, 50)  # 3:01 PM IST -> 9:31 AM UTC

expiry = '2024-09-26'

order = 0
order2 = 0
total_pnl = 0
SL = 0
SL2 = 0


while True:
    now = datetime.now()
    if time_1 < t(datetime.now().time().hour, datetime.now().time().minute) < time_2 :
        
        today = datetime.now()
        yesterday = today - timedelta(days=5)
        yesterday = yesterday.strftime('%Y-%m-%d')
        today = today.strftime('%Y-%m-%d')
        
        if order == 0 and now.second == 0 :
            nifty_spot = breeze.get_quotes(stock_code="NIFTY",
                                                   exchange_code="NSE",
                                                   expiry_date=f"{today}T06:00:00.000Z",
                                                   product_type="cash",
                                                   right="others",
                                                   strike_price="0")
            nifty_spot = nifty_spot['Success']
            nifty_spot = pd.DataFrame(nifty_spot)
            nifty_spot = nifty_spot['ltp'][0]
            
            atm = round(nifty_spot / 50) * 50
            ce_otm = atm + 100
            
            for j in range(0, 5):
                try:
                    ce_option = breeze.get_historical_data_v2(interval="1minute",
                                              from_date= f"{yesterday}T07:00:00.000Z",
                                              to_date= f"{today}T17:00:00.000Z",
                                              stock_code="NIFTY",
                                              exchange_code="NFO",
                                              product_type="options",
                                              expiry_date=f"{expiry}T07:00:00.000Z",
                                              right="call",
                                              strike_price=ce_otm)
                    break
                except:
                    pass
            ce_option = ce_option['Success']
            ce_option = pd.DataFrame(ce_option)
        
            ce_option.ta.rsi(close='close', length=14, append=True)
            ce_option['ATR'] = ta.atr(ce_option['high'], ce_option['low'], ce_option['close'], length=14)
        
            supertrend_result = ta.supertrend(ce_option['high'], ce_option['low'], ce_option['close'], length=10, multiplier=2)
            ce_option['supertrend'] = supertrend_result['SUPERTd_10_2.0']
        
            ce_option['volume_avg'] = ce_option['volume'].rolling(window=5).mean()
            ce_option['volume_check'] = (ce_option['volume'] > 1.5 * ce_option['volume_avg']).astype(int)
        
            last_row = ce_option.iloc[-1]
            atr = last_row['ATR']*1.5


        
            if last_row['RSI_14'] > 65 and last_row['supertrend'] == 1 and last_row['volume_check']==1:
                entry_time = datetime.now().strftime('%H:%M:%S')
                order = 1
                initial_point = 0
                leg = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f'{expiry}T06:00:00.000Z',
                                                        right="call",
                                                        strike_price=ce_otm)
                leg = leg['Success']
                leg = pd.DataFrame(leg)
                buy_price = float(leg['ltp'][0]) 
                SL = buy_price - atr
                print('call entry', atm, 'at', buy_price)
            else:
                print(now, 'no call position')
                
                
                
                
        if order == 1:
            time.sleep(20)
            for j in range(0, 5):
                try:
                    ce_option = breeze.get_historical_data_v2(interval="1minute",
                                              from_date= f"{yesterday}T07:00:00.000Z",
                                              to_date= f"{today}T17:00:00.000Z",
                                              stock_code="NIFTY",
                                              exchange_code="NFO",
                                              product_type="options",
                                              expiry_date=f"{expiry}T07:00:00.000Z",
                                              right="call",
                                              strike_price=ce_otm)
                    break
                except:
                    pass
            ce_option = ce_option['Success']
            ce_option = pd.DataFrame(ce_option)
        
            ce_option.ta.rsi(close='close', length=14, append=True)
            ce_option['ATR'] = ta.atr(ce_option['high'], ce_option['low'], ce_option['close'], length=14)
        
            supertrend_result = ta.supertrend(ce_option['high'], ce_option['low'], ce_option['close'], length=10, multiplier=2)
            ce_option['supertrend'] = supertrend_result['SUPERTd_10_2.0']
        
            ce_option['volume_avg'] = ce_option['volume'].rolling(window=5).mean()
            ce_option['volume_check'] = (ce_option['volume'] > 1.5 * ce_option['volume_avg']).astype(int)
        
            last_row = ce_option.iloc[-1]
            
            
            leg = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f'{expiry}T06:00:00.000Z',
                                                        right="call",
                                                        strike_price=ce_otm)
            leg = leg['Success']
            leg = pd.DataFrame(leg)
            leg = float(leg['ltp'][0])
            
            if leg - buy_price > initial_point :
                initial_point = leg - buy_price
                SL = leg - atr
            
            
            if last_row['RSI_14'] < 65 or last_row['supertrend'] != 1 or leg <= SL :
                order = 0
                exit_time = datetime.now().strftime('%H:%M:%S')
                sell_price = leg
                
                pnl = round(sell_price - buy_price, 2)
                print('call exit, pnl is:', pnl)
                
                
                csv_file = "rsi_supertrend_PT.csv"
                try:
                    with open(csv_file, 'x', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Date', 'Entry Time', 'Strike', 'CE or PE', 'Entry premium','Exit Time', 'Exit premium', 'PnL'])
                except FileExistsError:
                    pass
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([today, entry_time, ce_otm, 'call', buy_price, exit_time, sell_price, pnl])    
                
            else:
                print(now, 'no call exit')
                
        if order2 == 0 and now.second == 0 :
            nifty_spot = breeze.get_quotes(stock_code="NIFTY",
                                                   exchange_code="NSE",
                                                   expiry_date=f"{today}T06:00:00.000Z",
                                                   product_type="cash",
                                                   right="others",
                                                   strike_price="0")
            nifty_spot = nifty_spot['Success']
            nifty_spot = pd.DataFrame(nifty_spot)
            nifty_spot = nifty_spot['ltp'][0]
            
            atm = round(nifty_spot / 50) * 50
            pe_otm = atm - 100
            
            for j in range(0, 5):
                try:
                    pe_option = breeze.get_historical_data_v2(interval="1minute",
                                              from_date= f"{yesterday}T07:00:00.000Z",
                                              to_date= f"{today}T17:00:00.000Z",
                                              stock_code="NIFTY",
                                              exchange_code="NFO",
                                              product_type="options",
                                              expiry_date=f"{expiry}T07:00:00.000Z",
                                              right="put",
                                              strike_price=pe_otm)
                    break
                except:
                    pass
            pe_option = pe_option['Success']
            pe_option = pd.DataFrame(pe_option)
        
            pe_option.ta.rsi(close='close', length=14, append=True)
            pe_option['ATR'] = ta.atr(pe_option['high'], pe_option['low'], pe_option['close'], length=14)
        
            supertrend_result = ta.supertrend(pe_option['high'], pe_option['low'], pe_option['close'], length=10, multiplier=2)
            pe_option['supertrend'] = supertrend_result['SUPERTd_10_2.0']
        
            pe_option['volume_avg'] = pe_option['volume'].rolling(window=5).mean()
            pe_option['volume_check'] = (pe_option['volume'] > 1.5 * pe_option['volume_avg']).astype(int)
        
            last_row = pe_option.iloc[-1]
            atr_pe = last_row['ATR']*1.5


        
            if last_row['RSI_14'] > 65 and last_row['supertrend'] == 1 and last_row['volume_check']==1:
                entry_time = datetime.now().strftime('%H:%M:%S')
                order2 = 1
                initial_point2 = 0
                leg = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f'{expiry}T06:00:00.000Z',
                                                        right="put",
                                                        strike_price=pe_otm)
                leg = leg['Success']
                leg = pd.DataFrame(leg)
                buy_price_pe = float(leg['ltp'][0]) 
                SL2 = buy_price_pe - atr_pe
                
                print('put entry', pe_otm, 'at', buy_price_pe)
            else:
                print(now, 'no put position')
                
                
                
        if order2 == 1:
            time.sleep(20)
            for j in range(0, 5):
                try:
                    pe_option = breeze.get_historical_data_v2(interval="1minute",
                                              from_date= f"{yesterday}T07:00:00.000Z",
                                              to_date= f"{today}T17:00:00.000Z",
                                              stock_code="NIFTY",
                                              exchange_code="NFO",
                                              product_type="options",
                                              expiry_date=f"{expiry}T07:00:00.000Z",
                                              right="put",
                                              strike_price=pe_otm)
                    break
                except:
                    pass
            pe_option = pe_option['Success']
            pe_option = pd.DataFrame(pe_option)
        
            pe_option.ta.rsi(close='close', length=14, append=True)
            pe_option['ATR'] = ta.atr(pe_option['high'], pe_option['low'], pe_option['close'], length=14)
        
            supertrend_result = ta.supertrend(pe_option['high'], pe_option['low'], pe_option['close'], length=10, multiplier=2)
            pe_option['supertrend'] = supertrend_result['SUPERTd_10_2.0']
        
            pe_option['volume_avg'] = pe_option['volume'].rolling(window=5).mean()
            pe_option['volume_check'] = (pe_option['volume'] > 1.5 * pe_option['volume_avg']).astype(int)
        
            last_row = pe_option.iloc[-1]
            
            leg2 = breeze.get_option_chain_quotes(stock_code="NIFTY",
                                                        exchange_code="NFO",
                                                        product_type="options",
                                                        expiry_date=f'{expiry}T06:00:00.000Z',
                                                        right="put",
                                                        strike_price=pe_otm)
            leg2 = leg2['Success']
            leg2 = pd.DataFrame(leg2)
            leg2 = float(leg2['ltp'][0])
            
            if leg2 - buy_price_pe > initial_point2 :
                initial_point2 = leg2 - buy_price_pe
                SL2 = leg2 - atr_pe
            
            
            if last_row['RSI_14'] < 65 or last_row['supertrend'] != 1 or leg2 <= SL2 :
                order2 = 0
                exit_time = datetime.now().strftime('%H:%M:%S')
                sell_price = leg2
                
                pnl = round(sell_price - buy_price_pe, 2)
                print('put exit, pnl is:', pnl)
                
                
                csv_file = "rsi_supertrend_PT.csv"
                try:
                    with open(csv_file, 'x', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['Date', 'Entry Time', 'Strike', 'CE or PE', 'Entry premium','Exit Time', 'Exit premium', 'PnL'])
                except FileExistsError:
                    pass
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([today, entry_time, pe_otm, 'put', buy_price_pe, exit_time, sell_price, pnl])    
                
            else:
                print(now, 'no put exit')
