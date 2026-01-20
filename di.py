import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import io
import pytz
from openai import OpenAI
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)
else:
    openai_client = None
    st.warning("OpenAI API key not found. Some features may be limited.")

# Page config
st.set_page_config(
    page_title="Die Cut Test Report System",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chinese cities dictionary
CHINESE_CITIES = {
    "Guangzhou": "广州",
    "Shenzhen": "深圳",
    "Dongguan": "东莞",
    "Foshan": "佛山",
    "Zhongshan": "中山",
    "Huizhou": "惠州",
    "Zhuhai": "珠海",
    "Jiangmen": "江门",
    "Zhaoqing": "肇庆",
    "Shanghai": "上海",
    "Beijing": "北京",
    "Suzhou": "苏州",
    "Hangzhou": "杭州",
    "Ningbo": "宁波",
    "Wenzhou": "温州",
    "Wuhan": "武汉",
    "Chengdoo": "成都",
    "Chongqing": "重庆",
    "Tianjin": "天津",
    "Nanjing": "南京",
    "Xi'an": "西安",
    "Qingdao": "青岛",
    "Dalian": "大连",
    "Shenyang": "沈阳",
    "Changsha": "长沙",
    "Zhengzhou": "郑州",
    "Jinan": "济南",
    "Harbin": "哈尔滨",
    "Changchun": "长春",
    "Taiyuan": "太原",
    "Shijiazhuang": "石家庄",
    "Lanzhou": "兰州",
    "Xiamen": "厦门",
    "Fuzhou": "福州",
    "Nanning": "南宁",
    "Kunming": "昆明",
    "Guiyang": "贵阳",
    "Haikou": "海口",
    "Ürümqi": "乌鲁木齐",
    "Lhasa": "拉萨"
}

# Custom icons
ICONS = {
    "title": "✂️",
    "basic_info": "📋",
    "die_cut_test": "🔪",
    "batch_test": "📦",
    "main_check": "✓",
    "tech_specs": "📏",
    "test_results": "🧪",
    "issues_solutions": "⚠️",
    "signatures": "✍️",
    "generate": "📊",
    "download": "📥",
    "settings": "⚙️",
    "language": "🌐",
    "location": "📍",
    "time": "🕐",
    "info": "ℹ️",
    "factory": "🏭",
    "brand": "🏷️",
    "style": "👕",
    "sales": "👔",
    "tech": "🔧",
    "qc": "👁️",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "check": "✓",
    "test": "🧪",
    "measure": "📐",
    "calendar": "📅",
    "quantity": "🔢"
}

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        padding: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1.2rem;
        padding: 0.8rem 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 0.8rem 2rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .location-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        box-shadow: 0 3px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .footer {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        margin-top: 2rem;
        border-top: 3px solid #667eea;
    }
    .checkbox-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .test-row {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-left: 4px solid #667eea;
    }
    .size-table-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for user inputs
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "en"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "en"
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Shanghai"
if 'translation_cache' not in st.session_state:
    st.session_state.translation_cache = {}
if 'english_values' not in st.session_state:
    st.session_state.english_values = {
        'contract_no': '',
        'brand': '',
        'agent_factory': '',
        'style_name': '',
        'qty': '',
        'sales': '',
        'factory_style': '',
        'size': '',
        'die_qty': '',
        'batch_qty': '',
        'last_no_comments': '',
        'color_comments': '',
        'tack_free_comments': '',
        'tech_specs_comments': '',
        'size_run_comments': '',
        'fitting_comments': '',
        'top_sample_comments': '',
        'tech_comments_description': '',
        'sole_bonding_result': '',
        'top_piece_result': '',
        'straps_strength_result': '',
        'heel_attachment_result': '',
        'insole_perment_result': '',
        'toe_post_result': '',
        'die_cut_issues': '',
        'batch_test_issues': '',
        'factory_representative': '',
        'gs_qc': '',
        'grandstep_technician': '',
        'area_manager': '',
        'qa_manager': ''
    }
if 'size_data' not in st.session_state:
    st.session_state.size_data = []

# SEPARATE TEXT DICTIONARIES
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
    "generate_pdf": "Generate PDF Report",
    "download_pdf": "Download PDF Report",
    "contract_no": "Contract No.",
    "brand": "Brand",
    "agent_factory": "Agent and Factory",
    "style_name": "Style Name",
    "qty": "QTY",
    "sales": "Sales",
    "factory_style": "Factory style",
    "ship_date": "Ship Date",
    "size": "Size",
    "die_qty": "QTY (Die)",
    "batch_qty": "QTY (Batches)",
    "test_dates": "Test Dates",
    "footer_text": "Die Cut Test Report System",
    "generate_success": "PDF Generated Successfully!",
    "fill_required": "Please fill in required fields!",
    "creating_pdf": "Creating PDF report...",
    "pdf_details": "PDF Details",
    "report_language": "Report Language",
    "generated": "Generated",
    "location": "Location",
    "error_generating": "Error generating PDF",
    "select_location": "Select Location",
    "user_interface_language": "User Interface Language",
    "pdf_report_language": "PDF Report Language",
    "test_location": "Test Location",
    "local_time": "Local Time",
    "quick_guide": "Quick Guide",
    "powered_by": "Powered by Streamlit",
    "copyright": "© 2024 - Die Cut Test Platform",
    "check_items": "Check Items",
    "comments": "Comments",
    "yes": "YES",
    "no": "NO",
    "test_standards": "Test Standards",
    "pass_fail": "Pass/Fail",
    "client_standard": "Client's Standard",
    "result": "Result",
    "disclaimer": "Disclaimer",
    "factory_rep": "Factory Representative",
    "gs_qc": "GS QC",
    "gs_tech": "Grand Step Technician",
    "area_manager": "Area Manager",
    "qa_manager": "QA Manager",
    "updated_date": "Updated Date",
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
    "main_issues": "Main issues & Solution",
    "signature_date": "Date",
    "updated_2022": "Updated 2022.8.30",
    "disclaimer_text": "Note: This review information does not release the factory from any responsibilities in the event of claims being received from our customer.",
    "add_size": "Add Size",
    "remove_size": "Remove",
    "size_table_title": "Size & Quantity Details",
    "total": "Total",
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
    "generate_pdf": "生成PDF报告",
    "download_pdf": "下载PDF报告",
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
    "test_dates": "测试日期",
    "footer_text": "斩刀试做报告系统",
    "generate_success": "PDF生成成功！",
    "fill_required": "请填写必填字段！",
    "creating_pdf": "正在创建PDF报告...",
    "pdf_details": "PDF详情",
    "report_language": "报告语言",
    "generated": "生成时间",
    "location": "地点",
    "error_generating": "生成PDF错误",
    "select_location": "选择地点",
    "user_interface_language": "用户界面语言",
    "pdf_report_language": "PDF报告语言",
    "test_location": "测试地点",
    "local_time": "本地时间",
    "quick_guide": "快速指南",
    "powered_by": "由Streamlit驱动",
    "copyright": "© 2024 - 斩刀测试平台",
    "check_items": "检查项目",
    "comments": "建议",
    "yes": "是",
    "no": "否",
    "test_standards": "测试标准",
    "pass_fail": "通过/失败",
    "client_standard": "客人标准",
    "result": "结果",
    "disclaimer": "免责声明",
    "factory_rep": "工厂代表",
    "gs_qc": "志途验货员",
    "gs_tech": "志途师傅",
    "area_manager": "地区经理",
    "qa_manager": "品管经理",
    "updated_date": "更新日期",
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
    "main_issues": "主要问题及解决方案",
    "signature_date": "日期",
    "updated_2022": "更新 2022.8.30",
    "disclaimer_text": "此报表不免除我客人收到货后索赔而引起的货物供应商(工厂)的任何责任.",
    "add_size": "添加尺码",
    "remove_size": "删除",
    "size_table_title": "尺码与数量详情",
    "total": "总计",
}

def get_text(key, fallback=None):
    """Get text based on current UI language"""
    lang = st.session_state.ui_language
    if lang == "zh":
        return MANDARIN_TEXTS.get(key, fallback or key)
    else:
        return ENGLISH_TEXTS.get(key, fallback or key)

def get_pdf_text(key, pdf_language):
    """Get text for PDF based on selected language"""
    if pdf_language == "zh":
        return MANDARIN_TEXTS.get(key, key)
    else:
        return ENGLISH_TEXTS.get(key, key)

# SIMPLIFIED NUMBER HANDLING - NO CONVERSIONS, JUST DISPLAY
def get_display_text(value):
    """Convert any value to display text"""
    if value is None:
        return ''
    if isinstance(value, str):
        return value.strip()
    return str(value)

def translate_text_with_openai(text, target_language):
    """Translate text using OpenAI"""
    if text is None:
        return ""
    
    text_str = str(text).strip()
    if text_str == "":
        return ""
    
    cache_key = (text_str, target_language)
    if cache_key in st.session_state.translation_cache:
        cached_result = st.session_state.translation_cache[cache_key]
        return str(cached_result) if cached_result is not None else ""
    
    if not openai_client:
        return text_str
    
    if target_language == "zh":
        target_lang_name = "Simplified Chinese"
    else:
        target_lang_name = "English"
    
    try:
        prompt = f"""Translate this text to {target_lang_name}. 
        IMPORTANT: Preserve all numbers, measurements, units, and special codes exactly as they are.
        
        Text to translate: {text_str}
        
        Translation:"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=500,
            temperature=0.1
        )
        
        translated = response.choices[0].message.content.strip()
        st.session_state.translation_cache[cache_key] = translated
        return str(translated) if translated is not None else text_str
        
    except Exception as e:
        return text_str

def get_display_value(field_key):
    """Get value for display based on current UI language"""
    english_value = st.session_state.english_values.get(field_key, '')
    if not english_value:
        return ''
    
    if st.session_state.ui_language == "en":
        result = str(english_value) if english_value is not None else ''
    else:
        result = translate_text_with_openai(english_value, "zh")
    
    return str(result) if result is not None else ''

def update_english_value(field_key, displayed_value):
    """Update the English value based on user input"""
    if not displayed_value or displayed_value.strip() == "":
        st.session_state.english_values[field_key] = ''
        return
    
    display_str = str(displayed_value).strip()
    
    if st.session_state.ui_language == "en":
        st.session_state.english_values[field_key] = display_str
    else:
        def contains_chinese(text):
            if not text:
                return False
            text_str = str(text) if text is not None else ""
            for char in text_str:
                if '\u4e00' <= char <= '\u9fff':
                    return True
            return False
        
        if contains_chinese(display_str):
            english_text = translate_text_with_openai(display_str, "en")
            st.session_state.english_values[field_key] = english_text
        else:
            st.session_state.english_values[field_key] = display_str

def get_pdf_display_value(field_key, pdf_language):
    """Get value for PDF generation based on PDF language"""
    english_value = st.session_state.english_values.get(field_key, '')
    if not english_value:
        return ''
    
    if pdf_language == "en":
        result = str(english_value) if english_value is not None else ''
    else:
        result = translate_text_with_openai(english_value, "zh")
    
    return str(result) if result is not None else ''

# Helper function for size management
def add_size_row():
    """Add a new empty size row"""
    st.session_state.size_data.append({
        'size': '',
        'die_qty': '',
        'batch_qty': ''
    })

def remove_size_row(index):
    """Remove a size row by index"""
    if 0 <= index < len(st.session_state.size_data):
        st.session_state.size_data.pop(index)

# SIMPLIFIED PDF Generation - NO NUMBER CALCULATIONS
class DieCutPDF(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.pdf_language = kwargs.pop('pdf_language', 'en')
        self.selected_city = kwargs.pop('selected_city', '')
        self.chinese_city = kwargs.pop('chinese_city', '')
        super().__init__(*args, **kwargs)
        
    def onFirstPage(self, canvas, doc):
        """Add header to first page"""
        canvas.saveState()
        
        if self.pdf_language == "zh":
            canvas.setFont('Helvetica-Bold', 14)
        else:
            canvas.setFont('Helvetica-Bold', 14)
            
        canvas.setFillColor(colors.HexColor('#667eea'))
        
        if self.pdf_language == "zh":
            company_name = "志途"
            report_title = "斩刀试做报告"
        else:
            company_name = "Grandstep"
            report_title = "Die Cut Test Report"
        
        canvas.drawCentredString(doc.pagesize[0]/2, doc.pagesize[1] - 0.5*inch, company_name)
        
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(colors.HexColor('#333333'))
        canvas.drawCentredString(doc.pagesize[0]/2, doc.pagesize[1] - 0.7*inch, report_title)
        
        canvas.setStrokeColor(colors.HexColor('#667eea'))
        canvas.setLineWidth(1)
        canvas.line(1*inch, doc.pagesize[1] - 0.8*inch, doc.pagesize[0] - 1*inch, doc.pagesize[1] - 0.8*inch)
        
        canvas.restoreState()
        self._addFooter(canvas, doc, 1)
        
    def onLaterPages(self, canvas, doc):
        """Add header to later pages"""
        canvas.saveState()
        
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(0.5)
        canvas.line(0.5*inch, doc.pagesize[1] - 0.5*inch, doc.pagesize[0] - 0.5*inch, doc.pagesize[1] - 0.5*inch)
        
        canvas.restoreState()
        self._addFooter(canvas, doc, canvas.getPageNumber())
        
    def _addFooter(self, canvas, doc, page_num):
        """Add footer to pages"""
        canvas.saveState()
        
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(0.5)
        canvas.line(0.5*inch, 0.6*inch, doc.pagesize[0] - 0.5*inch, 0.6*inch)
        
        if self.pdf_language == "zh":
            canvas.setFont('Helvetica', 8)
        else:
            canvas.setFont('Helvetica', 8)
            
        canvas.setFillColor(colors.HexColor('#666666'))
        
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_tz)
        
        if self.pdf_language == "zh":
            location_text = f"地点: {self.chinese_city}"
            date_text = f"日期: {current_time.strftime('%Y年%m月%d日')}"
            page_num_text = f"第 {page_num} 页"
        else:
            location_text = f"Location: {self.selected_city}"
            date_text = f"Date: {current_time.strftime('%Y-%m-%d')}"
            page_num_text = f"Page {page_num}"
        
        canvas.drawString(0.5*inch, 0.3*inch, location_text)
        
        company_footer = "志途质量检测" if self.pdf_language == "zh" else "Grandstep QC"
        if self.pdf_language == "zh":
            canvas.setFont('Helvetica-Bold', 8)
        else:
            canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(colors.HexColor('#667eea'))
        canvas.drawCentredString(doc.pagesize[0]/2, 0.3*inch, company_footer)
        
        if self.pdf_language == "zh":
            canvas.setFont('Helvetica', 8)
        else:
            canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        right_text = f"{date_text} | {page_num_text}"
        canvas.drawRightString(doc.pagesize[0] - 0.5*inch, 0.3*inch, right_text)
        
        canvas.restoreState()

def safe_date_format(date_val, format_str):
    """Safely format a date, handling None values"""
    if date_val is None:
        return ""
    try:
        if hasattr(date_val, 'strftime'):
            return date_val.strftime(format_str)
        else:
            return str(date_val)
    except Exception:
        return str(date_val)

def generate_pdf():
    """Generate Die Cut Test PDF report - SIMPLIFIED VERSION"""
    buffer = io.BytesIO()
    
    selected_city = st.session_state.selected_city
    chinese_city = CHINESE_CITIES[selected_city]
    pdf_lang = st.session_state.pdf_language
    
    doc = DieCutPDF(
        buffer, 
        pagesize=A4,
        topMargin=1.2*inch,
        bottomMargin=0.8*inch,
        leftMargin=0.6*inch,
        rightMargin=0.6*inch,
        pdf_language=pdf_lang,
        selected_city=selected_city,
        chinese_city=chinese_city
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # ========== DEFINE STYLES ==========
    
    primary_color = colors.HexColor('#667eea')
    secondary_color = colors.HexColor('#764ba2')
    dark_bg = colors.HexColor('#2c3e50')
    success_color = colors.HexColor('#48bb78')
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=primary_color,
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceBefore=5
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=dark_bg,
        spaceBefore=12,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        leftIndent=0,
        borderWidth=2,
        borderColor=primary_color,
        borderPadding=(0, 0, 0, 5),
        backgroundColor=colors.HexColor('#f0f4ff')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        backColor=primary_color
    )
    
    if pdf_lang == "zh":
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=10
        )
        
        table_cell_bold_style = ParagraphStyle(
            'TableCellBold',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=10
        )
    else:
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=10
        )
        
        table_cell_bold_style = ParagraphStyle(
            'TableCellBold',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leading=10
        )
    
    table_cell_center_style = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=10
    )
    
    small_style = ParagraphStyle(
        'SmallStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=9,
        fontName='Helvetica',
        textColor=colors.HexColor('#555555')
    )
    
    def create_paragraph(text, style, bold=False, color=None):
        """Create paragraph with appropriate styling"""
        if text is None:
            text = ""
        elif not isinstance(text, str):
            text = str(text)
        
        if bold and not hasattr(style, 'bold'):
            style = ParagraphStyle(
                f"BoldStyle_{hash(text)}",
                parent=style,
                fontName='Helvetica-Bold'
            )
        
        if color:
            style = ParagraphStyle(
                f"ColoredStyle_{hash(text)}",
                parent=style,
                textColor=color
            )
            
        return Paragraph(text, style)
    
    # ========== REPORT HEADER ==========
    
    title_text = get_pdf_text("title", pdf_lang)
    elements.append(create_paragraph(title_text, title_style, bold=True))
    
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    
    if pdf_lang == "zh":
        subtitle_text = f"报告生成: {current_time.strftime('%Y年%m月%d日 %H时%M分')} | 测试地点: {chinese_city}"
    else:
        subtitle_text = f"Report Generated: {current_time.strftime('%Y-%m-%d %H:%M')} | Test Location: {selected_city}"
    
    elements.append(create_paragraph(subtitle_text, subtitle_style))
    elements.append(Spacer(1, 8))
    elements.append(Spacer(1, 12))
    
    # ========== BASIC INFORMATION ==========
    
    basic_info_title = create_paragraph(get_pdf_text("basic_info", pdf_lang), section_header_style, bold=True)
    elements.append(basic_info_title)
    
    contract_no_val = get_pdf_display_value('contract_no', pdf_lang)
    brand_val = get_pdf_display_value('brand', pdf_lang)
    agent_factory_val = get_pdf_display_value('agent_factory', pdf_lang)
    style_name_val = get_pdf_display_value('style_name', pdf_lang)
    qty_val = get_pdf_display_value('qty', pdf_lang)
    sales_val = get_pdf_display_value('sales', pdf_lang)
    factory_style_val = get_pdf_display_value('factory_style', pdf_lang)
    ship_date_val = st.session_state.get('ship_date', current_time)
    
    contract_no_val = get_display_text(contract_no_val)
    brand_val = get_display_text(brand_val)
    agent_factory_val = get_display_text(agent_factory_val)
    style_name_val = get_display_text(style_name_val)
    qty_val = get_display_text(qty_val)
    sales_val = get_display_text(sales_val)
    factory_style_val = get_display_text(factory_style_val)
    
    basic_data = []
    
    contract_label = get_pdf_text("contract_no", pdf_lang)
    brand_label = get_pdf_text("brand", pdf_lang)
    agent_label = get_pdf_text("agent_factory", pdf_lang)
    
    basic_data.append([
        create_paragraph(f"{contract_label}", table_cell_bold_style, bold=True),
        create_paragraph(contract_no_val, table_cell_style),
        create_paragraph(f"{brand_label}", table_cell_bold_style, bold=True),
        create_paragraph(brand_val, table_cell_style),
        create_paragraph(f"{agent_label}", table_cell_bold_style, bold=True),
        create_paragraph(agent_factory_val, table_cell_style)
    ])
    
    style_label = get_pdf_text("style_name", pdf_lang)
    qty_label = get_pdf_text("qty", pdf_lang)
    sales_label = get_pdf_text("sales", pdf_lang)
    
    basic_data.append([
        create_paragraph(f"{style_label}", table_cell_bold_style, bold=True),
        create_paragraph(style_name_val, table_cell_style),
        create_paragraph(f"{qty_label}", table_cell_bold_style, bold=True),
        create_paragraph(qty_val, table_cell_style),
        create_paragraph(f"{sales_label}", table_cell_bold_style, bold=True),
        create_paragraph(sales_val, table_cell_style)
    ])
    
    factory_label = get_pdf_text("factory_style", pdf_lang)
    ship_label = get_pdf_text("ship_date", pdf_lang)
    
    if pdf_lang == "zh":
        ship_date_formatted = safe_date_format(ship_date_val, '%Y年%m月%d日')
    else:
        ship_date_formatted = safe_date_format(ship_date_val, '%Y-%m-%d')
    
    basic_data.append([
        create_paragraph(f"{factory_label}", table_cell_bold_style, bold=True),
        create_paragraph(factory_style_val, table_cell_style),
        create_paragraph(f"{ship_label}", table_cell_bold_style, bold=True),
        create_paragraph(ship_date_formatted, table_cell_style),
        create_paragraph("", table_cell_bold_style),
        create_paragraph("", table_cell_style)
    ])
    
    if pdf_lang == "zh":
        basic_table = Table(basic_data, colWidths=[1.0*inch, 1.5*inch, 1.0*inch, 1.3*inch, 1.0*inch, 1.5*inch])
    else:
        basic_table = Table(basic_data, colWidths=[0.9*inch, 1.4*inch, 0.8*inch, 1.2*inch, 0.9*inch, 1.4*inch])
    
    basic_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f7fafc'), colors.white]),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 12))
    
    # ========== SIZE & QUANTITY TABLE ==========
    # SIMPLIFIED - NO CALCULATIONS, JUST DISPLAY
    
    size_data = st.session_state.size_data
    
    if size_data:
        size_label = get_pdf_text("size", pdf_lang)
        die_qty_label = get_pdf_text("die_qty", pdf_lang)
        batch_qty_label = get_pdf_text("batch_qty", pdf_lang)
        
        qty_data = [[
            create_paragraph(size_label, table_header_style, bold=True),
            create_paragraph(die_qty_label, table_header_style, bold=True),
            create_paragraph(batch_qty_label, table_header_style, bold=True)
        ]]
        
        for item in size_data:
            # Get display values - NO CONVERSIONS
            size_val = item.get('size', '')
            die_qty_val = item.get('die_qty', '')
            batch_qty_val = item.get('batch_qty', '')
            
            # Clean for display
            size_display = get_display_text(size_val) or '-'
            die_qty_display = get_display_text(die_qty_val) or '-'
            batch_qty_display = get_display_text(batch_qty_val) or '-'
            
            qty_data.append([
                create_paragraph(size_display, table_cell_center_style),
                create_paragraph(die_qty_display, table_cell_center_style),
                create_paragraph(batch_qty_display, table_cell_center_style)
            ])
        
        qty_table = Table(qty_data, colWidths=[2.0*inch, 2.0*inch, 2.0*inch])
        qty_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(qty_table)
    else:
        # Fallback to simple display
        size_label = get_pdf_text("size", pdf_lang)
        die_qty_label = get_pdf_text("die_qty", pdf_lang)
        batch_qty_label = get_pdf_text("batch_qty", pdf_lang)
        
        size_val = get_pdf_display_value('size', pdf_lang)
        die_qty_val = get_pdf_display_value('die_qty', pdf_lang)
        batch_qty_val = get_pdf_display_value('batch_qty', pdf_lang)
        
        size_display = get_display_text(size_val) or '-'
        die_qty_display = get_display_text(die_qty_val) or '-'
        batch_qty_display = get_display_text(batch_qty_val) or '-'
        
        qty_data = [
            [
                create_paragraph(size_label, table_cell_bold_style, bold=True),
                create_paragraph(die_qty_label, table_cell_bold_style, bold=True),
                create_paragraph(batch_qty_label, table_cell_bold_style, bold=True)
            ],
            [
                create_paragraph(size_display, table_cell_center_style),
                create_paragraph(die_qty_display, table_cell_center_style),
                create_paragraph(batch_qty_display, table_cell_center_style)
            ]
        ]
        
        qty_table = Table(qty_data, colWidths=[2.0*inch, 2.0*inch, 2.0*inch])
        qty_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(qty_table)
    
    elements.append(Spacer(1, 15))
    
    # ========== MAIN CHECK POINTS ==========
    
    main_check_title = create_paragraph(get_pdf_text("main_check", pdf_lang), section_header_style, bold=True)
    elements.append(main_check_title)
    
    check_header = [
        create_paragraph(get_pdf_text("check_items", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("yes", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("no", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("comments", pdf_lang), table_header_style, bold=True)
    ]
    
    check_data = [check_header]
    
    check_items = [
        (get_pdf_text("last_no_correct", pdf_lang), "last_no_yes", "last_no_no", "last_no_comments"),
        (get_pdf_text("color_matches", pdf_lang), "color_yes", "color_no", "color_comments"),
        (get_pdf_text("tack_free", pdf_lang), "tack_free_yes", "tack_free_no", "tack_free_comments"),
        (get_pdf_text("size_run_match", pdf_lang), "size_run_yes", "size_run_no", "size_run_comments"),
        (get_pdf_text("fitting_correct", pdf_lang), "fitting_yes", "fitting_no", "fitting_comments"),
        (get_pdf_text("top_sample_sent", pdf_lang), "top_sample_yes", "top_sample_no", "top_sample_comments"),
    ]
    
    for item, yes_key, no_key, comment_key in check_items:
        yes_check = "✓" if st.session_state.get(yes_key, False) else ""
        no_check = "✓" if st.session_state.get(no_key, False) else ""
        comment = get_pdf_display_value(comment_key, pdf_lang)
        comment = get_display_text(comment)
        
        row = [
            create_paragraph(item, table_cell_style),
            create_paragraph(yes_check, table_cell_center_style),
            create_paragraph(no_check, table_cell_center_style),
            create_paragraph(comment if comment else "-", small_style)
        ]
        check_data.append(row)
    
    if pdf_lang == "zh":
        check_table = Table(check_data, colWidths=[2.5*inch, 0.5*inch, 0.5*inch, 2.0*inch])
    else:
        check_table = Table(check_data, colWidths=[2.2*inch, 0.4*inch, 0.4*inch, 2.6*inch])
    
    check_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(check_table)
    elements.append(Spacer(1, 15))
    
    # ========== TECHNICAL SPECIFICATIONS ==========
    
    tech_specs_title = create_paragraph(get_pdf_text("tech_specs", pdf_lang), section_header_style, bold=True)
    elements.append(tech_specs_title)
    
    same_check = "✓" if st.session_state.get('tech_specs_same', False) else ""
    tech_specs_comments_val = get_pdf_display_value('tech_specs_comments', pdf_lang)
    tech_specs_comments_val = get_display_text(tech_specs_comments_val)
    
    same_label = get_pdf_text("same", pdf_lang)
    if_not_label = get_pdf_text("if_not_same", pdf_lang)
    
    tech_data = [
        [
            create_paragraph(same_label, table_cell_bold_style, bold=True),
            create_paragraph(same_check, table_cell_center_style),
            create_paragraph(if_not_label, table_cell_bold_style, bold=True)
        ],
        [
            create_paragraph("", table_cell_style),
            create_paragraph("", table_cell_style),
            create_paragraph(tech_specs_comments_val if tech_specs_comments_val else "-", table_cell_style)
        ]
    ]
    
    tech_table = Table(tech_data, colWidths=[1.0*inch, 0.4*inch, 4.2*inch])
    tech_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#f0f4ff')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (2, 0), (2, -1)),
    ]))
    elements.append(tech_table)
    elements.append(Spacer(1, 15))
    
    # ========== TEST RESULTS ==========
    
    test_results_title = create_paragraph(get_pdf_text("test_results", pdf_lang), section_header_style, bold=True)
    elements.append(test_results_title)
    
    test_header = [
        create_paragraph(get_pdf_text("check_items", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("result", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("client_standard", pdf_lang), table_header_style, bold=True),
        create_paragraph("PASS/FAIL", table_header_style, bold=True)
    ]
    
    test_data = [test_header]
    
    if pdf_lang == "zh":
        test_items = [
            (get_pdf_text("sole_bonding", pdf_lang), "sole_bonding_result", "sole_bonding_pass", "sole_bonding_fail",
             "边墙鞋≥2.0 N/mm\n其他≥3.0 N/mm"),
            (get_pdf_text("heel_attachment", pdf_lang), "heel_attachment_result", "heel_attachment_pass", "heel_attachment_fail",
             "≥500N"),
            (get_pdf_text("top_piece", pdf_lang), "top_piece_result", "top_piece_pass", "top_piece_fail",
             "≥140N"),
            (get_pdf_text("insole_perment", pdf_lang), "insole_perment_result", "insole_perment_pass", "insole_perment_fail",
             "400N时变形量≤15%"),
            (get_pdf_text("straps_strength", pdf_lang), "straps_strength_result", "straps_strength_pass", "straps_strength_fail",
             "女鞋≥200N\n男鞋≥250N\n弹性部位≥150N\n童鞋≥250N"),
            (get_pdf_text("toe_post", pdf_lang), "toe_post_result", "toe_post_pass", "toe_post_fail",
             "EVA和橡胶材料≥150N\n其他材料≥200N")
        ]
    else:
        test_items = [
            (get_pdf_text("sole_bonding", pdf_lang), "sole_bonding_result", "sole_bonding_pass", "sole_bonding_fail",
             "Sidewall shoes ≥2.0 N/mm\nOthers ≥3.0 N/mm"),
            (get_pdf_text("heel_attachment", pdf_lang), "heel_attachment_result", "heel_attachment_pass", "heel_attachment_fail",
             "≥500N"),
            (get_pdf_text("top_piece", pdf_lang), "top_piece_result", "top_piece_pass", "top_piece_fail",
             "≥140N"),
            (get_pdf_text("insole_perment", pdf_lang), "insole_perment_result", "insole_perment_pass", "insole_perment_fail",
             "Deformation ≤15%\nat 400N"),
            (get_pdf_text("straps_strength", pdf_lang), "straps_strength_result", "straps_strength_pass", "straps_strength_fail",
             "Women ≥200N\nMen ≥250N\nElastic ≥150N\nChildren ≥250N"),
            (get_pdf_text("toe_post", pdf_lang), "toe_post_result", "toe_post_pass", "toe_post_fail",
             "EVA & rubber ≥150N\nOther ≥200N")
        ]
    
    for item, result_key, pass_key, fail_key, standard in test_items:
        result = get_pdf_display_value(result_key, pdf_lang)
        result = get_display_text(result)
        
        pass_check = st.session_state.get(pass_key, False)
        fail_check = st.session_state.get(fail_key, False)
        
        if pass_check:
            status = "PASS"
            status_color = success_color
        elif fail_check:
            status = "FAIL"
            status_color = colors.red
        else:
            status = "-"
            status_color = colors.HexColor('#666666')
        
        status_style = ParagraphStyle(
            'StatusStyle',
            parent=small_style,
            textColor=status_color,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        row = [
            create_paragraph(item, table_cell_style),
            create_paragraph(result if result else "-", table_cell_center_style),
            create_paragraph(standard, small_style),
            create_paragraph(status, status_style)
        ]
        test_data.append(row)
    
    if pdf_lang == "zh":
        test_table = Table(test_data, colWidths=[2.0*inch, 1.0*inch, 2.0*inch, 1.0*inch])
    else:
        test_table = Table(test_data, colWidths=[1.8*inch, 0.9*inch, 1.8*inch, 0.9*inch])
    
    test_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(test_table)
    elements.append(Spacer(1, 15))
    
    # ========== SIGNATURES ==========
    
    signatures_title = create_paragraph(get_pdf_text("signatures", pdf_lang), section_header_style, bold=True)
    elements.append(signatures_title)
    
    signature_date_val = st.session_state.get('signature_date', current_time)
    
    signatures = [
        (get_pdf_text("factory_rep", pdf_lang), "factory_representative", get_pdf_text("signature_date", pdf_lang)),
        (get_pdf_text("gs_qc", pdf_lang), "gs_qc", get_pdf_text("signature_date", pdf_lang)),
        (get_pdf_text("gs_tech", pdf_lang), "grandstep_technician", get_pdf_text("signature_date", pdf_lang)),
        (get_pdf_text("area_manager", pdf_lang), "area_manager", get_pdf_text("signature_date", pdf_lang)),
        (get_pdf_text("qa_manager", pdf_lang), "qa_manager", get_pdf_text("signature_date", pdf_lang)),
    ]
    
    if pdf_lang == "zh":
        date_formatted = safe_date_format(signature_date_val, '%Y年%m月%d日')
    else:
        date_formatted = safe_date_format(signature_date_val, '%Y-%m-%d')
    
    sig_data = []
    
    header_style = ParagraphStyle(
        'SignatureHeader',
        parent=table_cell_bold_style,
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.white,
        backColor=primary_color
    )
    
    sig_data.append([
        create_paragraph(get_pdf_text("check_items", pdf_lang), header_style),
        create_paragraph("姓名/签名" if pdf_lang == "zh" else "Name/Signature", header_style),
        create_paragraph("日期" if pdf_lang == "zh" else "Date", header_style)
    ])
    
    for label, key, date_label in signatures:
        value = get_pdf_display_value(key, pdf_lang)
        value = get_display_text(value)
        
        sig_row = [
            create_paragraph(label, table_cell_bold_style, bold=True),
            create_paragraph(value if value else "___________________", table_cell_style),
            create_paragraph(date_formatted, table_cell_center_style)
        ]
        sig_data.append(sig_row)
    
    if pdf_lang == "zh":
        signatures_table = Table(sig_data, colWidths=[2.2*inch, 2.5*inch, 1.3*inch])
    else:
        signatures_table = Table(sig_data, colWidths=[2.0*inch, 2.5*inch, 1.5*inch])
    
    signatures_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
    ]))
    
    elements.append(signatures_table)
    elements.append(Spacer(1, 15))
    
    # ========== FOOTER NOTES ==========
    
    updated_text = get_pdf_text("updated_2022", pdf_lang)
    elements.append(create_paragraph(updated_text, 
                                   ParagraphStyle(
                                       'Updated',
                                       parent=small_style,
                                       alignment=TA_RIGHT,
                                       fontSize=7
                                   )))
    
    elements.append(Spacer(1, 8))
    
    disclaimer_text = get_pdf_text("disclaimer_text", pdf_lang)
    elements.append(create_paragraph(disclaimer_text, small_style))
    
    # Build PDF
    try:
        doc.build(elements)
    except Exception as e:
        st.error(f"Error building PDF: {str(e)}")
        raise e
    
    buffer.seek(0)
    return buffer

# Sidebar
with st.sidebar:
    st.markdown(f'### {ICONS["settings"]} {get_text("settings")}')
    
    st.markdown(f'#### {ICONS["language"]} {get_text("language")}')
    
    ui_language = st.selectbox(
        get_text("user_interface_language"),
        ["English", "Mandarin"],
        index=0 if st.session_state.ui_language == "en" else 1,
        key="ui_lang_select"
    )
    
    new_ui_lang = "en" if ui_language == "English" else "zh"
    if new_ui_lang != st.session_state.ui_language:
        st.session_state.ui_language = new_ui_lang
        st.rerun()
    
    pdf_language = st.selectbox(
        get_text("pdf_report_language"),
        ["English", "Mandarin"],
        index=0 if st.session_state.pdf_language == "en" else 1,
        key="pdf_lang_select"
    )
    st.session_state.pdf_language = "en" if pdf_language == "English" else "zh"
    
    st.markdown(f'#### {ICONS["location"]} {get_text("location")}')
    selected_city = st.selectbox(
        get_text("select_location"),
        list(CHINESE_CITIES.keys()),
        index=list(CHINESE_CITIES.keys()).index(st.session_state.selected_city) 
        if st.session_state.selected_city in CHINESE_CITIES else 0,
        key="city_select"
    )
    st.session_state.selected_city = selected_city
    
    st.markdown(f"""
    <div class="location-badge">
        {ICONS["location"]} {selected_city} ({CHINESE_CITIES[selected_city]})
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'#### {ICONS["time"]} {get_text("local_time")}')
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    st.metric(
        get_text("local_time"), 
        current_time.strftime('%H:%M:%S'),
        current_time.strftime('%Y-%m-%d')
    )
    
    st.markdown("---")
    st.markdown(f'### {ICONS["info"]} {get_text("quick_guide")}')
    st.info(f"""
    {ICONS["info"]} **{get_text("quick_guide")}:**
    1. {ICONS["basic_info"]} {get_text("basic_info")}
    2. {ICONS["check"]} {get_text("main_check")}
    3. {ICONS["test_results"]} {get_text("test_results")}
    4. {ICONS["signatures"]} {get_text("signatures")}
    5. {ICONS["generate"]} {get_text("generate_pdf")}
    """)

# Main Title
st.markdown(f"""
<div class="main-header">
    {ICONS["title"]} {get_text("title")}
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    f"{ICONS['basic_info']} {get_text('basic_info')}",
    f"{ICONS['check']} {get_text('main_check')}",
    f"{ICONS['test_results']} {get_text('test_results')}",
    f"{ICONS['signatures']} {get_text('signatures')}"
])

with tab1:
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["basic_info"]}</span>
        {get_text("basic_info")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        die_cut_date = st.date_input(
            f"{ICONS['calendar']} {get_text('die_cut_date')}",
            datetime.now(),
            key="die_cut_date"
        )
    with col2:
        batch_test_date = st.date_input(
            f"{ICONS['calendar']} {get_text('batch_test_date')}",
            datetime.now(),
            key="batch_test_date"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        contract_no_display = get_display_value('contract_no')
        contract_no_input = st.text_input(
            f"{ICONS['info']} {get_text('contract_no')}", 
            value=contract_no_display,
            placeholder="CON-2024-001",
            key="contract_no_input"
        )
        if contract_no_input != contract_no_display:
            update_english_value('contract_no', contract_no_input)
        
        style_name_display = get_display_value('style_name')
        style_name_input = st.text_input(
            f"{ICONS['style']} {get_text('style_name')}", 
            value=style_name_display,
            placeholder="STYLE-2024-001",
            key="style_name_input"
        )
        if style_name_input != style_name_display:
            update_english_value('style_name', style_name_input)
        
        factory_style_display = get_display_value('factory_style')
        factory_style_input = st.text_input(
            f"{ICONS['factory']} {get_text('factory_style')}", 
            value=factory_style_display,
            placeholder="FAC-STYLE-001",
            key="factory_style_input"
        )
        if factory_style_input != factory_style_display:
            update_english_value('factory_style', factory_style_input)
    
    with col2:
        brand_display = get_display_value('brand')
        brand_input = st.text_input(
            f"{ICONS['brand']} {get_text('brand')}", 
            value=brand_display,
            placeholder="Brand Name",
            key="brand_input"
        )
        if brand_input != brand_display:
            update_english_value('brand', brand_input)
        
        qty_display = get_display_value('qty')
        qty_input = st.text_input(
            f"{ICONS['quantity']} {get_text('qty')}", 
            value=qty_display,
            placeholder="1000 pairs",
            key="qty_input"
        )
        if qty_input != qty_display:
            update_english_value('qty', qty_input)
        
        agent_factory_display = get_display_value('agent_factory')
        agent_factory_input = st.text_input(
            f"{ICONS['factory']} {get_text('agent_factory')}", 
            value=agent_factory_display,
            placeholder="Agent & Factory Name",
            key="agent_factory_input"
        )
        if agent_factory_input != agent_factory_display:
            update_english_value('agent_factory', agent_factory_input)
        
        sales_display = get_display_value('sales')
        sales_input = st.text_input(
            f"{ICONS['sales']} {get_text('sales')}", 
            value=sales_display,
            placeholder="Sales Representative",
            key="sales_input"
        )
        if sales_input != sales_display:
            update_english_value('sales', sales_input)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ship_date = st.date_input(
            f"{ICONS['calendar']} {get_text('ship_date')}", 
            datetime.now(),
            key="ship_date"
        )
    
    st.markdown(f"""
    <div class="section-header" style="margin-top: 30px;">
        <span class="section-header-icon">{ICONS["measure"]}</span>
        {get_text("size_table_title")}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="size-table-container">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
    with col1:
        st.markdown(f"**{get_text('size')}**")
    with col2:
        st.markdown(f"**{get_text('die_qty')}**")
    with col3:
        st.markdown(f"**{get_text('batch_qty')}**")
    with col4:
        st.markdown("**&nbsp;**")
    
    for i, size_item in enumerate(st.session_state.size_data):
        col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
        with col1:
            size_key = f"size_{i}"
            size_val = st.text_input(
                "Size",
                value=size_item.get('size', ''),
                placeholder="US 8, EU 41",
                key=size_key,
                label_visibility="collapsed"
            )
            st.session_state.size_data[i]['size'] = size_val
        with col2:
            die_qty_key = f"die_qty_{i}"
            die_qty_val = st.text_input(
                "Die Qty",
                value=size_item.get('die_qty', ''),
                placeholder="50",
                key=die_qty_key,
                label_visibility="collapsed"
            )
            st.session_state.size_data[i]['die_qty'] = die_qty_val
        with col3:
            batch_qty_key = f"batch_qty_{i}"
            batch_qty_val = st.text_input(
                "Batch Qty",
                value=size_item.get('batch_qty', ''),
                placeholder="200",
                key=batch_qty_key,
                label_visibility="collapsed"
            )
            st.session_state.size_data[i]['batch_qty'] = batch_qty_val
        with col4:
            if st.button(f"❌", key=f"remove_{i}", help=get_text("remove_size")):
                remove_size_row(i)
                st.rerun()
    
    if st.button(f"{ICONS['quantity']} {get_text('add_size')}", use_container_width=True):
        add_size_row()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["main_check"]}</span>
        {get_text("main_check")}
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"#### {ICONS['check']} {get_text('check_items')}")
        
        st.markdown(f"**{get_text('last_no_correct')}**")
        col1, col2 = st.columns(2)
        with col1:
            last_no_yes = st.checkbox(get_text('yes'), key="last_no_yes")
        with col2:
            last_no_no = st.checkbox(get_text('no'), key="last_no_no")
        
        last_no_comments_display = get_display_value('last_no_comments')
        last_no_comments_input = st.text_area(
            get_text('comments'),
            value=last_no_comments_display,
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="last_no_comments_input",
            label_visibility="collapsed"
        )
        if last_no_comments_input != last_no_comments_display:
            update_english_value('last_no_comments', last_no_comments_input)
        
        st.markdown(f"**{get_text('color_matches')}**")
        col1, col2 = st.columns(2)
        with col1:
            color_yes = st.checkbox(get_text('yes'), key="color_yes")
        with col2:
            color_no = st.checkbox(get_text('no'), key="color_no")
        
        color_comments_display = get_display_value('color_comments')
        color_comments_input = st.text_area(
            get_text('comments'),
            value=color_comments_display,
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="color_comments_input",
            label_visibility="collapsed"
        )
        if color_comments_input != color_comments_display:
            update_english_value('color_comments', color_comments_input)
        
        st.markdown(f"**{get_text('tack_free')}**")
        col1, col2 = st.columns(2)
        with col1:
            tack_free_yes = st.checkbox(get_text('yes'), key="tack_free_yes")
        with col2:
            tack_free_no = st.checkbox(get_text('no'), key="tack_free_no")
        
        tack_free_comments_display = get_display_value('tack_free_comments')
        tack_free_comments_input = st.text_area(
            get_text('comments'),
            value=tack_free_comments_display,
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="tack_free_comments_input",
            label_visibility="collapsed"
        )
        if tack_free_comments_input != tack_free_comments_display:
            update_english_value('tack_free_comments', tack_free_comments_input)
        
        st.markdown(f"**{get_text('tech_specs_compare')}**")
        tech_specs_same = st.checkbox(get_text('same'), key="tech_specs_same")
        
        tech_specs_comments_display = get_display_value('tech_specs_comments')
        tech_specs_comments_input = st.text_area(
            get_text('if_not_same'),
            value=tech_specs_comments_display,
            placeholder=f"{get_text('if_not_same')}...",
            height=80,
            key="tech_specs_comments_input",
            label_visibility="visible"
        )
        if tech_specs_comments_input != tech_specs_comments_display:
            update_english_value('tech_specs_comments', tech_specs_comments_input)
    
    with col_right:
        st.markdown(f"#### {ICONS['check']} {get_text('check_items')}")
        
        st.markdown(f"**{get_text('size_run_match')}**")
        col1, col2 = st.columns(2)
        with col1:
            size_run_yes = st.checkbox(get_text('yes'), key="size_run_yes")
        with col2:
            size_run_no = st.checkbox(get_text('no'), key="size_run_no")
        
        size_run_comments_display = get_display_value('size_run_comments')
        size_run_comments_input = st.text_area(
            get_text('comments'),
            value=size_run_comments_display,
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="size_run_comments_input",
            label_visibility="collapsed"
        )
        if size_run_comments_input != size_run_comments_display:
            update_english_value('size_run_comments', size_run_comments_input)
        
        st.markdown(f"**{get_text('fitting_correct')}**")
        col1, col2 = st.columns(2)
        with col1:
            fitting_yes = st.checkbox(get_text('yes'), key="fitting_yes")
        with col2:
            fitting_no = st.checkbox(get_text('no'), key="fitting_no")
        
        fitting_comments_display = get_display_value('fitting_comments')
        fitting_comments_input = st.text_area(
            get_text('comments'),
            value=fitting_comments_display,
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="fitting_comments_input",
            label_visibility="collapsed"
        )
        if fitting_comments_input != fitting_comments_display:
            update_english_value('fitting_comments', fitting_comments_input)
        
        st.markdown(f"**{get_text('top_sample_sent')}**")
        col1, col2 = st.columns(2)
        with col1:
            top_sample_yes = st.checkbox(get_text('yes'), key="top_sample_yes")
        with col2:
            top_sample_no = st.checkbox(get_text('no'), key="top_sample_no")
        
        top_sample_comments_display = get_display_value('top_sample_comments')
        top_sample_comments_input = st.text_area(
            get_text('comments'),
            value=top_sample_comments_display,
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="top_sample_comments_input",
            label_visibility="collapsed"
        )
        if top_sample_comments_input != top_sample_comments_display:
            update_english_value('top_sample_comments', top_sample_comments_input)
        
        st.markdown(f"**{get_text('tech_comments_completed')}**")
        col1, col2 = st.columns(2)
        with col1:
            tech_comments_yes = st.checkbox(get_text('yes'), key="tech_comments_yes")
        with col2:
            tech_comments_no = st.checkbox(get_text('no'), key="tech_comments_no")
        
        tech_comments_description_display = get_display_value('tech_comments_description')
        tech_comments_description_input = st.text_area(
            get_text('if_not_same'),
            value=tech_comments_description_display,
            placeholder=f"{get_text('if_not_same')}...",
            height=80,
            key="tech_comments_description_input",
            label_visibility="visible"
        )
        if tech_comments_description_input != tech_comments_description_display:
            update_english_value('tech_comments_description', tech_comments_description_input)

with tab3:
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["test_results"]}</span>
        {get_text("test_results")}
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"#### {ICONS['test']} {get_text('test_results')}")
        
        st.markdown(f"**{get_text('sole_bonding')}**")
        sole_bonding_result_display = get_display_value('sole_bonding_result')
        sole_bonding_result_input = st.text_input(
            f"{get_text('result')}",
            value=sole_bonding_result_display,
            placeholder=f"{get_text('result')}...",
            key="sole_bonding_result_input",
            label_visibility="collapsed"
        )
        if sole_bonding_result_input != sole_bonding_result_display:
            update_english_value('sole_bonding_result', sole_bonding_result_input)
        
        col_pass, col_fail = st.columns(2)
        with col_pass:
            sole_bonding_pass = st.checkbox("PASS", key="sole_bonding_pass")
        with col_fail:
            sole_bonding_fail = st.checkbox("FAIL", key="sole_bonding_fail")
        
        st.markdown(f"**{get_text('top_piece')}**")
        top_piece_result_display = get_display_value('top_piece_result')
        top_piece_result_input = st.text_input(
            f"{get_text('result')}",
            value=top_piece_result_display,
            placeholder=f"{get_text('result')}...",
            key="top_piece_result_input",
            label_visibility="collapsed"
        )
        if top_piece_result_input != top_piece_result_display:
            update_english_value('top_piece_result', top_piece_result_input)
        
        col_pass, col_fail = st.columns(2)
        with col_pass:
            top_piece_pass = st.checkbox("PASS", key="top_piece_pass")
        with col_fail:
            top_piece_fail = st.checkbox("FAIL", key="top_piece_fail")
        
        st.markdown(f"**{get_text('straps_strength')}**")
        straps_strength_result_display = get_display_value('straps_strength_result')
        straps_strength_result_input = st.text_input(
            f"{get_text('result')}",
            value=straps_strength_result_display,
            placeholder=f"{get_text('result')}...",
            key="straps_strength_result_input",
            label_visibility="collapsed"
        )
        if straps_strength_result_input != straps_strength_result_display:
            update_english_value('straps_strength_result', straps_strength_result_input)
        
        col_pass, col_fail = st.columns(2)
        with col_pass:
            straps_strength_pass = st.checkbox("PASS", key="straps_strength_pass")
        with col_fail:
            straps_strength_fail = st.checkbox("FAIL", key="straps_strength_fail")
    
    with col_right:
        st.markdown(f"#### {ICONS['test']} {get_text('test_results')}")
        
        st.markdown(f"**{get_text('heel_attachment')}**")
        heel_attachment_result_display = get_display_value('heel_attachment_result')
        heel_attachment_result_input = st.text_input(
            f"{get_text('result')}",
            value=heel_attachment_result_display,
            placeholder=f"{get_text('result')}...",
            key="heel_attachment_result_input",
            label_visibility="collapsed"
        )
        if heel_attachment_result_input != heel_attachment_result_display:
            update_english_value('heel_attachment_result', heel_attachment_result_input)
        
        col_pass, col_fail = st.columns(2)
        with col_pass:
            heel_attachment_pass = st.checkbox("PASS", key="heel_attachment_pass")
        with col_fail:
            heel_attachment_fail = st.checkbox("FAIL", key="heel_attachment_fail")
        
        st.markdown(f"**{get_text('insole_perment')}**")
        insole_perment_result_display = get_display_value('insole_perment_result')
        insole_perment_result_input = st.text_input(
            f"{get_text('result')}",
            value=insole_perment_result_display,
            placeholder=f"{get_text('result')}...",
            key="insole_perment_result_input",
            label_visibility="collapsed"
        )
        if insole_perment_result_input != insole_perment_result_display:
            update_english_value('insole_perment_result', insole_perment_result_input)
        
        col_pass, col_fail = st.columns(2)
        with col_pass:
            insole_perment_pass = st.checkbox("PASS", key="insole_perment_pass")
        with col_fail:
            insole_perment_fail = st.checkbox("FAIL", key="insole_perment_fail")
        
        st.markdown(f"**{get_text('toe_post')}**")
        toe_post_result_display = get_display_value('toe_post_result')
        toe_post_result_input = st.text_input(
            f"{get_text('result')}",
            value=toe_post_result_display,
            placeholder=f"{get_text('result')}...",
            key="toe_post_result_input",
            label_visibility="collapsed"
        )
        if toe_post_result_input != toe_post_result_display:
            update_english_value('toe_post_result', toe_post_result_input)
        
        col_pass, col_fail = st.columns(2)
        with col_pass:
            toe_post_pass = st.checkbox("PASS", key="toe_post_pass")
        with col_fail:
            toe_post_fail = st.checkbox("FAIL", key="toe_post_fail")

with tab4:
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["signatures"]}</span>
        {get_text("signatures")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        factory_representative_display = get_display_value('factory_representative')
        factory_representative_input = st.text_input(
            f"{ICONS['factory']} {get_text('factory_rep')}",
            value=factory_representative_display,
            placeholder=f"{get_text('factory_rep')}...",
            key="factory_representative_input"
        )
        if factory_representative_input != factory_representative_display:
            update_english_value('factory_representative', factory_representative_input)
        
        gs_qc_display = get_display_value('gs_qc')
        gs_qc_input = st.text_input(
            f"{ICONS['qc']} {get_text('gs_qc')}",
            value=gs_qc_display,
            placeholder=f"{get_text('gs_qc')}...",
            key="gs_qc_input"
        )
        if gs_qc_input != gs_qc_display:
            update_english_value('gs_qc', gs_qc_input)
        
        area_manager_display = get_display_value('area_manager')
        area_manager_input = st.text_input(
            f"{ICONS['tech']} {get_text('area_manager')}",
            value=area_manager_display,
            placeholder=f"{get_text('area_manager')}...",
            key="area_manager_input"
        )
        if area_manager_input != area_manager_display:
            update_english_value('area_manager', area_manager_input)
    
    with col2:
        grandstep_technician_display = get_display_value('grandstep_technician')
        grandstep_technician_input = st.text_input(
            f"{ICONS['tech']} {get_text('gs_tech')}",
            value=grandstep_technician_display,
            placeholder=f"{get_text('gs_tech')}...",
            key="grandstep_technician_input"
        )
        if grandstep_technician_input != grandstep_technician_display:
            update_english_value('grandstep_technician', grandstep_technician_input)
        
        qa_manager_display = get_display_value('qa_manager')
        qa_manager_input = st.text_input(
            f"{ICONS['qc']} {get_text('qa_manager')}",
            value=qa_manager_display,
            placeholder=f"{get_text('qa_manager')}...",
            key="qa_manager_input"
        )
        if qa_manager_input != qa_manager_display:
            update_english_value('qa_manager', qa_manager_input)
        
        signature_date = st.date_input(
            f"{ICONS['calendar']} {get_text('signature_date')}",
            datetime.now(),
            key="signature_date"
        )
    
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; margin-top: 20px;'>
        <strong>{get_text('disclaimer')}:</strong> {get_text('disclaimer_text')}
    </div>
    """, unsafe_allow_html=True)

# Generate PDF Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(f"{ICONS['generate']} {get_text('generate_pdf')}", use_container_width=True):
        if not st.session_state.english_values.get('contract_no') or not st.session_state.english_values.get('style_name'):
            st.error(f"{ICONS['error']} {get_text('fill_required')}")
        else:
            with st.spinner(f"{ICONS['time']} {get_text('creating_pdf')}"):
                try:
                    pdf_buffer = generate_pdf()
                    st.success(f"{ICONS['success']} {get_text('generate_success')}")
                    
                    with st.expander(f"{ICONS['info']} {get_text('pdf_details')}"):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric(get_text("location"), f"{selected_city} ({CHINESE_CITIES[selected_city]})")
                            st.metric(get_text("report_language"), "Mandarin" if st.session_state.pdf_language == "zh" else "English")
                        with col_info2:
                            china_tz = pytz.timezone('Asia/Shanghai')
                            current_time = datetime.now(china_tz)
                            st.metric(get_text("generated"), current_time.strftime('%H:%M:%S'))
                    
                    filename = f"DieCut_Test_{st.session_state.english_values.get('contract_no', '')}_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    st.download_button(
                        label=f"{ICONS['download']} {get_text('download_pdf')}",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"{ICONS['error']} {get_text('error_generating')}: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <p style='font-size: 1.2rem; font-weight: 600; color: #667eea; margin-bottom: 0.5rem;'>
        {ICONS['title']} {get_text('footer_text')}
    </p>
    <p style='font-size: 0.9rem; color: #666666;'>
        {ICONS['location']} {get_text('location')}: {selected_city} ({CHINESE_CITIES[selected_city]}) | 
        {ICONS['language']} {get_text('report_language')}: {'Mandarin' if st.session_state.pdf_language == 'zh' else 'English'}
    </p>
    <p style='font-size: 0.8rem; color: #999999; margin-top: 1rem;'>
        {get_text('powered_by')} | {get_text('copyright')}
    </p>
</div>
""", unsafe_allow_html=True)
