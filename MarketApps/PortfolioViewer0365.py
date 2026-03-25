from tkinter import Tk, Frame, Label, ttk, Button, Entry, StringVar, Toplevel
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import requests
import json
import os
from urllib.parse import quote
from dataclasses import dataclass
from typing import Dict, Optional


# ─────────────────────────────────────────────
#  Yahoo Finance crumb-based data fetcher
# ─────────────────────────────────────────────
class YahooCrumbFetcher:
    """Fetches OHLCV history and market cap from Yahoo Finance.
    Single request per call — no retries, no crumb needed."""

    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0.0.0 Safari/537.36'
        ),
        'Accept':          'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer':         'https://finance.yahoo.com/',
    }
    PERIOD_DAYS = {'1mo': 32, '3mo': 95, '6mo': 185}

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def fetch_history(self, ticker: str, period: str, interval: str):
        """Returns (df, info) — info extracted from chart meta, no extra request needed."""
        now   = datetime.now()
        start = now - timedelta(days=self.PERIOD_DAYS.get(period, 35))
        url   = f'https://query2.finance.yahoo.com/v8/finance/chart/{quote(ticker, safe="")}'
        r     = self.session.get(url, params={
            'period1':  int(start.timestamp()),
            'period2':  int(now.timestamp()),
            'interval': interval,
        }, timeout=15)
        print(f"[chart] {ticker} → HTTP {r.status_code}")
        r.raise_for_status()

        chart = r.json().get('chart', {})
        if chart.get('error'):
            raise RuntimeError(f"Yahoo error for {ticker}: {chart['error']}")
        result = (chart.get('result') or [None])[0]
        if result is None:
            raise RuntimeError(f"No data returned for {ticker!r} — check the symbol.")

        quotes = result['indicators']['quote'][0]
        df = pd.DataFrame(
            {'Close': quotes['close'], 'Volume': quotes['volume']},
            index=pd.to_datetime(result['timestamp'], unit='s', utc=True),
        )
        df.index = df.index.tz_convert('America/New_York').tz_localize(None)
        df = df.dropna(subset=['Close'])
        if df.empty:
            raise RuntimeError(f"All close prices were null for {ticker!r}.")

        # Avg weekly dollar turnover
        weekly    = df.resample('W').mean()
        avg_price = weekly['Close'].mean()
        avg_vol   = weekly['Volume'].mean()
        turnover  = int(avg_price * avg_vol) if (avg_price and avg_vol) else 0
        # opbrks/wk: 8x10-period rolling std divided by 0.50 bracket width
        rolling_std = 4 * df['Close'].rolling(10).std()
        opbrks      = round(float(rolling_std.iloc[-1]) / 0.50, 1) if not rolling_std.dropna().empty else 0.0
        info = {'symbol': ticker, 'marketCap': turnover, 'opbrks': opbrks}
        print(f"[meta]  {ticker} turnover={turnover} opbrks={opbrks}")
        return df, info



# ─────────────────────────────────────────────
#  In-memory + JSON-file cache
# ─────────────────────────────────────────────
@dataclass
class CachedData:
    data:      pd.DataFrame   # OHLCV history (at minimum a 'Close' column)
    info:      dict           # ticker info  (symbol, marketCap, …)
    timestamp: datetime
    period:    str            # period key this data was fetched for


class DataCache:
    """Two-level cache: fast in-memory dict, persistent JSON files on disk."""

    def __init__(
        self,
        cache_duration: timedelta = timedelta(minutes=1200),
        cache_dir: Optional[str] = None,
    ):
        self.cache: Dict[str, Dict[str, CachedData]] = {}
        self.cache_duration = cache_duration
        self.cache_dir = cache_dir or os.path.join(
            os.getcwd(),
            'stock_cache',
        )

    # ── helpers ───────────────────────────────────────────────────
    @staticmethod
    def _safe_name(ticker: str) -> str:
        """Convert ticker to a filesystem-safe string."""
        return ticker.replace('^', 'IDX_').replace('/', '_').replace('*', '_')

    def _filepath(self, ticker: str, period: str) -> str:
        return os.path.join(
            self.cache_dir,
            f'{self._safe_name(ticker)}_{period}.json',
        )

    # ── public API ────────────────────────────────────────────────
    def get(self, ticker: str, period: str) -> Optional[CachedData]:
        # 1. Check in-memory cache first
        entry = self.cache.get(ticker, {}).get(period)
        if entry and (datetime.now() - entry.timestamp) <= self.cache_duration:
            return entry

        # 2. Fall back to file cache
        return self._load_file(ticker, period)

    def set(self, ticker: str, period: str, data: pd.DataFrame, info: dict):
        ts = datetime.now()
        cached = CachedData(data=data, info=info, timestamp=ts, period=period)
        self.cache.setdefault(ticker, {})[period] = cached
        self._save_file(ticker, period, data, info, ts)

    def clear(self):
        self.cache.clear()
        # Also remove stale files from disk
        if os.path.isdir(self.cache_dir):
            for fname in os.listdir(self.cache_dir):
                if fname.endswith('.json'):
                    try:
                        os.remove(os.path.join(self.cache_dir, fname))
                    except OSError:
                        pass

    # ── file I/O ──────────────────────────────────────────────────
    def _save_file(
        self,
        ticker: str,
        period: str,
        data: pd.DataFrame,
        info: dict,
        timestamp: datetime,
    ):
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            payload = {
                'timestamp': timestamp.isoformat(),
                'period':    period,
                'info':      info,
                'close_index': [str(idx) for idx in data.index],
                'close_values': [
                    None if np.isnan(v) else v
                    for v in data['Close'].tolist()
                ],
                'volume_values': [
                    None if (v is None or (isinstance(v, float) and np.isnan(v))) else v
                    for v in data['Volume'].tolist()
                ],
            }
            with open(self._filepath(ticker, period), 'w') as fh:
                json.dump(payload, fh)
        except Exception as exc:
            print(f"[cache] Could not save {ticker}/{period} to disk: {exc}")

    def _load_file(self, ticker: str, period: str) -> Optional[CachedData]:
        path = self._filepath(ticker, period)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, 'r') as fh:
                payload = json.load(fh)
            ts = datetime.fromisoformat(payload['timestamp'])
            if (datetime.now() - ts) > self.cache_duration:
                return None
            index  = pd.to_datetime(payload['close_index'])
            df     = pd.DataFrame({
                'Close':  payload['close_values'],
                'Volume': payload.get('volume_values', [0]*len(payload['close_values'])),
            }, index=index)
            df     = df.dropna(subset=['Close'])
            cached = CachedData(
                data=df,
                info=payload['info'],
                timestamp=ts,
                period=period,
            )
            # Promote into memory cache
            self.cache.setdefault(ticker, {})[period] = cached
            return cached
        except Exception as exc:
            print(f"[cache] Could not load {ticker}/{period} from disk: {exc}")
            return None


# ─────────────────────────────────────────────
#  Pop-up ticker keyboard
# ─────────────────────────────────────────────
class PopupKeyboard:
    def __init__(self, master, entries, togglelog=True):
        self.master = master
        self.entries = entries
        self.current_entry_index = 0
        self.togglelog = togglelog
        self.keyboard_window = None
        self.text_display = None
        for entry in self.entries:
            entry.configure(bg='white')
            entry.bind('<FocusIn>',  self.on_entry_focus)
            entry.bind('<FocusOut>', self.on_entry_unfocus)

    def on_entry_focus(self, event):
        event.widget.configure(bg='#e6f3ff')
        self.current_entry_index = self.entries.index(event.widget)

    def on_entry_unfocus(self, event):
        event.widget.configure(bg='white')

    def fill_entries_from_textbox(self):
        if not self.text_display:
            return
        text    = self.text_display.get().strip().upper()
        tickers = text.split()
        for i, entry in enumerate(self.entries):
            if i != 7:
                entry.delete(0, 'end')
        ticker_index = 0
        entry_index  = 0
        while ticker_index < len(tickers) and entry_index < len(self.entries):
            if entry_index != 7:
                self.entries[entry_index].delete(0, 'end')
                self.entries[entry_index].insert(0, tickers[ticker_index])
                ticker_index += 1
            entry_index += 1
        self.text_display.delete(0, 'end')

    def toggle_keyboard(self):
        if self.keyboard_window is None or not self.keyboard_window.winfo_exists():
            self.show_keyboard()
        else:
            self.hide_keyboard()

    def show_keyboard(self):
        self.keyboard_window = Toplevel(self.master)
        self.keyboard_window.title("Ticker Keyboard")
        self.keyboard_window.resizable(0, 0)
        x = self.master.winfo_x() - 43
        y = self.master.winfo_y() + 750
        self.keyboard_window.geometry(f"+{x}+{y}")
        keyboard_layout = [
            ['1','2','3','4','5','6','7','8','9','0'],
            ['Q','W','E','R','T','Y','U','I','O','P'],
            ['A','S','D','F','G','H','J','K','L','^'],
            ['Z','X','C','V','B','N','M','-USD'],
            ['《','<','CLEAR','FILL','》'],
        ]
        max_cols    = 10
        button_style = {
            'width': 1, 'height': 1, 'font': ('Helvetica', 3),
            'relief': 'raised', 'bg': '#f0f0f0', 'activebackground': '#e0e0e0',
        }
        for row_idx, row in enumerate(keyboard_layout):
            x_padding = (max_cols - len(row)) // 2
            for col_idx, key in enumerate(row):
                local_style = button_style.copy()
                if key in ['CLEAR', 'FILL']:
                    local_style['width'] = 3
                btn = Button(
                    self.keyboard_window, text=key,
                    command=lambda k=key: self.handle_key_press(k),
                    **local_style,
                )
                btn.grid(row=row_idx, column=col_idx + x_padding, padx=2, pady=2)
        self.text_display = Entry(
            self.keyboard_window, justify='center',
            font=('Helvetica', 6), bg='white', relief='sunken',
        )
        self.text_display.grid(
            row=len(keyboard_layout), column=0,
            columnspan=max_cols, padx=4, pady=4, sticky='ew',
        )
        self.text_display.insert(0, "Paste space-separated tickers here...")
        self.text_display.bind('<FocusIn>', self.on_textbox_focus)

    def on_textbox_focus(self, event):
        if self.text_display.get() == "Paste space-separated tickers here...":
            self.text_display.delete(0, 'end')

    def hide_keyboard(self):
        if self.keyboard_window:
            self.keyboard_window.destroy()
            self.keyboard_window = None
            self.text_display    = None

    def handle_key_press(self, key):
        if not self.entries:
            return
        if key == 'FILL':
            self.fill_entries_from_textbox()
            return
        current_entry = self.entries[self.current_entry_index]
        current_text  = current_entry.get()
        if key == 'CLEAR':
            current_entry.delete(0, 'end')
        elif key == '<':
            if current_text.endswith('-USD'):
                current_entry.delete(0, 'end')
                current_entry.insert(0, current_text[:-4])
            else:
                current_entry.delete(len(current_text) - 1, 'end')
        elif key == '《':
            current_entry.configure(bg='white')
            self.current_entry_index = (self.current_entry_index - 1) % len(self.entries)
            self.entries[self.current_entry_index].focus()
            self.entries[self.current_entry_index].configure(bg='#e6f3ff')
        elif key == '》':
            current_entry.configure(bg='white')
            self.current_entry_index = (self.current_entry_index + 1) % len(self.entries)
            self.entries[self.current_entry_index].focus()
            self.entries[self.current_entry_index].configure(bg='#e6f3ff')
        else:
            current_entry.insert(current_entry.index('insert'), key)
            current_entry.focus()


# ─────────────────────────────────────────────
#  Main window
# ─────────────────────────────────────────────
master = Tk()
master.title("PortfolioViewer0365")
master.geometry("1050x1800+200+100")

# Shared data objects
data_cache     = DataCache()
crumb_fetcher  = YahooCrumbFetcher()

# Master grid
mstr_grid = Frame(master, width=1050, height=1800)
mstr_grid.grid()
for i in range(50):
    mstr_grid.grid_rowconfigure(i, weight=1, minsize=30)
for i in range(16):
    mstr_grid.grid_columnconfigure(i, weight=1, minsize=60)
mstr_grid.grid_propagate(False)

# Plot frames
box_grid1 = Frame(mstr_grid, width=750, height=1000)
box_grid1.grid_propagate(False)
box_grid1.grid(row=0, column=0, columnspan=12, rowspan=11, sticky='news')

box_grid2 = Frame(mstr_grid, width=1400, height=2000)
box_grid2.grid(row=16, column=0, columnspan=16, rowspan=25, sticky='news')
box_grid2.grid_propagate(False)

# Time period selector
lbl_time_prd = Label(mstr_grid, text="Time Period")
lbl_time_prd.grid(row=0, column=13, columnspan=3, sticky='news')
prd_select  = StringVar()
period_ddbox = ttk.Combobox(mstr_grid, width=15, textvariable=prd_select, state='readonly')
period_ddbox['values'] = ('1 MO', '3 MO', '6 MO')
period_ddbox.grid(row=1, column=13, columnspan=3, sticky='nw')
period_ddbox.current(0)

# Portfolio label + entry boxes
lbl_portfolio = Label(mstr_grid, text="Portfolio")
lbl_portfolio.grid(row=2, column=13, columnspan=3, sticky='s')


def auto_capitalize(event):
    w = event.widget
    w.delete(0, 'end')
    w.insert(0, w.get().upper())


stock_entries = []
for f in range(3, 11):
    entry = Entry(mstr_grid, justify='center')
    entry.grid(row=f, column=13, columnspan=3, sticky='news')
    entry.bind('<KeyRelease>', auto_capitalize)
    stock_entries.append(entry)

stock_entries[7].insert(0, '^VIX')


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def format_market_cap(value):
    if not value:
        return "N/A"
    prefixes = [(1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "K")]
    for scale, prefix in prefixes:
        if abs(value) >= scale:
            sv = value / scale
            fmt = f"{sv:.0f}" if sv >= 100 else f"{sv:.1f}" if sv >= 10 else f"{sv:.2f}"
            return f"{fmt} {prefix}ɓ"
    return f"{value:.2f} ɓ"


# ─────────────────────────────────────────────
#  Main plot function
# ─────────────────────────────────────────────
def plot_portfolio(ding=None, togglelog=True):
    date_form  = ['%m-%d', '%m-%d', '%m-%d']
    tm_prd     = ['1mo',   '3mo',   '6mo']
    tm_intrvl  = ['1d',    '5d',    '1wk']

    slctr           = period_ddbox.current()
    selected_period = period_ddbox.get()
    current_period  = tm_prd[slctr]

    stock_data    = []
    valid_tickers = []
    market_caps   = []
    opbrks_list   = []

    plt.close('all')

    for entry in stock_entries:
        ticker = entry.get().strip()
        if not ticker:
            continue
        try:
            cached = data_cache.get(ticker, current_period)
            if cached is None:
                df, info = crumb_fetcher.fetch_history(ticker, current_period, tm_intrvl[slctr])
                if not df.empty:
                    data_cache.set(ticker, current_period, df, info)
                    stock_data.append(df)
                    valid_tickers.append(ticker)
                    market_caps.append(0 if ticker == '^VIX' else info.get('marketCap', 0))
                    opbrks_list.append(0 if ticker == '^VIX' else info.get('opbrks', 0))
            else:
                stock_data.append(cached.data)
                valid_tickers.append(ticker)
                market_caps.append(0 if ticker == '^VIX' else cached.info.get('marketCap', 0))
                opbrks_list.append(0 if ticker == '^VIX' else cached.info.get('opbrks', 0))
        except Exception as exc:
            msg = f"ERROR fetching {ticker}: {exc}"
            print(msg)
            # Show the error in box_grid1 so it is visible on screen
            for w in box_grid1.winfo_children():
                w.destroy()
            Label(
                box_grid1, text=msg, justify='left', wraplength=700,
                fg='red', font=('Helvetica', 7),
            ).pack(anchor='nw', padx=6, pady=4)
            box_grid1.update_idletasks()
            continue

    # Clear existing plot widgets
    for widget in box_grid1.winfo_children():
        widget.destroy()
    for widget in box_grid2.winfo_children():
        widget.destroy()

    if not stock_data:
        Label(box_grid1, text="No valid stock data.\nCheck ticker symbols or network.", justify='center').pack(expand=True)
        Label(box_grid2, text="No valid stock data.\nCheck ticker symbols or network.", justify='center').pack(expand=True)
        return

    # Rank by opbrks/wk (most active options ticker = rank 1)
    non_vix_idx  = [i for i, t in enumerate(valid_tickers) if t != '^VIX']
    non_vix_opbr = [opbrks_list[i] for i in non_vix_idx]
    rankings     = np.zeros(len(opbrks_list))
    for rank, idx in enumerate(np.argsort(non_vix_opbr)[::-1]):
        rankings[non_vix_idx[idx]] = rank + 1

    current_datetime = datetime.now().strftime("%m-%d-%Y %H:%M:%S")

    # ── Close-price figure (box_grid2) ────────────────────────────
    full_figure = plt.figure(figsize=(15, 4))
    full_ax     = full_figure.add_subplot(111)

    for data, ticker in zip(stock_data, valid_tickers):
        plot_data = data['Close'] if togglelog else np.log10(data['Close'])
        if ticker == '^VIX':
            full_ax.plot(data.index, plot_data, label=ticker,
                         linestyle=':', linewidth=2.5, color='purple')
        else:
            full_ax.plot(data.index, plot_data, label=ticker)

    full_ax.set_xlabel(f'Date-({current_datetime})')
    full_ax.xaxis.set_major_formatter(mdates.DateFormatter(date_form[slctr]))
    full_ax.set_ylabel('Asset Close Price ($)' if togglelog else 'log[Asset Close Price] ~(logibucks)')
    full_ax.set_title('Asset Close Price Over Time' if togglelog else 'log[Asset Close Price] Over Time')
    full_ax.legend()
    full_ax.grid(True, linestyle='--', alpha=0.7)

    # ── Percentage-of-average figure (box_grid1) ──────────────────
    figure = plt.figure(figsize=(10, 5))
    ax2    = figure.add_subplot(111)

    lines  = []
    labels = []

    # Pre-compute VIX % series for correlation (align on common dates)
    vix_pct = None
    if '^VIX' in valid_tickers:
        vix_data  = stock_data[valid_tickers.index('^VIX')]['Close']
        vix_pct   = (vix_data / vix_data.mean() - 1) * 100

    for i, (data, ticker) in enumerate(zip(stock_data, valid_tickers)):
        close_prices      = data['Close']
        percentage_prices = (close_prices / close_prices.mean() - 1) * 100
        display_ticker    = ticker.replace('-USD', '•')

        if ticker == '^VIX':
            line  = ax2.plot(data.index, percentage_prices,
                             linestyle=':', linewidth=3, color='purple')[0]
            label = f'{ticker} (% of Avg)'
            rank  = float('inf')
        else:
            rank         = len(rankings) - rankings[i]
            turnover_str = format_market_cap(market_caps[i])
            opbrks_val   = opbrks_list[i]
            line         = ax2.plot(data.index, percentage_prices,
                                    linewidth=1.25 * rank)[0]
            # VIX correlation on aligned dates
            if vix_pct is not None:
                aligned = percentage_prices.align(vix_pct, join='inner')
                vix_corr = aligned[0].corr(aligned[1])
                corr_str = f'{vix_corr:+.2f}'
            else:
                corr_str = ' n/a'
            label = f'{display_ticker} <{int(rank)}> [({opbrks_val:.0f} opbraks, {turnover_str})/wk, {corr_str}vix]'

        lines.append((rank, line))
        labels.append((rank, label))

    sorted_pairs  = sorted(zip(lines, labels), key=lambda x: x[0][0])
    sorted_lines  = [p[0][1] for p in sorted_pairs]
    sorted_labels = [p[1][1] for p in sorted_pairs]

    ax2.set_xlabel(f'Date-({current_datetime})')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter(date_form[slctr]))
    ax2.set_ylabel('Percentage of Average Price (%)')
    ax2.set_title(f'opbrks/wk Ranked Asset Price Percentages Relative to {selected_period} Average (%)')
    ax2.legend(sorted_lines, sorted_labels, fontsize=11)
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=3, alpha=0.5)

    # Embed in tkinter
    full_canvas = FigureCanvasTkAgg(full_figure, box_grid2)
    full_canvas.draw()
    full_canvas.get_tk_widget().pack(fill='both', expand=True)

    canvas = FigureCanvasTkAgg(figure, box_grid1)
    canvas.draw()
    canvas.get_tk_widget().grid(sticky='news')
    box_grid1.rowconfigure(0, weight=1)
    box_grid1.columnconfigure(0, weight=1)


# ─────────────────────────────────────────────
#  Button callbacks
# ─────────────────────────────────────────────
def toggle_log_scale():
    global keyboard
    keyboard.togglelog = not keyboard.togglelog
    btn_togglelog.config(text='Linear' if keyboard.togglelog else 'Log')
    plot_portfolio(togglelog=keyboard.togglelog)


def clear_cache():
    data_cache.clear()
    plot_portfolio(togglelog=keyboard.togglelog)


# ─────────────────────────────────────────────
#  Controls
# ─────────────────────────────────────────────
keyboard = PopupKeyboard(master, stock_entries, togglelog=True)

btn_keyboard = Button(mstr_grid, font=('Helvetica', 4),
                      text="⧇⧇⧇⧇\n⧇⧇⧇⧇⧇", command=keyboard.toggle_keyboard)
btn_keyboard.grid(row=13, column=13, columnspan=2, rowspan=2, sticky='news')

btn_togglelog = Button(mstr_grid, text="Linear", font=('Helvetica', 6), command=toggle_log_scale)
btn_togglelog.grid(row=13, column=15, columnspan=1, rowspan=2, sticky='news')

btn_pltport = Button(mstr_grid, text="V I E W   P O R T F O L I O", font=('Helvetica', 8))
btn_pltport.grid(row=12, column=0, rowspan=3, columnspan=12, sticky='news')
btn_pltport.bind("<Button-1>", lambda e: plot_portfolio(togglelog=keyboard.togglelog))

btn_clear_cache = Button(mstr_grid, text="↻", font=('Helvetica, Bold', 3), command=clear_cache)
btn_clear_cache.grid(row=12, column=13, rowspan=1, columnspan=3, sticky='news')

# Auto-run on launch
master.after(600, lambda: plot_portfolio(togglelog=keyboard.togglelog))

master.mainloop()
