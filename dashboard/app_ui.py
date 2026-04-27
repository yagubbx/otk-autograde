# dashboard/app_ui.py
import streamlit as st
import requests
import base64

API_URL = "http://127.0.0.1:8000/api/v1/evaluate"

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
st.caption("Agentic Workflow & Ağıllı Keşləmə (Smart Caching) Sistemi")
st.divider()

col1, col2 = st.columns(2)

# ================= SOL SÜTUN (Sual Binası) =================
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

# ================= SAĞ SÜTUN (Şagirdin Cavabı) =================
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

# ================= İCRA VƏ NƏTİCƏ =================
if submit_btn:
    if not sagird_helli_text and not sagird_helli_sekli:
        st.error("⚠️ Lütfən şagirdin cavabını (mətn və ya şəkil) daxil edin!")
    else:
        with st.spinner("🤖 Agentlər işləyir... Göz Agenti oxuyur, Hakim Agent qərar verir..."):
            
            # API-ya gedəcək məlumatları hazırlayırıq
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
                    
                    # 1. METRİKALAR
                    with st.container(border=True):
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("👤 Şagird ID", data["sagird_id"])
                        m_col2.metric("📊 Yekun Bal", f"{data['verilen_bal']} / 1.0")
                        m_col3.metric("🧠 Əminlik", f"{int(data['confidence_score'] * 100)}%")
                    
                    # 2. ŞƏFFAFLIQ PANeli (Göz Agentinin gördükləri)
                    st.markdown("### 🔍 Agentlərin Analiz Jurnalı (Log)")
                    
                    with st.expander("⚙️ Sualın Analizi (Keş Məlumatı)", expanded=True):
                        st.markdown(f'<div class="agent-log">{data["sualin_analizi"]}</div>', unsafe_allow_html=True)
                        
                    with st.expander("👁️ Göz Agenti (Şagirdin Şəklindən Oxunanlar)", expanded=True):
                        st.markdown(f'<div class="agent-log">{data.get("sagirdin_analizi", "Şəkil yüklənməyib.")}</div>', unsafe_allow_html=True)
                    
                    # 3. YEKUN QƏRAR (Hakim Agentin Şərhi)
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