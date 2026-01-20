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
    "Guangzhou": "广东",
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
    "Chengdu": "成都",
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'ui_language' not in st.session_state:
    st.session_state.ui_language = "en"
if 'pdf_language' not in st.session_state:
    st.session_state.pdf_language = "en"
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Shanghai"

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

# ENHANCED PDF Generation with pure language support
# Replace the DieCutPDF class with this corrected version:

class DieCutPDF(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        self.pdf_language = kwargs.pop('pdf_language', 'en')
        self.selected_city = kwargs.pop('selected_city', '')
        self.chinese_city = kwargs.pop('chinese_city', '')
        super().__init__(*args, **kwargs)
        
    def onFirstPage(self, canvas, doc):
        """Add header to first page"""
        canvas.saveState()
        
        # Company header at top center
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(colors.HexColor('#667eea'))
        
        if self.pdf_language == "zh":
            company_name = "志途"
            report_title = "斩刀试做报告"
        else:
            company_name = "Grandstep"
            report_title = "Die Cut Test Report"
        
        # Company name at top center
        canvas.drawCentredString(doc.pagesize[0]/2, doc.pagesize[1] - 0.5*inch, company_name)
        
        # Report title below company name
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(colors.HexColor('#333333'))
        canvas.drawCentredString(doc.pagesize[0]/2, doc.pagesize[1] - 0.7*inch, report_title)
        
        # Add decorative line
        canvas.setStrokeColor(colors.HexColor('#667eea'))
        canvas.setLineWidth(1)
        canvas.line(1*inch, doc.pagesize[1] - 0.8*inch, doc.pagesize[0] - 1*inch, doc.pagesize[1] - 0.8*inch)
        
        canvas.restoreState()
        self._addFooter(canvas, doc, 1)
        
    def onLaterPages(self, canvas, doc):
        """Add header to later pages"""
        canvas.saveState()
        
        # Add decorative line at top of other pages
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(0.5)
        canvas.line(0.5*inch, doc.pagesize[1] - 0.5*inch, doc.pagesize[0] - 0.5*inch, doc.pagesize[1] - 0.5*inch)
        
        canvas.restoreState()
        self._addFooter(canvas, doc, canvas.getPageNumber())
        
    def _addFooter(self, canvas, doc, page_num):
        """Add footer to pages"""
        canvas.saveState()
        
        # Footer border
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(0.5)
        canvas.line(0.5*inch, 0.6*inch, doc.pagesize[0] - 0.5*inch, 0.6*inch)
        
        # Footer text
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        
        # China timezone for footer
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
        
        # Left: Location
        canvas.drawString(0.5*inch, 0.3*inch, location_text)
        
        # Center: Company name
        company_footer = "志途质量检测" if self.pdf_language == "zh" else "Grandstep QC"
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(colors.HexColor('#667eea'))
        canvas.drawCentredString(doc.pagesize[0]/2, 0.3*inch, company_footer)
        
        # Right: Date and page number
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        right_text = f"{date_text} | {page_num_text}"
        canvas.drawRightString(doc.pagesize[0] - 0.5*inch, 0.3*inch, right_text)
        
        canvas.restoreState()
def generate_pdf():
    """Generate Die Cut Test PDF report with enhanced design"""
    buffer = io.BytesIO()
    
    # Get location info
    selected_city = st.session_state.selected_city
    chinese_city = CHINESE_CITIES[selected_city]
    pdf_lang = st.session_state.pdf_language
    
    # Create PDF with better margins
    doc = DieCutPDF(
        buffer, 
        pagesize=A4,
        topMargin=1.2*inch,  # Increased from 0.8*inch
        bottomMargin=0.8*inch,
        leftMargin=0.6*inch,
        rightMargin=0.6*inch,
        pdf_language=pdf_lang,
        selected_city=selected_city,
        chinese_city=chinese_city
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # ========== DEFINE ENHANCED STYLES ==========
    
    # Primary color scheme
    primary_color = colors.HexColor('#667eea')
    secondary_color = colors.HexColor('#764ba2')
    light_bg = colors.HexColor('#f8f9fa')
    dark_bg = colors.HexColor('#2c3e50')
    success_color = colors.HexColor('#48bb78')
    warning_color = colors.HexColor('#ed8936')
    
    # Title style with gradient effect simulation
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=primary_color,
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        underlineWidth=1,
        underlineColor=secondary_color,
        underlineOffset=-0.1*inch,
        spaceBefore=5
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    # Section header style
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
    
    # Table header style
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        backColor=primary_color
    )
    
    # Table cell styles
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        fontName='Helvetica',
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
    
    table_cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        leading=10
    )
    
    # Small text style
    small_style = ParagraphStyle(
        'SmallStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=9,
        fontName='Helvetica',
        textColor=colors.HexColor('#555555')
    )
    
    small_bold_style = ParagraphStyle(
        'SmallBoldStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#333333')
    )
    
    # Signature style
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=9,
        textColor=dark_bg,
        fontName='Helvetica-Bold',
        leading=12
    )
    
    # Disclaimer style
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.red,
        fontName='Helvetica-Oblique',
        leading=8,
        borderWidth=1,
        borderColor=colors.HexColor('#fed7d7'),
        borderPadding=2,
        backColor=colors.HexColor('#fff5f5')
    )
    
    # Success/Fail indicators
    pass_style = ParagraphStyle(
        'Pass',
        parent=small_style,
        textColor=success_color,
        fontName='Helvetica-Bold'
    )
    
    fail_style = ParagraphStyle(
        'Fail',
        parent=small_style,
        textColor=colors.red,
        fontName='Helvetica-Bold'
    )
    
    # Helper function for creating paragraphs
    def create_paragraph(text, style, bold=False, color=None):
        """Create paragraph with appropriate styling"""
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
    
    # Main Title
    title_text = get_pdf_text("title", pdf_lang)
    elements.append(create_paragraph(title_text, title_style, bold=True))
    
    # Subtitle with test dates
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    
    die_cut_date = st.session_state.get('die_cut_date', current_time)
    batch_test_date = st.session_state.get('batch_test_date', current_time)
    
    if pdf_lang == "zh":
        # Pure Chinese date format
        subtitle_text = f"报告生成: {current_time.strftime('%Y年%m月%d日 %H时%M分')} | 测试地点: {chinese_city}"
    else:
        # Pure English date format
        subtitle_text = f"Report Generated: {current_time.strftime('%Y-%m-%d %H:%M')} | Test Location: {selected_city}"
    
    elements.append(create_paragraph(subtitle_text, subtitle_style))
    elements.append(Spacer(1, 8))
    
    # Add decorative line

    elements.append(Spacer(1, 12))
    
    # ========== TEST DATES HEADER ==========
    
    die_cut_text = get_pdf_text("die_cut_test", pdf_lang)
    batches_text = get_pdf_text("batch_test", pdf_lang)
    date_text = get_pdf_text("signature_date", pdf_lang)
    
    # Create test date header with pure language
    if pdf_lang == "zh":
        test_header_data = [
            [
                create_paragraph(die_cut_text, table_cell_bold_style, bold=True),
                create_paragraph(":", small_bold_style),
                create_paragraph(die_cut_date.strftime('%Y年%m月%d日') if hasattr(die_cut_date, 'strftime') else str(die_cut_date), small_bold_style),
                create_paragraph("", small_style),
                create_paragraph(batches_text, table_cell_bold_style, bold=True),
                create_paragraph(":", small_bold_style),
                create_paragraph(batch_test_date.strftime('%Y年%m月%d日') if hasattr(batch_test_date, 'strftime') else str(batch_test_date), small_bold_style)
            ]
        ]
    else:
        test_header_data = [
            [
                create_paragraph(die_cut_text, table_cell_bold_style, bold=True),
                create_paragraph(":", small_bold_style),
                create_paragraph(die_cut_date.strftime('%Y-%m-%d') if hasattr(die_cut_date, 'strftime') else str(die_cut_date), small_bold_style),
                create_paragraph("", small_style),
                create_paragraph(batches_text, table_cell_bold_style, bold=True),
                create_paragraph(":", small_bold_style),
                create_paragraph(batch_test_date.strftime('%Y-%m-%d') if hasattr(batch_test_date, 'strftime') else str(batch_test_date), small_bold_style)
            ]
        ]
    
    test_header_table = Table(test_header_data, colWidths=[1.2*inch, 0.1*inch, 1.0*inch, 0.2*inch, 1.2*inch, 0.1*inch, 1.0*inch])
    test_header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 0), (-1, -1), 0.5, primary_color),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, primary_color),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(test_header_table)
    elements.append(Spacer(1, 15))
    
    # ========== BASIC INFORMATION ==========
    
    # Section header
    basic_info_title = create_paragraph(get_pdf_text("basic_info", pdf_lang), section_header_style, bold=True)
    elements.append(basic_info_title)
    
    # Get values
    contract_no_val = st.session_state.get('contract_no', '')
    brand_val = st.session_state.get('brand', '')
    agent_factory_val = st.session_state.get('agent_factory', '')
    style_name_val = st.session_state.get('style_name', '')
    qty_val = st.session_state.get('qty', '')
    sales_val = st.session_state.get('sales', '')
    factory_style_val = st.session_state.get('factory_style', '')
    ship_date_val = st.session_state.get('ship_date', '')
    
    # Create a cleaner table layout with pure language
    basic_data = []
    
    # Row 1
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
    
    # Row 2
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
    
    # Row 3
    factory_label = get_pdf_text("factory_style", pdf_lang)
    ship_label = get_pdf_text("ship_date", pdf_lang)
    
    if pdf_lang == "zh":
        ship_date_formatted = ship_date_val.strftime('%Y年%m月%d日') if hasattr(ship_date_val, 'strftime') else str(ship_date_val)
    else:
        ship_date_formatted = ship_date_val.strftime('%Y-%m-%d') if hasattr(ship_date_val, 'strftime') else str(ship_date_val)
    
    basic_data.append([
        create_paragraph(f"{factory_label}", table_cell_bold_style, bold=True),
        create_paragraph(factory_style_val, table_cell_style),
        create_paragraph(f"{ship_label}", table_cell_bold_style, bold=True),
        create_paragraph(ship_date_formatted, table_cell_style),
        create_paragraph("", table_cell_bold_style),
        create_paragraph("", table_cell_style)
    ])
    
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
    
    # ========== QUANTITY INFORMATION ==========
    
    size_val = st.session_state.get('size', '')
    die_qty_val = st.session_state.get('die_qty', '')
    batch_qty_val = st.session_state.get('batch_qty', '')
    
    size_label = get_pdf_text("size", pdf_lang)
    die_qty_label = get_pdf_text("die_qty", pdf_lang)
    batch_qty_label = get_pdf_text("batch_qty", pdf_lang)
    
    qty_data = [
        [
            create_paragraph(size_label, table_cell_bold_style, bold=True),
            create_paragraph(die_qty_label, table_cell_bold_style, bold=True),
            create_paragraph(batch_qty_label, table_cell_bold_style, bold=True)
        ],
        [
            create_paragraph(size_val, table_cell_center_style),
            create_paragraph(die_qty_val, table_cell_center_style),
            create_paragraph(batch_qty_val, table_cell_center_style)
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
    
    # Create a visually appealing check points table with pure language
    check_header = [
        create_paragraph(get_pdf_text("check_items", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("yes", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("no", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("comments", pdf_lang), table_header_style, bold=True)
    ]
    
    check_data = [check_header]
    
    # Define check items
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
        comment = st.session_state.get(comment_key, '')
        
        row = [
            create_paragraph(item, table_cell_style),
            create_paragraph(yes_check, table_cell_center_style),
            create_paragraph(no_check, table_cell_center_style),
            create_paragraph(comment if comment else "-", small_style)
        ]
        check_data.append(row)
    
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
    
    # Tech specs comparison with better styling
    same_check = "✓" if st.session_state.get('tech_specs_same', False) else ""
    tech_specs_comments_val = st.session_state.get('tech_specs_comments', '')
    
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
    
    # ========== TECH COMMENTS ==========
    
    tech_comments_title = create_paragraph(get_pdf_text("tech_comments_completed", pdf_lang), 
                                          ParagraphStyle(
                                              'TechComments',
                                              parent=section_header_style,
                                              fontSize=10,
                                              spaceAfter=6
                                          ), bold=True)
    elements.append(tech_comments_title)
    
    tech_comments_yes = "✓" if st.session_state.get('tech_comments_yes', False) else ""
    tech_comments_no = "✓" if st.session_state.get('tech_comments_no', False) else ""
    tech_comments_desc = st.session_state.get('tech_comments_description', '')
    
    yes_label = get_pdf_text("yes", pdf_lang)
    no_label = get_pdf_text("no", pdf_lang)
    
    comments_data = [
        [
            create_paragraph(yes_label, table_cell_bold_style, bold=True),
            create_paragraph(tech_comments_yes, table_cell_center_style),
            create_paragraph(no_label, table_cell_bold_style, bold=True),
            create_paragraph(tech_comments_no, table_cell_center_style),
            create_paragraph(get_pdf_text("if_not_same", pdf_lang), table_cell_bold_style, bold=True)
        ],
        [
            create_paragraph("", table_cell_style),
            create_paragraph("", table_cell_style),
            create_paragraph("", table_cell_style),
            create_paragraph("", table_cell_style),
            create_paragraph(tech_comments_desc if tech_comments_desc else "-", table_cell_style)
        ]
    ]
    
    comments_table = Table(comments_data, colWidths=[0.6*inch, 0.3*inch, 0.6*inch, 0.3*inch, 4.0*inch])
    comments_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (4, 0), colors.HexColor('#f0f4ff')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (3, 0), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('SPAN', (4, 0), (4, -1)),
    ]))
    elements.append(comments_table)
    elements.append(Spacer(1, 15))
    
    # ========== TEST RESULTS ==========
    
    test_results_title = create_paragraph(get_pdf_text("test_results", pdf_lang), section_header_style, bold=True)
    elements.append(test_results_title)
    
    # Test results table with pure language
    test_header = [
        create_paragraph(get_pdf_text("check_items", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("result", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("client_standard", pdf_lang), table_header_style, bold=True),
        create_paragraph(get_pdf_text("pass_fail", pdf_lang), table_header_style, bold=True)
    ]
    
    test_data = [test_header]
    
    # Test items with pure language standards
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
        result = st.session_state.get(result_key, '')
        pass_check = st.session_state.get(pass_key, False)
        fail_check = st.session_state.get(fail_key, False)
        
        if pass_check:
            status = create_paragraph("PASS", pass_style)
        elif fail_check:
            status = create_paragraph("FAIL", fail_style)
        else:
            if pdf_lang == "zh":
                status = create_paragraph("待定", small_style)
            else:
                status = create_paragraph("PENDING", small_style)
        
        row = [
            create_paragraph(item, table_cell_style),
            create_paragraph(result if result else "-", table_cell_center_style),
            create_paragraph(standard, small_style),
            status
        ]
        test_data.append(row)
    
    test_table = Table(test_data, colWidths=[1.8*inch, 0.9*inch, 1.8*inch, 0.9*inch])
    test_table.setStyle(TableStyle([
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ('BACKGROUND', (0, 0), (-1, 0), primary_color),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align all cells
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('PADDING', (0, 0), (-1, -1), 4),
    ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
]))
    elements.append(test_table)
    elements.append(Spacer(1, 15))
    
    # ========== ISSUES & SOLUTIONS ==========
    
    issues_title = create_paragraph(get_pdf_text("issues_solutions", pdf_lang), section_header_style, bold=True)
    elements.append(issues_title)
    
    # Two-column layout for issues
    die_cut_issues = st.session_state.get('die_cut_issues', '')
    batch_test_issues = st.session_state.get('batch_test_issues', '')
    
    if pdf_lang == "zh":
        no_issues_text = "无问题报告"
    else:
        no_issues_text = "No issues reported"
    
    issues_data = [
        [
            create_paragraph(get_pdf_text("die_cut_test", pdf_lang), 
                           ParagraphStyle(
                               'IssuesHeader',
                               parent=table_cell_bold_style,
                               fontSize=9,
                               textColor=primary_color,
                               alignment=TA_CENTER,
                               backColor=colors.HexColor('#f0f4ff')
                           ), bold=True),
            create_paragraph(get_pdf_text("batch_test", pdf_lang), 
                           ParagraphStyle(
                               'IssuesHeader',
                               parent=table_cell_bold_style,
                               fontSize=9,
                               textColor=secondary_color,
                               alignment=TA_CENTER,
                               backColor=colors.HexColor('#f5f0ff')
                           ), bold=True)
        ],
        [
            create_paragraph(die_cut_issues if die_cut_issues else no_issues_text, 
                           ParagraphStyle(
                               'IssuesContent',
                               parent=table_cell_style,
                               fontSize=8,
                               borderWidth=1,
                               borderColor=colors.HexColor('#e2e8f0'),
                               borderPadding=6,
                               backColor=colors.HexColor('#f8f9fa')
                           )),
            create_paragraph(batch_test_issues if batch_test_issues else no_issues_text, 
                           ParagraphStyle(
                               'IssuesContent',
                               parent=table_cell_style,
                               fontSize=8,
                               borderWidth=1,
                               borderColor=colors.HexColor('#e2e8f0'),
                               borderPadding=6,
                               backColor=colors.HexColor('#f8f9fa')
                           ))
        ]
    ]
    
    issues_table = Table(issues_data, colWidths=[2.8*inch, 2.8*inch])
    issues_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#c3dafe')),
    ]))
    elements.append(issues_table)
    elements.append(Spacer(1, 20))
    
    # ========== SIGNATURES ==========
    
       # ========== SIGNATURES ==========
    
    signatures_title = create_paragraph(get_pdf_text("signatures", pdf_lang), section_header_style, bold=True)
    elements.append(signatures_title)
    
    signature_date_val = st.session_state.get('signature_date', current_time)
    
    # Create professional signature table
    signatures = [
        (get_pdf_text("factory_rep", pdf_lang), "factory_representative", get_pdf_text("signature_date", pdf_lang)),
        (get_pdf_text("gs_qc", pdf_lang), "gs_qc", get_pdf_text("signature_date", pdf_lang)),
        (get_pdf_text("gs_tech", pdf_lang), "grandstep_technician", get_pdf_text("signature_date", pdf_lang)),
        (get_pdf_text("area_manager", pdf_lang), "area_manager", get_pdf_text("signature_date", pdf_lang)),
        (get_pdf_text("qa_manager", pdf_lang), "qa_manager", get_pdf_text("signature_date", pdf_lang)),
    ]
    
    # Format date based on language
    if pdf_lang == "zh":
        date_formatted = signature_date_val.strftime('%Y年%m月%d日') if hasattr(signature_date_val, 'strftime') else str(signature_date_val)
    else:
        date_formatted = signature_date_val.strftime('%Y-%m-%d') if hasattr(signature_date_val, 'strftime') else str(signature_date_val)
    
    # Create signature data
    sig_data = []
    
    # Header row
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
        create_paragraph("Name/Signature", header_style),
        create_paragraph("Date", header_style)
    ])
    
    # Signature rows
    for label, key, date_label in signatures:
        value = st.session_state.get(key, '')
        
        sig_row = [
            create_paragraph(label, table_cell_bold_style, bold=True),
            create_paragraph(value if value else "___________________", 
                           ParagraphStyle(
                               'SignatureLine',
                               parent=table_cell_style,
                               fontSize=10,
                               textColor=dark_bg
                           )),
            create_paragraph(date_formatted, table_cell_center_style)
        ]
        sig_data.append(sig_row)
    
    # Create signature table with professional styling
    signatures_table = Table(sig_data, colWidths=[2.0*inch, 2.5*inch, 1.5*inch])
    signatures_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center align header
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Center align dates
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),  # White line under header
    ]))
    
    elements.append(signatures_table)
    elements.append(Spacer(1, 15))
    # ========== FOOTER NOTES ==========
    
    # Updated date
    updated_text = get_pdf_text("updated_2022", pdf_lang)
    elements.append(create_paragraph(updated_text, 
                                   ParagraphStyle(
                                       'Updated',
                                       parent=small_style,
                                       alignment=TA_RIGHT,
                                       fontSize=7
                                   )))
    
    elements.append(Spacer(1, 8))
    
    # Disclaimer with better styling
 
    
    # Final decorative element
    elements.append(create_paragraph("•" * 80, ParagraphStyle(
        'EndLine',
        parent=styles['Normal'],
        fontSize=7,
        textColor=primary_color,
        alignment=TA_CENTER,
        spaceBefore=8
    )))
    
    # Build PDF
    try:
        doc.build(elements)
    except Exception as e:
        # Fallback to simple build if custom class fails
        SimpleDocTemplate.build(doc, elements)
    
    buffer.seek(0)
    return buffer
    buffer.seek(0)
    return buffer

# Sidebar
with st.sidebar:
    st.markdown(f'### {ICONS["settings"]} {get_text("settings")}')
    
    # Language settings - SEPARATED
    st.markdown(f'#### {ICONS["language"]} {get_text("language")}')
    
    # UI Language
    ui_language = st.selectbox(
        get_text("user_interface_language"),
        ["English", "Mandarin"],
        index=0 if st.session_state.ui_language == "en" else 1,
        key="ui_lang_select"
    )
    st.session_state.ui_language = "en" if ui_language == "English" else "zh"
    
    # PDF Language (separate from UI)
    pdf_language = st.selectbox(
        get_text("pdf_report_language"),
        ["English", "Mandarin"],
        index=0 if st.session_state.pdf_language == "en" else 1,
        key="pdf_lang_select"
    )
    st.session_state.pdf_language = "en" if pdf_language == "English" else "zh"
    
    # Location
    st.markdown(f'#### {ICONS["location"]} {get_text("location")}')
    selected_city = st.selectbox(
        get_text("select_location"),
        list(CHINESE_CITIES.keys()),
        index=list(CHINESE_CITIES.keys()).index(st.session_state.selected_city) 
        if st.session_state.selected_city in CHINESE_CITIES else 0,
        key="city_select"
    )
    st.session_state.selected_city = selected_city
    
    # Location badge
    st.markdown(f"""
    <div class="location-badge">
        {ICONS["location"]} {selected_city} ({CHINESE_CITIES[selected_city]})
    </div>
    """, unsafe_allow_html=True)
    
    # Time
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
    # Basic Information
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["basic_info"]}</span>
        {get_text("basic_info")}
    </div>
    """, unsafe_allow_html=True)
    
    # Test Dates
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
    
    # Main info
    col1, col2 = st.columns(2)
    with col1:
        contract_no = st.text_input(
            f"{ICONS['info']} {get_text('contract_no')}", 
            placeholder="CON-2024-001",
            key="contract_no"
        )
        style_name = st.text_input(
            f"{ICONS['style']} {get_text('style_name')}", 
            placeholder="STYLE-2024-001",
            key="style_name"
        )
        factory_style = st.text_input(
            f"{ICONS['factory']} {get_text('factory_style')}", 
            placeholder="FAC-STYLE-001",
            key="factory_style"
        )
        size = st.text_input(
            f"{ICONS['measure']} {get_text('size')}", 
            placeholder="US 8, EU 41, UK 7",
            key="size"
        )
    
    with col2:
        brand = st.text_input(
            f"{ICONS['brand']} {get_text('brand')}", 
            placeholder="Brand Name",
            key="brand"
        )
        qty = st.text_input(
            f"{ICONS['quantity']} {get_text('qty')}", 
            placeholder="1000 pairs",
            key="qty"
        )
        agent_factory = st.text_input(
            f"{ICONS['factory']} {get_text('agent_factory')}", 
            placeholder="Agent & Factory Name",
            key="agent_factory"
        )
        sales = st.text_input(
            f"{ICONS['sales']} {get_text('sales')}", 
            placeholder="Sales Representative",
            key="sales"
        )
    
    # Quantity and Ship Date
    col1, col2, col3 = st.columns(3)
    with col1:
        die_qty = st.text_input(
            f"{ICONS['quantity']} {get_text('die_qty')}", 
            placeholder="50 pairs",
            key="die_qty"
        )
    with col2:
        batch_qty = st.text_input(
            f"{ICONS['quantity']} {get_text('batch_qty')}", 
            placeholder="200 pairs",
            key="batch_qty"
        )
    with col3:
        ship_date = st.date_input(
            f"{ICONS['calendar']} {get_text('ship_date')}", 
            datetime.now(),
            key="ship_date"
        )

with tab2:
    # Main Check Points
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["main_check"]}</span>
        {get_text("main_check")}
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"#### {ICONS['check']} {get_text('check_items')}")
        
        # Last No. Correct
        st.markdown(f"**{get_text('last_no_correct')}**")
        col1, col2 = st.columns(2)
        with col1:
            last_no_yes = st.checkbox(get_text('yes'), key="last_no_yes")
        with col2:
            last_no_no = st.checkbox(get_text('no'), key="last_no_no")
        last_no_comments = st.text_area(
            get_text('comments'),
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="last_no_comments",
            label_visibility="collapsed"
        )
        
        # Color matches cfm sample
        st.markdown(f"**{get_text('color_matches')}**")
        col1, col2 = st.columns(2)
        with col1:
            color_yes = st.checkbox(get_text('yes'), key="color_yes")
        with col2:
            color_no = st.checkbox(get_text('no'), key="color_no")
        color_comments = st.text_area(
            get_text('comments'),
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="color_comments",
            label_visibility="collapsed"
        )
        
        # TACK FREE POLICY FOLLOW?
        st.markdown(f"**{get_text('tack_free')}**")
        col1, col2 = st.columns(2)
        with col1:
            tack_free_yes = st.checkbox(get_text('yes'), key="tack_free_yes")
        with col2:
            tack_free_no = st.checkbox(get_text('no'), key="tack_free_no")
        tack_free_comments = st.text_area(
            get_text('comments'),
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="tack_free_comments",
            label_visibility="collapsed"
        )
        
        # Tech specifications
        st.markdown(f"**{get_text('tech_specs_compare')}**")
        tech_specs_same = st.checkbox(get_text('same'), key="tech_specs_same")
        tech_specs_comments = st.text_area(
            get_text('if_not_same'),
            placeholder=f"{get_text('if_not_same')}...",
            height=80,
            key="tech_specs_comments",
            label_visibility="visible"
        )
    
    with col_right:
        st.markdown(f"#### {ICONS['check']} {get_text('check_items')}")
        
        # Size Run Match Order
        st.markdown(f"**{get_text('size_run_match')}**")
        col1, col2 = st.columns(2)
        with col1:
            size_run_yes = st.checkbox(get_text('yes'), key="size_run_yes")
        with col2:
            size_run_no = st.checkbox(get_text('no'), key="size_run_no")
        size_run_comments = st.text_area(
            get_text('comments'),
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="size_run_comments",
            label_visibility="collapsed"
        )
        
        # Fitting Correct
        st.markdown(f"**{get_text('fitting_correct')}**")
        col1, col2 = st.columns(2)
        with col1:
            fitting_yes = st.checkbox(get_text('yes'), key="fitting_yes")
        with col2:
            fitting_no = st.checkbox(get_text('no'), key="fitting_no")
        fitting_comments = st.text_area(
            get_text('comments'),
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="fitting_comments",
            label_visibility="collapsed"
        )
        
        # Already Sent top sample to office?
        st.markdown(f"**{get_text('top_sample_sent')}**")
        col1, col2 = st.columns(2)
        with col1:
            top_sample_yes = st.checkbox(get_text('yes'), key="top_sample_yes")
        with col2:
            top_sample_no = st.checkbox(get_text('no'), key="top_sample_no")
        top_sample_comments = st.text_area(
            get_text('comments'),
            placeholder=f"{get_text('comments')}...",
            height=60,
            key="top_sample_comments",
            label_visibility="collapsed"
        )
        
        # Tech Comments Completed
        st.markdown(f"**{get_text('tech_comments_completed')}**")
        col1, col2 = st.columns(2)
        with col1:
            tech_comments_yes = st.checkbox(get_text('yes'), key="tech_comments_yes")
        with col2:
            tech_comments_no = st.checkbox(get_text('no'), key="tech_comments_no")
        tech_comments_description = st.text_area(
            get_text('if_not_same'),
            placeholder=f"{get_text('if_not_same')}...",
            height=80,
            key="tech_comments_description",
            label_visibility="visible"
        )

with tab3:
    # Test Results
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["test_results"]}</span>
        {get_text("test_results")}
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"#### {ICONS['test']} {get_text('test_results')}")
        
        # Sole Bonding
        st.markdown(f"**{get_text('sole_bonding')}**")
        sole_bonding_result = st.text_input(
            f"{get_text('result')}",
            placeholder=f"{get_text('result')}...",
            key="sole_bonding_result",
            label_visibility="collapsed"
        )
        col_pass, col_fail = st.columns(2)
        with col_pass:
            sole_bonding_pass = st.checkbox("PASS", key="sole_bonding_pass")
        with col_fail:
            sole_bonding_fail = st.checkbox("FAIL", key="sole_bonding_fail")
        
        # Top piece attachment strength
        st.markdown(f"**{get_text('top_piece')}**")
        top_piece_result = st.text_input(
            f"{get_text('result')}",
            placeholder=f"{get_text('result')}...",
            key="top_piece_result",
            label_visibility="collapsed"
        )
        col_pass, col_fail = st.columns(2)
        with col_pass:
            top_piece_pass = st.checkbox("PASS", key="top_piece_pass")
        with col_fail:
            top_piece_fail = st.checkbox("FAIL", key="top_piece_fail")
        
        # Strength of Straps & buckle
        st.markdown(f"**{get_text('straps_strength')}**")
        straps_strength_result = st.text_input(
            f"{get_text('result')}",
            placeholder=f"{get_text('result')}...",
            key="straps_strength_result",
            label_visibility="collapsed"
        )
        col_pass, col_fail = st.columns(2)
        with col_pass:
            straps_strength_pass = st.checkbox("PASS", key="straps_strength_pass")
        with col_fail:
            straps_strength_fail = st.checkbox("FAIL", key="straps_strength_fail")
    
    with col_right:
        st.markdown(f"#### {ICONS['test']} {get_text('test_results')}")
        
        # Heel Attachment
        st.markdown(f"**{get_text('heel_attachment')}**")
        heel_attachment_result = st.text_input(
            f"{get_text('result')}",
            placeholder=f"{get_text('result')}...",
            key="heel_attachment_result",
            label_visibility="collapsed"
        )
        col_pass, col_fail = st.columns(2)
        with col_pass:
            heel_attachment_pass = st.checkbox("PASS", key="heel_attachment_pass")
        with col_fail:
            heel_attachment_fail = st.checkbox("FAIL", key="heel_attachment_fail")
        
        # Insole Perment set at 400N
        st.markdown(f"**{get_text('insole_perment')}**")
        insole_perment_result = st.text_input(
            f"{get_text('result')}",
            placeholder=f"{get_text('result')}...",
            key="insole_perment_result",
            label_visibility="collapsed"
        )
        col_pass, col_fail = st.columns(2)
        with col_pass:
            insole_perment_pass = st.checkbox("PASS", key="insole_perment_pass")
        with col_fail:
            insole_perment_fail = st.checkbox("FAIL", key="insole_perment_fail")
        
        # Toe Post Attachment
        st.markdown(f"**{get_text('toe_post')}**")
        toe_post_result = st.text_input(
            f"{get_text('result')}",
            placeholder=f"{get_text('result')}...",
            key="toe_post_result",
            label_visibility="collapsed"
        )
        col_pass, col_fail = st.columns(2)
        with col_pass:
            toe_post_pass = st.checkbox("PASS", key="toe_post_pass")
        with col_fail:
            toe_post_fail = st.checkbox("FAIL", key="toe_post_fail")
    
    # Issues & Solutions
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["issues_solutions"]}</span>
        {get_text("issues_solutions")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{get_text('die_cut_test')}**")
        die_cut_issues = st.text_area(
            f"{get_text('main_issues')}",
            placeholder=f"{get_text('main_issues')}...",
            height=150,
            key="die_cut_issues"
        )
    with col2:
        st.markdown(f"**{get_text('batch_test')}**")
        batch_test_issues = st.text_area(
            f"{get_text('main_issues')}",
            placeholder=f"{get_text('main_issues')}...",
            height=150,
            key="batch_test_issues"
        )

with tab4:
    # Signatures
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{ICONS["signatures"]}</span>
        {get_text("signatures")}
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        factory_representative = st.text_input(
            f"{ICONS['factory']} {get_text('factory_rep')}",
            placeholder=f"{get_text('factory_rep')}...",
            key="factory_representative"
        )
        gs_qc = st.text_input(
            f"{ICONS['qc']} {get_text('gs_qc')}",
            placeholder=f"{get_text('gs_qc')}...",
            key="gs_qc"
        )
        area_manager = st.text_input(
            f"{ICONS['tech']} {get_text('area_manager')}",
            placeholder=f"{get_text('area_manager')}...",
            key="area_manager"
        )
    
    with col2:
        grandstep_technician = st.text_input(
            f"{ICONS['tech']} {get_text('gs_tech')}",
            placeholder=f"{get_text('gs_tech')}...",
            key="grandstep_technician"
        )
        qa_manager = st.text_input(
            f"{ICONS['qc']} {get_text('qa_manager')}",
            placeholder=f"{get_text('qa_manager')}...",
            key="qa_manager"
        )
        signature_date = st.date_input(
            f"{ICONS['calendar']} {get_text('signature_date')}",
            datetime.now(),
            key="signature_date"
        )
    
    # Disclaimer
 

# Generate PDF Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(f"{ICONS['generate']} {get_text('generate_pdf')}", use_container_width=True):
        if not st.session_state.get('contract_no') or not st.session_state.get('style_name'):
            st.error(f"{ICONS['error']} {get_text('fill_required')}")
        else:
            with st.spinner(f"{ICONS['time']} {get_text('creating_pdf')}"):
                try:
                    pdf_buffer = generate_pdf()
                    st.success(f"{ICONS['success']} {get_text('generate_success')}")
                    
                    # Display PDF preview info
                    with st.expander(f"{ICONS['info']} {get_text('pdf_details')}"):
                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.metric(get_text("location"), f"{selected_city} ({CHINESE_CITIES[selected_city]})")
                            st.metric(get_text("report_language"), "Mandarin" if st.session_state.pdf_language == "zh" else "English")
                        with col_info2:
                            china_tz = pytz.timezone('Asia/Shanghai')
                            current_time = datetime.now(china_tz)
                            st.metric(get_text("generated"), current_time.strftime('%H:%M:%S'))
                    
                    # Download button
                    filename = f"DieCut_Test_{st.session_state.get('contract_no', '')}_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
