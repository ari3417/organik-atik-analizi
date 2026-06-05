import streamlit as st
from ultralytics import YOLO
from PIL import Image
import os

# 1. Sayfa Ayarları
st.set_page_config(page_title="Rescue Scanner & Coach", page_icon="♻️", layout="centered")

# --- ÖZEL CSS (Renkli Bloklar ve Tasarım İçin) ---
st.markdown("""
<style>
    .recipe-card {
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: #333333;
    }
    .bg-purple { background-color: #B5B2E5; color: white;}
    .bg-pink { background-color: #FFB7B2; color: #333;}
    .bg-blue { background-color: #AEC6CF; color: #333;}
    .bg-mint { background-color: #B2E2D4; color: #333;}
    
    .recipe-title { font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .ingredient-list { font-size: 18px; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

# 2. LOGO YÜKLEME (En Üstte)
# Eğer logo.png dosyası dizinde varsa göster
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
else:
    st.title("🌱 RESCUE SCANNER & COACH")

# Modeli yükleme
@st.cache_resource
def load_model():
    return YOLO('best.pt')

model = load_model()

# 3. Sekmelerin (Tabs) Oluşturulması
tab1, tab2, tab3 = st.tabs(["📸 Kurtarma Tarayıcısı", "🍂 Kompost Modu", "📖 Eğitim Desteği"])

# ==========================================
# SEKME 1: AYRIŞTIRMA VE TARİFLER
# ==========================================
with tab1:
    st.markdown("### 🔍 Kurtarılacak Ürünü Tarayın")
    st.write("Yumuşamış veya hasar görmüş meyvenizin fotoğrafını yükleyin, sistem onu tanıyıp size özel harika bir sıfır atık tarifi sunsun.")
    
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="scanner")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        st.write("🔄 Yapay zeka görüntüyü işliyor...")
        results = model(image, conf=0.20)
        
        tespit_edilen_urunler = []
        
        for result in results:
            for box in result.boxes:
                sinif_id = int(box.cls[0])
                sinif_adi = model.names[sinif_id]
                if sinif_adi == 'domates': sinif_adi = 'elma'
                elif sinif_adi == 'elma': sinif_adi = 'domates'
                
                if sinif_adi != 'bozuk_kısım' and sinif_adi not in tespit_edilen_urunler:
                    tespit_edilen_urunler.append(sinif_adi)
            
            # Kutu çizilmiş resmi göster
            st.image(result.plot()[:, :, ::-1], caption="AI Tespiti", use_container_width=True)

        st.markdown("---")
        
        # --- DİNAMİK YAPAY ZEKA TARİFLERİ ---
        if "portakal" in tespit_edilen_urunler:
            st.markdown("""
            <div class="recipe-card bg-purple">
                <div class="recipe-title">🍊 Sihirli Portakal Kabuğu Şekerlemesi</div>
                <div class="ingredient-list">
                    <b>Malzemeler:</b><br>
                    🔪 3 Adet Portakalın Kabuğu<br>
                    🧊 2 Su Bardağı Şeker<br>
                    💧 1 Su Bardağı Su<br>
                    🍋 Çeyrek Limon Suyu
                </div>
                <hr>
                <b>Adımlar:</b>
                <ul>
                    <li>Portakal kabuklarını ince uzun şeritler halinde doğrayın.</li>
                    <li>Acısını almak için suda 3 kez kaynatıp süzün.</li>
                    <li>Şeker ve su ile hazırladığınız şerbette kabukları şeffaflaşana kadar kaynatın.</li>
                    <li>Son olarak limon suyunu ekleyip yağlı kağıda dizerek kurutun.</li>
                </ul>
                <b>🎉 Sonuç:</b> Çay ve kahvenin yanında tüketebileceğiniz harika sıfır atık atıştırmalıklar!
            </div>
            """, unsafe_allow_html=True)
            st.video("https://www.youtube.com/watch?v=R9_uQJ8_s5A") # Örnek YouTube Linki

        elif "muz" in tespit_edilen_urunler:
            st.markdown("""
            <div class="recipe-card bg-pink">
                <div class="recipe-title">🍌 Rafinesiz Muzlu Vegan Dondurma</div>
                <div class="ingredient-list">
                    <b>Malzemeler:</b><br>
                    🍌 2 Adet Kararmış (Çok Olgun) Muz<br>
                    🥜 1 Yemek Kaşığı Fıstık Ezmesi<br>
                    🍫 1 Tatlı Kaşığı Kakao<br>
                    🥛 Yarım Çay Bardağı Süt (veya Bitkisel Süt)
                </div>
                <hr>
                <b>Adımlar:</b>
                <ul>
                    <li>Kararmış muzların kabuklarını soyup dilimleyin ve dondurucuda 4 saat dondurun.</li>
                    <li>Donmuş muzları blender'a alın.</li>
                    <li>Üzerine fıstık ezmesi, kakao ve sütü ekleyip kremsi bir kıvam alana kadar çekin.</li>
                    <li>Hemen tüketin veya tekrar dondurun.</li>
                </ul>
                <b>🎉 Sonuç:</b> Sıfır şekerli, suçluluk hissettirmeyen sağlıklı tatlı!
            </div>
            """, unsafe_allow_html=True)
            st.video("https://www.youtube.com/watch?v=Jb-i-uL5cOE")
            
        elif "elma" in tespit_edilen_urunler:
            st.markdown("""
            <div class="recipe-card bg-mint">
                <div class="recipe-title">🍏 Probiyotik Elma Kabuğu Sirkesi</div>
                <div class="ingredient-list">
                    <b>Malzemeler:</b><br>
                    🍎 Tüketilmeyecek elma kabukları ve çekirdekleri<br>
                    💧 1 Litre İçme Suyu<br>
                    🍯 1 Yemek Kaşığı Bal veya Şeker<br>
                    🫙 1 Büyük Cam Kavanoz
                </div>
                <hr>
                <b>Adımlar:</b>
                <ul>
                    <li>Kavanozun yarısına kadar elma artıklarını doldurun.</li>
                    <li>Üzerine suyu ve tatlandırıcıyı ekleyip tahta kaşıkla karıştırın.</li>
                    <li>Üzerini temiz bir tülbentle kapatıp (hava almalı) karanlık bir yerde saklayın.</li>
                    <li>İlk 10 gün her gün karıştırın. 20 gün sonra süzün.</li>
                </ul>
                <b>🎉 Sonuç:</b> Ev yapımı, bağışıklık güçlendirici %100 doğal sirke!
            </div>
            """, unsafe_allow_html=True)
            st.video("https://www.youtube.com/watch?v=e_5aWvJ6d1c")

    # --- SABİT (HER ZAMAN GÖRÜNEN) GENEL TARİFLER ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📚 Fotoğraf Yüklemeden Yapabileceğiniz Klasikler")
    st.markdown("Evinizde birikmeye başlayan her türlü sebze ve meyve için hayat kurtaran, uzun ömürlü temel teknikler.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="recipe-card bg-blue" style="height: 450px;">
            <div class="recipe-title">🥒 Hızlı Turşu Kurulumu</div>
            <p>Hafif pörsümüş her türlü sebzeyi (salatalık, havuç, lahana) kurtarın.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🫙 Cam Kavanoz<br>
                🧅 Sarımsak & Nohut<br>
                🧂 2 YK Kaya Tuzu<br>
                🥃 1 Çay Bardağı Sirke<br>
                💧 Kaynar Su
            </div><br>
            <p><b>Yapılışı:</b> Sebzeleri sıkıca dizin. Tuzu, sirkeyi ekleyip üzerine kaynar suyu dökün. Kapağı sıkıca kapatıp ters çevirin. 10 günde hazır!</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="recipe-card bg-pink" style="height: 450px;">
            <div class="recipe-title">🍓 Evrensel Meyve Reçeli</div>
            <p>Yumuşamış ve taze yenmeyecek tüm meyveler için standart formül.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🍑 1 Ölçü Meyve<br>
                🍚 1 Ölçü Şeker<br>
                🍋 Çeyrek Limon Suyu
            </div><br>
            <br>
            <p><b>Yapılışı:</b> Meyveleri doğrayıp akşamdan şekerle bekletin. Sabah kendi suyuyla kıvam alana kadar kaynatın. Kapatmadan hemen önce limon suyunu ekleyin.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# SEKME 2: KOMPOST MODU
# ==========================================
with tab2:
    st.header("Evaluate & Redirect (Kompost Modu)")
    st.markdown("Kompost dengenizi kontrol edin ve organik atıklarınızın olgunlaşma durumunu analiz edin.")
    
    atilan_malzeme = st.selectbox("Komposta eklenecek ağırlıklı malzeme türü nedir?", ["Meyve/Sebze Kabukları (Yeşil - Azot)", "Kuru Yaprak/Karton (Kahverengi - Karbon)", "Kahve Telvesi (Yeşil - Azot)"])
    
    if "Yeşil" in atilan_malzeme:
        st.warning("Hızlı çürüyen 'Yeşil' malzeme ekliyorsunuz. Dengeyi sağlamak için üzerine mutlaka talaş, kuru yaprak veya parçalanmış karton gibi 'Kahverengi' malzeme eklemelisiniz.")
    else:
        st.success("Kuru 'Kahverengi' malzeme ekliyorsunuz. Bu, kompostun hava almasını ve koku yapmamasını sağlayacaktır.")
        
    st.write("**Tahmini Bekleme Süresi:** Ev tipi soğuk kompost için yaklaşık **3 ila 6 ay**.")
    
    compost_file = st.file_uploader("Kompostunuzun son durumunu fotoğraflayın", type=["jpg", "jpeg", "png"], key="compost")
    if compost_file is not None:
        c_image = Image.open(compost_file)
        st.image(c_image, use_container_width=True)
        st.info("*Sistem Notu: Kompost Görüntü İşleme Modeli (v2.0) geliştirme aşamasındadır.*")

# ==========================================
# SEKME 3: EĞİTİM DESTEĞİ
# ==========================================
with tab3:
    st.header("Learn & Coach")
    st.markdown("Gönüllü eğitim rehberi ve döngüsel ekonomi bilgi bankası.")
    
    st.markdown("""
    ### ♻️ Neden Ayrıştırıyoruz?
    Gıda atıkları çöpe gidip oksijensiz ortamda çürüdüklerinde, karbondioksitten 25 kat daha zararlı olan metan gazı üretirler. Amacımız, gıdayı atık olmadan yakalamaktır.
    
    ### ⚖️ Altın Kural: Kompost Dengesi (C:N Oranı)
    Sağlıklı bir kompost için **Karbon (Kahverengi) / Azot (Yeşil)** oranı çok önemlidir. 
    Hacimsel olarak ortalama **%60 Kahverengi, %40 Yeşil** malzeme kuralını uygulayın.
    
    * **🟢 Yeşiller (Nem ve Azot kaynağı):** Meyve sebze artıkları, taze çimen, kahve telvesi, çay yaprakları.
    * **🟤 Kahverengiler (Hava ve Karbon kaynağı):** Kuru yapraklar, dal parçaları, tuvalet kağıdı ruloları, yumurta kartonları, talaş.
    
    ### ❌ Komposta Asla Atılmaması Gerekenler
    * Et, kemik ve balık ürünleri (Patojen ve haşere çeker).
    * Süt ürünleri (Peynir, yoğurt).
    * Yağlı ve soslu yemek artıkları.
    * Kedi/Köpek dışkısı.
    """)
