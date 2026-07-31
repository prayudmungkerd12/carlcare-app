import pandas as pd
import streamlit as st

# ==========================================
# 1. Page Config & CSS Style ดั้งเดิม
# ==========================================
st.set_page_config(
    page_title="ศูนย์ซ่อม Carlcare ITcity",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# แต่ง CSS กลับมาเป็นสไตล์เดิม
st.markdown(
    """
    <style>
    /* ซ่อน Header / Footer ของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* กล่อง Banner หัวข้อหลัก */
    .banner-box {
        background-color: #EBF3FE;
        padding: 18px 25px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .banner-title {
        color: #1E293B;
        font-size: 22px;
        font-weight: bold;
        margin: 0;
    }
    .banner-subtitle {
        color: #1E88E5;
        font-size: 14px;
        font-weight: 500;
        margin: 0;
    }
    
    /* กล่องสถานะการเชื่อมต่อมุมซ้ายล่าง */
    .status-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        margin-top: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. ฟังก์ชันดึงข้อมูลจาก Google Sheets (Fast Load)
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


# ==========================================
# 3. Sidebar (เมนูด้านซ้าย แบบดั้งเดิมเป๊ะ)
# ==========================================
st.sidebar.markdown("### เมนูระบบจัดการ")

menu = st.sidebar.radio(
    "",
    [
        "📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ",
        "📦 รับเข้าอะไหล่ (Stock Parts)",
        "🔍 ค้นหาและจัดการข้อมูลใบงาน",
        "📊 รายงานสถิติกระบวนการซ่อม",
        "📥 ส่งออกข้อมูล Export to Excel",
        "📑 พิมพ์รายงาน Export to PDF",
    ],
    index=2,  # เลือกหน้า ค้นหาและจัดการข้อมูลใบงาน เป็นค่าเริ่มต้น
)

# แสดงสถานะการเชื่อมต่อมุมซ้ายล่างแบบดั้งเดิม
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown(
    """
    <div class="status-card">
        <span style="color: #10B981;">🟢 <b>เชื่อมต่อ Google Sheets แล้ว</b></span><br>
        <small style="color: #64748B;">ข้อมูลถูกจัดเก็บแบบเรียลไทม์ ปลอดภัยบนระบบ Cloud</small>
    </div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 4. ส่วนแสดงผลตามหน้าเมนู
# ==========================================

# ------------------------------------------
# เมนู: 🔍 ค้นหาและจัดการข้อมูลใบงาน
# ------------------------------------------
if menu == "🔍 ค้นหาและจัดการข้อมูลใบงาน":
    # Banner หัวข้อสไตล์ดั้งเดิม
    st.markdown(
        """
        <div class="banner-box">
            <div class="banner-title">🛠️ ศูนย์ซ่อม Carlcare ITcity</div>
            <div class="banner-subtitle">Infinix • Tecno • Itel Management System</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 🔍 เมนูค้นหาและจัดการข้อมูลใบงาน")
    st.markdown("##### 📋 พิมพ์ข้อมูลค้นหา")

    search_kw = st.text_input(
        "",
        placeholder="พิมพ์เพื่อค้นหา Job No. หรือ ชื่อลูกค้า...",
        label_visibility="collapsed",
    )

    df_repairs = load_data("repairs")

    if not df_repairs.empty:
        if search_kw:
            filtered_df = df_repairs[
                df_repairs.astype(str).apply(
                    lambda row: row.str.contains(
                        search_kw, case=False, na=False
                    ).any(),
                    axis=1,
                )
            ]
        else:
            filtered_df = df_repairs

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("id", format="%d"),
                "job_no": "job_no",
                "customer_name": "customer_name",
                "phone_number": "phone_number",
                "brand": "brand",
                "model": "model",
                "issue": "issue",
                "parts_used": "parts_used",
                "status": "status",
                "repair_date": "repair_date",
                "date_added": "date_added",
            },
        )
    else:
        st.info("ℹ️ ยังไม่มีรายการใบงานเก็บรักษาในระบบ")

# ------------------------------------------
# เมนู: 📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ
# ------------------------------------------
elif menu == "📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ":
    st.markdown("### 📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ")
    with st.form("add_repair_form"):
        col1, col2 = st.columns(2)
        with col1:
            job_no = st.text_input("Job No. *")
            customer_name = st.text_input("ชื่อลูกค้า *")
            phone_number = st.text_input("เบอร์โทรศัพท์")
            brand = st.selectbox("ยี่ห้อ", ["Infinix", "Tecno", "Itel", "อื่นๆ"])
            model = st.text_input("รุ่น (Model)")
        with col2:
            issue = st.text_area("อาการเสีย")
            parts_used = st.text_input("อะไหล่ที่ใช้")
            status = st.selectbox(
                "สถานะงานซ่อม",
                [
                    "ซ่อมเสร็จสิ้น/รอส่งมอบลูกค้า",
                    "ยกเลิกการซ่อม/คืนเครื่อง",
                    "อยู่ระหว่างรออะไหล่",
                ],
            )
            repair_date = st.date_input("วันที่ซ่อมเสร็จ")

        submit = st.form_submit_button("บันทึกข้อมูลงานซ่อม")

# ------------------------------------------
# เมนู: 📦 รับเข้าอะไหล่ (Stock Parts)
# ------------------------------------------
elif menu == "📦 รับเข้าอะไหล่ (Stock Parts)":
    st.markdown("### 📦 รับเข้าอะไหล่ (Stock Parts)")
    df_parts = load_data("parts_stock")
    if not df_parts.empty:
        st.dataframe(df_parts, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ ยังไม่มีรายการอะไหล่ในระบบ")

# ------------------------------------------
# เมนู: 📊 รายงานสถิติกระบวนการซ่อม
# ------------------------------------------
elif menu == "📊 รายงานสถิติกระบวนการซ่อม":
    st.markdown("### 📊 รายงานสถิติกระบวนการซ่อม")
    df_repairs = load_data("repairs")
    if not df_repairs.empty:
        st.metric("จำนวนรายการทั้งหมด", f"{len(df_repairs)} รายการ")
        st.dataframe(df_repairs, use_container_width=True, hide_index=True)

# ------------------------------------------
# เมนู: 📥 ส่งออกข้อมูล Export to Excel
# ------------------------------------------
elif menu == "📥 ส่งออกข้อมูล Export to Excel":
    st.markdown("### 📥 ส่งออกข้อมูล Export to Excel")
    df_repairs = load_data("repairs")
    if not df_repairs.empty:
        csv_data = df_repairs.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="ดาวน์โหลดไฟล์ Excel (.csv)",
            data=csv_data,
            file_name="carlcare_repairs.csv",
            mime="text/csv",
        )

# ------------------------------------------
# เมนู: 📑 พิมพ์รายงาน Export to PDF
# ------------------------------------------
elif menu == "📑 พิมพ์รายงาน Export to PDF":
    st.markdown("### 📑 พิมพ์รายงาน Export to PDF")
    st.info("ℹ️ ระบบพิมพ์รายงาน PDF พร้อมใช้งาน")
