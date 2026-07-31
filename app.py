import io
from datetime import datetime
import pandas as pd
import requests
import streamlit as st

# =======================================================
# 📌 ตั้งค่า Google Sheets & Webhook สำหรับบันทึกข้อมูล
# =======================================================
# 1. URL สำหรับดึงข้อมูลอ่านสด
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1laqAl0kHMP19qJCqhzAq6Ll7MkpDAQxH3k-xEvG0bj8/export?format=csv&gid=0"

# 2. URL สำหรับรับค่าบันทึกข้อมูล (เปลี่ยนเป็น URL Webhook หรือ Google Form ของคุณ)
SAVE_WEBHOOK_URL = "https://script.google.com/macros/s/YOUR_APPS_SCRIPT_ID/exec"

# =======================================================
# 1. การตั้งค่าหน้าจอและ CSS สไตล์
# =======================================================
st.set_page_config(
    page_title="Carlcare ITcity",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] { background-color: #F8FAFC !important; }
    .main .block-container { padding: 0.8rem 2rem !important; max-width: 100% !important; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F0F7FF 0%, #E8F2FE 50%, #E2EEFC 100%) !important;
        border-right: 1px solid #D0E1FD !important;
        box-shadow: 4px 0 15px rgba(14, 165, 233, 0.03);
    }
    
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        color: #334155 !important;
        border: 1px solid transparent !important;
        padding: 0.6rem 1rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        transition: all 0.25s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(14, 165, 233, 0.08) !important;
        color: #0369A1 !important;
        border-color: rgba(14, 165, 233, 0.2) !important;
    }
    
    .sidebar-title {
        font-size: 1.15rem !important;
        color: #1E293B !important;
        font-weight: 800 !important;
        margin-top: 15px;
        margin-bottom: 20px;
        padding-left: 6px;
        letter-spacing: 0.02em;
    }
    
    .sidebar-footer {
        background-color: rgba(255, 255, 255, 0.6);
        padding: 12px 14px;
        border-radius: 8px;
        margin-top: 40px;
        font-size: 0.8rem;
        color: #475569;
        border: 1px solid #D0E1FD;
        backdrop-filter: blur(5px);
    }
    
    .compact-header {
        background: linear-gradient(135deg, #E0F2FE 0%, #F0F9FF 100%);
        border: 1px solid #BAE6FD; padding: 0.5rem 1.5rem; border-radius: 8px; margin-bottom: 1rem;
        display: flex; justify-content: space-between; align-items: center;
    }
    .compact-header h3 { color: #0369A1 !important; margin: 0 !important; font-weight: 700; font-size: 1.25rem !important; }
    .compact-header p { color: #0EA5E9 !important; margin: 0 !important; font-weight: 600; font-size: 0.85rem; }
    
    div[data-testid="stForm"], .list-filter-card {
        background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important; padding: 1.2rem 1.5rem !important; margin-bottom: 1rem !important;
    }
    .stTextInput input, .stDateInput input, .stNumberInput input {
        background-color: #FFFFFF !important; color: #1E293B !important; border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important; padding: 0.15rem 0.5rem !important; height: 34px !important;
    }
    div[data-baseweb="base-input"] { background-color: transparent !important; border: none !important; }
    
    div[data-testid="stRadio"] > div,
    div[data-testid="stRadio"] [role="radiogroup"] {
        display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 20px !important;
    }
    div.brand-container div[data-testid="stRadio"] [role="radiogroup"] {
        background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 6px !important; padding: 5px 14px !important; height: 34px !important;
    }
    div.status-container div[data-testid="stRadio"] [role="radiogroup"] {
        background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 8px !important; padding: 8px 16px !important;
    }
    label p { color: #475569 !important; font-size: 0.85rem !important; font-weight: 600; margin-bottom: 4px !important; }
    h3, p, span, h4 { color: #334155 !important; }
    </style>
""", unsafe_allow_html=True)

# =======================================================
# 2. ฟังก์ชันดึงข้อมูลจาก Google Sheets
# =======================================================
@st.cache_data(ttl=3)
def load_data_from_gsheets():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if not df.empty:
            return df
    except Exception as e:
        st.warning(f"⚠️ ไม่สามารถเชื่อมต่อ Google Sheets ได้ชั่วคราว: {e}")
    return pd.DataFrame()

# Header หน้าตาหลัก
st.markdown("""
    <div class="compact-header">
        <h3>🛠️ ศูนย์ซ่อม Carlcare ITcity</h3>
        <p>Infinix • Tecno • Itel Management System</p>
    </div>
""", unsafe_allow_html=True)

# Session State Initial
if "active_menu" not in st.session_state: 
    st.session_state.active_menu = "บันทึกข้อมูล"

# Sidebar Menu
with st.sidebar:
    st.markdown('<p class="sidebar-title">เมนูระบบจัดการ</p>', unsafe_allow_html=True)
    
    if st.button("📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ", use_container_width=True, type="primary" if st.session_state.active_menu == "บันทึกข้อมูล" else "secondary"):
        st.session_state.active_menu = "บันทึกข้อมูล"
        st.rerun()
        
    if st.button("📦 รับเข้าอะไหล่ (Stock Parts)", use_container_width=True, type="primary" if st.session_state.active_menu == "รับเข้าอะไหล่" else "secondary"):
        st.session_state.active_menu = "รับเข้าอะไหล่"
        st.rerun()
        
    if st.button("🔍 ค้นหาและจัดการข้อมูลใบงาน", use_container_width=True, type="primary" if st.session_state.active_menu == "จัดการใบงาน" else "secondary"):
        st.session_state.active_menu = "จัดการใบงาน"
        st.rerun()
        
    if st.button("📊 รายงานสถิติกระบวนการซ่อม", use_container_width=True, type="primary" if st.session_state.active_menu == "สถิติการซ่อม" else "secondary"):
        st.session_state.active_menu = "สถิติการซ่อม"
        st.rerun()
        
    if st.button("📥 ส่งออกข้อมูล Export to Excel", use_container_width=True, type="primary" if st.session_state.active_menu == "ส่งออก Excel" else "secondary"):
        st.session_state.active_menu = "ส่งออก Excel"
        st.rerun()
        
    if st.button("📄 พิมพ์รายงาน Export to PDF", use_container_width=True, type="primary" if st.session_state.active_menu == "ส่งออก PDF" else "secondary"):
        st.session_state.active_menu = "ส่งออก PDF"
        st.rerun()

    st.markdown("""
        <div class="sidebar-footer">
            <span style="color:#0284C7;">🔵</span> <b>ระบบออนไลน์เชื่อมต่อคลังข้อมูล</b><br>
            <span style='font-size:0.75rem; opacity:0.85; line-height:1.3;'>ดึงข้อมูลสดจาก Google Sheets ความเร็วสูง</span>
        </div>
    """, unsafe_allow_html=True)

# โหลดข้อมูลสดจาก Google Sheets
df_repairs = load_data_from_gsheets()

# =======================================================
# 💻 1. เมนูบันทึกข้อมูลเครื่องซ่อมเสร็จ
# =======================================================
if st.session_state.active_menu == "บันทึกข้อมูล":
    st.markdown("📝 **เมนูบันทึกข้อมูลเครื่องซ่อมเสร็จ (เพิ่มข้อมูลใบงานใหม่)**")
    
    with st.form(key="repair_input_form", clear_on_submit=True):
        form_r1_c1, form_r1_c2 = st.columns([4, 2])
        with form_r1_c1:
            job_no = st.text_input("เลขที่ใบงาน (Job No.)", placeholder="ระบุเลขใบงาน", key="form_job_no").strip()
        with form_r1_c2:
            repair_date = st.date_input("วันที่รับซ่อม", value=datetime.now(), key="form_repair_date")
            repair_date_str = repair_date.strftime("%Y-%m-%d")

        form_r2_c1, form_r2_c2 = st.columns(2)
        with form_r2_c1:
            customer_name = st.text_input("ชื่อลูกค้า", placeholder="ชื่อ-นามสกุลลูกค้า", key="form_customer_name")
        with form_r2_c2:
            phone_number = st.text_input("เบอร์โทรศัพท์", placeholder="เบอร์โทรติดต่อ", key="form_phone_number")

        form_r3_c1, form_r3_c2 = st.columns(2)
        with form_r3_c1:
            st.markdown('<div class="brand-container">', unsafe_allow_html=True)
            brand = st.radio("แบรนด์สินค้า", ["Infinix", "Tecno", "Itel"], index=0, key="form_brand")
            st.markdown('</div>', unsafe_allow_html=True)
        with form_r3_c2:
            model = st.text_input("รุ่น/โมเดล", placeholder="เช่น Hot 40 Pro", key="form_model")

        form_r4_c1, form_r4_c2 = st.columns(2)
        with form_r4_c1:
            issue = st.text_input("อาการเสีย", placeholder="อาการเสียที่แจ้งซ่อม", key="form_issue")
        with form_r4_c2:
            parts_used = st.text_input("อะไหล่ที่ใช้", placeholder="รายการอะไหล่ที่เปลี่ยน", key="form_parts_used")
        
        st.markdown('<div class="status-container">', unsafe_allow_html=True)
        status_selected = st.radio("status_selected", ["🟢 รับเครื่องแล้ว/รอตรวจเช็ค", "🟡 กำลังดำเนินการซ่อม", "🔵 ซ่อมเสร็จสิ้น/รอส่งมอบลูกค้า", "🔴 ยกเลิกการซ่อม/คืนเครื่อง"], index=0, label_visibility="collapsed", key="form_status")
        st.markdown('</div>', unsafe_allow_html=True)
        clean_status = status_selected.split(" ", 1)[1]

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        submit_button = st.form_submit_button(label='💾 บันทึกข้อมูลงานซ่อม', use_container_width=True)

    # 📌 ส่วนประมวลผลการส่งข้อมูลบันทึก
    if submit_button:
        if job_no and customer_name and model and issue:
            data_payload = {
                "job_no": job_no,
                "repair_date": repair_date_str,
                "customer_name": customer_name,
                "phone_number": phone_number,
                "brand": brand,
                "model": model,
                "issue": issue,
                "parts_used": parts_used,
                "status": clean_status
            }
            
            try:
                # ส่งข้อมูลผ่าน Webhook/Apps Script
                response = requests.post(SAVE_WEBHOOK_URL, json=data_payload, timeout=10)
                
                if response.status_code == 200:
                    st.success("🎉 บันทึกข้อมูลลง Google Sheets เรียบร้อยแล้ว!")
                    st.cache_data.clear()  # เคลียร์แคชเพื่อให้แสดงข้อมูลล่าสุดทันที
                else:
                    st.warning("⚠️ ส่งข้อมูลสำเร็จแล้ว แตลับหลังได้รับสถานะผิดปกติ กรุณาตรวจสอบ Google Apps Script")
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อเพื่อบันทึกข้อมูล: {e}")
        else:
            st.error("⚠️ กรุณากรอกข้อมูลสำคัญให้ครบถ้วน (เลขใบงาน, ชื่อลูกค้า, รุ่นสินค้า และอาการเสีย)")

# =======================================================
# 📦 2. เมนูรับเข้าอะไหล่
# =======================================================
elif st.session_state.active_menu == "รับเข้าอะไหล่":
    st.markdown("📦 **เมนูรับเข้าอะไหล่ (Stock Parts)**")
    st.info("ℹ️ ฟังก์ชันรับเข้าอะไหล่สำหรับจัดการคลังสต็อก")

# =======================================================
# 🔍 3. เมนู ค้นหาและจัดการข้อมูลใบงาน
# =======================================================
elif st.session_state.active_menu == "จัดการใบงาน":
    st.markdown("🔍 **เมนูค้นหาและจัดการข้อมูลใบงาน**")
    if not df_repairs.empty:
        search_query = st.text_input("📋 พิมพ์ข้อมูลค้นหา", placeholder="พิมพ์เพื่อค้นหา Job No. หรือ ชื่อลูกค้า...").strip()
        display_df = df_repairs.iloc[::-1].reset_index(drop=True)
        if search_query:
            mask = False
            for col in display_df.columns:
                mask = mask | display_df[col].astype(str).str.contains(search_query, case=False, na=False)
            display_df = display_df[mask]
        st.dataframe(display_df, hide_index=True, use_container_width=True)
    else:
        st.info("ℹ️ ยังไม่มีข้อมูลในตาราง")

# =======================================================
# 📊 4. เมนู สถิติการซ่อม
# =======================================================
elif st.session_state.active_menu == "สถิติการซ่อม":
    st.markdown("📊 **เมนู แสดงสถิติ การซ่อม**")
    if not df_repairs.empty:
        st.metric("📦 รายการซ่อมทั้งหมด", f"{len(df_repairs)} รายการ")
        st.dataframe(df_repairs, hide_index=True, use_container_width=True)

# =======================================================
# 📥 5. เมนู Export Excel
# =======================================================
elif st.session_state.active_menu == "ส่งออก Excel":
    st.markdown("📥 **เมนู Export to Excel**")
    if not df_repairs.empty:
        buffer = io.BytesIO()
        df_repairs.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ Excel (.xlsx)",
            data=buffer,
            file_name=f"Carlcare_Export_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =======================================================
# 📄 6. เมนู Export PDF
# =======================================================
elif st.session_state.active_menu == "ส่งออก PDF":
    st.markdown("📄 **เมนู Export to PDF**")
    if not df_repairs.empty:
        st.dataframe(df_repairs, hide_index=True, height=400)
        st.markdown('<a href="javascript:window.print()" style="background-color:#0EA5E9;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;">🖨️ สั่งพิมพ์รายงาน (PDF)</a>', unsafe_allow_html=True)
