import streamlit as st
import pandas as pd
import numpy as np
import warnings
import re
warnings.filterwarnings('ignore')

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        background-color: #1E3A8A; color: white; padding: 15px;
        border-radius: 10px; text-align: center; font-size: 24px;
        font-weight: bold; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-card {
        background-color: #1E3A8A; color: white; padding: 12px;
        border-radius: 8px; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 105px; display: flex; flex-direction: column; justify-content: center;
    }
    .kpi-title { font-size: 16px; font-weight: bold; margin-bottom: 6px; color: #E5E7EB; }
    .kpi-value { font-size: 19px; font-weight: bold; color: white; }
    .card-title {
        background-color: #1E3A8A; color: white; padding: 10px;
        border-radius: 8px; margin-bottom: 10px; font-weight: bold;
        font-size: 15px; text-align: center; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .report-title {
        background-color: #3B82F6; color: white; padding: 12px;
        border-radius: 8px; text-align: center; font-size: 18px;
        font-weight: bold; margin-bottom: 15px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; }

    [data-testid="stDataFrame"] thead tr th {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        border-bottom: 2px solid #3B82F6 !important;
        padding: 8px 12px !important;
        white-space: nowrap !important;
    }
    [data-testid="stDataFrame"] tbody tr td {
        color: #111827 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 6px 12px !important;
    }
    [data-testid="stDataFrame"] tbody tr:nth-child(even) td {
        background-color: #EFF6FF !important;
    }
    [data-testid="stDataFrame"] tbody tr:nth-child(odd) td {
        background-color: #FFFFFF !important;
    }
    [data-testid="stDataFrame"] tbody tr:hover td {
        background-color: #DBEAFE !important;
    }
    [data-testid="stDataFrame"] > div {
        overflow-x: auto !important;
    }
    [data-testid="stDataFrame"] thead {
        position: sticky;
        top: 0;
        z-index: 10;
    }
</style>
""", unsafe_allow_html=True)


# ── Exact column names produced by aggregation — used as sort keys ────────────
COL_QTY     = 'Qty'
COL_SALES   = 'Total Sales (USD)'
COL_PL_USD  = 'P&L Amt USD'
COL_NET_PL  = 'Net PL%'
COL_BALANCE = 'Balance'


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_num(val):
    if val is None: return 0.0
    try:
        if pd.isna(val): return 0.0
    except: pass
    if isinstance(val, (int, float, np.number)):
        return float(val)
    cleaned = re.sub(r'[^\d.\-]', '', str(val))
    try:
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0


def normalise(s):
    return re.sub(r'[\s\-_]', '', str(s)).lower()


def find_col(df, *keywords):
    for kw in keywords:
        nkw = normalise(kw)
        for col in df.columns:
            if nkw in normalise(col):
                return col
    return None


def find_subcategory_col(df):
    for col in df.columns:
        if normalise(col) == 'subcategory':
            return col
    for col in df.columns:
        if 'sub' in normalise(col) and 'cat' in normalise(col):
            return col
    return None


def find_type_col(df):
    """Find the 'type' / category column in main sheet."""
    for col in df.columns:
        if normalise(col) == 'type':
            return col
    for col in df.columns:
        if 'type' in normalise(col):
            return col
    return None


def fmt_usd(v):  return f"${safe_num(v):,.2f}"
def fmt_qty(v):  return f"{safe_num(v):,.0f}"
def fmt_pct(v):  return f"{safe_num(v):.2f}%"


# ── Data loading ──────────────────────────────────────────────────────────────

def load_data(uploaded_file):
    try:
        xl = pd.read_excel(uploaded_file, sheet_name=None, header=None)
        missing = [s for s in ['main', 'new INV'] if s not in xl]
        if missing:
            st.error(f"Missing sheets: {', '.join(missing)}")
            return None, None

        raw_main = xl['main']
        hdr = 0
        for i in range(min(10, len(raw_main))):
            if raw_main.iloc[i].astype(str).str.upper().str.contains('SELLER SKU|ORDER NO').any():
                hdr = i
                break
        main_df = pd.read_excel(uploaded_file, sheet_name='main', header=hdr)
        main_df.columns = [str(c).strip() for c in main_df.columns]

        raw_inv = xl['new INV']
        hdr_inv = 0
        for i in range(min(10, len(raw_inv))):
            row_str = raw_inv.iloc[i].astype(str).str.lower()
            if row_str.str.contains('master sku|total balance|category|sub').any():
                hdr_inv = i
                break
        inv_df = pd.read_excel(uploaded_file, sheet_name='new INV', header=hdr_inv)
        inv_df.columns = [str(c).strip() for c in inv_df.columns]

        return main_df, inv_df

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None, None


# ── Filter inventory by selected category ─────────────────────────────────────

def filter_inv_by_category(inv_df, selected_category):
    """
    Filter the new INV sheet by Main Category column.
    If 'All' is selected, return the full inv_df.
    """
    if selected_category == 'All':
        return inv_df

    main_cat_col = find_col(inv_df, 'Main Category')
    if not main_cat_col:
        return inv_df  # can't filter, return as-is

    mask = inv_df[main_cat_col].astype(str).str.strip().str.lower() == selected_category.lower()
    return inv_df[mask].copy()


# ── KPI calculation ───────────────────────────────────────────────────────────

def calculate_kpis(main_df, inv_df, selected_category='All'):
    kpis = {}

    status_col = find_col(main_df, 'Status')
    working = main_df.copy()
    if status_col:
        working = working[~working[status_col].astype(str).str.lower().str.contains('cancel', na=False)]

    qty_col    = find_col(working, 'Qty')
    sales_col  = find_col(working, 'Final Sales Price (usd)', 'FINAL PRICE')
    pl_usd_col = find_col(working, 'P&L Amt USD', 'P&L Amt')
    pl_pct_col = find_col(working, 'P&L%')

    kpis['Total Qty Sold']  = pd.to_numeric(working[qty_col],    errors='coerce').sum() if qty_col    else 0
    kpis['Total Sales USD'] = pd.to_numeric(working[sales_col],  errors='coerce').sum() if sales_col  else 0
    kpis['PL Amount USD']   = pd.to_numeric(working[pl_usd_col], errors='coerce').sum() if pl_usd_col else 0

    if pl_pct_col and sales_col:
        pct_vals  = pd.to_numeric(working[pl_pct_col], errors='coerce')
        sale_vals = pd.to_numeric(working[sales_col],  errors='coerce')
        mask = pct_vals.notna() & sale_vals.notna() & (sale_vals != 0)
        if mask.any():
            raw_pct = (pct_vals[mask] * sale_vals[mask]).sum() / sale_vals[mask].sum()
        else:
            raw_pct = pct_vals.mean() if not pct_vals.isna().all() else 0
        kpis['Net PL %'] = raw_pct * 100
    elif kpis['Total Sales USD']:
        kpis['Net PL %'] = (kpis['PL Amount USD'] / kpis['Total Sales USD']) * 100
    else:
        kpis['Net PL %'] = 0

    # ── Filter inv by selected category for balance ───────────────────────────
    filtered_inv = filter_inv_by_category(inv_df, selected_category)
    tb_col = find_col(filtered_inv, 'Total Balance')
    if tb_col:
        kpis['Total Balance'] = pd.to_numeric(filtered_inv[tb_col], errors='coerce').sum()
    else:
        kpis['Total Balance'] = 0

    kpis['Sales %'] = (kpis['Total Qty Sold'] / kpis['Total Balance'] * 100) if kpis['Total Balance'] else 0

    date_col = find_col(main_df, 'Date1')
    if date_col:
        try:
            non_null = main_df[date_col].dropna()
            kpis['Report Date'] = non_null.iloc[0] if not non_null.empty else 'N/A'
        except Exception:
            kpis['Report Date'] = 'N/A'
    else:
        kpis['Report Date'] = 'N/A'

    return kpis


def kpi_card(title, value, fmt='number'):
    if fmt == 'usd':
        v = f"${safe_num(value):,.2f}"
    elif fmt == 'pct':
        v = f"{safe_num(value):.2f}%"
    else:
        v = f"{safe_num(value):,.0f}"
    return f"""<div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{v}</div>
    </div>"""


# ── Aggregation — returns RAW NUMERIC DataFrames ──────────────────────────────

def aggregate_sales(df, group_col, qty_col, sales_col, pl_usd_col, pl_pct_col, status_col):
    work = df.copy()
    if status_col and status_col in work.columns:
        work = work[~work[status_col].astype(str).str.lower().str.contains('cancel', na=False)]

    agg_dict = {}
    for src, dst in [(qty_col, COL_QTY), (sales_col, COL_SALES), (pl_usd_col, COL_PL_USD)]:
        if src and src in work.columns:
            work[src] = pd.to_numeric(work[src], errors='coerce')
            agg_dict[dst] = (src, 'sum')

    if not agg_dict:
        return pd.DataFrame()

    result = work.groupby(group_col, dropna=False).agg(
        **{k: v for k, v in agg_dict.items()}
    ).reset_index()

    for col in [COL_QTY, COL_SALES, COL_PL_USD]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce')

    if pl_pct_col and pl_pct_col in work.columns and sales_col and sales_col in work.columns:
        work[pl_pct_col] = pd.to_numeric(work[pl_pct_col], errors='coerce')
        tmp = work[[group_col, sales_col, pl_pct_col]].dropna()
        tmp = tmp[tmp[sales_col] != 0].copy()
        if not tmp.empty:
            tmp['_w'] = tmp[sales_col] * tmp[pl_pct_col]
            wt = tmp.groupby(group_col).agg(ws=('_w', 'sum'), ts=(sales_col, 'sum')).reset_index()
            wt[COL_NET_PL] = (wt['ws'] / wt['ts'].replace(0, np.nan)) * 100
            result = result.merge(wt[[group_col, COL_NET_PL]], on=group_col, how='left')
            result[COL_NET_PL] = pd.to_numeric(result[COL_NET_PL], errors='coerce')

    return result


def build_subcat_table(filtered_main, inv_df, qty_col, sales_col,
                       pl_usd_col, pl_pct_col, status_col):
    sub_col_main = find_subcategory_col(filtered_main)
    sub_col_inv  = find_subcategory_col(inv_df)
    tb_col       = find_col(inv_df, 'Total Balance')

    if not sub_col_main:
        return None, f"Sub-Category col not found in main. Cols: {list(filtered_main.columns)}"
    if not sub_col_inv:
        return None, f"Sub-Category col not found in new INV. Cols: {list(inv_df.columns)}"
    if not tb_col:
        return None, f"Total Balance col not found in new INV. Cols: {list(inv_df.columns)}"

    agg = aggregate_sales(filtered_main, sub_col_main,
                          qty_col, sales_col, pl_usd_col, pl_pct_col, status_col)
    if agg.empty:
        return pd.DataFrame(), None

    inv_work = inv_df[[sub_col_inv, tb_col]].copy()
    inv_work[tb_col] = pd.to_numeric(inv_work[tb_col], errors='coerce').fillna(0)
    inv_work['_key'] = inv_work[sub_col_inv].astype(str).apply(normalise)

    bal = (inv_work.groupby('_key')[tb_col]
           .sum().reset_index()
           .rename(columns={tb_col: COL_BALANCE}))

    agg['_key'] = agg[sub_col_main].astype(str).apply(normalise)
    merged = agg.merge(bal, on='_key', how='left')
    merged[COL_BALANCE] = pd.to_numeric(merged[COL_BALANCE], errors='coerce').fillna(0)
    merged = merged.drop(columns=['_key'])

    return merged, None


# ── Sort (on raw numbers) then format for display ─────────────────────────────

def sort_and_display(raw_df, sort_col, ascending, max_rows):
    df = raw_df.copy()

    if sort_col in df.columns:
        df[sort_col] = pd.to_numeric(df[sort_col], errors='coerce')
        df = df.sort_values(sort_col, ascending=ascending, na_position='last')

    df = df.head(max_rows).reset_index(drop=True)

    for col in df.columns:
        if df[col].dtype == object:
            continue
        if col == COL_SALES or col == COL_PL_USD:
            df[col] = df[col].apply(fmt_usd)
        elif col == COL_QTY:
            df[col] = df[col].apply(fmt_qty)
        elif col == COL_NET_PL:
            df[col] = df[col].apply(fmt_pct)
        elif col == COL_BALANCE:
            df[col] = df[col].apply(fmt_qty)

    return df


# ── Render table ──────────────────────────────────────────────────────────────

def render_table_with_scroll(display_df, table_height=420):
    st.dataframe(
        display_df,
        height=table_height,
        use_container_width=True,
        hide_index=True
    )


# ── Main app ──────────────────────────────────────────────────────────────────

def main():
    st.markdown('<div class="main-title">👟 Sales Analytics Dashboard</div>',
                unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "📤 Upload Excel File (.xlsx)", type=['xlsx', 'xls'],
        help="Workbook must contain 'main' and 'new INV' sheets"
    )

    if uploaded_file is None:
        st.info("👆 Please upload your Excel workbook to begin analysis.")
        with st.expander("📋 Expected Sheet Structure"):
            st.markdown("""
**Sheet: `main`** — transaction rows  
Key columns: `SELLER SKU`, `Date`, `Qty`, `type` (category), `Sub- Category`, `Season`,
`Channel`, `Country`, `Status`, `Final Sales Price (usd)`, `P&L Amt USD`, `P&L%`

**Sheet: `new INV`** — inventory snapshot  
Columns: `Master Sku`, `Sum`, `Main Category` (Footwear / Apparel), `Category`, `Sub- Category`, `Qty`, `Todays order`, `Total Balance`
            """)
        return

    main_df, inv_df = load_data(uploaded_file)
    if main_df is None or inv_df is None:
        return

    with st.expander("🔍 Column Detection Debug"):
        st.write("**main columns:**", list(main_df.columns))
        st.write("**new INV columns:**", list(inv_df.columns))
        sub_m = find_subcategory_col(main_df)
        sub_i = find_subcategory_col(inv_df)
        tb    = find_col(inv_df, 'Total Balance')
        tc    = find_type_col(main_df)
        mc    = find_col(inv_df, 'Main Category')
        st.write(f"Sub-Category in main → `{sub_m}` | in new INV → `{sub_i}` | Total Balance → `{tb}`")
        st.write(f"Type/Category col in main → `{tc}` | Main Category in new INV → `{mc}`")
        if sub_i and tb:
            st.write("Sample new INV:", inv_df[[sub_i, tb]].dropna().head(10).to_dict('records'))

    status_col  = find_col(main_df, 'Status')
    qty_col     = find_col(main_df, 'Qty')
    sales_col   = find_col(main_df, 'Final Sales Price (usd)', 'FINAL PRICE')
    pl_usd_col  = find_col(main_df, 'P&L Amt USD', 'P&L Amt')
    pl_pct_col  = find_col(main_df, 'P&L%')
    season_col  = find_col(main_df, 'Season')
    channel_col = find_col(main_df, 'Channel')
    country_col = find_col(main_df, 'Country')
    type_col    = find_type_col(main_df)   # ← the "type" / category column

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Display Settings")
        st.markdown("#### 🗂️ Category")

        # ── Category filter (type col in main / Main Category in new INV) ─────
        sel_category = 'All'
        if type_col:
            # Get unique values from the type column — typically Footwear, Apparel
            cat_values = sorted(main_df[type_col].dropna().astype(str).str.strip().unique().tolist())
            cat_options = ['All'] + cat_values
            sel_category = st.selectbox(
                "Category",
                cat_options,
                help="Filters both Sales (main) and Inventory (new INV → Main Category)"
            )
        else:
            # Fallback: read directly from new INV Main Category column
            mc_col = find_col(inv_df, 'Main Category')
            if mc_col:
                cat_values = sorted(inv_df[mc_col].dropna().astype(str).str.strip().unique().tolist())
                cat_options = ['All'] + cat_values
                sel_category = st.selectbox(
                    "Category (from Inventory)",
                    cat_options,
                    help="Filters Inventory by Main Category"
                )
            else:
                st.warning("No category/type column detected.")

        st.markdown("---")
        st.markdown("#### 🔍 Filters")

        sel_status = 'All'
        if status_col:
            statuses = ['All'] + sorted(main_df[status_col].dropna().unique().tolist())
            sel_status = st.selectbox("Status", statuses)

        sel_channel = 'All'
        if channel_col:
            channels = ['All'] + sorted(main_df[channel_col].dropna().unique().tolist())
            sel_channel = st.selectbox("Channel", channels)

        sel_country = 'All'
        if country_col:
            countries = ['All'] + sorted(main_df[country_col].dropna().unique().tolist())
            sel_country = st.selectbox("Country", countries)

        st.markdown("---")
        st.markdown("#### 📐 Table Rows")
        subcat_rows = st.slider("Sub-Category rows", 1, 30, 15)
        season_rows = st.slider("Season rows",       1, 30, 10)

        st.markdown("---")
        st.markdown("#### 🔄 Sort Tables By")
        sort_col_sel = st.selectbox(
            "Column",
            options=[COL_QTY, COL_SALES, COL_PL_USD, COL_NET_PL, COL_BALANCE],
            index=1,
            format_func=lambda x: {
                COL_QTY:     f"📦 {COL_QTY}",
                COL_SALES:   f"💰 {COL_SALES}",
                COL_PL_USD:  f"📊 {COL_PL_USD}",
                COL_NET_PL:  f"📈 {COL_NET_PL}",
                COL_BALANCE: f"🏦 {COL_BALANCE} (Sub-Cat only)",
            }.get(x, x)
        )
        sort_order = st.radio("Order", ["Descending (High to Low)", "Ascending (Low to High)"], index=0)
        ascending  = sort_order.startswith("Ascending")

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = main_df.copy()

    # Filter main by type/category
    if sel_category != 'All' and type_col:
        filtered = filtered[
            filtered[type_col].astype(str).str.strip().str.lower() == sel_category.lower()
        ]

    if sel_status  != 'All' and status_col:
        filtered = filtered[filtered[status_col]  == sel_status]
    if sel_channel != 'All' and channel_col:
        filtered = filtered[filtered[channel_col] == sel_channel]
    if sel_country != 'All' and country_col:
        filtered = filtered[filtered[country_col] == sel_country]

    # Filter inventory by Main Category matching selected_category
    filtered_inv = filter_inv_by_category(inv_df, sel_category)

    # ── KPIs (use filtered main + filtered inv) ───────────────────────────────
    kpis = calculate_kpis(filtered, filtered_inv, sel_category)

    # ── Title & KPI cards ──────────────────────────────────────────────────────
    cat_label = sel_category if sel_category != 'All' else 'All Categories'
    st.markdown(
        f'<div class="report-title">Sales Report For Malaysia — {cat_label}</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    bal_label = f"Total Balance ({cat_label})"
    with c1: st.markdown(kpi_card("Total Qty Sold",    kpis['Total Qty Sold'],  'number'), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Total Sales (USD)", kpis['Total Sales USD'], 'usd'),    unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("P&L Amount (USD)",  kpis['PL Amount USD'],   'usd'),    unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Net P&L %",         kpis['Net PL %'],        'pct'),    unsafe_allow_html=True)
    with c5: st.markdown(kpi_card(bal_label,           kpis['Total Balance'],   'number'), unsafe_allow_html=True)
    with c6: st.markdown(kpi_card("Sales %",           kpis['Sales %'],         'pct'),    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar quick stats (after KPI calc)
    with st.sidebar:
        st.markdown("---")
        st.markdown("#### 📊 Quick Stats")
        st.write(f"**Category:** {cat_label}")
        st.write(f"**Report Date:** {kpis['Report Date']}")
        st.write(f"**Total Balance:** {kpis['Total Balance']:,.0f}")
        st.write(f"**Total Sales:** ${kpis['Total Sales USD']:,.2f}")
        st.write(f"**Net P&L %:** {kpis['Net PL %']:.2f}%")
        st.write(f"**Total Orders:** {len(filtered):,.0f}")

    # ── Build RAW numeric aggregations (use filtered_inv for balance) ──────────
    sub_raw, sub_err = build_subcat_table(
        filtered, filtered_inv, qty_col, sales_col, pl_usd_col, pl_pct_col, status_col
    )

    sea_raw = pd.DataFrame()
    if season_col:
        sea_raw = aggregate_sales(
            filtered, season_col, qty_col, sales_col, pl_usd_col, pl_pct_col, status_col
        )

    # ── Sort numerically, then format display copy ────────────────────────────
    sub_display = None
    if sub_raw is not None and not sub_raw.empty:
        sub_display = sort_and_display(sub_raw, sort_col_sel, ascending, subcat_rows)

    sea_display = None
    if not sea_raw.empty:
        sort_for_sea = sort_col_sel if sort_col_sel in sea_raw.columns else COL_SALES
        sea_display = sort_and_display(sea_raw, sort_for_sea, ascending, season_rows)

    # ── Render tables ─────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(f'<div class="card-title">Sub-Category Wise Sales — {cat_label}</div>',
                    unsafe_allow_html=True)
        if sub_err:
            st.warning(sub_err)
        elif sub_display is not None and not sub_display.empty:
            render_table_with_scroll(sub_display, table_height=420)
        else:
            st.warning("No sub-category data to display.")

    with col_right:
        st.markdown(f'<div class="card-title">Season Wise Sales — {cat_label}</div>',
                    unsafe_allow_html=True)
        if sea_display is not None and not sea_display.empty:
            render_table_with_scroll(sea_display, table_height=420)
        else:
            st.warning("Season data not available.")

    st.markdown("<br>")
    st.info(
        f"📊 Category: **{cat_label}** | Sorted by **{sort_col_sel}** ({sort_order}) | "
        f"Filters — Status: {sel_status} | Channel: {sel_channel} | Country: {sel_country}"
    )

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("### 📥 Export Options")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button("⬇️ Download Filtered Data", filtered.to_csv(index=False).encode(),
                           "filtered_main.csv", "text/csv")
    with e2:
        st.download_button("⬇️ Download Filtered Inventory", filtered_inv.to_csv(index=False).encode(),
                           "filtered_inventory.csv", "text/csv")
    with e3:
        kpi_text = (
            f"Sales Report For Malaysia — {cat_label}\n"
            f"Total Qty Sold          : {kpis['Total Qty Sold']:,.0f}\n"
            f"Total Sales (USD)       : ${kpis['Total Sales USD']:,.2f}\n"
            f"P&L Amount (USD)        : ${kpis['PL Amount USD']:,.2f}\n"
            f"Net P&L %               : {kpis['Net PL %']:.2f}%\n"
            f"Total Balance           : {kpis['Total Balance']:,.0f}\n"
            f"Sales %                 : {kpis['Sales %']:.2f}%\n"
        )
        if st.button("📋 Show KPI Summary"):
            st.code(kpi_text, language="text")


if __name__ == "__main__":
    main()
