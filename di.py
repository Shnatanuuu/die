import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import re

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# ─── Register Chinese font ──────────────────────────────────────────────────
try:
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    CHINESE_FONT = 'STSong-Light'
except Exception:
    CHINESE_FONT = 'Helvetica'

# ─── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Die Cut Test Report System",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Chinese cities ─────────────────────────────────────────────────────────
CHINESE_CITIES = {
    "Guangzhou": "广州", "Shenzhen": "深圳", "Dongguan": "东莞",
    "Foshan": "佛山", "Zhongshan": "中山", "Huizhou": "惠州",
    "Zhuhai": "珠海", "Jiangmen": "江门", "Zhaoqing": "肇庆",
    "Shanghai": "上海", "Beijing": "北京", "Suzhou": "苏州",
    "Hangzhou": "杭州", "Ningbo": "宁波", "Wenzhou": "温州",
    "Wuhan": "武汉", "Chengdu": "成都", "Chongqing": "重庆",
    "Tianjin": "天津", "Nanjing": "南京", "Xi'an": "西安",
    "Qingdao": "青岛", "Dalian": "大连", "Shenyang": "沈阳",
    "Changsha": "长沙", "Zhengzhou": "郑州", "Jinan": "济南",
    "Harbin": "哈尔滨", "Changchun": "长春", "Taiyuan": "太原",
    "Shijiazhuang": "石家庄", "Lanzhou": "兰州", "Xiamen": "厦门",
    "Fuzhou": "福州", "Nanning": "南宁", "Kunming": "昆明",
    "Guiyang": "贵阳", "Haikou": "海口", "Ürümqi": "乌鲁木齐",
    "Lhasa": "拉萨",
}

# ─── UI text dictionaries ───────────────────────────────────────────────────
ENGLISH_TEXTS = {
    "title": "Die Cut Test Report System",
    "basic_info": "Basic Information",
    "die_cut_test": "Die Cut Test",
    "batch_test": "Batches Test",
    "main_check": "Main Check Points",
    "tech_specs": "Technical Specifications",
    "test_results": "Test Results",
    "issues_solutions": "Issues & Solutions",
    "signatures": "Signatures",
    "generate_pdf": "🎯 Generate PDF Report",
    "download_pdf": "📥 Download PDF Report",
    "contract_no": "Contract No.",
    "brand": "Brand",
    "agent_factory": "Agent and Factory",
    "style_name": "Style Name",
    "qty": "QTY",
    "sales": "Sales",
    "factory_style": "Factory Style",
    "ship_date": "Ship Date",
    "size": "Size",
    "die_qty": "QTY (Die)",
    "batch_qty": "QTY (Batches)",
    "footer_text": "Die Cut Test Report System",
    "generate_success": "PDF Generated Successfully!",
    "fill_required": "Please fill in Contract No. and Style Name!",
    "creating_pdf": "Creating PDF report...",
    "pdf_details": "PDF Details",
    "report_language": "Report Language",
    "generated": "Generated",
    "location": "Location",
    "error_generating": "Error generating PDF",
    "select_location": "Select Location",
    "user_interface_language": "User Interface Language",
    "pdf_report_language": "PDF Report Language",
    "local_time": "Local Time",
    "quick_guide": "Quick Guide",
    "powered_by": "Powered by Streamlit",
    "copyright": "© 2025 - Die Cut Test Platform",
    "check_items": "Check Items",
    "comments": "Comments",
    "yes": "YES",
    "no": "NO",
    "pass_": "PASS",
    "fail_": "FAIL",
    "client_standard": "Client's Standard",
    "result": "Result",
    "disclaimer": "Disclaimer",
    "factory_rep": "Factory Representative",
    "gs_qc": "GS QC",
    "gs_tech": "Grand Step Technician",
    "area_manager": "Area Manager",
    "qa_manager": "QA Manager",
    "die_cut_date": "Die Cut Date",
    "batch_test_date": "Batch Test Date",
    "last_no_correct": "Last No. Correct",
    "color_matches": "Color matches cfm sample",
    "tack_free": "TACK FREE POLICY FOLLOW?",
    "tech_comments_completed": "All Tech Report Comments ALREADY COMPLETED or No?",
    "size_run_match": "Size Run Match Order",
    "fitting_correct": "Fitting Correct",
    "top_sample_sent": "Already Sent top sample to office?",
    "tech_specs_compare": "Check the shoe Tech Specifications compare to Tech Report same or not?",
    "same": "SAME",
    "if_not_same": "IF not same, Description simply and within the Tolerance or not?",
    "sole_bonding": "Sole Bonding",
    "top_piece": "Top piece attachment strength",
    "straps_strength": "Strength of Straps & buckle",
    "heel_attachment": "Heel Attachment",
    "insole_perment": "Insole Perment set at 400N",
    "toe_post": "Toe Post Attachment",
    "signature_date": "Date",
    "updated_2022": "Updated 2022.8.30",
    "disclaimer_text": "Note: This review information does not release the factory from any responsibilities in the event of claims being received from our customer.",
    "add_size": "Add Size",
    "remove_size": "Remove",
    "size_table_title": "Size & Quantity Details",
    "total": "Total",
    "tab_basic": "📋 Basic Info",
    "tab_check": "✓ Check Points",
    "tab_test": "🧪 Test Results",
    "tab_sign": "✍️ Signatures",
    "ui_lang": "User Interface Language",
    "pdf_lang": "PDF Report Language",
    "translation_active": "Translation API: Active",
    "translation_off": "Translation API: Not Configured",
}

MANDARIN_TEXTS = {
    "title": "斩刀试做报告系统",
    "basic_info": "基本信息",
    "die_cut_test": "斩刀试做",
    "batch_test": "小批量试做",
    "main_check": "主要核查内容",
    "tech_specs": "技术规格",
    "test_results": "测试结果",
    "issues_solutions": "问题与解决方案",
    "signatures": "签名",
    "generate_pdf": "🎯 生成PDF报告",
    "download_pdf": "📥 下载PDF报告",
    "contract_no": "订单号",
    "brand": "商标",
    "agent_factory": "贸易商和工厂",
    "style_name": "型体",
    "qty": "数量",
    "sales": "销售",
    "factory_style": "工厂款号",
    "ship_date": "交期",
    "size": "试做号码数",
    "die_qty": "数量(斩刀)",
    "batch_qty": "数量(小批量)",
    "footer_text": "斩刀试做报告系统",
    "generate_success": "PDF生成成功！",
    "fill_required": "请填写订单号和型体！",
    "creating_pdf": "正在创建PDF报告...",
    "pdf_details": "PDF详情",
    "report_language": "报告语言",
    "generated": "生成时间",
    "location": "地点",
    "error_generating": "生成PDF错误",
    "select_location": "选择地点",
    "user_interface_language": "用户界面语言",
    "pdf_report_language": "PDF报告语言",
    "local_time": "本地时间",
    "quick_guide": "快速指南",
    "powered_by": "由Streamlit驱动",
    "copyright": "© 2025 - 斩刀测试平台",
    "check_items": "检查项目",
    "comments": "建议",
    "yes": "是",
    "no": "否",
    "pass_": "通过",
    "fail_": "不通过",
    "client_standard": "客人标准",
    "result": "结果",
    "disclaimer": "免责声明",
    "factory_rep": "工厂代表",
    "gs_qc": "志途验货员",
    "gs_tech": "志途师傅",
    "area_manager": "地区经理",
    "qa_manager": "品管经理",
    "die_cut_date": "斩刀日期",
    "batch_test_date": "小批量日期",
    "last_no_correct": "楦头编号正确",
    "color_matches": "颜色和确认样相符",
    "tack_free": "无钉作业?",
    "tech_comments_completed": "所有技术报告上师傅提的问题点是否都已改善？",
    "size_run_match": "配码和订单是否相符",
    "fitting_correct": "试穿是否正确",
    "top_sample_sent": "大货样已寄回公司?",
    "tech_specs_compare": "技术数据，规格，对比全套报告是否一致",
    "same": "一致",
    "if_not_same": "如果不一样，简单描述，是否在公差接受的范围内",
    "sole_bonding": "底拉力",
    "top_piece": "天皮拉脱",
    "straps_strength": "功能性条待拉脱",
    "heel_attachment": "跟拉脱",
    "insole_perment": "中底钢芯变形率",
    "toe_post": "夹指带拉脱",
    "signature_date": "日期",
    "updated_2022": "更新 2022.8.30",
    "disclaimer_text": "此报表不免除我客人收到货后索赔而引起的货物供应商(工厂)的任何责任.",
    "add_size": "添加尺码",
    "remove_size": "删除",
    "size_table_title": "尺码与数量详情",
    "total": "总计",
    "tab_basic": "📋 基本信息",
    "tab_check": "✓ 核查内容",
    "tab_test": "🧪 测试结果",
    "tab_sign": "✍️ 签名",
    "ui_lang": "界面语言",
    "pdf_lang": "PDF报告语言",
    "translation_active": "翻译API: 已启用",
    "translation_off": "翻译API: 未配置",
}

def t(key):
    lang = st.session_state.get('ui_language', 'en')
    if lang == 'zh':
        return MANDARIN_TEXTS.get(key, ENGLISH_TEXTS.get(key, key))
    return ENGLISH_TEXTS.get(key, key)

def pt(key, pdf_lang):
    if pdf_lang == 'zh':
        return MANDARIN_TEXTS.get(key, ENGLISH_TEXTS.get(key, key))
    return ENGLISH_TEXTS.get(key, key)

# ─── Translation ─────────────────────────────────────────────────────────────
def translate_text_api(text, target_language="zh"):
    if not text or not str(text).strip():
        return text or ''
    if not openai_client:
        return text
    text = str(text)
    cache_key = f"{text}|{target_language}"
    if cache_key in st.session_state.get('translation_cache', {}):
        return st.session_state.translation_cache[cache_key]
    clean = text.replace(' ', '').replace('-', '').replace('/', '')
    if clean.isdigit() or re.match(r'^[A-Za-z]*\d+[A-Za-z]*$', clean):
        return text
    if re.search(r'[\u4e00-\u9fff]', text):
        return text
    try:
        lang_name = "Simplified Chinese" if target_language == "zh" else "English"
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate to {lang_name}. Preserve numbers, codes, measurements. Return ONLY the translation."},
                {"role": "user", "content": text}
            ],
            temperature=0.1, max_tokens=500
        )
        result = resp.choices[0].message.content.strip()
        if 'translation_cache' not in st.session_state:
            st.session_state.translation_cache = {}
        st.session_state.translation_cache[cache_key] = result
        return result
    except Exception:
        return text

# ─── Session state ────────────────────────────────────────────────────────────
for key, val in [
    ('ui_language', 'en'),
    ('pdf_language', 'en'),
    ('selected_city', 'Shanghai'),
    ('translation_cache', {}),
    ('size_data', []),
    ('english_values', {
        'contract_no': '', 'brand': '', 'agent_factory': '', 'style_name': '',
        'qty': '', 'sales': '', 'factory_style': '',
        'last_no_comments': '', 'color_comments': '', 'tack_free_comments': '',
        'tech_specs_comments': '', 'size_run_comments': '', 'fitting_comments': '',
        'top_sample_comments': '', 'tech_comments_description': '',
        'sole_bonding_result': '', 'top_piece_result': '', 'straps_strength_result': '',
        'heel_attachment_result': '', 'insole_perment_result': '', 'toe_post_result': '',
        'factory_representative': '', 'gs_qc': '', 'grandstep_technician': '',
        'area_manager': '', 'qa_manager': ''
    }),
]:
    if key not in st.session_state:
        st.session_state[key] = val

def get_ev(field_key):
    return st.session_state.english_values.get(field_key, '')

def set_ev(field_key, value):
    if value is None or str(value).strip() == '':
        st.session_state.english_values[field_key] = ''
        return
    v = str(value).strip()
    if st.session_state.ui_language == 'en':
        st.session_state.english_values[field_key] = v
    else:
        has_cjk = any('\u4e00' <= c <= '\u9fff' for c in v)
        if has_cjk:
            st.session_state.english_values[field_key] = translate_text_api(v, 'en')
        else:
            st.session_state.english_values[field_key] = v

def display_val(field_key):
    ev = get_ev(field_key)
    if not ev:
        return ''
    if st.session_state.ui_language == 'en':
        return ev
    return translate_text_api(ev, 'zh')

def pdf_val(field_key, pdf_lang):
    ev = get_ev(field_key)
    if not ev:
        return ''
    if pdf_lang == 'en':
        return ev
    return translate_text_api(ev, 'zh')

def add_size_row():
    st.session_state.size_data.append({'size': '', 'die_qty': '', 'batch_qty': ''})

def remove_size_row(index):
    if 0 <= index < len(st.session_state.size_data):
        st.session_state.size_data.pop(index)

# ══════════════════════════════════════════════════════════════════════════════
#  PDF DESIGN TOKENS  (matching the Production Risk Assessment style)
# ══════════════════════════════════════════════════════════════════════════════
C_PRIMARY   = colors.HexColor('#1a1a2e')
C_ACCENT    = colors.HexColor('#e94560')
C_ACCENT2   = colors.HexColor('#0f3460')
C_LIGHT     = colors.HexColor('#f0f4ff')
C_WHITE     = colors.white
C_GREY_TEXT = colors.HexColor('#555555')
C_GREY_LINE = colors.HexColor('#dddddd')
C_GREEN     = colors.HexColor('#27ae60')
C_RED       = colors.HexColor('#e74c3c')
C_ORANGE    = colors.HexColor('#f39c12')

PAGE_W, PAGE_H = A4
HEADER_H  = 60
FOOTER_H  = 36
MARGIN_L  = 40
MARGIN_R  = 40
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


def _font(pdf_lang, bold=False):
    if pdf_lang == "zh":
        return CHINESE_FONT
    return 'Helvetica-Bold' if bold else 'Helvetica'


# ─── Character & text width helpers ──────────────────────────────────────────
def _char_width(ch, font_size):
    cp = ord(ch)
    if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or
            0x3000 <= cp <= 0x303F or 0xFF00 <= cp <= 0xFFEF or
            0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF):
        return font_size * 1.0
    return font_size * 0.52


def _text_width(text, font_size):
    return sum(_char_width(ch, font_size) for ch in str(text))


def _wrap_text(text, max_width, font_size):
    if not text or not str(text).strip():
        return ["—"]
    text = str(text)
    lines = []
    for paragraph in text.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split()
        current, current_w = "", 0.0
        for word in words:
            word_w = _text_width(word, font_size)
            space_w = _text_width(" ", font_size)
            if current == "":
                if word_w > max_width:
                    for ch in word:
                        ch_w = _char_width(ch, font_size)
                        if current_w + ch_w > max_width and current:
                            lines.append(current); current = ch; current_w = ch_w
                        else:
                            current += ch; current_w += ch_w
                else:
                    current, current_w = word, word_w
            else:
                test_w = current_w + space_w + word_w
                if test_w <= max_width:
                    current += " " + word; current_w = test_w
                else:
                    lines.append(current)
                    if word_w > max_width:
                        current, current_w = "", 0.0
                        for ch in word:
                            ch_w = _char_width(ch, font_size)
                            if current_w + ch_w > max_width and current:
                                lines.append(current); current = ch; current_w = ch_w
                            else:
                                current += ch; current_w += ch_w
                    else:
                        current, current_w = word, word_w
        if current:
            lines.append(current)
    return lines if lines else ["—"]


# ─── Shared drawing primitives ────────────────────────────────────────────────
def draw_page_frame(c, page_num, total_pages, pdf_lang, city, city_zh, gen_time):
    w, h = PAGE_W, PAGE_H
    # Header bar
    c.setFillColor(C_PRIMARY)
    c.rect(0, h - HEADER_H, w, HEADER_H, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.rect(0, h - HEADER_H, 6, HEADER_H, fill=1, stroke=0)
    fn = _font(pdf_lang, bold=True)
    header_l = "Grand Step (H.K.) Ltd"
    header_r = "斩刀试做报告" if pdf_lang == "zh" else "DIE CUT TEST REPORT"
    c.setFillColor(C_WHITE); c.setFont(fn, 13)
    c.drawString(MARGIN_L, h - HEADER_H + 22, header_l)
    c.setFont(_font(pdf_lang), 9)
    c.drawRightString(w - MARGIN_R, h - HEADER_H + 22, header_r)
    # Footer bar
    c.setFillColor(C_PRIMARY)
    c.rect(0, 0, w, FOOTER_H, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.rect(0, FOOTER_H - 3, w, 3, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang), 7.5)
    loc_str  = f"地点: {city} ({city_zh})" if pdf_lang == "zh" else f"Location: {city}"
    pg_str   = f"第 {page_num} 页 / 共 {total_pages} 页" if pdf_lang == "zh" else f"Page {page_num} of {total_pages}"
    time_str = f"生成时间: {gen_time}" if pdf_lang == "zh" else f"Generated: {gen_time}"
    c.drawString(MARGIN_L, 13, loc_str)
    c.drawCentredString(w / 2, 13, time_str)
    c.drawRightString(w - MARGIN_R, 13, pg_str)


def draw_section_header(c, y, label, pdf_lang):
    bar_h = 22
    c.setFillColor(C_ACCENT2)
    c.roundRect(MARGIN_L, y - bar_h, CONTENT_W, bar_h, 4, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 10)
    c.drawString(MARGIN_L + 10, y - bar_h + 7, label)
    return y - bar_h - 8


def draw_kv_row(c, x, y, w, label, value, pdf_lang, shade=False):
    ROW_H = 18
    if shade:
        c.setFillColor(C_LIGHT)
        c.rect(x, y - ROW_H, w, ROW_H, fill=1, stroke=0)
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.4)
    c.line(x, y - ROW_H, x + w, y - ROW_H)
    lw = w * 0.38
    c.setFillColor(C_ACCENT2); c.setFont(_font(pdf_lang, bold=True), 8)
    c.drawString(x + 6, y - ROW_H + 6, str(label))
    c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), 8)
    c.drawString(x + lw + 6, y - ROW_H + 6, str(value)[:80])
    return y - ROW_H


def draw_two_col_kv(c, y, pairs, pdf_lang, shade_alt=True):
    col_w = (CONTENT_W - 10) / 2
    for i, (l1, v1, l2, v2) in enumerate(pairs):
        shade = (i % 2 == 0) and shade_alt
        draw_kv_row(c, MARGIN_L,              y, col_w, l1, v1, pdf_lang, shade)
        draw_kv_row(c, MARGIN_L + col_w + 10, y, col_w, l2, v2, pdf_lang, shade)
        y -= 18
    return y


def draw_text_block(c, y, label, text, pdf_lang, accent_color=None):
    if not text or not str(text).strip():
        text = "—"
    if accent_color is None:
        accent_color = C_ACCENT2
    FONT_SIZE = 8; LINE_H = 14; PADDING = 8; LABEL_H = 18
    lines = _wrap_text(text, CONTENT_W - 20, FONT_SIZE)
    total_text_h = len(lines) * LINE_H + PADDING * 2
    block_h = LABEL_H + total_text_h
    c.setFillColor(C_LIGHT)
    c.rect(MARGIN_L, y - block_h, CONTENT_W, block_h, fill=1, stroke=0)
    c.setFillColor(accent_color)
    c.rect(MARGIN_L, y - LABEL_H, CONTENT_W, LABEL_H, fill=1, stroke=0)
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.4)
    c.rect(MARGIN_L, y - block_h, CONTENT_W, block_h, fill=0, stroke=1)
    c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 8)
    c.drawString(MARGIN_L + 8, y - LABEL_H + 6, str(label))
    ty = y - LABEL_H - PADDING - LINE_H + 4
    c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), FONT_SIZE)
    for line in lines:
        if line:
            c.drawString(MARGIN_L + 10, ty, line)
        ty -= LINE_H
    return y - block_h - 6


def draw_check_table(c, y, rows, col_labels, pdf_lang):
    """
    Four-column check table: Item | YES | NO | Comments
    rows: list of (label, yes_bool, no_bool, comment_str)
    """
    COL_WIDTHS = [CONTENT_W * 0.42, CONTENT_W * 0.09, CONTENT_W * 0.09, CONTENT_W * 0.40]
    HDR_H = 22; ROW_PAD = 6; FONT_SIZE = 8; LINE_H = 13
    col_inner = [cw - 12 for cw in COL_WIDTHS]
    fn_b = _font(pdf_lang, bold=True); fn_r = _font(pdf_lang)
    # Header
    c.setFillColor(C_ACCENT)
    c.rect(MARGIN_L, y - HDR_H, CONTENT_W, HDR_H, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(fn_b, 8.5)
    cx = MARGIN_L + 6
    for i, lbl in enumerate(col_labels):
        c.drawString(cx, y - HDR_H + 8, lbl)
        cx += COL_WIDTHS[i]
    y -= HDR_H
    table_top = y
    for i, (item, yes_v, no_v, comment) in enumerate(rows):
        item_lines    = _wrap_text(item,    col_inner[0], FONT_SIZE)
        comment_lines = _wrap_text(comment, col_inner[3], FONT_SIZE)
        max_lines = max(len(item_lines), len(comment_lines), 1)
        row_h = max_lines * LINE_H + ROW_PAD * 2
        if i % 2 == 0:
            c.setFillColor(C_LIGHT)
            c.rect(MARGIN_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
        c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
        c.line(MARGIN_L, y - row_h, MARGIN_L + CONTENT_W, y - row_h)
        cx_sep = MARGIN_L
        for cw in COL_WIDTHS[:-1]:
            cx_sep += cw
            c.line(cx_sep, y, cx_sep, y - row_h)
        # Item text
        c.setFillColor(C_PRIMARY); c.setFont(fn_r, FONT_SIZE)
        ty = y - ROW_PAD - LINE_H + 3
        for ln in item_lines:
            if ln: c.drawString(MARGIN_L + 6, ty, ln)
            ty -= LINE_H
        # YES / NO ticks
        yes_x = MARGIN_L + COL_WIDTHS[0] + COL_WIDTHS[1] / 2
        no_x  = MARGIN_L + COL_WIDTHS[0] + COL_WIDTHS[1] + COL_WIDTHS[2] / 2
        mid_y = y - row_h / 2
        c.setFont(fn_b, 10)
        if yes_v:
            c.setFillColor(C_GREEN); c.drawCentredString(yes_x, mid_y - 4, "✓")
        if no_v:
            c.setFillColor(C_RED);   c.drawCentredString(no_x,  mid_y - 4, "✗")
        # Comment text
        c.setFillColor(C_PRIMARY); c.setFont(fn_r, FONT_SIZE)
        ty = y - ROW_PAD - LINE_H + 3
        for ln in comment_lines:
            if ln: c.drawString(MARGIN_L + COL_WIDTHS[0] + COL_WIDTHS[1] + COL_WIDTHS[2] + 6, ty, ln)
            ty -= LINE_H
        y -= row_h
    table_body_h = table_top - y
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
    c.rect(MARGIN_L, y, CONTENT_W, table_body_h, fill=0, stroke=1)
    return y - 6


def draw_test_results_table(c, y, rows, col_labels, pdf_lang):
    """
    Four-column test table: Item | Result | Client Standard | PASS/FAIL
    rows: list of (label, result_str, standard_str, pass_bool, fail_bool)
    """
    COL_WIDTHS = [CONTENT_W * 0.30, CONTENT_W * 0.18, CONTENT_W * 0.35, CONTENT_W * 0.17]
    HDR_H = 22; ROW_PAD = 6; FONT_SIZE = 8; LINE_H = 13
    col_inner = [cw - 12 for cw in COL_WIDTHS]
    fn_b = _font(pdf_lang, bold=True); fn_r = _font(pdf_lang)
    # Header
    c.setFillColor(C_ACCENT)
    c.rect(MARGIN_L, y - HDR_H, CONTENT_W, HDR_H, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(fn_b, 8.5)
    cx = MARGIN_L + 6
    for i, lbl in enumerate(col_labels):
        c.drawString(cx, y - HDR_H + 8, lbl)
        cx += COL_WIDTHS[i]
    y -= HDR_H
    table_top = y
    for i, (item, result, standard, pass_v, fail_v) in enumerate(rows):
        item_lines     = _wrap_text(item,     col_inner[0], FONT_SIZE)
        result_lines   = _wrap_text(result,   col_inner[1], FONT_SIZE)
        standard_lines = _wrap_text(standard, col_inner[2], FONT_SIZE)
        max_lines = max(len(item_lines), len(result_lines), len(standard_lines), 1)
        row_h = max_lines * LINE_H + ROW_PAD * 2
        if i % 2 == 0:
            c.setFillColor(C_LIGHT)
            c.rect(MARGIN_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
        c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
        c.line(MARGIN_L, y - row_h, MARGIN_L + CONTENT_W, y - row_h)
        cx_sep = MARGIN_L
        for cw in COL_WIDTHS[:-1]:
            cx_sep += cw
            c.line(cx_sep, y, cx_sep, y - row_h)
        ty = y - ROW_PAD - LINE_H + 3
        c.setFillColor(C_ACCENT2); c.setFont(fn_b, FONT_SIZE)
        for ln in item_lines:
            if ln: c.drawString(MARGIN_L + 6, ty, ln)
            ty -= LINE_H
        ty = y - ROW_PAD - LINE_H + 3
        c.setFillColor(C_PRIMARY); c.setFont(fn_r, FONT_SIZE)
        for ln in result_lines:
            if ln: c.drawString(MARGIN_L + COL_WIDTHS[0] + 6, ty, ln)
            ty -= LINE_H
        ty = y - ROW_PAD - LINE_H + 3
        for ln in standard_lines:
            if ln: c.drawString(MARGIN_L + COL_WIDTHS[0] + COL_WIDTHS[1] + 6, ty, ln)
            ty -= LINE_H
        mid_y = y - row_h / 2
        pf_x = MARGIN_L + COL_WIDTHS[0] + COL_WIDTHS[1] + COL_WIDTHS[2] + COL_WIDTHS[3] / 2
        if pass_v:
            c.setFillColor(C_GREEN); c.setFont(fn_b, 8.5)
            c.drawCentredString(pf_x, mid_y - 4, pt("pass_", pdf_lang))
        elif fail_v:
            c.setFillColor(C_RED);   c.setFont(fn_b, 8.5)
            c.drawCentredString(pf_x, mid_y - 4, pt("fail_", pdf_lang))
        else:
            c.setFillColor(C_GREY_TEXT); c.setFont(fn_r, 8)
            c.drawCentredString(pf_x, mid_y - 4, "—")
        y -= row_h
    table_body_h = table_top - y
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
    c.rect(MARGIN_L, y, CONTENT_W, table_body_h, fill=0, stroke=1)
    return y - 6


def draw_size_table(c, y, size_data, pdf_lang):
    """Three-column size/qty table."""
    if not size_data:
        return y
    COL_WIDTHS = [CONTENT_W / 3, CONTENT_W / 3, CONTENT_W / 3]
    HDR_H = 22; ROW_H = 18; FONT_SIZE = 8
    fn_b = _font(pdf_lang, bold=True); fn_r = _font(pdf_lang)
    headers = [pt("size", pdf_lang), pt("die_qty", pdf_lang), pt("batch_qty", pdf_lang)]
    c.setFillColor(C_ACCENT)
    c.rect(MARGIN_L, y - HDR_H, CONTENT_W, HDR_H, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(fn_b, 8.5)
    cx = MARGIN_L + 6
    for i, h in enumerate(headers):
        c.drawString(cx, y - HDR_H + 8, h)
        cx += COL_WIDTHS[i]
    y -= HDR_H
    table_top = y
    for i, item in enumerate(size_data):
        if i % 2 == 0:
            c.setFillColor(C_LIGHT)
            c.rect(MARGIN_L, y - ROW_H, CONTENT_W, ROW_H, fill=1, stroke=0)
        c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
        c.line(MARGIN_L, y - ROW_H, MARGIN_L + CONTENT_W, y - ROW_H)
        cx_sep = MARGIN_L + COL_WIDTHS[0]
        c.line(cx_sep, y, cx_sep, y - ROW_H)
        cx_sep += COL_WIDTHS[1]
        c.line(cx_sep, y, cx_sep, y - ROW_H)
        c.setFillColor(C_PRIMARY); c.setFont(fn_r, FONT_SIZE)
        c.drawString(MARGIN_L + 6,                                   y - ROW_H + 6, str(item.get('size', '') or '—'))
        c.drawString(MARGIN_L + COL_WIDTHS[0] + 6,                   y - ROW_H + 6, str(item.get('die_qty', '') or '—'))
        c.drawString(MARGIN_L + COL_WIDTHS[0] + COL_WIDTHS[1] + 6,   y - ROW_H + 6, str(item.get('batch_qty', '') or '—'))
        y -= ROW_H
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
    c.rect(MARGIN_L, y, CONTENT_W, table_top - y, fill=0, stroke=1)
    return y - 6


def draw_signatures_table(c, y, sigs, pdf_lang):
    """Signature rows: Label | Name | Date"""
    COL_WIDTHS = [CONTENT_W * 0.35, CONTENT_W * 0.40, CONTENT_W * 0.25]
    HDR_H = 22; ROW_H = 28; FONT_SIZE = 8
    fn_b = _font(pdf_lang, bold=True); fn_r = _font(pdf_lang)
    headers = [pt("check_items", pdf_lang),
               "姓名/签名" if pdf_lang == "zh" else "Name / Signature",
               "日期" if pdf_lang == "zh" else "Date"]
    c.setFillColor(C_ACCENT)
    c.rect(MARGIN_L, y - HDR_H, CONTENT_W, HDR_H, fill=1, stroke=0)
    c.setFillColor(C_WHITE); c.setFont(fn_b, 8.5)
    cx = MARGIN_L + 6
    for i, h in enumerate(headers):
        c.drawString(cx, y - HDR_H + 8, h)
        cx += COL_WIDTHS[i]
    y -= HDR_H
    table_top = y
    for i, (label, name, date_str) in enumerate(sigs):
        if i % 2 == 0:
            c.setFillColor(C_LIGHT)
            c.rect(MARGIN_L, y - ROW_H, CONTENT_W, ROW_H, fill=1, stroke=0)
        c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
        c.line(MARGIN_L, y - ROW_H, MARGIN_L + CONTENT_W, y - ROW_H)
        cx_sep = MARGIN_L + COL_WIDTHS[0]
        c.line(cx_sep, y, cx_sep, y - ROW_H)
        cx_sep += COL_WIDTHS[1]
        c.line(cx_sep, y, cx_sep, y - ROW_H)
        c.setFillColor(C_ACCENT2); c.setFont(fn_b, FONT_SIZE)
        c.drawString(MARGIN_L + 6, y - ROW_H + 10, str(label))
        # Signature line
        line_x1 = MARGIN_L + COL_WIDTHS[0] + 8
        line_x2 = MARGIN_L + COL_WIDTHS[0] + COL_WIDTHS[1] - 8
        if name:
            c.setFillColor(C_PRIMARY); c.setFont(fn_r, FONT_SIZE)
            c.drawString(line_x1, y - ROW_H + 10, str(name))
        c.setStrokeColor(C_PRIMARY); c.setLineWidth(0.8)
        c.line(line_x1, y - ROW_H + 6, line_x2, y - ROW_H + 6)
        c.setFillColor(C_PRIMARY); c.setFont(fn_r, FONT_SIZE)
        c.drawString(MARGIN_L + COL_WIDTHS[0] + COL_WIDTHS[1] + 6, y - ROW_H + 10, str(date_str))
        y -= ROW_H
    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
    c.rect(MARGIN_L, y, CONTENT_W, table_top - y, fill=0, stroke=1)
    return y - 6


# ══════════════════════════════════════════════════════════════════════════════
#  PDF GENERATION
# ══════════════════════════════════════════════════════════════════════════════
def generate_pdf():
    pdf_lang = st.session_state.pdf_language
    city     = st.session_state.selected_city
    city_zh  = CHINESE_CITIES.get(city, city)
    china_tz = pytz.timezone('Asia/Shanghai')
    now      = datetime.now(china_tz)
    gen_time = now.strftime('%Y-%m-%d %H:%M')

    def tx(text):
        if pdf_lang == "en" or not openai_client:
            return str(text) if text else ''
        return translate_text_api(str(text) if text else '', "zh")

    def loc(en_val, zh_val):
        return zh_val if pdf_lang == "zh" else en_val

    # ── Pull form data ────────────────────────────────────────────────────
    contract_no   = pdf_val('contract_no',    pdf_lang)
    brand_v       = pdf_val('brand',          pdf_lang)
    agent_factory = pdf_val('agent_factory',  pdf_lang)
    style_name    = pdf_val('style_name',     pdf_lang)
    qty_v         = pdf_val('qty',            pdf_lang)
    sales_v       = pdf_val('sales',          pdf_lang)
    factory_style = pdf_val('factory_style',  pdf_lang)

    die_cut_date_val   = st.session_state.get('die_cut_date',   now.date())
    batch_test_date_val = st.session_state.get('batch_test_date', now.date())
    ship_date_val      = st.session_state.get('ship_date',      now.date())
    signature_date_val = st.session_state.get('signature_date', now.date())

    def fmt_date(d):
        if d is None: return ''
        try:
            if pdf_lang == "zh": return d.strftime('%Y年%m月%d日')
            return d.strftime('%Y-%m-%d')
        except: return str(d)

    size_data = st.session_state.size_data

    # Check points
    check_items_data = [
        (pt("last_no_correct", pdf_lang),
         st.session_state.get("last_no_yes", False), st.session_state.get("last_no_no", False),
         tx(get_ev('last_no_comments'))),
        (pt("color_matches", pdf_lang),
         st.session_state.get("color_yes", False),   st.session_state.get("color_no", False),
         tx(get_ev('color_comments'))),
        (pt("tack_free", pdf_lang),
         st.session_state.get("tack_free_yes", False), st.session_state.get("tack_free_no", False),
         tx(get_ev('tack_free_comments'))),
        (pt("size_run_match", pdf_lang),
         st.session_state.get("size_run_yes", False), st.session_state.get("size_run_no", False),
         tx(get_ev('size_run_comments'))),
        (pt("fitting_correct", pdf_lang),
         st.session_state.get("fitting_yes", False),  st.session_state.get("fitting_no", False),
         tx(get_ev('fitting_comments'))),
        (pt("top_sample_sent", pdf_lang),
         st.session_state.get("top_sample_yes", False), st.session_state.get("top_sample_no", False),
         tx(get_ev('top_sample_comments'))),
        (pt("tech_comments_completed", pdf_lang),
         st.session_state.get("tech_comments_yes", False), st.session_state.get("tech_comments_no", False),
         tx(get_ev('tech_comments_description'))),
    ]

    tech_specs_same    = st.session_state.get('tech_specs_same', False)
    tech_specs_comment = tx(get_ev('tech_specs_comments'))

    # Test results
    if pdf_lang == "zh":
        standards = {
            "sole_bonding":      "边墙鞋≥2.0 N/mm\n其他≥3.0 N/mm",
            "heel_attachment":   "≥500N",
            "top_piece":         "≥140N",
            "insole_perment":    "400N时变形量≤15%",
            "straps_strength":   "女鞋≥200N\n男鞋≥250N\n弹性≥150N\n童鞋≥250N",
            "toe_post":          "EVA和橡胶≥150N\n其他≥200N",
        }
    else:
        standards = {
            "sole_bonding":      "Sidewall ≥2.0 N/mm\nOthers ≥3.0 N/mm",
            "heel_attachment":   "≥500N",
            "top_piece":         "≥140N",
            "insole_perment":    "Deformation ≤15% at 400N",
            "straps_strength":   "Women ≥200N / Men ≥250N\nElastic ≥150N / Children ≥250N",
            "toe_post":          "EVA & rubber ≥150N\nOther ≥200N",
        }

    test_rows_data = [
        (pt("sole_bonding",    pdf_lang), tx(get_ev('sole_bonding_result')),    standards["sole_bonding"],
         st.session_state.get("sole_bonding_pass", False),    st.session_state.get("sole_bonding_fail", False)),
        (pt("heel_attachment", pdf_lang), tx(get_ev('heel_attachment_result')), standards["heel_attachment"],
         st.session_state.get("heel_attachment_pass", False), st.session_state.get("heel_attachment_fail", False)),
        (pt("top_piece",       pdf_lang), tx(get_ev('top_piece_result')),       standards["top_piece"],
         st.session_state.get("top_piece_pass", False),       st.session_state.get("top_piece_fail", False)),
        (pt("insole_perment",  pdf_lang), tx(get_ev('insole_perment_result')),  standards["insole_perment"],
         st.session_state.get("insole_perment_pass", False),  st.session_state.get("insole_perment_fail", False)),
        (pt("straps_strength", pdf_lang), tx(get_ev('straps_strength_result')), standards["straps_strength"],
         st.session_state.get("straps_strength_pass", False), st.session_state.get("straps_strength_fail", False)),
        (pt("toe_post",        pdf_lang), tx(get_ev('toe_post_result')),        standards["toe_post"],
         st.session_state.get("toe_post_pass", False),        st.session_state.get("toe_post_fail", False)),
    ]

    # Signatures
    sig_date_str = fmt_date(signature_date_val)
    sigs = [
        (pt("factory_rep",   pdf_lang), tx(get_ev('factory_representative')), sig_date_str),
        (pt("gs_qc",         pdf_lang), tx(get_ev('gs_qc')),                  sig_date_str),
        (pt("gs_tech",       pdf_lang), tx(get_ev('grandstep_technician')),   sig_date_str),
        (pt("area_manager",  pdf_lang), tx(get_ev('area_manager')),           sig_date_str),
        (pt("qa_manager",    pdf_lang), tx(get_ev('qa_manager')),             sig_date_str),
    ]

    # ── Two-pass render ───────────────────────────────────────────────────
    def _build(buf_out, total_pages_known):
        c = rl_canvas.Canvas(buf_out, pagesize=A4)
        fn_b = _font(pdf_lang, bold=True)
        fn_r = _font(pdf_lang)
        page_counter = [1]

        def new_page():
            c.showPage()
            page_counter[0] += 1
            draw_page_frame(c, page_counter[0], total_pages_known, pdf_lang, city, city_zh, gen_time)
            return PAGE_H - HEADER_H - 20

        def maybe_new_page(y, min_space=120):
            if y < FOOTER_H + min_space:
                return new_page()
            return y

        # ── PAGE 1 ──────────────────────────────────────────────────────
        draw_page_frame(c, 1, total_pages_known, pdf_lang, city, city_zh, gen_time)
        y = PAGE_H - HEADER_H - 20

        # Cover banner
        c.setFillColor(C_PRIMARY)
        c.rect(MARGIN_L, y - 120, CONTENT_W, 120, fill=1, stroke=0)
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - 120, 8, 120, fill=1, stroke=0)
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - 6, CONTENT_W, 6, fill=1, stroke=0)

        c.setFillColor(C_WHITE); c.setFont(fn_b, 20)
        c.drawString(MARGIN_L + 24, y - 40, "Grand Step (H.K.) Ltd")
        c.setFont(fn_r, 11)
        c.setFillColor(colors.HexColor('#aab8ff'))
        c.drawString(MARGIN_L + 24, y - 60,
                     "斩刀试做报告" if pdf_lang == "zh" else "DIE CUT TEST REPORT")

        pill_items = [
            (loc("Die Cut Date", "斩刀日期"), fmt_date(die_cut_date_val)),
            (loc("Location", "地点"), f"{city} {city_zh}" if pdf_lang == "zh" else city),
            (loc("Language", "语言"), "中文" if pdf_lang == "zh" else "English"),
        ]
        px = MARGIN_L + 24
        for lbl, val in pill_items:
            c.setFillColor(colors.HexColor('#0d2244'))
            pill_w = _text_width(f"{lbl}: {val}", 7) + 16
            c.roundRect(px, y - 108, pill_w, 16, 4, fill=1, stroke=0)
            c.setFillColor(colors.HexColor('#aab8ff')); c.setFont(fn_b, 7)
            c.drawString(px + 8, y - 100, f"{lbl}:")
            lbl_w = _text_width(lbl, 7) + 8
            c.setFillColor(C_WHITE); c.setFont(fn_r, 7)
            c.drawString(px + 8 + lbl_w, y - 100, val)
            px += pill_w + 8
        y -= 136

        # ── 1. BASIC INFORMATION ─────────────────────────────────────────
        y = draw_section_header(c, y, loc("1. BASIC INFORMATION", "1. 基本信息"), pdf_lang)

        pairs = [
            (loc("Contract No.", "订单号"),      contract_no or '—',
             loc("Brand", "商标"),               brand_v or '—'),
            (loc("Agent / Factory", "贸易商/工厂"), agent_factory or '—',
             loc("Style Name", "型体"),          style_name or '—'),
            (loc("QTY", "数量"),                 qty_v or '—',
             loc("Sales", "销售"),               sales_v or '—'),
            (loc("Factory Style", "工厂款号"),   factory_style or '—',
             loc("Ship Date", "交期"),           fmt_date(ship_date_val)),
            (loc("Die Cut Date", "斩刀日期"),    fmt_date(die_cut_date_val),
             loc("Batch Test Date", "小批量日期"), fmt_date(batch_test_date_val)),
        ]
        y = draw_two_col_kv(c, y, pairs, pdf_lang)
        y -= 10

        # ── 2. SIZE & QTY TABLE ──────────────────────────────────────────
        y = maybe_new_page(y, 100)
        y = draw_section_header(c, y, loc("2. SIZE & QUANTITY", "2. 尺码与数量"), pdf_lang)
        if size_data:
            y = draw_size_table(c, y, size_data, pdf_lang)
        else:
            c.setFillColor(C_GREY_TEXT); c.setFont(fn_r, 8)
            c.drawString(MARGIN_L + 6, y - 14, loc("No size data entered.", "未输入尺码数据。"))
            y -= 20
        y -= 6

        # ── 3. MAIN CHECK POINTS ─────────────────────────────────────────
        y = maybe_new_page(y, 160)
        y = draw_section_header(c, y, loc("3. MAIN CHECK POINTS", "3. 主要核查内容"), pdf_lang)

        check_col_labels = [
            pt("check_items", pdf_lang),
            pt("yes", pdf_lang),
            pt("no", pdf_lang),
            pt("comments", pdf_lang),
        ]

        # Render check table row-by-row with page breaks
        COL_WIDTHS_CHK = [CONTENT_W * 0.42, CONTENT_W * 0.09, CONTENT_W * 0.09, CONTENT_W * 0.40]
        HDR_H_CHK = 22; ROW_PAD_CHK = 6; FS_CHK = 8; LH_CHK = 13
        col_inner_chk = [cw - 12 for cw in COL_WIDTHS_CHK]

        def draw_check_header(cy):
            c.setFillColor(C_ACCENT)
            c.rect(MARGIN_L, cy - HDR_H_CHK, CONTENT_W, HDR_H_CHK, fill=1, stroke=0)
            c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 8.5)
            cx2 = MARGIN_L + 6
            for ii, lbl in enumerate(check_col_labels):
                c.drawString(cx2, cy - HDR_H_CHK + 8, lbl)
                cx2 += COL_WIDTHS_CHK[ii]
            return cy - HDR_H_CHK

        y = draw_check_header(y)
        chk_table_top = y

        for ri, (item, yes_v, no_v, comment) in enumerate(check_items_data):
            item_lines    = _wrap_text(item,    col_inner_chk[0], FS_CHK)
            comment_lines = _wrap_text(comment, col_inner_chk[3], FS_CHK)
            max_lines = max(len(item_lines), len(comment_lines), 1)
            row_h = max_lines * LH_CHK + ROW_PAD_CHK * 2
            if y - row_h < FOOTER_H + 20:
                tb_h = chk_table_top - y
                if tb_h > 0:
                    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
                    c.rect(MARGIN_L, y, CONTENT_W, tb_h, fill=0, stroke=1)
                y = new_page()
                y = draw_check_header(y)
                chk_table_top = y
            if ri % 2 == 0:
                c.setFillColor(C_LIGHT)
                c.rect(MARGIN_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
            c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
            c.line(MARGIN_L, y - row_h, MARGIN_L + CONTENT_W, y - row_h)
            cx_sep = MARGIN_L
            for cw in COL_WIDTHS_CHK[:-1]:
                cx_sep += cw
                c.line(cx_sep, y, cx_sep, y - row_h)
            ty = y - ROW_PAD_CHK - LH_CHK + 3
            c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), FS_CHK)
            for ln in item_lines:
                if ln: c.drawString(MARGIN_L + 6, ty, ln)
                ty -= LH_CHK
            mid_y = y - row_h / 2
            yes_x = MARGIN_L + COL_WIDTHS_CHK[0] + COL_WIDTHS_CHK[1] / 2
            no_x  = MARGIN_L + COL_WIDTHS_CHK[0] + COL_WIDTHS_CHK[1] + COL_WIDTHS_CHK[2] / 2
            if yes_v:
                c.setFillColor(C_GREEN); c.setFont(_font(pdf_lang, bold=True), 10)
                c.drawCentredString(yes_x, mid_y - 4, "✓")
            if no_v:
                c.setFillColor(C_RED);   c.setFont(_font(pdf_lang, bold=True), 10)
                c.drawCentredString(no_x, mid_y - 4, "✗")
            ty = y - ROW_PAD_CHK - LH_CHK + 3
            c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), FS_CHK)
            for ln in comment_lines:
                if ln: c.drawString(MARGIN_L + COL_WIDTHS_CHK[0] + COL_WIDTHS_CHK[1] + COL_WIDTHS_CHK[2] + 6, ty, ln)
                ty -= LH_CHK
            y -= row_h

        tb_h = chk_table_top - y
        if tb_h > 0:
            c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
            c.rect(MARGIN_L, y, CONTENT_W, tb_h, fill=0, stroke=1)
        y -= 10

        # ── 4. TECHNICAL SPECS ───────────────────────────────────────────
        y = maybe_new_page(y, 100)
        y = draw_section_header(c, y, loc("4. TECHNICAL SPECIFICATIONS", "4. 技术规格"), pdf_lang)

        same_label = pt("same", pdf_lang)
        same_tick  = "✓" if tech_specs_same else "□"
        spec_line  = f"{same_label}: {same_tick}    {pt('if_not_same', pdf_lang)}: {tech_specs_comment or '—'}"
        y = draw_text_block(c, y, pt("tech_specs_compare", pdf_lang), spec_line, pdf_lang, C_ACCENT2)
        y -= 6

        # ── 5. TEST RESULTS ──────────────────────────────────────────────
        y = maybe_new_page(y, 180)
        y = draw_section_header(c, y, loc("5. TEST RESULTS", "5. 测试结果"), pdf_lang)

        test_col_labels = [
            pt("check_items", pdf_lang),
            pt("result", pdf_lang),
            pt("client_standard", pdf_lang),
            "PASS / FAIL",
        ]

        COL_WIDTHS_TST = [CONTENT_W * 0.30, CONTENT_W * 0.18, CONTENT_W * 0.35, CONTENT_W * 0.17]
        HDR_H_TST = 22; ROW_PAD_TST = 6; FS_TST = 8; LH_TST = 13
        col_inner_tst = [cw - 12 for cw in COL_WIDTHS_TST]

        def draw_test_header(cy):
            c.setFillColor(C_ACCENT)
            c.rect(MARGIN_L, cy - HDR_H_TST, CONTENT_W, HDR_H_TST, fill=1, stroke=0)
            c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 8.5)
            cx2 = MARGIN_L + 6
            for ii, lbl in enumerate(test_col_labels):
                c.drawString(cx2, cy - HDR_H_TST + 8, lbl)
                cx2 += COL_WIDTHS_TST[ii]
            return cy - HDR_H_TST

        y = draw_test_header(y)
        tst_table_top = y

        for ri, (item, result, standard, pass_v, fail_v) in enumerate(test_rows_data):
            item_lines     = _wrap_text(item,     col_inner_tst[0], FS_TST)
            result_lines   = _wrap_text(result,   col_inner_tst[1], FS_TST)
            standard_lines = _wrap_text(standard, col_inner_tst[2], FS_TST)
            max_lines = max(len(item_lines), len(result_lines), len(standard_lines), 1)
            row_h = max_lines * LH_TST + ROW_PAD_TST * 2
            if y - row_h < FOOTER_H + 20:
                tb_h = tst_table_top - y
                if tb_h > 0:
                    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
                    c.rect(MARGIN_L, y, CONTENT_W, tb_h, fill=0, stroke=1)
                y = new_page()
                y = draw_test_header(y)
                tst_table_top = y
            if ri % 2 == 0:
                c.setFillColor(C_LIGHT)
                c.rect(MARGIN_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
            c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
            c.line(MARGIN_L, y - row_h, MARGIN_L + CONTENT_W, y - row_h)
            cx_sep = MARGIN_L
            for cw in COL_WIDTHS_TST[:-1]:
                cx_sep += cw
                c.line(cx_sep, y, cx_sep, y - row_h)
            ty = y - ROW_PAD_TST - LH_TST + 3
            c.setFillColor(C_ACCENT2); c.setFont(_font(pdf_lang, bold=True), FS_TST)
            for ln in item_lines:
                if ln: c.drawString(MARGIN_L + 6, ty, ln)
                ty -= LH_TST
            ty = y - ROW_PAD_TST - LH_TST + 3
            c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), FS_TST)
            for ln in result_lines:
                if ln: c.drawString(MARGIN_L + COL_WIDTHS_TST[0] + 6, ty, ln)
                ty -= LH_TST
            ty = y - ROW_PAD_TST - LH_TST + 3
            for ln in standard_lines:
                if ln: c.drawString(MARGIN_L + COL_WIDTHS_TST[0] + COL_WIDTHS_TST[1] + 6, ty, ln)
                ty -= LH_TST
            mid_y = y - row_h / 2
            pf_x = MARGIN_L + COL_WIDTHS_TST[0] + COL_WIDTHS_TST[1] + COL_WIDTHS_TST[2] + COL_WIDTHS_TST[3] / 2
            if pass_v:
                c.setFillColor(C_GREEN); c.setFont(_font(pdf_lang, bold=True), 8.5)
                c.drawCentredString(pf_x, mid_y - 4, pt("pass_", pdf_lang))
            elif fail_v:
                c.setFillColor(C_RED);   c.setFont(_font(pdf_lang, bold=True), 8.5)
                c.drawCentredString(pf_x, mid_y - 4, pt("fail_", pdf_lang))
            else:
                c.setFillColor(C_GREY_TEXT); c.setFont(_font(pdf_lang), 8)
                c.drawCentredString(pf_x, mid_y - 4, "—")
            y -= row_h

        tb_h = tst_table_top - y
        if tb_h > 0:
            c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
            c.rect(MARGIN_L, y, CONTENT_W, tb_h, fill=0, stroke=1)
        y -= 10

        # ── 6. SIGNATURES ────────────────────────────────────────────────
        y = maybe_new_page(y, 200)
        y = draw_section_header(c, y, loc("6. SIGNATURES & APPROVALS", "6. 签名与批准"), pdf_lang)

        COL_WIDTHS_SIG = [CONTENT_W * 0.35, CONTENT_W * 0.40, CONTENT_W * 0.25]
        HDR_H_SIG = 22; ROW_H_SIG = 28; FS_SIG = 8
        sig_headers = [pt("check_items", pdf_lang),
                       "姓名/签名" if pdf_lang == "zh" else "Name / Signature",
                       "日期" if pdf_lang == "zh" else "Date"]
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - HDR_H_SIG, CONTENT_W, HDR_H_SIG, fill=1, stroke=0)
        c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 8.5)
        cx2 = MARGIN_L + 6
        for h in sig_headers:
            c.drawString(cx2, y - HDR_H_SIG + 8, h)
            cx2 += COL_WIDTHS_SIG[len(sig_headers) - len(sig_headers)]  # iterate properly
        # Redraw properly
        c.setFillColor(C_ACCENT)
        c.rect(MARGIN_L, y - HDR_H_SIG, CONTENT_W, HDR_H_SIG, fill=1, stroke=0)
        c.setFillColor(C_WHITE); c.setFont(_font(pdf_lang, bold=True), 8.5)
        offsets = [0, COL_WIDTHS_SIG[0], COL_WIDTHS_SIG[0] + COL_WIDTHS_SIG[1]]
        for oi, h in zip(offsets, sig_headers):
            c.drawString(MARGIN_L + oi + 6, y - HDR_H_SIG + 8, h)
        y -= HDR_H_SIG
        sig_table_top = y

        for ri, (label, name, date_str) in enumerate(sigs):
            if y - ROW_H_SIG < FOOTER_H + 20:
                tb_h = sig_table_top - y
                if tb_h > 0:
                    c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
                    c.rect(MARGIN_L, y, CONTENT_W, tb_h, fill=0, stroke=1)
                y = new_page()
                sig_table_top = y
            if ri % 2 == 0:
                c.setFillColor(C_LIGHT)
                c.rect(MARGIN_L, y - ROW_H_SIG, CONTENT_W, ROW_H_SIG, fill=1, stroke=0)
            c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.3)
            c.line(MARGIN_L, y - ROW_H_SIG, MARGIN_L + CONTENT_W, y - ROW_H_SIG)
            c.line(MARGIN_L + COL_WIDTHS_SIG[0], y, MARGIN_L + COL_WIDTHS_SIG[0], y - ROW_H_SIG)
            c.line(MARGIN_L + COL_WIDTHS_SIG[0] + COL_WIDTHS_SIG[1], y,
                   MARGIN_L + COL_WIDTHS_SIG[0] + COL_WIDTHS_SIG[1], y - ROW_H_SIG)
            c.setFillColor(C_ACCENT2); c.setFont(_font(pdf_lang, bold=True), FS_SIG)
            c.drawString(MARGIN_L + 6, y - ROW_H_SIG + 10, str(label))
            line_x1 = MARGIN_L + COL_WIDTHS_SIG[0] + 8
            line_x2 = MARGIN_L + COL_WIDTHS_SIG[0] + COL_WIDTHS_SIG[1] - 8
            if name:
                c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), FS_SIG)
                c.drawString(line_x1, y - ROW_H_SIG + 10, str(name))
            c.setStrokeColor(C_PRIMARY); c.setLineWidth(0.8)
            c.line(line_x1, y - ROW_H_SIG + 6, line_x2, y - ROW_H_SIG + 6)
            c.setFillColor(C_PRIMARY); c.setFont(_font(pdf_lang), FS_SIG)
            c.drawString(MARGIN_L + COL_WIDTHS_SIG[0] + COL_WIDTHS_SIG[1] + 6, y - ROW_H_SIG + 10, str(date_str))
            y -= ROW_H_SIG

        tb_h = sig_table_top - y
        if tb_h > 0:
            c.setStrokeColor(C_GREY_LINE); c.setLineWidth(0.5)
            c.rect(MARGIN_L, y, CONTENT_W, tb_h, fill=0, stroke=1)
        y -= 16

        # ── Disclaimer & note ────────────────────────────────────────────
        y = maybe_new_page(y, 60)
        upd = pt("updated_2022", pdf_lang)
        disc = pt("disclaimer_text", pdf_lang)
        c.setFillColor(C_GREY_TEXT); c.setFont(_font(pdf_lang), 7.5)
        c.drawRightString(MARGIN_L + CONTENT_W, y, upd)
        y -= 12
        disc_lines = _wrap_text(disc, CONTENT_W - 20, 7.5)
        for ln in disc_lines:
            if ln: c.drawString(MARGIN_L, y, ln)
            y -= 11

        c.save()
        return page_counter[0]

    # Pass 1
    count_buf = io.BytesIO()
    actual_total = _build(count_buf, 99)
    # Pass 2
    buf = io.BytesIO()
    _build(buf, actual_total)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
#  STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  .main-header{font-size:2.6rem;font-weight:800;text-align:center;
    color:#4299E1;margin-bottom:1.5rem;padding:0.5rem;}
  .section-header{font-size:1.4rem;font-weight:700;color:#1a1a2e;
    margin:2rem 0 1rem;padding:0.7rem 1.2rem;
    background:linear-gradient(135deg,#f0f4ff 0%,#dde4ff 100%);
    border-radius:10px;border-left:5px solid #e94560;}
  .stButton>button{background:linear-gradient(135deg,#1a1a2e 0%,#e94560 100%);
    color:white;font-size:1.1rem;font-weight:600;padding:0.9rem 2rem;
    border-radius:10px;border:none;width:100%;transition:all .3s;}
  .stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 16px rgba(233,69,96,.35);}
  .footer{text-align:center;padding:1.5rem;
    background:linear-gradient(135deg,#f0f4ff 0%,#dde4ff 100%);
    border-radius:12px;margin-top:2rem;border-top:3px solid #e94560;}
  .location-badge{display:inline-flex;align-items:center;gap:6px;
    background:linear-gradient(135deg,#1a1a2e 0%,#0f3460 100%);
    color:white;padding:.4rem .9rem;border-radius:20px;font-weight:600;font-size:.85rem;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    st.markdown(f"#### 🌐 {t('ui_lang')}")
    ui_choice = st.selectbox(t('ui_lang'), ["English", "中文 (Mandarin)"],
                             index=0 if st.session_state.ui_language == "en" else 1,
                             key="ui_lang_select", label_visibility="collapsed")
    new_ui = "en" if ui_choice == "English" else "zh"
    if new_ui != st.session_state.ui_language:
        st.session_state.ui_language = new_ui
        st.session_state.translation_cache = {}
        st.rerun()

    st.markdown(f"#### 📄 {t('pdf_lang')}")
    pdf_choice = st.selectbox(t('pdf_lang'), ["English", "中文 (Mandarin)"],
                              index=0 if st.session_state.pdf_language == "en" else 1,
                              key="pdf_lang_select", label_visibility="collapsed")
    st.session_state.pdf_language = "en" if pdf_choice == "English" else "zh"

    st.markdown("#### 📍 Location")
    city_keys = list(CHINESE_CITIES.keys())
    city_idx  = city_keys.index(st.session_state.selected_city) if st.session_state.selected_city in city_keys else 0
    sel_city  = st.selectbox("Location", city_keys, index=city_idx,
                             key="city_select", label_visibility="collapsed")
    st.session_state.selected_city = sel_city
    st.markdown(f'<div class="location-badge">📍 {sel_city} ({CHINESE_CITIES.get(sel_city,"")})</div>',
                unsafe_allow_html=True)

    st.markdown("#### 🕐 Local Time")
    china_tz = pytz.timezone('Asia/Shanghai')
    now_cn   = datetime.now(china_tz)
    st.metric("Local Time", now_cn.strftime('%H:%M:%S'), now_cn.strftime('%Y-%m-%d'))

    if openai_client:
        st.success(f"✅ {t('translation_active')}")
    else:
        st.warning(f"⚠️ {t('translation_off')}")

    st.markdown("---")
    st.markdown("### ℹ️ Quick Guide")
    for step in ["1. Fill Basic Info", "2. Complete Check Points", "3. Enter Test Results",
                 "4. Add Signatures", "5. Generate PDF"]:
        st.write(step)

# ── Main header ────────────────────────────────────────────────────────────
st.markdown(f'<div class="main-header">✂️ {t("title")}</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([t("tab_basic"), t("tab_check"), t("tab_test"), t("tab_sign")])

# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="section-header">📋 {t("basic_info")}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.date_input(f"📅 {t('die_cut_date')}",   datetime.now().date(), key="die_cut_date")
    with c2:
        st.date_input(f"📅 {t('batch_test_date')}", datetime.now().date(), key="batch_test_date")

    c1, c2 = st.columns(2)
    with c1:
        v = display_val('contract_no')
        inp = st.text_input(f"📄 {t('contract_no')}", value=v, placeholder="CON-2024-001", key="contract_no_inp")
        if inp != v: set_ev('contract_no', inp)

        v = display_val('style_name')
        inp = st.text_input(f"👕 {t('style_name')}", value=v, placeholder="STYLE-2024-001", key="style_name_inp")
        if inp != v: set_ev('style_name', inp)

        v = display_val('qty')
        inp = st.text_input(f"🔢 {t('qty')}", value=v, placeholder="1000 pairs", key="qty_inp")
        if inp != v: set_ev('qty', inp)

        v = display_val('factory_style')
        inp = st.text_input(f"🏭 {t('factory_style')}", value=v, placeholder="FAC-001", key="factory_style_inp")
        if inp != v: set_ev('factory_style', inp)

    with c2:
        v = display_val('brand')
        inp = st.text_input(f"🏷️ {t('brand')}", value=v, placeholder="Brand Name", key="brand_inp")
        if inp != v: set_ev('brand', inp)

        v = display_val('agent_factory')
        inp = st.text_input(f"🏭 {t('agent_factory')}", value=v, placeholder="Agent & Factory", key="agent_factory_inp")
        if inp != v: set_ev('agent_factory', inp)

        v = display_val('sales')
        inp = st.text_input(f"👔 {t('sales')}", value=v, placeholder="Sales Rep", key="sales_inp")
        if inp != v: set_ev('sales', inp)

        st.date_input(f"📅 {t('ship_date')}", datetime.now().date(), key="ship_date")

    st.markdown(f'<div class="section-header">📏 {t("size_table_title")}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([3, 3, 3, 1])
    c1.markdown(f"**{t('size')}**"); c2.markdown(f"**{t('die_qty')}**")
    c3.markdown(f"**{t('batch_qty')}**"); c4.markdown("&nbsp;")

    for i, item in enumerate(st.session_state.size_data):
        c1, c2, c3, c4 = st.columns([3, 3, 3, 1])
        with c1:
            v = st.text_input("Size", value=item.get('size', ''), placeholder="US 8", key=f"size_{i}", label_visibility="collapsed")
            st.session_state.size_data[i]['size'] = v
        with c2:
            v = st.text_input("Die", value=item.get('die_qty', ''), placeholder="50", key=f"die_qty_{i}", label_visibility="collapsed")
            st.session_state.size_data[i]['die_qty'] = v
        with c3:
            v = st.text_input("Batch", value=item.get('batch_qty', ''), placeholder="200", key=f"batch_qty_{i}", label_visibility="collapsed")
            st.session_state.size_data[i]['batch_qty'] = v
        with c4:
            if st.button("❌", key=f"remove_{i}"):
                remove_size_row(i); st.rerun()

    if st.button(f"➕ {t('add_size')}", use_container_width=True):
        add_size_row(); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="section-header">✓ {t("main_check")}</div>', unsafe_allow_html=True)

    cl, cr = st.columns(2)

    check_items_left = [
        ("last_no_correct", "last_no_yes", "last_no_no", "last_no_comments"),
        ("color_matches",   "color_yes",   "color_no",   "color_comments"),
        ("tack_free",       "tack_free_yes","tack_free_no","tack_free_comments"),
    ]
    check_items_right = [
        ("size_run_match",         "size_run_yes",      "size_run_no",      "size_run_comments"),
        ("fitting_correct",        "fitting_yes",       "fitting_no",       "fitting_comments"),
        ("top_sample_sent",        "top_sample_yes",    "top_sample_no",    "top_sample_comments"),
        ("tech_comments_completed","tech_comments_yes", "tech_comments_no", "tech_comments_description"),
    ]

    for col_obj, items in [(cl, check_items_left), (cr, check_items_right)]:
        with col_obj:
            for lbl_key, yes_key, no_key, comment_key in items:
                st.markdown(f"**{t(lbl_key)}**")
                c1, c2 = st.columns(2)
                with c1: st.checkbox(t('yes'), key=yes_key)
                with c2: st.checkbox(t('no'),  key=no_key)
                v = display_val(comment_key)
                inp = st.text_area(t('comments'), value=v, height=60, key=f"{comment_key}_inp", label_visibility="collapsed")
                if inp != v: set_ev(comment_key, inp)
                st.markdown("---")

    st.markdown(f"**{t('tech_specs_compare')}**")
    st.checkbox(t('same'), key="tech_specs_same")
    v = display_val('tech_specs_comments')
    inp = st.text_area(t('if_not_same'), value=v, height=80, key="tech_specs_comments_inp")
    if inp != v: set_ev('tech_specs_comments', inp)

# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f'<div class="section-header">🧪 {t("test_results")}</div>', unsafe_allow_html=True)

    test_fields = [
        ("sole_bonding",    "sole_bonding_result",    "sole_bonding_pass",    "sole_bonding_fail"),
        ("top_piece",       "top_piece_result",       "top_piece_pass",       "top_piece_fail"),
        ("straps_strength", "straps_strength_result", "straps_strength_pass", "straps_strength_fail"),
        ("heel_attachment", "heel_attachment_result", "heel_attachment_pass", "heel_attachment_fail"),
        ("insole_perment",  "insole_perment_result",  "insole_perment_pass",  "insole_perment_fail"),
        ("toe_post",        "toe_post_result",        "toe_post_pass",        "toe_post_fail"),
    ]

    cl, cr = st.columns(2)
    for i, (lbl_key, result_key, pass_key, fail_key) in enumerate(test_fields):
        col_obj = cl if i < 3 else cr
        with col_obj:
            st.markdown(f"**{t(lbl_key)}**")
            v = display_val(result_key)
            inp = st.text_input(t('result'), value=v, placeholder=f"{t('result')}...",
                                key=f"{result_key}_inp", label_visibility="collapsed")
            if inp != v: set_ev(result_key, inp)
            c1, c2 = st.columns(2)
            with c1: st.checkbox("PASS", key=pass_key)
            with c2: st.checkbox("FAIL", key=fail_key)
            st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f'<div class="section-header">✍️ {t("signatures")}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    sig_fields_left  = [("factory_rep","factory_representative"), ("gs_qc","gs_qc"), ("area_manager","area_manager")]
    sig_fields_right = [("gs_tech","grandstep_technician"), ("qa_manager","qa_manager")]

    with c1:
        for lbl_key, ev_key in sig_fields_left:
            v = display_val(ev_key)
            inp = st.text_input(f"✍️ {t(lbl_key)}", value=v, placeholder=t(lbl_key), key=f"{ev_key}_inp")
            if inp != v: set_ev(ev_key, inp)
    with c2:
        for lbl_key, ev_key in sig_fields_right:
            v = display_val(ev_key)
            inp = st.text_input(f"✍️ {t(lbl_key)}", value=v, placeholder=t(lbl_key), key=f"{ev_key}_inp")
            if inp != v: set_ev(ev_key, inp)
        st.date_input(f"📅 {t('signature_date')}", datetime.now().date(), key="signature_date")

    st.markdown(f"""
    <div style='background:#f0f4ff;padding:15px;border-radius:8px;
         border-left:4px solid #e94560;margin-top:20px;'>
        <strong>{t('disclaimer')}:</strong> {t('disclaimer_text')}
    </div>
    """, unsafe_allow_html=True)

# ── Generate button ─────────────────────────────────────────────────────────
st.markdown("---")
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    if st.button(t('generate_pdf'), use_container_width=True):
        if not get_ev('contract_no') or not get_ev('style_name'):
            st.error(f"⚠️ {t('fill_required')}")
        else:
            with st.spinner(f"⏳ {t('creating_pdf')}"):
                try:
                    pdf_buf = generate_pdf()
                    st.success(f"✅ {t('generate_success')}")
                    with st.expander(f"ℹ️ {t('pdf_details')}"):
                        mc1, mc2 = st.columns(2)
                        with mc1:
                            st.metric(t('location'),
                                      f"{st.session_state.selected_city} ({CHINESE_CITIES.get(st.session_state.selected_city,'')})")
                            st.metric(t('report_language'),
                                      "中文" if st.session_state.pdf_language == "zh" else "English")
                        with mc2:
                            st.metric(t('generated'),
                                      datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%H:%M:%S'))
                    fname = (f"DieCut_{get_ev('contract_no')}_{st.session_state.selected_city}"
                             f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                    st.download_button(label=t('download_pdf'), data=pdf_buf,
                                       file_name=fname, mime="application/pdf",
                                       use_container_width=True)
                except Exception as e:
                    st.error(f"❌ {t('error_generating')}: {str(e)}")
                    with st.expander("Debug"):
                        import traceback; st.code(traceback.format_exc())

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  <p style="font-size:1.1rem;font-weight:700;color:#1a1a2e;margin-bottom:.4rem;">
    ✂️ {t('footer_text')}
  </p>
  <p style="font-size:.85rem;color:#555;">
    📍 {st.session_state.selected_city} ({CHINESE_CITIES.get(st.session_state.selected_city,'')}) &nbsp;|&nbsp;
    🌐 {"中文" if st.session_state.pdf_language=="zh" else "English"}
  </p>
  <p style="font-size:.75rem;color:#999;margin-top:.8rem;">
    {t('powered_by')} &nbsp;|&nbsp; {t('copyright')}
  </p>
</div>
""", unsafe_allow_html=True)
