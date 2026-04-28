# dashboard/app_ui.py
import streamlit as st
import requests
import base64
import pandas as pd
import time

# API Ünvanları
BASE_API_URL = "http://127.0.0.1:8000/api/v1"
API_URL = f"{BASE_API_URL}/evaluate"
BATCH_API_URL = f"{BASE_API_URL}/evaluate/batch"

st.set_page_config(page_title="OTK AutoGrade | Enterprise", page_icon="🏛️", layout="wide")

# Xüsusi UI Stilləri
st.markdown("""
<style>
.agent-log {
    background-color: #1E293B;
    border-left: 4px solid #F59E0B;
    padding: 1rem;
    border-radius: 4px;
    font-family: monospace;
    font-size: 14px;
    white-space: pre-wrap;
    margin-bottom: 1rem;
}
.ai-decision {
    background-color: rgba(16, 185, 129, 0.1);
    border-left: 4px solid #10B981;
    padding: 1.5rem;
    border-radius: 4px;
    font-size: 16px;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# Köməkçi funksiya: Şəkli oxuyub base64-ə çevirir
def get_base64(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.read()).decode('utf-8')
    return None

st.title("🏛️ OTK AutoGrade - Enterprise Panel")
st.caption("Agentic Workflow, Ağıllı Keşləmə & Asinxron Kütləvi Yoxlama Sistemi")
st.divider()

# TAB-LAR YARADILIR
tab_single, tab_batch = st.tabs(["👤 Fərdi Yoxlama", "📚 Kütləvi (Sinif) Yoxlaması"])

# =========================================================================
# TAB 1: FƏRDİ YOXLAMA (Köhnə kodun bura daxil edildi)
# =========================================================================
with tab_single:
    col1, col2 = st.columns(2)

    # SOL SÜTUN (Sual Binası)
    with col1:
        with st.container(border=True):
            st.subheader("📚 Sual Konfiqurasiyası")
            st.info("💡 Eyni Sual ID-si ilə edilən təkrar sorğular avtomatik olaraq bazadan oxunacaq (0 Token xərci).")
            
            sual_id = st.text_input("🔑 Sual ID", value="py_001")
            
            # Sual Şərti
            with st.expander("📝 Sualın Şərti (Mətn və/və ya Şəkil)", expanded=True):
                sual_metni = st.text_area("Şərt (Mətn)", value="İstifadəçidən iki tam ədəd alıb cəmini tapan proqram yazın.")
                sual_sekli = st.file_uploader("Şərtin Şəkli (İstəyə bağlı)", type=["jpg", "png"], key="sual_img")
                
            # Düzgün Həll
            with st.expander("✅ Düzgün Həll (Mətn və/və ya Şəkil)", expanded=False):
                duzgun_hell = st.text_area("Həll (Mətn)", value="a = int(input())\nb = int(input())\nprint(a+b)")
                duzgun_hell_sekli = st.file_uploader("Həllin Şəkli (İstəyə bağlı)", type=["jpg", "png"], key="hell_img")
                
            # Meyarlar
            with st.expander("⚖️ Meyarlar (Mətn və/və ya Şəkil)", expanded=False):
                meyarlar = st.text_area("Meyarlar (Mətn)", value="1 bal: Tam düz\n0.5 bal: Tip çevirmə yoxdur\n0 bal: Səhvdir")
                meyarlar_sekli = st.file_uploader("Meyarların Şəkli (İstəyə bağlı)", type=["jpg", "png"], key="meyar_img")

    # SAĞ SÜTUN (Şagirdin Cavabı)
    with col2:
        with st.container(border=True):
            st.subheader("👨‍🎓 Şagirdin Cavabı")
            sagird_id = st.text_input("🔑 Şagird ID", value="std_1024")
            
            st.markdown("Aşağıdakılardan birini və ya hər ikisini daxil edə bilərsiniz:")
            
            sagird_helli_text = st.text_area("⌨️ Kod / Mətn", height=150, placeholder="Şagirdin yazdığı mətn burada...")
            sagird_helli_sekli = st.file_uploader("📸 Əl yazması / Şəkil", type=["jpg", "png", "jpeg"], key="sagird_img")
            
            if sagird_helli_sekli:
                st.image(sagird_helli_sekli, caption="Yüklənmiş Şəkil", use_container_width=True)

    st.write("")
    submit_btn = st.button("🚀 Agentləri İşə Sal (Qiymətləndir)", use_container_width=True, type="primary")

    # İCRA VƏ NƏTİCƏ (Fərdi)
    if submit_btn:
        if not sagird_helli_text and not sagird_helli_sekli:
            st.error("⚠️ Lütfən şagirdin cavabını (mətn və ya şəkil) daxil edin!")
        else:
            with st.spinner("🤖 Agentlər işləyir... Göz Agenti oxuyur, Hakim Agent qərar verir..."):
                payload = {
                    "sual_id": sual_id,
                    "sagird_id": sagird_id,
                    "sual_metni": sual_metni if sual_metni else None,
                    "sual_sekli_base64": get_base64(sual_sekli),
                    "duzgun_hell": duzgun_hell if duzgun_hell else None,
                    "duzgun_hell_sekli_base64": get_base64(duzgun_hell_sekli),
                    "meyarlar": meyarlar if meyarlar else None,
                    "meyarlar_sekli_base64": get_base64(meyarlar_sekli),
                    "sagird_helli_text": sagird_helli_text if sagird_helli_text else None,
                    "sagird_helli_base64": get_base64(sagird_helli_sekli)
                }
                
                try:
                    res = requests.post(API_URL, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        st.success("✅ Yoxlama Tamamlandı!")
                        
                        with st.container(border=True):
                            m_col1, m_col2, m_col3 = st.columns(3)
                            m_col1.metric("👤 Şagird ID", data["sagird_id"])
                            m_col2.metric("📊 Yekun Bal", f"{data['verilen_bal']} / 1.0")
                            m_col3.metric("🧠 Əminlik", f"{int(data['confidence_score'] * 100)}%")
                        
                        st.markdown("### 🔍 Agentlərin Analiz Jurnalı (Log)")
                        with st.expander("⚙️ Sualın Analizi (Keş Məlumatı)", expanded=True):
                            st.markdown(f'<div class="agent-log">{data["sualin_analizi"]}</div>', unsafe_allow_html=True)
                            
                        with st.expander("👁️ Göz Agenti (Şagirdin Şəklindən Oxunanlar)", expanded=True):
                            st.markdown(f'<div class="agent-log">{data.get("sagirdin_analizi", "Şəkil yüklənməyib.")}</div>', unsafe_allow_html=True)
                        
                        st.markdown("### ⚖️ Hakim Agentin Qərarı")
                        st.markdown(f"""
                        <div class="ai-decision">
                            <strong>Müəllimin Şərhi:</strong><br><br>
                            {data["serh"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ Backend Xətası: {res.text}")
                except Exception as e:
                    st.error(f"🔌 Bağlantı xətası: {e}")


# =========================================================================
# TAB 2: KÜTLƏVİ (SİNİF) YOXLAMASI
# =========================================================================
with tab_batch:
    st.header("📚 Kütləvi CSV Yoxlaması")
    st.markdown("Şagirdlərin cavabları olan `.csv` faylını yükləyin. Bütün sinif **eyni anda, saniyələr içində** yoxlanılacaq.")
    
    with st.container(border=True):
        b_sual_id = st.text_input("🔑 Sual ID (Bütün CSV üçün eyni sual yoxlanılır)", value="py_001", key="b_sual_id")
        uploaded_csv = st.file_uploader("📥 Şagird Cavabları (CSV formatında)", type=["csv"])
        
        st.info("ℹ️ CSV faylınızda mütləq `sagird_id` və `cavab_metni` adlı iki sütun olmalıdır.")
        
    if uploaded_csv and st.button("⚡ Bütün Sinfi Yoxla (Asinxron)", type="primary", use_container_width=True):
        # CSV-ni oxuyuruq
        df = pd.read_csv(uploaded_csv)
        st.write("📊 **Yüklənən Məlumatlar (İlkin baxış):**", df.head())
        
        if 'sagird_id' not in df.columns or 'cavab_metni' not in df.columns:
            st.error("❌ Xəta: CSV faylında `sagird_id` və `cavab_metni` sütunları tapılmadı!")
        else:
            # API üçün data hazırlayırıq
            batch_payload = []
            for index, row in df.iterrows():
                batch_payload.append({
                    "sual_id": b_sual_id,
                    "sagird_id": str(row['sagird_id']),
                    "sagird_helli_text": str(row['cavab_metni']),
                })
                
            with st.spinner(f"🚀 {len(batch_payload)} şagird paralel olaraq yoxlanılır. Saniyə ölçən işə düşdü..."):
                start_time = time.time()
                
                try:
                    # Endpoint-ə toplu sorğu atırıq
                    res = requests.post(BATCH_API_URL, json=batch_payload)
                    
                    end_time = time.time()
                    elapsed = round(end_time - start_time, 2)
                    
                    if res.status_code == 200:
                        results = res.json()
                        st.success(f"✅ {len(results)} şagirdin cavabı cəmi {elapsed} saniyəyə yoxlandı!")
                        
                        # Nəticələri cədvələ yığırıq
                        result_df = pd.DataFrame([{
                            "Şagird ID": r["sagird_id"], 
                            "Verilən Bal": r["verilen_bal"], 
                            "Müəllim Şərhi": r["serh"],
                            "Əminlik (%)": int(r["confidence_score"] * 100)
                        } for r in results])
                        
                        st.dataframe(result_df, use_container_width=True)
                        
                        # Nəticələri yükləmək üçün düymə
                        csv_export = result_df.to_csv(index=False).encode('utf-8-sig') # utf-8-sig Azərbaycanca şriftlər üçün
                        st.download_button(
                            label="📥 Nəticələri Cədvəl (CSV) olaraq yüklə",
                            data=csv_export,
                            file_name=f"netice_{b_sual_id}_{int(time.time())}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    else:
                        st.error(f"❌ Xəta: {res.text}")
                except Exception as e:
                    st.error(f"🔌 Bağlantı xətası: Cihazınızın və FastAPI-nin qoşulu olduğundan əmin olun. Detal: {e}")