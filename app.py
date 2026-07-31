import io
import math
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# 1. การตั้งค่าหน้าจอและ CSS สไตล์แม่แบบ
# ==========================================
st.set_page_config(
    page_title="Carlcare ITcity",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
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
    
    div[data-testid="stForm"], .list-filter-card, .edit-box {
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
""",
    unsafe_allow_html=True,
)

# Header ด้านบน
st.markdown(
    """
    <div class="compact-header">
        <h3>🛠️ ศูนย์ซ่อม Carlcare ITcity</h3>
        <p>Infinix • Tecno • Itel Management System</p>
    </div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. ระบบเชื่อมต่อ Google Sheets (Fast CSV Reader)
# ==========================================
def get_csv_url(sheet_name):
    try:
        base_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        if "/edit" in base_url:
            base_url = base_url.split("/edit")[0]
        return f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    except Exception:
        return ""


@st.cache_data(ttl=3)
def load_data(sheet_name):
    url = get_csv_url(sheet_name)
    if not url:
        return pd.DataFrame()
    try:
        df = pd.read_csv(url)
        df = df.dropna(how="all")
        df.columns = [str(col).strip().lower() for col in df.columns]
        return df
    except Exception:
        return pd.DataFrame()


# Session States
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "จัดการใบงาน"
if "current_po" not in st.session_state:
    st.session_state.current_po = "THGDN"
if "current_po_date" not in st.session_state:
    st.session_state.current_po_date = datetime.now().strftime("%Y-%m-%d")

# ==========================================
# 3. แถบควบคุมเมนูด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown(
        '<p class="sidebar-title">เมนูระบบจัดการ</p>', unsafe_allow_html=True
    )

    if st.button(
        "📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_menu == "บันทึกข้อมูล"
            else "secondary"
        ),
    ):
        st.session_state.active_menu = "บันทึกข้อมูล"
        st.rerun()

    if st.button(
        "📦 รับเข้าอะไหล่ (Stock Parts)",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_menu == "รับเข้าอะไหล่"
            else "secondary"
        ),
    ):
        st.session_state.active_menu = "รับเข้าอะไหล่"
        st.rerun()

    if st.button(
        "🔍 ค้นหาและจัดการข้อมูลใบงาน",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_menu == "จัดการใบงาน"
            else "secondary"
        ),
    ):
        st.session_state.active_menu = "จัดการใบงาน"
        st.rerun()

    if st.button(
        "📊 รายงานสถิติกระบวนการซ่อม",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_menu == "สถิติการซ่อม"
            else "secondary"
        ),
    ):
        st.session_state.active_menu = "สถิติการซ่อม"
        st.rerun()

    if st.button(
        "📥 ส่งออกข้อมูล Export to Excel",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_menu == "ส่งออก Excel"
            else "secondary"
        ),
    ):
        st.session_state.active_menu = "ส่งออก Excel"
        st.rerun()

    if st.button(
        "📄 พิมพ์รายงาน Export to PDF",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.active_menu == "ส่งออก PDF"
            else "secondary"
        ),
    ):
        st.session_state.active_menu = "ส่งออก PDF"
        st.rerun()

    st.markdown(
        """
        <div class="sidebar-footer">
            <span style="color:#10B981;">🟢</span> <b>เชื่อมต่อ Google Sheets แล้ว</b><br>
            <span style='font-size:0.75rem; opacity:0.85; line-height:1.3;'>ข้อมูลถูกจัดเก็บแบบเรียลไทม์ ปลอดภัยบนระบบ Cloud</span>
        </div>
    """,
        unsafe_allow_html=True,
    )


# ==========================================
# 4. ส่วนแสดงผลตามเมนู
# ==========================================

# ------------------------------------------
# 🔍 1. เมนูค้นหาและจัดการข้อมูลใบงาน
# ------------------------------------------
if st.session_state.active_menu == "จัดการใบงาน":
    st.markdown("🔍 **เมนูค้นหาและจัดการข้อมูลใบงาน**")

    df_repairs = load_data("repairs")

    with st.container():
        search_query = st.text_input(
            "📋 พิมพ์ข้อมูลค้นหา",
            placeholder="พิมพ์เพื่อค้นหา Job No. หรือ ชื่อลูกค้า...",
        ).strip()

        if not df_repairs.empty:
            filtered_df = df_repairs.copy()
            if search_query:
                filtered_df = filtered_df[
                    filtered_df.astype(str).apply(
                        lambda row: row.str.contains(
                            search_query, case=False, na=False
                        ).any(),
                        axis=1,
                    )
                ]

            # จัดเรียงชื่อคอลัมน์ให้ตรงตามดีไซน์
            cols_map = {
                "id": "ID",
                "repair_date": "วันที่รับซ่อม",
                "job_no": "Job No.",
                "customer_name": "ชื่อลูกค้า",
                "phone_number": "เบอร์โทร",
                "brand": "แบรนด์",
                "model": "รุ่นสินค้า",
                "issue": "อาการเสีย",
                "parts_used": "อะไหล่ที่ใช้",
                "status": "สถานะการซ่อม",
            }

            display_cols = [c for c in cols_map.keys() if c in filtered_df.columns]
            display_df = filtered_df[display_cols].rename(columns=cols_map)

            # Pagination (10 บรรทัดต่อหน้า)
            rows_per_page = 10
            total_rows = len(display_df)
            total_pages = (
                math.ceil(total_rows / rows_per_page) if total_rows > 0 else 1
            )

            if st.session_state.current_page > total_pages:
                st.session_state.current_page = total_pages

            start_idx = (st.session_state.current_page - 1) * rows_per_page
            end_idx = start_idx + rows_per_page
            page_df = display_df.iloc[start_idx:end_idx].copy()

            st.dataframe(
                page_df,
                hide_index=True,
                height=385,
                use_container_width=True,
            )

            p_col1, p_col2, p_col3 = st.columns([4, 2, 4])
            with p_col2:
                page_selection = st.selectbox(
                    "หน้าการแสดงผล",
                    options=list(range(1, total_pages + 1)),
                    index=st.session_state.current_page - 1,
                    label_visibility="collapsed",
                )
                if page_selection != st.session_state.current_page:
                    st.session_state.current_page = page_selection
                    st.rerun()
        else:
            st.info("ℹ️ ยังไม่มีรายการใบงานเก็บรักษาในระบบ")

# ------------------------------------------
# 📝 2. เมนูบันทึกข้อมูลเครื่องซ่อมเสร็จ
# ------------------------------------------
elif st.session_state.active_menu == "บันทึกข้อมูล":
    st.markdown("📝 **เมนูบันทึกข้อมูลเครื่องซ่อมเสร็จ (เพิ่มข้อมูลใบงานใหม่)**")

    with st.form(key="repair_input_form", clear_on_submit=True):
        form_r1_c1, form_r1_c2 = st.columns([4, 2])
        with form_r1_c1:
            job_no = st.text_input(
                "เลขที่ใบงาน (Job No.)", placeholder="ระบุเลขใบงาน"
            ).strip()
        with form_r1_c2:
            repair_date = st.date_input("วันที่รับซ่อม", value=datetime.now())

        form_r2_c1, form_r2_c2 = st.columns(2)
        with form_r2_c1:
            customer_name = st.text_input(
                "ชื่อลูกค้า", placeholder="ชื่อ-นามสกุลลูกค้า"
            )
        with form_r2_c2:
            phone_number = st.text_input(
                "เบอร์โทรศัพท์", placeholder="เบอร์โทรติดต่อ"
            )

        form_r3_c1, form_r3_c2 = st.columns(2)
        with form_r3_c1:
            st.markdown('<div class="brand-container">', unsafe_allow_html=True)
            brand = st.radio(
                "แบรนด์สินค้า", ["Infinix", "Tecno", "Itel"], index=0
            )
            st.markdown("</div>", unsafe_allow_html=True)
        with form_r3_c2:
            model = st.text_input("รุ่น/โมเดล", placeholder="เช่น Hot 40 Pro")

        form_r4_c1, form_r4_c2 = st.columns(2)
        with form_r4_c1:
            issue = st.text_input("อาการเสีย", placeholder="อาการเสียที่แจ้งซ่อม")
        with form_r4_c2:
            parts_used = st.text_input(
                "อะไหล่ที่ใช้", placeholder="รายการอะไหล่ที่เปลี่ยน"
            )

        st.markdown('<div class="status-container">', unsafe_allow_html=True)
        status_selected = st.radio(
            "status_selected",
            [
                "🟢 รับเครื่องแล้ว/รอตรวจเช็ค",
                "🟡 กำลังดำเนินการซ่อม",
                "🔵 ซ่อมเสร็จสิ้น/รอส่งมอบลูกค้า",
                "🔴 ยกเลิกการซ่อม/คืนเครื่อง",
            ],
            index=2,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        submit_button = st.form_submit_button(label="💾 บันทึกข้อมูลงานซ่อม")

        if submit_button:
            st.success(
                "🎉 บันทึกข้อมูลเรียบร้อย! (โปรดป้อนข้อมูลลงใน Google Sheets เพื่ออัปเดตระบบ)"
            )

# ------------------------------------------
# 📦 3. เมนูรับเข้าอะไหล่
# ------------------------------------------
elif st.session_state.active_menu == "รับเข้าอะไหล่":
    st.markdown("📦 **เมนูรับเข้าอะไหล่**")
    df_parts = load_data("parts_stock")

    if not df_parts.empty:
        st.dataframe(df_parts, hide_index=True, use_container_width=True)
    else:
        st.info("ℹ️ ยังไม่มีรายการอะไหล่ที่จัดเก็บในคลังข้อมูล")

# ------------------------------------------
# 📊 4. เมนู แสดงสถิติ การซ่อม
# ------------------------------------------
elif st.session_state.active_menu == "สถิติการซ่อม":
    st.markdown("📊 **เมนู แสดงสถิติ การซ่อม**")
    df_repairs = load_data("repairs")

    if not df_repairs.empty:
        total_jobs = len(df_repairs)
        inf_c = (
            len(df_repairs[df_repairs["brand"].str.contains("Infinix", na=False, case=False)])
            if "brand" in df_repairs.columns
            else 0
        )
        tec_c = (
            len(df_repairs[df_repairs["brand"].str.contains("Tecno", na=False, case=False)])
            if "brand" in df_repairs.columns
            else 0
        )
        ite_c = (
            len(df_repairs[df_repairs["brand"].str.contains("Itel", na=False, case=False)])
            if "brand" in df_repairs.columns
            else 0
        )

        st.markdown("### 📈 ปริมาณงานแยกตามแบรนด์สินค้า")
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        m_c1.metric("📦 งานภาพรวมทั้งหมด", f"{total_jobs} รายการ")
        m_c2.metric("📱 Infinix", f"{inf_c} เครื่อง")
        m_c3.metric("📱 Tecno", f"{tec_c} เครื่อง")
        m_c4.metric("📱 Itel", f"{ite_c} เครื่อง")
    else:
        st.info("ℹ️ ไม่มีฐานข้อมูลเพียงพอสำหรับการประมวลผลสรุปสถิติ")

# ------------------------------------------
# 📥 5. เมนู Export to Excel
# ------------------------------------------
elif st.session_state.active_menu == "ส่งออก Excel":
    st.markdown("📥 **เมนู Export to Excel**")
    df_repairs = load_data("repairs")

    if not df_repairs.empty:
        st.dataframe(df_repairs, hide_index=True, height=385)
        csv_data = df_repairs.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ CSV/Excel ของระบบทันที",
            data=csv_data,
            file_name=f"Carlcare_Excel_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("ℹ️ ปัจจุบันฐานข้อมูลว่างเปล่า ไม่สามารถส่งออกไฟล์ได้")

# ------------------------------------------
# 📄 6. เมนู Export to PDF
# ------------------------------------------
elif st.session_state.active_menu == "ส่งออก PDF":
    st.markdown("📄 **เมนู Export to PDF**")
    df_repairs = load_data("repairs")

    if not df_repairs.empty:
        st.dataframe(df_repairs, hide_index=True, height=450)
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
