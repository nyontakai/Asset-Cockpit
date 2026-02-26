import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# ------------------------------------------------------------------------------
# 設定 & マッピング
# ------------------------------------------------------------------------------
SAVE_FILE = "stock_data_v5.json"
METADATA_FILE = "metadata_db.json"

NAME_MAPPING = {
    "4661.T": "オリエンタルランド",
    "8593.T": "三菱HCキャピタル",
    "9433.T": "KDDI",
    "7203.T": "トヨタ自動車",
    "6758.T": "ソニーグループ",
    "9984.T": "ソフトバンクグループ",
    "8306.T": "三菱UFJフィナンシャルG",
    "8316.T": "三井住友FG",
    "8411.T": "みずほFG",
    "4063.T": "信越化学工業",
    "8031.T": "三井物産",
    "8766.T": "東京海上HD",
    "2914.T": "日本たばこ産業",
    "6098.T": "リクルートHD",
    "4502.T": "武田薬品工業",
    "6954.T": "ファナック",
    "7974.T": "任天堂",
    "9022.T": "JR東海",
    "6367.T": "ダイキン工業",
    "4503.T": "アステラス製薬",
    "9513.T": "電源開発 (J-POWER)",
    "8058.T": "三菱商事",
    "8001.T": "伊藤忠商事",
    "9432.T": "日本電信電話",
    "7267.T": "本田技研工業",
    "6501.T": "日立製作所",
    "6902.T": "デンソー",
    "6965.T": "浜松ホトニクス",
    "6702.T": "富士通",
    "6752.T": "パナソニックHD",
    "4568.T": "第一三共",
    "7201.T": "日産自動車",
    "6981.T": "村田製作所",
    "7751.T": "キヤノン",
    "8035.T": "東京エレクトロン",
    "2337.T": "いちご",
    "2502.T": "アサヒGHD",
    "2802.T": "味の素",
    "3382.T": "セブン&アイHD",
    "3402.T": "東レ",
    "3407.T": "旭化成",
    "4452.T": "花王",
    "4519.T": "中外製薬",
    "4901.T": "富士フイルムHD",
    "5108.T": "ブリヂストン",
    "6361.T": "荏原製作所",
    "6479.T": "ミネベアミツミ",
    "6503.T": "三菱電機",
    "6723.T": "ルネサスエレクトロニクス",
    "6753.T": "シャープ",
    "6861.T": "キーエンス",
    "6971.T": "京セラ",
    "7011.T": "三菱重工業",
    "1332.T": "ニッスイ",
    "1333.T": "マルハニチロ",
    "1925.T": "大和ハウス",
    "1928.T": "積水ハウス",
    "4664.T": "日本リライアンス",
    "9441.T": "ベルパーク",
    "6134.T": "富士製砥",
    "4661.T": "オリエンタルランド",
    "8306.T": "三菱UFJフィナンシャルG",
    "9513.T": "電源開発",
    "2337.T": "いちご",
}

SECTOR_MAPPING = {
    "Financial Services": "銀行・金融",
    "Healthcare": "医薬品・ヘルスケア",
    "Technology": "情報・通信",
    "Consumer Defensive": "生活必需品",
    "Communication Services": "通信サービス",
    "Industrials": "機械・工業",
    "Real Estate": "不動産",
    "Utilities": "電気・ガス",
    "Basic Materials": "化学・素材",
    "Consumer Cyclical": "一般消費財",
    "Energy": "エネルギー",
    "Information Technology": "情報技術",
}

COLOR_SUCCESS = "#00ff00"
COLOR_DANGER = "#ff4b4b"
COLOR_PRIMARY = "#00d4ff"

st.set_page_config(
    page_title="株価ダッシュボード Pro v8",
    page_icon="👑",
    layout="wide"
)

# --- カスタムCSS (究極UI) ---
st.markdown(f"""
<style>
/* サマリーカード */
.metric-card {{
    background-color: #262730;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    text-align: center;
}}
.metric-positive {{
    background-color: rgba(0, 255, 0, 0.05);
    border: 1px solid {COLOR_SUCCESS}55;
}}
.metric-negative {{
    background-color: rgba(255, 75, 75, 0.05);
    border: 1px solid {COLOR_DANGER}55;
}}
.metric-label {{
    font-size: 0.9rem;
    color: #ccc;
    margin-bottom: 5px;
}}
.metric-value {{
    font-size: 1.8rem;
    font-weight: bold;
    margin-bottom: 0;
}}
.metric-delta {{
    font-size: 0.9rem;
    margin-top: -5px;
}}

/* サンプルカードのフォント調整 */
div[data-testid="stMetricValue"] {{ font-size: 1.6rem !important; }}

/* マルチセレクトの赤背景を完全に上書き */
div[data-baseweb="select"] span[data-baseweb="tag"],
.stMultiSelect div[data-baseweb="tag"],
div[role="listbox"] span[data-baseweb="tag"] {{
    background-color: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    color: white !important;
}}

/* アップローダーのUI刷新 (v9.0 Flexbox版) */
[data-testid="stFileUploaderDropzone"] {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 1.5em !important;
    gap: 0.5em !important;
    border: 1px dashed rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}}
/* 不要な要素を非表示 */
[data-testid="stFileUploaderDropzone"] > div:not(button),
[data-testid="stFileUploaderDropzone"] span:not(button span),
[data-testid="stFileUploaderDropzone"] p {{
    display: none !important;
}}
[data-testid="stFileUploaderDropzone"] small {{
    display: none !important;
}}
/* 日本語テキストの注入 */
[data-testid="stFileUploaderDropzone"]::before {{
    content: "設定ファイルをドラッグ＆ドロップ";
    display: block;
    color: white;
    font-size: 0.95rem;
    font-weight: bold;
}}
[data-testid="stFileUploaderDropzone"]::after {{
    content: "※JSON形式の設定ファイルを読み込みます";
    display: block;
    color: #888;
    font-size: 0.75rem;
}}
/* ボタンの日本語化 */
[data-testid="stFileUploaderDropzone"] button {{
    margin-top: 0.5em !important;
    width: 80% !important;
}}
[data-testid="stFileUploaderDropzone"] button span {{
    display: none !important;
}}
[data-testid="stFileUploaderDropzone"] button::after {{
    content: "ファイルを選択";
    font-size: 0.85rem;
    color: white;
}}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# データの保存・読み込み
# ------------------------------------------------------------------------------
def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {"4661.T": {"buy_price": 0.0, "shares": 100}}

def save_data(data):
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"保存エラー: {e}")

# ------------------------------------------------------------------------------
# データ取得ロジック
# ------------------------------------------------------------------------------
@st.cache_data(ttl=600)
def fetch_bulk_data(ticker_list):
    """300銘柄以上でも確実に取得できるようチャンク分割して実行"""
    if not ticker_list: return {}
    CHUNK_SIZE = 50
    results = {}
    
    for i in range(0, len(ticker_list), CHUNK_SIZE):
        chunk = ticker_list[i:i + CHUNK_SIZE]
        try:
            df = yf.download(chunk, period="5d", interval="1d", group_by='ticker', progress=False)
            for tid in chunk:
                try:
                    ticker_df = df if len(chunk) == 1 else df[tid]
                    ticker_df = ticker_df.dropna(subset=['Close'])
                    if ticker_df.empty: continue
                    current_price = ticker_df['Close'].iloc[-1]
                    prev_close = ticker_df['Close'].iloc[-2]
                    results[tid] = {
                        "price": float(current_price),
                        "prev_close": float(prev_close),
                        "change_abs": float(current_price - prev_close),
                        "change_pct": float((current_price - prev_close) / prev_close * 100)
                    }
                except Exception: results[tid] = None
        except Exception: continue
    return results

def load_metadata_db():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception: return {}
    return {}

def save_metadata_db(db):
    try:
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
    except Exception: pass

def get_bulk_metadata(ticker_list):
    """永続DBとセッションキャッシュを活用した超高速メタデータ取得"""
    if 'metadata_cache' not in st.session_state:
        st.session_state.metadata_cache = load_metadata_db()
    
    missing = [tid for tid in ticker_list if tid not in st.session_state.metadata_cache]
    if missing:
        with st.sidebar:
            with st.spinner(f"新規銘柄のメタ情報を構築中..."):
                chunk_count = 0
                for tid in missing:
                    try:
                        info = yf.Ticker(tid).info
                        st.session_state.metadata_cache[tid] = info
                        chunk_count += 1
                        if chunk_count % 10 == 0:
                            save_metadata_db(st.session_state.metadata_cache)
                    except Exception: pass
                save_metadata_db(st.session_state.metadata_cache)
    
    return {tid: st.session_state.metadata_cache.get(tid, {}) for tid in ticker_list}

@st.cache_data(ttl=86400)
def fetch_dividend_history(tid):
    """過去の配当実績を取得して支払月を推測する"""
    try:
        t = yf.Ticker(tid)
        # dividendsが空の場合があるため、historyから取得を試みる
        divs = t.dividends
        if divs.empty:
            # 補助的にhistoryを取得
            hist = t.history(period="2y")
            if "Dividends" in hist.columns:
                divs = hist[hist["Dividends"] > 0]["Dividends"]
        
        if divs.empty:
            # 日本株の一般的な配当月（3月権利落ち→6月支払、9月権利落ち→12月支払）をデフォルトにする
            if ".T" in tid:
                return [6, 12]
            return []
            
        # 直近2年分の権利落ち月を抽出
        latest_divs = divs[divs.index > (datetime.now() - pd.DateOffset(years=2))]
        ex_months = list(latest_divs.index.month.unique())
        
        # 支払月を推定 (+3ヶ月)
        pay_months = []
        for m in ex_months:
            pay_m = (m + 3) if (m + 3) <= 12 else (m + 3 - 12)
            pay_months.append(pay_m)
        return list(set(pay_months))
    except Exception:
        if ".T" in tid: return [6, 12]
        return []

def get_display_name(tid, info):
    if tid in NAME_MAPPING: return NAME_MAPPING[tid]
    raw_name = info.get("longName") or info.get("shortName") or tid
    
    # 除去キーワードの拡充 (特に日本株の英語表記対策)
    removals = [
        "Corporation", "Corp", "Company", "Co., Ltd", "Co.,Ltd", "Limited", "Ltd", 
        "Holdings", "Group", "K.K.", "Inc", "Incorporated", "International", "Solutions",
        "Systems", "Industries", "Manufacturing", "Energy", "Electric", "Electronic",
        "Stock", "Exchange", "Global", "Partners", "Technology", "Technologies",
        "Service", "Services", "Park", "Japan", "Real", "Estate"
    ]
    
    cleaned = raw_name
    for r in removals:
        # 大文字小文字を区別せず、単語境界やピリオドの有無を考慮して置換
        import re
        # ピリオドの有無に関わらずマッチさせるためのパターン
        pattern = re.escape(r).replace(r"\.", r"\.?")
        cleaned = re.sub(r"(?i)\b" + pattern + r"\b", "", cleaned).strip()
    
    # 日本株（.T）の場合、記号なども徹底的に掃除
    if tid.endswith(".T"):
        cleaned = cleaned.replace("&", "").replace(",", "").strip()
        
    return cleaned if cleaned else tid

# ------------------------------------------------------------------------------
# メイン画面
# ------------------------------------------------------------------------------
def main():
    st.title("👑 マイ株価ダッシュボード Pro")

    if 'stock_configs' not in st.session_state:
        st.session_state.stock_configs = load_data()

    # --- サイドバー ---
    st.sidebar.header("🛡️ 銘柄・表示管理")
    
    # 表示モード
    display_mode = st.sidebar.radio("表示モード", ["カード形式", "リスト形式 (表)"], horizontal=True)
    
    st.sidebar.divider()
    
    # 銘柄追加 & プレビュー
    with st.sidebar.expander("➕ 銘柄を追加", expanded=True):
        new_code = st.text_input("証券コード (4桁)", max_chars=4, key="ticker_input")
        if new_code.isdigit() and len(new_code) == 4:
            preview_tid = f"{new_code}.T"
            # プレビュー用の簡易取得
            p_info = yf.Ticker(preview_tid).info
            p_name = get_display_name(preview_tid, p_info)
            if p_info:
                st.caption(f"🔍 プレビュー: **{p_name}**")
            else:
                st.caption("⚠️ 該当する銘柄が見つかりません")
        
        if st.button("追加実行", use_container_width=True):
            if new_code.isdigit() and len(new_code) == 4:
                full_code = f"{new_code}.T"
                if full_code not in st.session_state.stock_configs:
                    st.session_state.stock_configs[full_code] = {"buy_price": 0.0, "shares": 100}
                    save_data(st.session_state.stock_configs)
                    st.rerun()

    # JSON保存・読込
    st.sidebar.subheader("💾 設定の保存・読込")
    c1, c2 = st.sidebar.columns(2)
    with c1:
        st.download_button("📤 保存(JSON)", json.dumps(st.session_state.stock_configs, indent=4, ensure_ascii=False), 
                         file_name="portfolio.json", use_container_width=True)
    with c2:
        # ラベルを日本語化
        up = st.file_uploader("設定読込", type="json", label_visibility="collapsed")
        if up:
            st.session_state.stock_configs = json.load(up)
            save_data(st.session_state.stock_configs)
            st.rerun()

    st.sidebar.divider()
    
    # 編集モード切り替え
    st.sidebar.subheader("⚙️ データ編集")
    edit_mode = st.sidebar.toggle("一括編集モード（単価・株数）", value=False)
    
    st.sidebar.divider()
    
    # 登録リスト
    current_tickers = list(st.session_state.stock_configs.keys())
    if current_tickers:
        # 登録銘柄の表示名の取得もキャッシュを活用
        meta_all = get_bulk_metadata(current_tickers)
        options = {f"{get_display_name(tid, meta_all.get(tid, {}))} ({tid})": tid for tid in current_tickers}
        sel = st.sidebar.multiselect("登録済み銘柄 (×で削除)", options.keys(), default=options.keys())
        if len(sel) < len(current_tickers):
            if st.sidebar.button("削除を確定", type="primary", use_container_width=True):
                st.session_state.stock_configs = {options[label]: st.session_state.stock_configs[options[label]] for label in sel}
                save_data(st.session_state.stock_configs)
                st.rerun()

    st.sidebar.divider()
    # キャッシュクリアボタン
    if st.sidebar.button("🔃 データを強制更新", use_container_width=True):
        st.cache_data.clear()
        if 'metadata_cache' in st.session_state:
            del st.session_state.metadata_cache
        st.rerun()

    # --- データ計算 ---
    ticker_list = list(st.session_state.stock_configs.keys())
    if not ticker_list:
        st.info("銘柄を登録してください。")
        return

    all_data = []
    bulk_res = fetch_bulk_data(ticker_list)
    bulk_meta = get_bulk_metadata(ticker_list) # info取得をバルク管理へ移行
    
    total_pl = 0
    total_div = 0
    total_valuation = 0
    sector_valuation = {}
    monthly_dividends = {m: 0 for m in range(1, 13)}

    for tid in ticker_list:
        price_data = bulk_res.get(tid)
        if not price_data: continue
        
        info = bulk_meta.get(tid, {})
        cfg = st.session_state.stock_configs.get(tid, {"buy_price": 0.0, "shares": 100})
        
        # 基本情報
        name = get_display_name(tid, info)
        sec_raw = info.get("sector")
        sec = SECTOR_MAPPING.get(sec_raw, sec_raw or "その他業種")
        shares = cfg['shares']
        buy_p = cfg['buy_price']
        valuation = price_data['price'] * shares
        
        # 配当計算
        y_val = info.get("dividendYield", 0)
        yield_pct = y_val if y_val > 0.5 else y_val * 100
        one_share_div = (yield_pct / 100 * price_data['price'])
        div_sum = one_share_div * shares
        
        # 月別配当加算
        pay_months = fetch_dividend_history(tid)
        if pay_months and div_sum > 0:
            div_per_month = div_sum / len(pay_months)
            for m in pay_months: monthly_dividends[m] += div_per_month
        
        # 損益
        pl = (price_data['price'] - buy_p) * shares if buy_p > 0 else 0
        pl_pct = ((price_data['price'] - buy_p) / buy_p * 100) if buy_p > 0 else 0
        yoc = (one_share_div / buy_p * 100) if buy_p > 0 else 0
        
        total_pl += pl
        total_div += div_sum
        total_valuation += valuation
        sector_valuation[sec] = sector_valuation.get(sec, 0) + valuation
        
        all_data.append({
            "コード": tid, "銘柄名": name, "業種": sec, "現在値": price_data['price'],
            "前日比_率": price_data['change_pct'], 
            "PER": f"{float(info.get('trailingPE',0)):.1f}" if info.get('trailingPE') else "データなし",
            "配当利回り": yield_pct, "保有数": shares, "購入単価": buy_p, "含み損益": pl,
            "損益率": pl_pct, "配当合計": div_sum, "YOC": yoc, "時価": valuation
        })

    # --- トップセクション (2カラム) ---
    col_metrics, col_pie = st.columns([1, 1])
    
    with col_metrics:
        pl_class = "metric-positive" if total_pl >= 0 else "metric-negative"
        pl_arrow = "+" if total_pl >= 0 else ""
        avg_yield = (total_div / total_valuation * 100) if total_valuation > 0 else 0
        
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div class="metric-card {pl_class}" style="grid-column: span 2;">
                <div class="metric-label">合計含み損益</div>
                <div class="metric-value" style="color:{COLOR_SUCCESS if total_pl>=0 else COLOR_DANGER};">¥{total_pl:,.0f}</div>
                <div class="metric-delta">{pl_arrow}{total_pl/total_valuation*100:+.2f}% (時価: ¥{total_valuation:,.0f})</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">年間予想配当合計</div>
                <div class="metric-value" style="color:{COLOR_PRIMARY};">¥{total_div:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">平均配当利回り</div>
                <div class="metric-value">{avg_yield:.2f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_pie:
        # 業種別グラフ
        fig_pie = px.pie(values=list(sector_valuation.values()), names=list(sector_valuation.keys()), 
                        hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=250, paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 月別配当金受取予想 ---
    st.subheader("🗓️ 月別配当金受取予想")
    months_jp = [f"{i}月" for i in range(1, 13)]
    fig_bar = go.Figure(data=[go.Bar(x=months_jp, y=list(monthly_dividends.values()), marker_color=COLOR_PRIMARY)])
    fig_bar.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', 
                         plot_bgcolor='rgba(0,0,0,0)', font_color='white', yaxis=dict(gridcolor='rgba(255,255,255,0.1)'))
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- メインコンテンツ ---
    st.divider()

    if edit_mode:
        st.subheader("📁 ポートフォリオ一括編集")
        st.info("保有銘柄の「購入単価」と「枚数（株数）」を入力して保存ボタンを押してください。")
        edit_list = []
        for d in all_data:
            edit_list.append({
                "コード": d['コード'],
                "銘柄名": d['銘柄名'],
                "保有株数": int(d['保有数']),
                "購入単価": float(d['購入単価'])
            })
        
        edited_df = st.data_editor(pd.DataFrame(edit_list), use_container_width=True, hide_index=True)
        if st.button("✅ 編集内容を保存", type="primary", use_container_width=True):
            new_configs = {row['コード']: {"buy_price": row['購入単価'], "shares": row['保有株数']} for _, row in edited_df.iterrows()}
            st.session_state.stock_configs = new_configs
            save_data(new_configs)
            st.success("設定を保存しました！")
            st.rerun()
        return

    if display_mode == "リスト形式 (表)":
        df_list = pd.DataFrame([{
            "銘柄名": d['銘柄名'], "コード": d['コード'], "業種": d['業種'], "現在値": f"¥{d['現在値']:,.1f}",
            "保有数": f"{d['保有数']:,.0f}", "含み損益": f"¥{d['含み損益']:,.0f}", "損益率": f"{d['損益率']:+.2f}%",
            "配当利回り": f"{d['配当利回り']:.2f}%", "取得利回り(YOC)": f"{d['YOC']:.2f}%"
        } for d in all_data])
        st.dataframe(df_list, use_container_width=True, hide_index=True)
    else:
        # カード形式 (セクター別にグループ化)
        sector_data = {}
        for d in all_data:
            s = d['業種']
            if s not in sector_data: sector_data[s] = []
            sector_data[s].append(d)
        
        # セクター別に見出しとグリッドを表示
        for sector, items in sector_data.items():
            with st.expander(f"📌 {sector} ({len(items)}銘柄)", expanded=True):
                for i in range(0, len(items), 3):
                    cols = st.columns(3)
                    row_items = items[i : i+3]
                    for j, item in enumerate(row_items):
                        with cols[j]:
                            st.markdown(f"**{item['銘柄名']}** ({item['コード']})")
                            st.metric("現在値", f"¥{item['現在値']:,.1f}", f"{item['前日比_率']:+.2f}%")
                            
                            y_style = "color:#ffaa00; font-weight:bold;" if item['配当利回り'] >= 4.0 else ""
                            st.markdown(f"""
                            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#ccc; margin: 4px 0;">
                                <span>PER: {item['PER']}</span>
                                <span style="{y_style}">利回り: {item['配当利回り']:.2f}%</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if item['購入単価'] > 0:
                                pl_color = COLOR_SUCCESS if item['含み損益'] >= 0 else COLOR_DANGER
                                st.markdown(f"<div style='color:{pl_color}; font-size:1rem; font-weight:bold;'>¥{item['含み損益']:,.0f} ({item['損益率']:+,.2f}%)</div>", unsafe_allow_html=True)
                                st.caption(f"YOC: {item['YOC']:.2f}% | {item['保有数']:,.0f}株")
                    if i + 3 < len(items):
                        st.divider()

if __name__ == "__main__":
    main()
