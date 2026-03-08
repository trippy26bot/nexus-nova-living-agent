#!/usr/bin/env python3
"""
NOVA PAPER TRADING — Nexus Nova Strategy
Simulates $5 trades using real live market data.
"""

import json
import os
import sys
import time
import argparse
import requests
from datetime import datetime
from typing import Optional

# CONFIG
TRADE_SIZE_USD = 5.00
MAX_POSITIONS = 10
STOP_LOSS_PCT = 0.82
TAKE_PROFIT_1 = 1.30
TAKE_PROFIT_2 = 1.70
TAKE_PROFIT_3 = 2.50
MIN_LIQUIDITY = 50_000
MIN_VOLUME_24H = 10_000
MIN_BUY_RATIO = 0.55

LEDGER_FILE = os.path.expanduser("~/.nova/paper_ledger.json")
LOG_FILE = os.path.expanduser("~/.nova/paper_trades.md")

# COLORS
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def g(s): return f"{GREEN}{s}{RESET}"
def r(s): return f"{RED}{s}{RESET}"
def y(s): return f"{YELLOW}{s}{RESET}"
def c(s): return f"{CYAN}{s}{RESET}"
def b(s): return f"{BOLD}{s}{RESET}"

# LEDGER
def load_ledger():
    try:
        with open(LEDGER_FILE) as f:
            return json.load(f)
    except:
        return {
            "started": datetime.now().isoformat(),
            "balance_usd": 100.00,
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0.0,
            "open": [],
            "closed": [],
        }

def save_ledger(ledger):
    os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

def log_to_md(text):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(text + "\n")

# MARKET DATA
def get_trending_tokens():
    try:
        r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=10)
        return [t for t in r.json() if t.get("chainId") == "solana"]
    except:
        return []

def get_new_pairs():
    try:
        r = requests.get("https://api.dexscreener.com/token-profiles/latest/v1", timeout=10)
        return [t for t in r.json() if t.get("chainId") == "solana"]
    except:
        return []

def get_token_data(addr):
    try:
        r = requests.get(f"https://api.dexscreener.com/token-pairs/v1/solana/{addr}", timeout=8)
        pairs = r.json().get("pairs", [])
        if not pairs:
            return None
        return sorted(pairs, key=lambda x: x.get("volume",{}).get("h24",0), reverse=True)[0]
    except:
        return None

def get_ohlcv(pool, tf="hour", agg=1, lim=50):
    try:
        url = f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{pool}/ohlcv/{tf}"
        r = requests.get(url, params={"aggregate": agg, "limit": lim, "currency": "usd"},
            headers={"Accept": "application/json;version=20230302"}, timeout=10)
        candles = r.json().get("data",{}).get("attributes",{}).get("ohlcv_list",[])
        return sorted(candles, key=lambda x: x[0])
    except:
        return []

# SIGNAL ENGINE
def calc_rsi(closes, p=14):
    if len(closes) < p+1: return 50.0
    deltas = [closes[i]-closes[i-1] for i in range(1,len(closes))]
    gains = [d if d>0 else 0 for d in deltas]
    losses = [-d if d<0 else 0 for d in deltas]
    avg_g = sum(gains[-p:])/p
    avg_l = sum(losses[-p:])/p
    if avg_l==0: return 100.0
    return round(100-(100/(1+avg_g/avg_l)),1)

def calc_ema(data, p):
    if len(data)<p: return data[-1] if data else 0
    k=2/(p+1)
    ema=sum(data[:p])/p
    for x in data[p:]: ema=x*k+ema*(1-k)
    return ema

def detect_trend(closes):
    if len(closes)<21: return "UNKNOWN"
    e9=calc_ema(closes,9)
    e21=calc_ema(closes,21)
    price=closes[-1]
    if price>e9>e21: return "UPTREND"
    elif price<e9<e21: return "DOWNTREND"
    elif price>e21 and e9<e21: return "PULLBACK"
    return "RANGING"

def detect_pattern(candles):
    if len(candles)<3: return "NONE"
    c=candles[-1]; p=candles[-2]
    o,h,lo,cl = c[1],c[2],c[3],c[4]
    po,ph,plo,pcl = p[1],p[2],p[3],p[4]
    body=abs(cl-o); p_body=abs(pcl-po)
    lower=min(o,cl)-lo; upper=h-max(o,cl)
    rng=h-lo if h!=lo else 0.000001
    
    if cl>o and lower>=2*body and upper<=0.3*body and pcl<po: return "HAMMER"
    if cl>o and pcl<po and o<pcl and cl>po: return "BULLISH_ENGULF"
    if cl>o and pcl>po and pcl>po and cl>pcl: return "THREE_SOLDIERS"
    if upper>=2*body and lower<=0.1*rng and pcl>po: return "SHOOTING_STAR"
    if body<0.05*rng and pcl>po: return "DOJI_TOP"
    return "NONE"

BULLISH={"HAMMER","BULLISH_ENGULF","THREE_SOLDIERS"}
BEARISH={"SHOOTING_STAR","DOJI_TOP"}

def score_token(pair, candles):
    signals={}; score=0
    txns=pair.get("txns",{})
    buys=txns.get("h1",{}).get("buys",0)
    sells=txns.get("h1",{}).get("sells",0)
    total=buys+sells
    ratio=buys/total if total>0 else 0.5
    vol_h1=pair.get("volume",{}).get("h1",0) or 0
    vol_24h=pair.get("volume",{}).get("h24",0) or 0
    vol_avg=vol_24h/24 if vol_24h>0 else 0
    surge=vol_h1/vol_avg if vol_avg>0 else 1
    
    if ratio>=0.60 and surge>=1.2:
        signals["on_chain"]=f"BULLISH (ratio {ratio:.0%})"; score+=1
    elif ratio<0.40:
        signals["on_chain"]=f"BEARISH"; score-=1
    else:
        signals["on_chain"]=f"NEUTRAL"
    
    if len(candles)>=15:
        closes=[c[4] for c in candles]
        rsi=calc_rsi(closes)
        trend=detect_trend(closes)
        pattern=detect_pattern(candles)
        ta=0
        if rsi<35: ta+=2
        elif rsi<50: ta+=1
        elif rsi>75: ta-=2
        elif rsi>65: ta-=1
        if trend=="UPTREND": ta+=1
        elif trend=="PULLBACK": ta+=1
        elif trend=="DOWNTREND": ta-=1
        if pattern in BULLISH: ta+=1
        elif pattern in BEARISH: ta-=1
        if ta>=2:
            signals["technical"]=f"BULLISH (RSI {rsi})"; score+=1
        elif ta<=-1:
            signals["technical"]=f"BEARISH"; score-=1
        else:
            signals["technical"]=f"NEUTRAL"
    else:
        signals["technical"]="INSUFFICIENT"
    
    pc5=float(pair.get("priceChange",{}).get("m5","0") or 0)
    pc1=float(pair.get("priceChange",{}).get("h1","0") or 0)
    pc6=float(pair.get("priceChange",{}).get("h6","0") or 0)
    pc24=float(pair.get("priceChange",{}).get("h24","0") or 0)
    pos=sum([pc5>0,pc1>0,pc6>0,pc24>0])
    if pos>=3 and pc1>2:
        signals["sentiment"]="BULLISH"; score+=1
    elif pos<=1 and pc1<-5:
        signals["sentiment"]="BEARISH"; score-=1
    else:
        signals["sentiment"]="NEUTRAL"
    return {"score":score,"signals":signals}

# TRADE LOGIC
def check_positions(ledger):
    if not ledger["open"]: return ledger
    still=[]
    for pos in ledger["open"]:
        data=get_token_data(pos["token_address"])
        if not data: still.append(pos); continue
        curr=float(data.get("priceUsd") or data.get("priceNative") or 0)
        if curr==0: still.append(pos); continue
        entry=pos["entry_price"]
        pnl=((curr/entry)-1)*100
        pos["current_price"]=curr
        pos["pnl_pct"]=round(pnl,2)
        closed=False
        for tp in pos["take_profits"]:
            if not tp["hit"] and curr>=tp["target_price"]:
                tp["hit"]=True
                sell_pct=pos["remaining_pct"]*tp["sell_pct"]
                realized=sell_pct*TRADE_SIZE_USD*(curr/entry)
                cost=sell_pct*TRADE_SIZE_USD
                profit=realized-cost
                pos["remaining_pct"]-=sell_pct
                pos["realized_pnl"]+=profit
                ledger["balance_usd"]+=realized
                print(g(f" TP{tp['level']} HIT: {pos['name']} @ ${curr:.6f}"))
                if tp["level"]==1:
                    pos["stop_price"]=entry*1.01
                if pos["remaining_pct"]<=0.05:
                    closed=True
        if not closed and curr<=pos["stop_price"]:
            loss=-(pos["remaining_pct"]*TRADE_SIZE_USD*(1-curr/entry))
            pos["realized_pnl"]+=loss
            ledger["balance_usd"]+=pos["remaining_pct"]*TRADE_SIZE_USD*(curr/entry)
            print(r(f" STOP HIT: {pos['name']} @ ${curr:.6f}"))
            closed=True
        if closed:
            pos["exit_price"]=curr
            pos["exit_time"]=datetime.now().isoformat()
            pos["final_pnl"]=pos["realized_pnl"]
            ledger["closed"].append(pos)
            ledger["total_trades"]+=1
            ledger["total_pnl"]+=pos["final_pnl"]
            if pos["final_pnl"]>=0: ledger["wins"]+=1
            else: ledger["losses"]+=1
        else:
            still.append(pos)
    ledger["open"]=still
    return ledger

def enter_trade(ledger, addr, name, price, score, signals):
    tp1=price*TAKE_PROFIT_1
    tp2=price*TAKE_PROFIT_2
    tp3=price*TAKE_PROFIT_3
    stop=price*STOP_LOSS_PCT
    pos={
        "id":f"PT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "token_address":addr,
        "name":name,
        "entry_price":price,
        "entry_time":datetime.now().isoformat(),
        "stop_price":stop,
        "current_price":price,
        "pnl_pct":0.0,
        "realized_pnl":0.0,
        "remaining_pct":1.0,
        "score":score,
        "signals":signals,
        "take_profits":[
            {"level":1,"target_price":tp1,"sell_pct":0.50,"hit":False},
            {"level":2,"target_price":tp2,"sell_pct":0.60,"hit":False},
            {"level":3,"target_price":tp3,"sell_pct":1.00,"hit":False},
        ]
    }
    ledger["open"].append(pos)
    ledger["balance_usd"]-=TRADE_SIZE_USD
    print(g(f" ENTERED: {name}"))
    print(f" Entry: ${price:.6f} | Stop: ${stop:.6f}")
    return ledger

def run_scan(ledger):
    print(f"\n{b(c('=== NEXUS NOVA SCAN ==='))}")
    print(f" {datetime.now():%Y-%m-%d %H:%M}")
    print(f" Balance: ${ledger['balance_usd']:.2f} | Open: {len(ledger['open'])}")
    
    ledger=check_positions(ledger)
    if len(ledger["open"])>=MAX_POSITIONS:
        print(y(" Max positions. Monitoring only."))
        save_ledger(ledger)
        return ledger
    if ledger["balance_usd"]<TRADE_SIZE_USD:
        print(r(" Insufficient balance."))
        save_ledger(ledger)
        return ledger
    
    holding={p["token_address"] for p in ledger["open"]}
    candidates=[]
    for t in get_trending_tokens()[:30]+get_new_pairs()[:20]:
        a=t.get("tokenAddress") or t.get("address")
        if a and a not in holding:
            candidates.append(a)
    candidates=list(dict.fromkeys(candidates))[:40]
    print(f" Evaluating {len(candidates)} candidates...")
    
    entered=0
    for addr in candidates:
        if entered>=(MAX_POSITIONS-len(ledger["open"])): break
        if ledger["balance_usd"]<TRADE_SIZE_USD: break
        
        data=get_token_data(addr)
        if not data: continue
        name=data.get("baseToken",{}).get("symbol",addr[:8])
        liq=float(data.get("liquidity",{}).get("usd") or 0)
        vol24=float(data.get("volume",{}).get("h24") or 0)
        price=float(data.get("priceUsd") or data.get("priceNative") or 0)
        age_h=(time.time()*1000-(data.get("pairCreatedAt") or 0))/3600000
        
        if liq<MIN_LIQUIDITY: continue
        if vol24<MIN_VOLUME_24H: continue
        if price<=0: continue
        if age_h<1: continue
        
        pool=data.get("pairAddress","")
        candles=get_ohlcv(pool,"hour",1,50) if pool else []
        result=score_token(data,candles)
        score=result["score"]
        sigs=result["signals"]
        
        bearish=any("BEARISH" in v for v in sigs.values())
        if bearish or score<2: continue
        
        print(f"\n {y('CANDIDATE:')} {name} | Score: {score}")
        ledger=enter_trade(ledger,addr,name,price,score,sigs)
        entered+=1
        time.sleep(0.5)
    
    if entered==0:
        print(y(" No trades this cycle."))
    else:
        print(g(f"\n {entered} trade(s) entered."))
    save_ledger(ledger)
    return ledger

def report(ledger):
    wr=(ledger["wins"]/ledger["total_trades"]*100) if ledger["total_trades"]>0 else 0
    pnl=ledger["total_pnl"]
    print(f"\n{b(c('=== NOVA REPORT ==='))}")
    print(f" Started: {ledger['started'][:10]}")
    print(f" Balance: ${ledger['balance_usd']:.2f}")
    print(f" Trades: {ledger['total_trades']} | Wins: {g(str(ledger['wins']))} | Losses: {r(str(ledger['losses']))}")
    print(f" Win Rate: {wr:.1f}%")
    print(f" P&L: {(g if pnl>=0 else r)(f'${pnl:+.2f}')}")
    print(f" Open: {len(ledger['open'])}")
    if ledger["open"]:
        for p in ledger["open"]:
            pct=p.get("pnl_pct",0)
            print(f" {'🟢' if pct>=0 else '🔴'} {p['name']:<12} {pct:+.1f}%")

# MAIN
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--watch",action="store_true")
    a.add_argument("--report",action="store_true")
    a.add_argument("--reset",action="store_true")
    args=a.parse_args()
    
    if args.reset:
        for f in [LEDGER_FILE,LOG_FILE]:
            if os.path.exists(f): os.remove(f)
        print(g("Reset."))
        return
    
    ledger=load_ledger()
    if args.report:
        report(ledger); return
    if args.watch:
        print(b(c("\n CONTINUOUS MODE - Ctrl+C to stop\n")))
        try:
            while True:
                ledger=run_scan(ledger)
                print(y(" 30 sec...\n"))
                time.sleep(1)
        except KeyboardInterrupt:
            report(ledger)
    else:
        ledger=run_scan(ledger)
        report(ledger)

if __name__=="__main__": main()
