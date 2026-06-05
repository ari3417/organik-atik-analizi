import streamlit as st
from ultralytics import YOLO
from PIL import Image
import os
import base64
from io import BytesIO

# 1. Sayfa Ayarları
st.set_page_config(page_title="Rescue Scanner & Coach", page_icon="♻️", layout="centered")

# Görselleri HTML içine gömebilmek için dönüştürücü fonksiyon
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- ÖZEL CSS (Tamamen Yeni Tasarım İçin) ---
st.markdown("""
<style>
    /* Sabit Tarif Kartları */
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

    /* Fotoğraf üstüne binen Sekmeler (Tabs) */
    [data-testid="stImage"] {
        margin-bottom: -55px; /* Sekmeleri fotoğrafın üstüne çeker */
        position: relative;
        z-index: 1;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 15px;
        position: relative;
        z-index: 99;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 20px !important;
        border: 3px solid white !important;
        padding: 10px 25px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15) !important;
        color: #333 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }
    /* Sekme Renkleri */
    [data-testid="stTabs"] [data-baseweb="tab"]:nth-child(1) { background-color: #B2E2D4 !important; }
    [data-testid="stTabs"] [data-baseweb="tab"]:nth-child(2) { background-color: #FFD580 !important; }
    [data-testid="stTabs"] [data-baseweb="tab"]:nth-child(3) { background-color: #FFB7B2 !important; }

    /* Fotoğraf Yükleme Butonu Özelleştirmesi */
    [data-testid="stFileUploader"] section {
        background-color: #A8C9B4 !important;
        border: 2px solid #333 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"] section > div > span {
        display: none !important; /* Sürükle bırak metnini gizle */
    }
    [data-testid="stFileUploader"] small {
        display: none !important; /* Limit metnini gizle */
    }

    /* Hardal Sarısı Görüntü Kutuları */
    .mustard-box {
        background-color: #E2A600;
        border: 2px solid #5A4D2E;
        border-radius: 10px;
        padding: 10px;
        height: 100%;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #333;
        font-weight: bold;
        text-align: center;
    }
    .mustard-box img {
        max-width: 100%;
        border-radius: 5px;
        border: 1px solid rgba(0,0,0,0.2);
    }

    /* Aksiyon Planı Banner'ı */
    .action-banner {
        background-color: #9A9B7A;
        color: white;
        text-align: right;
        padding: 12px 25px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 0px 0px 10px 10px;
        margin-top: 10px;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# 2. LOGO YÜKLEME
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
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Üst Panel: Sol Yazı/Buton, Sağ İki Sarı Kutu
    col1, col2, col3 = st.columns([1.2, 1, 1], gap="small")
    
    with col1:
        st.markdown("""
        <div style="font-family: 'Arial Black', sans-serif; font-size: 42px; color: #A8C9B4; line-height: 1; margin-bottom: 20px; letter-spacing: -1px;">
            KURTARILACAK<br>ÜRÜNÜ TARAYIN
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="scanner", label_visibility="collapsed")
        
        st.markdown("""
        <div style="font-size: 14px; color: #555; margin-top: 15px; line-height: 1.4;">
            Yumuşamış veya hasar görmüş meyvenizin fotoğrafını yükleyin, sistem onu tanıyıp size özel harika bir sıfır atık tarifi sunsun.
        </div>
        """, unsafe_allow_html=True)

    # İşlem Mantığı ve Görsel Yerleşimi
    if uploaded_file is None:
        # Fotoğraf yüklenmediyse boş sarı kutuları göster
        with col2:
            st.markdown('<div class="mustard-box">Seçilen fotoğraf</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="mustard-box">AI Taraması</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="action-banner">AKSİYON PLANI (HASAR ORANI: - )</div>', unsafe_allow_html=True)

    else:
        # Fotoğraf Yüklendiğinde
        image = Image.open(uploaded_file)
        img_b64 = image_to_base64(image)
        
        st.write("🔄 Yapay zeka görüntüyü işliyor...")
        results = model(image, conf=0.20)
        
        toplam_meyve_alani = 0
        toplam_bozuk_alan = 0
        tespit_edilen_urunler = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                alan = (x2 - x1) * (y2 - y1)
                
                sinif_id = int(box.cls[0])
                sinif_adi = model.names[sinif_id]
                
                if sinif_adi == 'bozuk_kısım':
                    toplam_bozuk_alan += alan
                else:
                    toplam_meyve_alani += alan
                    if sinif_adi not in tespit_edilen_urunler:
                        tespit_edilen_urunler.append(sinif_adi)
            
            # AI Tespitli görüntüyü base64'e çevirme
            res_plotted = result.plot()[:, :, ::-1]
            res_img = Image.fromarray(res_plotted)
            res_b64 = image_to_base64(res_img)
            
            # Dolu Sarı Kutular
            with col2:
                st.markdown(f'''
                <div class="mustard-box">
                    <div style="margin-bottom:10px;">Seçilen fotoğraf</div>
                    <img src="data:image/png;base64,{img_b64}">
                </div>
                ''', unsafe_allow_html=True)
            with col3:
                st.markdown(f'''
                <div class="mustard-box">
                    <div style="margin-bottom:10px;">AI Taraması</div>
                    <img src="data:image/png;base64,{res_b64}">
                </div>
                ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- MATEMATİK VE AKSİYON PLANI ---
        if len(tespit_edilen_urunler) > 0:
            urun_ismi = ", ".join(tespit_edilen_urunler).upper()
            bozukluk_orani = (toplam_bozuk_alan / toplam_meyve_alani) * 100 if toplam_meyve_alani > 0 else 100
            if bozukluk_orani > 100: bozukluk_orani = 100.0
            
            # Alt Banner
            st.markdown(f'<div class="action-banner">AKSİYON PLANI (HASAR ORANI: %{bozukluk_orani:.1f})</div><br>', unsafe_allow_html=True)
            
            if bozukluk_orani <= 5.0:
                st.success("**Kategori: Doğrudan Yeniden Dağıtım (Taze Tüketim)**")
                st.write("Ürün kusursuz veya kusura çok yakın. Taze olarak tüketime veya gıda bankalarına gönderilmeye tamamen uygundur.")
                
            elif bozukluk_orani <= 45.0:
                st.warning("**Kategori: Yenilebilir Geri Kazanım (Sıfır Atık İleri Dönüşüm)**")
                st.write("Hasarlı kısımları kestikten sonra kalan temiz bölümlerle maksimum verim elde edebileceğiniz tarifler:")
                
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
                    </div>
                    """, unsafe_allow_html=True)
                    st.video("https://www.youtube.com/watch?v=lhbUMg1Swbo") 

                elif "muz" in tespit_edilen_urunler:
                    st.markdown("""
                    <div class="recipe-card bg-pink">
                        <div class="recipe-title">🍌 Rafinesiz Muzlu Vegan Dondurma</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍌 2 Adet Kararmış (Çok Olgun) Muz<br>
                            🥜 1 Yemek Kaşığı Fıstık Ezmesi<br>
                            🍫 1 Tatlı Kaşığı Kakao<br>
                            🥛 Yarım Çay Bardağı Süt
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Kararmış muzların kabuklarını soyup dilimleyin ve dondurucuda 4 saat dondurun.</li>
                            <li>Donmuş muzları blender'a alın.</li>
                            <li>Üzerine fıstık ezmesi, kakao ve sütü ekleyip kremsi bir kıvam alana kadar çekin.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.video("https://www.youtube.com/watch?v=HYQaK-6-9L4")
                    
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
                            <li>İlk 10 gün her gün karıştırın. 20 gün sonra süzün.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.video("https://www.youtube.com/watch?v=eE0I39eGMQA")
                    
            elif bozukluk_orani <= 80.0:
                st.error("**Kategori: Kompost (Organik Gübre)**")
                st.write(f"Bu {urun_ismi.lower()} tüketim limitlerini aşmış durumda. Lütfen 'Kompost Modu' sekmesine geçerek bu ürünü toprağa nasıl geri kazandıracağınızı öğrenin.")
            else:
                st.error("**Kategori: Güvenli Olmayan Atık**")
                st.write("Aşırı çürüme veya küflenme tespit edildi. Standart yığın kompostuna atmak patojen riski taşıyabilir. Kahverengi çöp kutusuna atın.")

        elif toplam_bozuk_alan > 0:
            st.info("Sistem sadece hasarlı bölgeyi algıladı ancak meyvenin türünü (elma, muz vb.) net olarak tanıyamadığı için özel bir tarif sunamıyor.")
        else:
            st.info("Sistem bu fotoğrafta net bir ürün tanıyamadı.")

    # --- SABİT (HER ZAMAN GÖRÜNEN) GENEL TARİFLER ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📚 Fotoğraf Yüklemeden Yapabileceğiniz Klasikler")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="recipe-card bg-blue">
            <div class="recipe-title">🥒 Hızlı Turşu Kurulumu</div>
            <p>Hafif pörsümüş her türlü sebzeyi kurtarın.</p>
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
        <div class="recipe-card bg-pink">
            <div class="recipe-title">🍓 Evrensel Meyve Reçeli</div>
            <p>Yumuşamış tüm meyveler için standart formül.</p>
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
    st.markdown("<br>", unsafe_allow_html=True)
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
    st.markdown("<br>", unsafe_allow_html=True)
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
