import io
import math
from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

# 📁 กำหนดเส้นทางฐานข้อมูล
DB_PATH = "repair_db.db"
PARTS_DB_PATH = "parts_db.db"

# --- ระบบจัดการฐานข้อมูล SQLite ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_no TEXT,
            customer_name TEXT,
            phone_number TEXT,
            brand TEXT,
            model TEXT,
            issue TEXT,
            parts_used TEXT,
            status TEXT,
            repair_date TEXT,
            date_added TEXT
        )
    ''')
    conn.commit()
    conn.close()

def init_parts_db():
    conn = sqlite3.connect(PARTS_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS parts_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_code TEXT,
            part_name TEXT,
            po_no TEXT,
            brand TEXT,
            quantity INTEGER,
            price_per_unit REAL,
            receive_date TEXT,
            date_added TEXT
        )
    ''')
    try:
        c.execute("ALTER TABLE parts_stock ADD COLUMN po_no TEXT")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    conn.close()

def add_repair(job_no, name, phone, brand, model, issue, parts, status, repair_date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO repairs (job_no, customer_name, phone_number, brand, model, issue, parts_used, status, repair_date, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_no, name, phone, brand, model, issue, parts, status, repair_date, current_date))
    conn.commit()
    conn.close()

def get_all_repairs():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM repairs", conn)
    conn.close()
    
    # 📌 จัดเรียงด้วย Pandas: แปลง ID เป็นตัวเลข แล้วเรียงจากใหม่สุดไปเก่าสุด (Descending)
    if not df.empty:
        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
            df = df.sort_values(by='id', ascending=False)
            
    return df

def is_job_duplicate_on_insert(job_no):
    if not job_no or not str(job_no).strip():
        return False
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM repairs WHERE job_no = ? LIMIT 1", (str(job_no).strip(),))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_part(part_code, part_name, po_no, brand, quantity, price, receive_date):
    conn = sqlite3.connect(PARTS_DB_PATH)
    c = conn.cursor()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO parts_stock (part_code, part_name, po_no, brand, quantity, price_per_unit, receive_date, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (part_code, part_name, po_no, brand, quantity, price, receive_date, current_date))
    conn.commit()
    conn.close()

def get_all_parts():
    conn = sqlite3.connect(PARTS_DB_PATH)
    df = pd.read_sql_query("SELECT * FROM parts_stock", conn)
    conn.close()
    
    if not df.empty:
        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
            df = df.sort_values(by='id', ascending=False)
            
    return df

def delete_part(row_id):
    conn = sqlite3.connect(PARTS_DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM parts_stock WHERE id=?", (int(row_id),))
    conn.commit()
    conn.close()

def update_po_info(old_po, new_po, new_date):
    conn = sqlite3.connect(PARTS_DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE parts_stock 
        SET po_no=?, receive_date=?
        WHERE po_no=?
    ''', (str(new_po).strip(), str(new_date).strip(), str(old_po).strip()))
    conn.commit()
    conn.close()

def delete_entire_po(po_no):
    conn = sqlite3.connect(PARTS_DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM parts_stock WHERE po_no=?", (str(po_no).strip(),))
    conn.commit()
    conn.close()

# --- ตั้งค่าหน้าจอและ UI ---
st.set_page_config(
    page_title="Carlcare ITcity", 
    page_icon="🛠️", 
    layout="wide",
    initial_sidebar_state="expanded"
)
init_db()
init_parts_db()

if "current_page" not in st.session_state: st.session_state.current_page = 1
if "active_menu" not in st.session_state: st.session_state.active_menu = "จัดการใบงาน"
if "current_po" not in st.session_state: st.session_state.current_po = "THGDN"
if "current_po_date" not in st.session_state: st.session_state.current_po_date = datetime.now().strftime("%Y-%m-%d")

df_repairs = get_all_repairs()
df_parts = get_all_parts()

# Custom CSS
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
    
    .po-status-box {
        background-color: #F0FDF4; border: 1px solid #BBF7D0; padding: 10px 15px; border-radius: 6px; color: #166534; font-weight: 500; font-size: 0.9rem; margin-bottom: 15px;
    }
    .po-edit-card {
        background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px 16px; margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="compact-header">
        <h3>🛠️ ศูนย์ซ่อม Carlcare ITcity</h3>
        <p>Infinix • Tecno • Itel Management System</p>
    </div>
""", unsafe_allow_html=True)

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
            <span style="color:#0284C7;">🔵</span> <b>ระบบออฟไลน์พร้อมใช้</b><br>
            <span style='font-size:0.75rem; opacity:0.85; line-height:1.3;'>ข้อมูลถูกจัดเก็บอย่างปลอดภัยบนเครื่องคอมพิวเตอร์นี้ร้อยเปอร์เซ็นต์</span>
        </div>
    """, unsafe_allow_html=True)

# =======================================================
# 🔍 1. เมนูค้นหาและจัดการข้อมูลใบงาน (เรียงใหม่สุด -> เก่าสุด)
# =======================================================
if st.session_state.active_menu == "จัดการใบงาน":
    st.markdown("🔍 **เมนูค้นหาและจัดการข้อมูลใบงาน**")
    
    with st.container():
        search_query = st.text_input("📋 พิมพ์ข้อมูลค้นหา", placeholder="พิมพ์เพื่อค้นหา Job No. หรือ ชื่อลูกค้า...").strip()
        
        if not df_repairs.empty:
            filtered_df = df_repairs.copy()
            
            # 📌 กรองตามคำค้นหา
            if search_query:
                filtered_df = filtered_df[
                    filtered_df['job_no'].astype(str).str.contains(search_query, case=False, na=False) |
                    filtered_df['customer_name'].astype(str).str.contains(search_query, case=False, na=False)
                ]
            
            display_df = filtered_df[["repair_date", "job_no", "customer_name", "phone_number", "brand", "model", "issue", "parts_used", "status"]].copy()
            display_df.columns = ["วันที่รับซ่อม", "Job No.", "ชื่อลูกค้า", "เบอร์โทร", "แบรนด์", "รุ่นสินค้า", "อาการเสีย", "อะไหล่ที่ใช้", "สถานะการซ่อม"]
            
            # 📌 ระบบแบ่งหน้า (Pagination) 10 รายการ/หน้า
            rows_per_page = 10
            total_rows = len(display_df)
            total_pages = math.ceil(total_rows / rows_per_page) if total_rows > 0 else 1
            
            if st.session_state.current_page > total_pages:
                st.session_state.current_page = total_pages
                
            start_idx = (st.session_state.current_page - 1) * rows_per_page
            end_idx = start_idx + rows_per_page
            page_df = display_df.iloc[start_idx:end_idx].copy()
            
            st.dataframe(
                page_df,
                hide_index=True,
                height=385,
                use_container_width=True
            )

            p_col1, p_col2, p_col3 = st.columns([4, 2, 4])
            with p_col2:
                page_selection = st.selectbox(
                    "หน้าการแสดงผล", options=list(range(1, total_pages + 1)), 
                    index=st.session_state.current_page - 1, label_visibility="collapsed"
                )
                if page_selection != st.session_state.current_page:
                    st.session_state.current_page = page_selection
                    st.rerun()
        else:
            st.info("ℹ️ ยังไม่มีรายการใบงานเก็บรักษาในระบบ")

# =======================================================
# 📝 2. เมนูบันทึกข้อมูลเครื่องซ่อมเสร็จ
# =======================================================
elif st.session_state.active_menu == "บันทึกข้อมูล":
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
        submit_button = st.form_submit_button(label='💾 บันทึกข้อมูลงานซ่อม')

    if submit_button:
        if job_no and customer_name and model and issue:
            if is_job_duplicate_on_insert(job_no):
                st.error("⚠️ ไม่สามารถบันทึกได้ เนื่องจากมีเลขที่ใบงานนี้อยู่ในระบบแล้ว!")
            else:
                add_repair(job_no, customer_name, phone_number, brand, model, issue, parts_used, clean_status, repair_date_str)
                st.success("🎉 บันทึกข้อมูลใบงานใหม่สำเร็จเรียบร้อยแล้ว!")
                st.rerun()
        else:
            st.error("⚠️ กรุณากรอกข้อมูลสำคัญให้ครบถ้วน (เลขใบงาน, ชื่อลูกค้า, รุ่นสินค้า และอาการเสีย)")

# =======================================================
# 📦 3. เมนูรับเข้าอะไหล่
# =======================================================
elif st.session_state.active_menu == "รับเข้าอะไหล่":
    st.markdown("📦 **เมนูรับเข้าอะไหล่**")
    
    col_po, col_item = st.columns([1, 2])
    
    with col_po:
        st.markdown("📌 **1. ตั้งค่าหัวบิล PO**")
        
        current_po_val = st.session_state.current_po if st.session_state.current_po else "THGDN"
        if not current_po_val.startswith("THGDN"):
            current_po_val = "THGDN" + current_po_val
            
        po_input = st.text_input("เลขที่ PO (PO Number)", value=current_po_val, placeholder="THGDN...").strip()
        
        if not po_input.startswith("THGDN"):
            po_input = "THGDN" + po_input

        po_date_input = st.date_input("วันที่รับสินค้าเข้า", value=datetime.strptime(st.session_state.current_po_date, "%Y-%m-%d"))
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("✅ ล็อกบิล PO นี้", use_container_width=True, type="primary"):
                st.session_state.current_po = po_input
                st.session_state.current_po_date = po_date_input.strftime("%Y-%m-%d")
                st.rerun()
        with c_btn2:
            if st.button("💾 บันทึกใบ PO", use_container_width=True):
                st.session_state.current_po = "THGDN"
                st.session_state.current_po_date = datetime.now().strftime("%Y-%m-%d")
                st.success("บันทึกข้อมูลใบ PO เรียบร้อยแล้ว!")
                st.rerun()
                
        if st.session_state.current_po and st.session_state.current_po != "THGDN":
            st.markdown(f"""
                <div class="po-status-box">
                    🔒 <b>กำลังทำงานที่บิล:</b><br>
                    เลขที่ PO: {st.session_state.current_po}<br>
                    วันที่: {st.session_state.current_po_date}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ กรุณาระบุเลขที่ PO ต่อท้าย THGDN และกดล็อกบิลก่อนเริ่มคีย์อะไหล่")

    with col_item:
        st.markdown("✨ **2. เพิ่มรายการอะไหล่เข้าคลัง**")
        with st.form(key="parts_multi_input_form", clear_on_submit=True):
            p_form_r1_c1, p_form_r1_c2 = st.columns(2)
            with p_form_r1_c1:
                part_code = st.text_input("รหัสอะไหล่ (Part Code / SKU)", placeholder="ระบุรหัสหรือบาร์โค้ด").strip()
            with p_form_r1_c2:
                part_name = st.text_input("ชื่อรายการอะไหล่", placeholder="เช่น หน้าจอชุด, แบตเตอรี่").strip()
                
            p_form_r2_c1, p_form_r2_c2 = st.columns([3, 1])
            with p_form_r2_c1:
                st.markdown('<div class="brand-container">', unsafe_allow_html=True)
                part_brand = st.radio("แบรนด์สินค้าที่รองรับ", ["Infinix", "Tecno", "Itel", "Common"], index=0, key="p_brand_radio")
                st.markdown('</div>', unsafe_allow_html=True)
            with p_form_r2_c2:
                part_qty = st.number_input("จำนวนที่รับเข้า (ชิ้น)", min_value=1, step=1, value=1)
                
            st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            part_submit = st.form_submit_button(label='➕ บันทึกชิ้นนี้เข้าบิล PO', use_container_width=True)
            
        if part_submit:
            if not st.session_state.current_po or st.session_state.current_po == "THGDN":
                st.error("❌ ไม่สามารถบันทึกได้! กรุณาระบุเลขที่ PO ต่อท้าย THGDN และกดปุ่ม 'ล็อกบิล PO นี้' ฝั่งซ้ายก่อน")
            elif part_code and part_name:
                add_part(part_code, part_name, st.session_state.current_po, part_brand, part_qty, 0.0, st.session_state.current_po_date)
                st.success(f"🎉 บันทึกอะไหล่ '{part_name}' เข้าสู่ PO: {st.session_state.current_po} สำเร็จ!")
                st.rerun()
            else:
                st.error("⚠️ กรุณาระบุข้อมูล 'รหัสอะไหล่' และ 'ชื่อรายการอะไหล่' ก่อนกดบันทึก")

    st.markdown("---")
    st.markdown("🔍 **รายการรับเข้าอะไหล่ (คลิกที่เลข PO เพื่อเปิดดูรายการอะไหล่)**")
    part_search = st.text_input("📋 ค้นหาข้อมูล (เลข PO, รหัส หรือชื่ออะไหล่)", placeholder="พิมพ์ค้นหา...").strip()
    
    if not df_parts.empty:
        if 'po_no' not in df_parts.columns:
            df_parts['po_no'] = ""
            
        filtered_parts = df_parts.copy()
        if part_search:
            filtered_parts = filtered_parts[
                filtered_parts['part_code'].str.contains(part_search, case=False, na=False) |
                filtered_parts['part_name'].str.contains(part_search, case=False, na=False) |
                filtered_parts['po_no'].str.contains(part_search, case=False, na=False)
            ]
            
        unique_pos = filtered_parts['po_no'].unique()
        
        if len(unique_pos) == 0 or (len(unique_pos) == 1 and unique_pos[0] == ""):
            st.info("ℹ️ ไม่พบรายการ PO ตามเงื่อนไขค้นหา")
        else:
            for po in unique_pos:
                po_disp = po if (po and str(po).strip() != "") else "ไม่ระบุ PO"
                po_group = filtered_parts[filtered_parts['po_no'] == po].sort_values(by="id", ascending=True).copy()
                
                total_items = len(po_group)
                total_qty = po_group['quantity'].sum()
                rec_date = po_group['receive_date'].iloc[0] if 'receive_date' in po_group.columns and not po_group['receive_date'].empty else "-"
                
                with st.expander(f"📄 **เลขที่ PO: {po_disp}** | วันที่รับเข้า: {rec_date} | จำนวน: {total_items} รายการ ({total_qty} ชิ้น)"):
                    
                    st.markdown('<div class="po-edit-card">', unsafe_allow_html=True)
                    st.markdown("🛠️ **จัดการข้อมูลหัวบิล PO นี้:**")
                    pe_c1, pe_c2, pe_c3, pe_c4 = st.columns([3, 2, 2, 2])
                    
                    with pe_c1:
                        edit_po_val = st.text_input("แก้ไขเลขที่ PO", value=po_disp, key=f"edit_po_txt_{po}").strip()
                    with pe_c2:
                        try:
                            d_val = datetime.strptime(str(rec_date), "%Y-%m-%d")
                        except:
                            d_val = datetime.now()
                        edit_po_date_val = st.date_input("แก้ไขวันที่", value=d_val, key=f"edit_po_date_{po}")
                    with pe_c3:
                        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
                        if st.button("✏️ อัปเดต PO นี้", key=f"btn_update_po_{po}", use_container_width=True):
                            if edit_po_val:
                                update_po_info(po, edit_po_val, edit_po_date_val.strftime("%Y-%m-%d"))
                                st.success("อัปเดตข้อมูล PO สำเร็จ!")
                                st.rerun()
                            else:
                                st.error("⚠️ เลข PO ห้ามเป็นค่าว่าง")
                    with pe_c4:
                        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
                        if st.button("🗑️ ลบ PO ทั้งชุด", key=f"btn_del_po_{po}", type="secondary", use_container_width=True):
                            st.session_state[f"confirm_del_po_{po}"] = True
                    
                    if st.session_state.get(f"confirm_del_po_{po}", False):
                        st.warning(f"⚠️ คุณต้องการลบบิล **{po_disp}** พร้อมกับอะไหล่ทั้งหมด **{total_items} รายการ** ใช่หรือไม่?")
                        cf_col1, cf_col2 = st.columns(2)
                        with cf_col1:
                            if st.button("🚨 ยืนยันการลบทั้งบิล", key=f"btn_confirm_yes_{po}", type="primary"):
                                delete_entire_po(po)
                                st.session_state[f"confirm_del_po_{po}"] = False
                                st.success(f"ลบบิล PO: {po_disp} เรียบร้อยแล้ว!")
                                st.rerun()
                        with cf_col2:
                            if st.button("❌ ยกเลิก", key=f"btn_confirm_no_{po}"):
                                st.session_state[f"confirm_del_po_{po}"] = False
                                st.rerun()
                                
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
                    
                    po_group["ลำดับที่"] = range(1, len(po_group) + 1)
                    sub_df = po_group[["ลำดับที่", "part_code", "part_name", "brand", "quantity", "id"]].copy()
                    sub_df_display = sub_df[["ลำดับที่", "part_code", "part_name", "brand", "quantity"]].copy()
                    sub_df_display.columns = ["ลำดับที่", "รหัสอะไหล่", "ชื่อรายการอะไหล่", "แบรนด์สินค้า", "จำนวนชิ้น"]
                    
                    st.dataframe(sub_df_display, hide_index=True, use_container_width=True)
                    
                    d_c1, d_c2 = st.columns([3, 7])
                    with d_c1:
                        del_seq = st.number_input(f"ระบุ ลำดับที่ ที่ต้องการลบชิ้นเดียว (ใน PO: {po_disp})", min_value=1, max_value=len(po_group), step=1, key=f"del_seq_{po}")
                    with d_c2:
                        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
                        if st.button("🗑️ ลบอะไหล่ชิ้นนี้", key=f"btn_del_{po}"):
                            target_row = sub_df[sub_df["ลำดับที่"] == del_seq]
                            if not target_row.empty:
                                real_id = int(target_row["id"].values[0])
                                delete_part(real_id)
                                st.success(f"ลบรายการอะไหล่ ลำดับที่ {del_seq} สำเร็จ!")
                                st.rerun()
                            else:
                                st.error("⚠️ ไม่พบระบุลำดับที่ดังกล่าว")
    else:
        st.info("ℹ️ ยังไม่มีรายการอะไหล่ที่จัดเก็บในคลังข้อมูล")

# =======================================================
# 📊 4. เมนู แสดงสถิติ การซ่อม
# =======================================================
elif st.session_state.active_menu == "สถิติการซ่อม":
    st.markdown("📊 **เมนู แสดงสถิติ การซ่อม**")
    if not df_repairs.empty:
        total_jobs = len(df_repairs)
        inf_c = len(df_repairs[df_repairs['brand'] == 'Infinix'])
        tec_c = len(df_repairs[df_repairs['brand'] == 'Tecno'])
        ite_c = len(df_repairs[df_repairs['brand'] == 'Itel'])
        
        done_c = len(df_repairs[df_repairs['status'].str.contains("เสร็จสิ้น", na=False)])
        pending_c = len(df_repairs[df_repairs['status'].str.contains("ดำเนินการ|รับเครื่อง", na=False)])
        cancel_c = len(df_repairs[df_repairs['status'].str.contains("ยกเลิก", na=False)])

        st.markdown("### 📈 ปริมาณงานแยกตามแบรนด์สินค้า")
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        m_c1.metric("📦 งานภาพรวมทั้งหมด", f"{total_jobs} รายการ")
        m_c2.metric("📱 Infinix", f"{inf_c} เครื่อง")
        m_c3.metric("📱 Tecno", f"{tec_c} เครื่อง")
        m_c4.metric("📱 Itel", f"{ite_c} เครื่อง")
        
        st.markdown("---")
        st.markdown("### ⏳ Status สถิติการซ่อม")
        ms_c1, ms_c2, ms_c3 = st.columns(3)
        ms_c1.metric("✅ ซ่อมเสร็จสมบูรณ์", f"{done_c} รายการ")
        ms_c2.metric("🛠️ อยู่ระหว่างกระบวนการ", f"{pending_c} รายการ")
        ms_c3.metric("❌ ยกเลิกและคืนเครื่อง", f"{cancel_c} รายการ")
    else:
        st.info("ℹ️ ไม่มีฐานข้อมูลเพียงพอสำหรับการประมวลผลสรุปสถิติ")

# =======================================================
# 📥 5. เมนู Export to Excel
# =======================================================
elif st.session_state.active_menu == "ส่งออก Excel":
    st.markdown("📥 **เมนู Export to Excel**")
    if not df_repairs.empty:
        export_df = df_repairs.copy()
        export_df = export_df[["id", "job_no", "customer_name", "phone_number", "brand", "model", "issue", "parts_used", "status", "repair_date", "date_added"]]
        export_df.columns = ["ID", "เลขที่ใบงาน", "ชื่อลูกค้า", "เบอร์โทรศัพท์", "แบรนด์", "รุ่น/โมเดล", "อาการเสีย", "อะไหล่ที่ใช้", "สถานะการซ่อม", "วันที่รับซ่อม", "วันที่บันทึกระบบ"]
        
        buffer = io.BytesIO()
        try:
            export_df.to_excel(buffer, index=False, sheet_name='Carlcare_Repairs')
        except:
            export_df.to_excel(buffer, index=False, engine='openpyxl', sheet_name='Carlcare_Repairs')
            
        buffer.seek(0)
        st.dataframe(export_df, hide_index=True, height=385)
        
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ Excel (.xlsx) ของระบบทันที",
            data=buffer,
            file_name=f"Carlcare_Excel_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ℹ️ ปัจจุบันฐานข้อมูลว่างเปล่า ไม่สามารถส่งออกไฟล์ได้")

# =======================================================
# 📄 6. เมนู Export to PDF
# =======================================================
elif st.session_state.active_menu == "ส่งออก PDF":
    st.markdown("📄 **เมนู Export to PDF**")
    if not df_repairs.empty:
        pdf_df = df_repairs.copy()[["repair_date", "job_no", "customer_name", "brand", "model", "status"]]
        pdf_df.columns = ["วันที่รับซ่อม", "เลขใบงาน", "ชื่อลูกค้า", "แบรนด์", "รุ่นสินค้า", "สถานะปัจจุบัน"]
        
        st.dataframe(pdf_df, hide_index=True, height=450)
        st.markdown("---")
        st.markdown("### 🖨️ จัดการและพิมพ์เอกสารรายงาน")
        
        print_js = """
        <a href="javascript:window.print()" style="
            text-decoration: none;
            background-color: #0EA5E9;
            color: white;
            padding: 10px 24px;
            font-weight: bold;
            border-radius: 6px;
            display: inline-block;
            box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.2);
            transition: background-color 0.2s;
        " onmouseover="this.style.backgroundColor='#0284C7'" onmouseout="this.style.backgroundColor='#0EA5E9'">
            🖨️ กดที่นี่เพื่อสั่งพิมพ์รายงาน (Print / Save to PDF)
        </a>
        """
        st.markdown(print_js, unsafe_allow_html=True)
    else:
        st.info("ℹ️ ยังไม่มีข้อมูลในระบบสำหรับการจัดพิมพ์รายงาน PDF")
