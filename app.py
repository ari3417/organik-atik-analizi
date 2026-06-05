import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np

# Sayfa ayarları ve başlık
st.set_page_config(page_title="Döngüsel Gıda & Organik Atık Analizi", layout="centered")

st.title("🌱 Kentsel Gıda Döngüsü Analiz Arayüzü")
st.markdown("""
Bu araç, pazar fazlası veya evsel organik atıklarınızı analiz ederek **ileri dönüşüm (upcycling)** veya **mikro-kompostlama** potansiyellerini hesaplar.
""")

@st.cache_resource
def load_model():
    return YOLO('best.pt')

model = load_model()

uploaded_file = st.file_uploader("Analiz etmek istediğiniz ürünün fotoğrafını yükleyin", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Yüklenen Fotoğraf", use_column_width=True)
    st.write("🔄 Görüntü işleniyor ve analiz ediliyor...")
    
    results = model(image, conf=0.20)
    BOZUK_ETIKETI = 'bozuk_kısım'
    
    for result in results:
        boxes = result.boxes
        toplam_meyve_alani = 0
        toplam_bozuk_alan = 0
        tespit_edilen_urunler = []
        
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            alan = (x2 - x1) * (y2 - y1)
            
            sinif_id = int(box.cls[0])
            sinif_adi = model.names[sinif_id]
            
            # Domates/Elma Hack'i
            if sinif_adi == 'domates':
                sinif_adi = 'elma'
            elif sinif_adi == 'elma':
                sinif_adi = 'domates'
            
            if sinif_adi == BOZUK_ETIKETI:
                toplam_bozuk_alan += alan
            else:
                toplam_meyve_alani += alan
                if sinif_adi not in tespit_edilen_urunler:
                    tespit_edilen_urunler.append(sinif_adi)
        
        st.markdown("---")
        st.subheader("📊 Analiz Sonuçları")
        
        if len(tespit_edilen_urunler) > 0:
            urun_ismi = ", ".join(tespit_edilen_urunler).upper()
            bozukluk_orani = (toplam_bozuk_alan / toplam_meyve_alani) * 100
            if bozukluk_orani > 100: bozukluk_orani = 100.0
            
            col1, col2 = st.columns(2)
            col1.metric("Tespit Edilen Ürün", urun_ismi)
            col2.metric("Hesaplanan Bozukluk Oranı", f"%{bozukluk_orani:.1f}")
            
            st.subheader("💡 Döngüsel Aksiyon Önerisi")
            if bozukluk_orani <= 10.0:
                st.success("**Aksiyon: Taze Tüketim / İleri Dönüşüm**")
                st.write(f"{urun_ismi.capitalize()} oldukça taze. Zedelenen kısmı kesip smoothie yapımında değerlendirebilirsiniz.")
            elif bozukluk_orani <= 40.0:
                st.warning("**Aksiyon: Koruma ve Değer Değişimi (Upcycling)**")
                st.write("Orta düzeyde bozulma. Reçel, marmelat veya turşu gibi ısıl/fermente işlemlerle sisteme geri kazandırabilirsiniz.")
            else:
                st.error("**Aksiyon: Organik Atık Yönetimi / Mikro-Kompostlama**")
                st.write("İleri derece bozulma. Çöpe atmak yerine evsel mikro-kompost süreçlerine yönlendirerek toprağa kazandırabilirsiniz.")
                
        elif toplam_bozuk_alan > 0:
            st.info("Sadece hasarlı bölge algılandı, ana ürün tespit edilemedi.")
        else:
            st.info("Net bir ürün veya bozulma tespit edilemedi.")
            
        st.markdown("---")
        st.write("🔍 **Yapay Zeka Tespit Görüntüsü**")
        res_plotted = result.plot()[:, :, ::-1]
        st.image(res_plotted, caption="Tespit Edilen Alanlar", use_column_width=True)
