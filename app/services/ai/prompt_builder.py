# app/services/ai/prompt_builder.py
import json

class PromptBuilder:
    @staticmethod
    def build_judge_prompt(sual_metni: str, duzgun_hell: str, meyarlar: str) -> str:
        """
        Bu, Sistem Prompt-udur (System Message). 
        AI-ın xarakterini və yoxlama qaydalarını təyin edir.
        """
        return f"""
        Sən OTK (Təhsilin Qiymətləndirilməsi Mərkəzi) üçün işləyən ÇOX SƏRT və OBYEKTİV bir Baş Yoxlayıcı Müəllimsən.
        Sənin vəzifən şagirdin həllini yalnız və yalnız verilmiş meyarlara əsasən qiymətləndirməkdir.

        # SUALIN ŞƏRTİ:
        {sual_metni}

        # DÜZGÜN HƏLL:
        {duzgun_hell}

        # QİYMƏTLƏNDİRMƏ MEYARLARI (BUNLARDAN KƏNARA ÇIXMAQ QƏTİ QADAĞANDIR):
        {meyarlar}

        # QAYDALAR:
        1. Emosional bal vermə. Şagird "cəhd edib" deyə bal verilmir.
        2. Meyarda göstərilən şərtlərdən biri belə çatışmırsa, tam bal (1) verilə bilməz.
        3. Cavabını YALNIZ VƏ YALNIZ aşağıdakı JSON formatında qaytar. Başqa heç bir mətn yazma.

        # ÇIXIŞ FORMATI (OUTPUT FORMAT):
        {{
            "verilen_bal": 0.0, // Yalnız 0, 0.5 və ya 1 ola bilər
            "serh": "Şagird filan yerdə səhv etdiyi üçün filan meyar əsasında 0.5 bal verildi.",
            "confidence_score": 0.95 // 0 ilə 1 arasında
        }}
        """

    @staticmethod
    def build_user_message(sagird_helli_text: str = None, sagird_helli_image: str = None) -> list:
        """
        Bu, İstifadəçi Mesajıdır (User Message). Şagirdin həllini AI-ya ötürür.
        """
        content = []
        
        # Əgər mətn formatında həll gəlibsə
        if sagird_helli_text:
            content.append({
                "type": "text", 
                "text": f"ŞAGİRDİN HƏLLİ:\n{sagird_helli_text}"
            })
            
        # Əgər şəkil (Base64) gəlibsə
        if sagird_helli_image:
            content.append({
                "type": "text",
                "text": "ŞAGİRDİN YAZILI HƏLLİNİN ŞƏKLİ AŞAĞIDADIR. Xahiş edirəm diqqətlə oxu."
            })
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{sagird_helli_image}",
                    "detail": "high" # AI şəkli yüksək keyfiyyətdə analiz etsin
                }
            })
            
        return content