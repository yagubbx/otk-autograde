# dashboard/app_ui.py
import streamlit as st
import requests
import base64

API_URL = "http://127.0.0.1:8000/api/v1/evaluate"

# Səhifənin əsas tənzimləmələri
st.set_page_config(page_title="OTK AutoGrade", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

# Yalnız AI şərhi qutusunu fərqləndirmək üçün çox minimal CSS
st.markdown("""
<style>
.ai-comment {
    background-color: rgba(59, 130, 246, 0.1);
    border-left: 4px solid #3B82F6;
    padding: 1.5rem;
    border-radius: 4px;
    margin-top: 1rem;
    font-size: 16px;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# Başlıq
st.title("🎓 OTK AutoGrade Panel")
st.caption("Süni İntellekt Əsaslı Avtomatlaşdırılmış Qiymətləndirmə Sistemi")
st.divider() # İncə bir xətt çəkir

# Ekranı iki bərabər hissəyə bölürük
col1, col2 = st.columns(2)

# SOL SÜTUN (Sual Məlumatları)
with col1:
    # st.container(border=True) - Bu, elementi çox səliqəli bir "kart" içinə salır (Streamlit-in ən yaxşı xüsusiyyəti)
    with st.container(border=True):
        st.subheader("📚 Sualın Təfərrüatları")
        sual_id = st.text_input("Sualın ID-si", value="inf_001")
        sual_metni = st.text_area("Sualın Şərti", value="X və Y-in cəmini tapan alqoritmin blok-sxemini qurun.", height=100)
        duzgun_hell = st.text_area("Düzgün Həll", value="Başlanğıc -> X və Y daxil et -> Z = X + Y -> Z-i çap et -> Son", height=100)
        meyarlar = st.text_area("Meyarlar", value="1 bal: Bütün bloklar düzgündür.\n0.5 bal: Hesablama düzdür, amma giriş/çıxış blokları səhvdir.\n0 bal: Tam səhvdir.", height=100)

# SAĞ SÜTUN (Şagirdin Cavabı)
with col2:
    with st.container(border=True):
        st.subheader("📝 Şagirdin Həlli")
        sagird_id = st.text_input("Şagirdin ID-si", value="std_999")
        
        # Seçim qutusu (Mətn və ya Şəkil)
        cavab_novu = st.radio("Məlumatın Növünü Seçin", ["Mətn Daxil Et", "Şəkil Yüklə"], horizontal=True)
        
        sagird_helli_text = ""
        sagird_helli_base64 = ""
        
        if cavab_novu == "Mətn Daxil Et":
            sagird_helli_text = st.text_area("Şagirdin Cavabı", value="X və Y daxil etdim, sonra vurdum çap etdim.", height=210)
        else:
            uploaded_file = st.file_uploader("Əl yazmasını yükləyin (JPG, PNG)", type=["jpg", "png", "jpeg"])
            if uploaded_file:
                st.image(uploaded_file, use_container_width=True)
                # Şəkli AI üçün arxa planda oxunula bilən formata çeviririk
                sagird_helli_base64 = base64.b64encode(uploaded_file.read()).decode('utf-8')

st.write("") # Bir az boşluq

# Əsas Düymə (type="primary" düyməni avtomatik mavi edir)
submit_btn = st.button("🚀 Süni İntellektlə Yoxla", use_container_width=True, type="primary")

# NƏTİCƏNİN İŞLƏNMƏSİ
if submit_btn:
    # Validasiya (Əgər məlumat boşdursa, xəbərdarlıq ver)
    if cavab_novu == "Mətn Daxil Et" and not sagird_helli_text:
        st.error("⚠️ Lütfən şagirdin cavabını daxil edin!")
    elif cavab_novu == "Şəkil Yüklə" and not sagird_helli_base64:
        st.error("⚠️ Lütfən qiymətləndirmək üçün şəkli yükləyin!")
    else:
        # Spinner dönərkən arxada AI işləyir
        with st.spinner("🤖 AI şagirdin cavabını analiz edir. Bu bir neçə saniyə çəkə bilər..."):
            payload = {
                "sual_id": sual_id,
                "sual_metni": sual_metni,
                "duzgun_hell": duzgun_hell,
                "meyarlar": meyarlar,
                "sagird_id": sagird_id,
                "sagird_helli_text": sagird_helli_text if cavab_novu == "Mətn Daxil Et" else None,
                "sagird_helli_base64": sagird_helli_base64 if cavab_novu == "Şəkil Yüklə" else None
            }
            
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.success("✅ Qiymətləndirmə uğurla tamamlandı!")
                    
                    # Nəticəni gözəl bir çərçivə içərisində göstəririk
                    with st.container(border=True):
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("👤 Şagird ID", data["sagird_id"])
                        m_col2.metric("📊 Verilən Bal", f"{data['verilen_bal']} / 1.0")
                        m_col3.metric("🧠 Əminlik Dərəcəsi", f"{int(data['confidence_score'] * 100)}%")
                        
                        st.markdown(f"""
                        <div class="ai-comment">
                            <strong>Müəllimin (AI) Şərhi və Əsaslandırma:</strong><br><br>
                            {data["serh"]}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Backend Xətası: {res.text}")
            except Exception as e:
                st.error(f"🔌 Bağlantı Xətası: Lütfən backend-in (FastAPI) aktiv olduğundan əmin olun. Xəta: {e}")