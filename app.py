import pandas as pd
import streamlit as st

# ==========================================
# 1. การตั้งค่าหน้าเว็บ (Page Config)
# ==========================================
st.set_page_config(
    page_title="Carlcare ITcity Management System",
    page_icon="🛠️",
    layout="wide",
)


# ==========================================
# 2. ฟังก์ชันดึงข้อมูลจาก Google Sheets (วิธีใหม่: อ่านตรงผ่าน CSV)
# ==========================================
def get_csv_url(sheet_name):
    """แปลง URL ใน Secrets ให้เป็นลิงก์ Export CSV ตามชื่อแท็บที่ระบุ"""
    try:
        base_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # ตัดส่วนท้ายของ URL ออกเพื่อให้ได้ Base URL ที่ถูกต้อง
        if "/edit" in base_url:
            base_url = base_url.split("/edit")[0]
        return f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    except Exception as e:
        st.error(
            "⚠️ ไม่พบการตั้งค่า [connections.gsheets] ใน Secrets กรุณาตรวจสอบการตั้งค่า"
        )
        return ""


# ตั้งค่า cache ไว้ 5 วินาที เพื่อให้ดึงข้อมูลใหม่เสมอเมื่อมีการอัปเดต
@st.cache_data(ttl=5)
def load_data(sheet_name):
    url = get_csv_url(sheet_name)
    if not url:
        return pd.DataFrame()
    try:
        # อ่านข้อมูล CSV จาก Google Sheets
        df = pd.read_csv(url)

        # ลบแถวหรือคอลัมน์ที่เป็นค่าว่างทั้งหมดออก
        df = df.dropna(how="all")

        # แปลงชื่อคอลัมน์ให้เป็นตัวพิมพ์เล็กและไม่มีเว้นวรรคส่วนเกิน
        df.columns = [str(col).strip().lower() for col in df.columns]

        return df
    except Exception as e:
        st.error(f"❌ ไม่สามารถดึงข้อมูลจากแท็บ {sheet_name} ได้: {e}")
        return pd.DataFrame()


# ==========================================
# 3. โครงสร้างเมนูหลัก (Sidebar Navigation)
# ==========================================
st.sidebar.title("🛠️ เมนูระบบจัดการ")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "เลือกรายการที่ต้องการ:",
    [
        "🔍 ค้นหาและจัดการข้อมูลใบงาน",
        "📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ",
        "📦 รับเข้าอะไหล่ (Stock Parts)",
        "📊 รายงานสถิติกระบวนการซ่อม",
        "📥 ส่งออกข้อมูล Export to Excel",
    ],
)

st.sidebar.markdown("---")
# ปุ่มกดล้าง Cache สำหรับดึงข้อมูลใหม่ทันที
if st.sidebar.button("🔄 อัปเดต/ดึงข้อมูลใหม่ (Refresh)"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("🟢 เชื่อมต่อ Google Sheets (Fast CSV Mode)")


# ==========================================
# 4. ส่วนแสดงผลเนื้อหาตามเมนู
# ==========================================

# ------------------------------------------
# เมนู 1: ค้นหาและจัดการข้อมูลใบงาน
# ------------------------------------------
if menu == "🔍 ค้นหาและจัดการข้อมูลใบงาน":
    st.title("🛠️ ศูนย์ซ่อม Carlcare ITcity")
    st.subheader("🔍 เมนูค้นหาและจัดการข้อมูลใบงาน")

    # โหลดข้อมูล
    df_repairs = load_data("repairs")

    search_kw = st.text_input(
        "🔎 พิมพ์ข้อมูลค้นหา",
        placeholder="พิมพ์เพื่อค้นหา Job No., ชื่อลูกค้า, เบอร์โทรศัพท์, หรือรุ่น...",
    )

    if not df_repairs.empty:
        # จัดการกรองข้อมูลตามคำค้นหา
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

        st.write(f"📋 **รายการใบงานทั้งหมด ({len(filtered_df)} รายการ)**")

        # แสดงผลตารางข้อมูล
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", format="%d"),
                "job_no": "Job No.",
                "customer_name": "ชื่อลูกค้า",
                "phone_number": "เบอร์โทรศัพท์",
                "brand": "ยี่ห้อ",
                "model": "รุ่น",
                "issue": "อาการเสีย",
                "parts_used": "อะไหล่ที่ใช้",
                "status": "สถานะ",
                "repair_date": "วันที่ซ่อม",
                "date_added": "วันที่บันทึก",
            },
        )
    else:
        st.info("ℹ️ ยังไม่มีรายการใบงานเก็บรักษาในระบบ หรือกำลังโหลดข้อมูล...")

# ------------------------------------------
# เมนู 2: บันทึกข้อมูลเครื่องซ่อมเสร็จ
# ------------------------------------------
elif menu == "📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ":
    st.title("📝 บันทึกข้อมูลเครื่องซ่อมเสร็จ")
    st.info(
        "💡 สำหรับการเพิ่มข้อมูลใหม่ แนะนำให้กรอกผ่านหน้านี้ หรือพิมพ์ลงบน Google Sheets แท็บ 'repairs' โดยตรงได้เลยครับ"
    )

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

        submit = st.form_submit_button("💾 บันทึกข้อมูล")

        if submit:
            if not job_no or not customer_name:
                st.warning("⚠️ กรุณากรอก Job No. และ ชื่อลูกค้า")
            else:
                st.success(
                    "✅ บันทึกข้อมูลเรียบร้อย! (โปรดเปิดไปเพิ่มแถวใน Google Sheets หรือเชื่อมต่อ gspread เพิ่มเติมสำหรับการบันทึกย้อนกลับ)"
                )

# ------------------------------------------
# เมนู 3: รับเข้าอะไหล่ (Stock Parts)
# ------------------------------------------
elif menu == "📦 รับเข้าอะไหล่ (Stock Parts)":
    st.title("📦 คลังอะไหล่ (Stock Parts)")

    df_parts = load_data("parts_stock")

    if not df_parts.empty:
        st.dataframe(df_parts, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ ไม่พบข้อมูลในแท็บ parts_stock")

# ------------------------------------------
# เมนู 4: รายงานสถิติกระบวนการซ่อม
# ------------------------------------------
elif menu == "📊 รายงานสถิติกระบวนการซ่อม":
    st.title("📊 รายงานสถิติกระบวนการซ่อม")

    df_repairs = load_data("repairs")

    if not df_repairs.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("จำนวนงานซ่อมทั้งหมด", f"{len(df_repairs)} รายการ")

        if "brand" in df_repairs.columns:
            brand_counts = df_repairs["brand"].value_counts()
            st.write("### 📱 สัดส่วนแยกตามยี่ห้อ")
            st.bar_chart(brand_counts)
    else:
        st.info("ℹ️ ไม่มีข้อมูลสถิติ")

# ------------------------------------------
# เมนู 5: ส่งออกข้อมูล Export to Excel
# ------------------------------------------
elif menu == "📥 ส่งออกข้อมูล Export to Excel":
    st.title("📥 ส่งออกข้อมูลเป็นไฟล์ Excel")

    df_repairs = load_data("repairs")

    if not df_repairs.empty:
        st.write("กดปุ่มด้านล่างเพื่อดาวน์โหลดข้อมูลทั้งหมดเป็นไฟล์ CSV/Excel")

        csv_data = df_repairs.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 ดาวน์โหลดข้อมูลงานซ่อม (.csv)",
            data=csv_data,
            file_name="carlcare_repairs_export.csv",
            mime="text/csv",
        )
