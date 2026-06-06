import streamlit as st
from ultralytics import YOLO
from PIL import Image
import os
import base64
from io import BytesIO

# 1. Sayfa Ayarları
st.set_page_config(page_title="Gıda Kurtarma Tarayıcısı & Rehberi", page_icon="♻️", layout="centered")

# Görselleri HTML içine gömebilmek için dönüştürücü fonksiyon
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- ÖZEL CSS (Renkli Bloklar ve Tasarım İçin) ---
st.markdown("""
<style>
    /* Sabit Tarif Kartları */
    .recipe-card {
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: #333333;
        height: 100%;
    }
    .bg-purple { background-color: #B5B2E5; color: white;}
    .bg-pink { background-color: #FFB7B2; color: #333;}
    .bg-blue { background-color: #AEC6CF; color: #333;}
    .bg-mint { background-color: #B2E2D4; color: #333;}
    .recipe-title { font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .ingredient-list { font-size: 16px; line-height: 1.8; }

    /* Fotoğraf üstüne binen Sekmeler (Tabs) */
    [data-testid="stImage"] {
        margin-bottom: -55px; 
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
        display: none !important; 
    }
    [data-testid="stFileUploader"] small {
        display: none !important; 
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
    st.title("🌱 GIDA KURTARMA TARAYICISI & REHBERİ")

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
    
    # Üst Panel: Tam genişlikte başlık ve yükleme alanı
    st.markdown("""
    <div style="font-family: 'Arial Black', sans-serif; font-size: 42px; color: #A8C9B4; line-height: 1; margin-bottom: 20px; letter-spacing: -1px; text-align: center;">
        KURTARILACAK ÜRÜNÜ TARAYIN
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="scanner", label_visibility="collapsed")
    
    st.markdown("""
    <div style="font-size: 14px; color: #555; margin-top: 15px; margin-bottom: 10px; line-height: 1.4; text-align: center;">
        Yumuşamış veya hasar görmüş meyvenizin fotoğrafını yükleyin, sistem onu tanıp size özel harika bir sıfır atık tarifi sunsun.
    </div>
    """, unsafe_allow_html=True)

    # --- ÖRNEK FOTOĞRAF GALERİSİ BAŞLANGICI ---
    if "secilen_ornek" not in st.session_state:
        st.session_state.secilen_ornek = None

    ornek_kategoriler = {
        "🥀 Çürümüş (Kompostluk)": [
            "curumus_elma.png", "curumus_muz.png", "curumus_portakal.png", "curumus_domates.jpg", "curumus_salatalik.png"
        ],
        "🤕 Kurtarılabilir (Tariflik)": [
            "kurtarilabilecek_elma.png", "kurtarilabilecek_muz.png", "kurtarilabilecek_portakal.png", "kurtarilabilecek_domates.jpg", "kurtarilabilecek_salatalik.png"
        ],
        "✨ Taze (Doğrudan Tüketim)": [
            "taze_elma.png", "taze_muz.png", "taze_portakal.png", "taze_domates.png", "taze_salatalik.png"
        ]
    }

    st.markdown("<p style='text-align:center; font-size:16px; font-weight:bold; color:#A8C9B4; margin-bottom:15px;'>Deneyebileceğiniz Test Fotoğrafları:</p>", unsafe_allow_html=True)

    for kategori_adi, fotolar in ornek_kategoriler.items():
        mevcut_fotolar = [f for f in fotolar if os.path.exists(f)]
        if mevcut_fotolar:
            st.markdown(f"<p style='font-size:14px; font-weight:bold; color:#555; margin-bottom:5px; margin-top:10px;'>{kategori_adi}</p>", unsafe_allow_html=True)
            galeri_kolonlari = st.columns(len(mevcut_fotolar))
            for i, ornek_foto in enumerate(mevcut_fotolar):
                with galeri_kolonlari[i]:
                    st.image(ornek_foto, use_container_width=True)
                    if st.button("👆 Seç", key=f"sec_{ornek_foto}", use_container_width=True):
                        st.session_state.secilen_ornek = ornek_foto
                    
    st.markdown("<br>", unsafe_allow_html=True)
    # --- ÖRNEK FOTOĞRAF GALERİSİ BİTİŞİ ---

    # Alt Panel: İki büyük sarı kutu
    col1, col2 = st.columns(2, gap="large")

    # İşlenecek Görüntü Mantığı (Kullanıcı kendi mi yükledi, yoksa örnek mi seçti?)
    islenecek_resim = None
    if uploaded_file is not None:
        islenecek_resim = Image.open(uploaded_file)
        st.session_state.secilen_ornek = None # Kendisi yüklerse örnek seçimi sıfırla
    elif st.session_state.secilen_ornek is not None:
        islenecek_resim = Image.open(st.session_state.secilen_ornek)

    # Görüntü Kutuları Yönetimi
    if islenecek_resim is None:
        with col1:
            st.markdown('<div class="mustard-box">Seçilen fotoğraf</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="mustard-box">AI Taraması</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="action-banner">AKSİYON PLANI (HASAR ORANI: - )</div>', unsafe_allow_html=True)

    else:
        image = islenecek_resim
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
            
            res_plotted = result.plot()[:, :, ::-1]
            res_img = Image.fromarray(res_plotted)
            res_b64 = image_to_base64(res_img)
            
            with col1:
                st.markdown(f'''
                <div class="mustard-box">
                    <div style="margin-bottom:10px;">Seçilen fotoğraf</div>
                    <img src="data:image/png;base64,{img_b64}">
                </div>
                ''', unsafe_allow_html=True)
            with col2:
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
                    
                    st.markdown("""
                    <div class="recipe-card bg-purple">
                        <div class="recipe-title">🍊 Doğal Yüzey Temizleyici Sirke</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍊 Sıkılmış portakal/limon kabukları<br>
                            🥃 Beyaz Sirke<br>
                            🫙 Büyük Cam Kavanoz
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Kullanılmış narenciye kabuklarını kavanoza ağzına kadar doldurun.</li>
                            <li>Üzerini tamamen geçecek kadar beyaz sirke ekleyin ve kapağını sıkıca kapatın.</li>
                            <li>2 hafta boyunca karanlık bir dolapta bekletip süzün.</li>
                            <li>Sprey şişesine alıp yarı yarıya suyla seyrelterek mutfak tezgahlarında kullanın!</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if "muz" in tespit_edilen_urunler:
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
                    
                    st.markdown("""
                    <div class="recipe-card bg-pink">
                        <div class="recipe-title">🍌 Muz Kabuğu Sıvı Bitki Gübresi</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍌 Tüketilmiş muzların kabukları<br>
                            💧 1 Litre İçme Suyu<br>
                            🫙 Geniş Cam Kavanoz
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Muz kabuklarını makasla küçük parçalar halinde doğrayın.</li>
                            <li>Kavanoza alıp üzerine suyu ekleyin ve kapağını kapatın.</li>
                            <li>24-48 saat oda sıcaklığında bekletin.</li>
                            <li>Bu potasyum zengini suyu süzerek ev bitkilerinizi sulamak için kullanın (Kalan kabukları komposta atın!).</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                if "elma" in tespit_edilen_urunler:
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
                    
                    st.markdown("""
                    <div class="recipe-card bg-mint">
                        <div class="recipe-title">🍏 Tarçınlı Fırın Elma Cipsi</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍎 Yumuşamış elmalar<br>
                            🍂 Toz Tarçın<br>
                            🍋 Çeyrek Limonun Suyu
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Elmaları kararmaması için limonlu suda bekleterek çok ince halkalar halinde dilimleyin.</li>
                            <li>Yağlı kağıt serili tepsiye dizip üzerlerine tarçın serpin.</li>
                            <li>100 derece fırında iyice kuruyana kadar (yaklaşık 1.5 - 2 saat) pişirin.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if "domates" in tespit_edilen_urunler:
                    st.markdown("""
                    <div class="recipe-card bg-pink">
                        <div class="recipe-title">🍅 Fırınlanmış Konsantre Domates Sosu</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍅 Yumuşamış domatesler<br>
                            🫒 3 Yemek Kaşığı Zeytinyağı<br>
                            🧄 2 Diş Sarımsak<br>
                            🌿 Kekik ve Tuz
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Domatesleri iri parçalara bölün ve fırın tepsisine dizin.</li>
                            <li>Üzerine zeytinyağı, sarımsak ve baharatları gezdirin.</li>
                            <li>200 derece fırında suları hafif çekip karamelize olana kadar pişirin.</li>
                            <li>Fırından çıkınca blenderdan geçirip kavanozlayın.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if "salatalık" in tespit_edilen_urunler:
                    st.markdown("""
                    <div class="recipe-card bg-blue">
                        <div class="recipe-title">🥒 Sıfır Atık Detoks & Cilt Toniği</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🥒 Pörsümüş salatalık ve sap kısımları<br>
                            🍋 Yarım Limon<br>
                            🌿 Taze Nane<br>
                            💧 İçme Suyu
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Salatalığın orta kısımlarını halka doğrayıp limon ve nane ile sürahiye atın (İçme suyu için).</li>
                            <li>Tüketilmeyen uç kısımlarını ve kabuklarını blenderdan geçirin.</li>
                            <li>Çıkan saf salatalık suyunu süzüp buz kalıplarına dondurun.</li>
                            <li>Sabahları yüzünüzde gezdirerek doğal tonik olarak kullanın!</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                # KOMPOST POTANSİYELİ HESAPLAYICI
                if bozukluk_orani > 0:
                    tahmini_atik_gr = int((bozukluk_orani / 100) * 150) 
                    tahmini_gubre_gr = int(tahmini_atik_gr * 0.4) 
                    if tahmini_atik_gr > 0:
                        st.markdown(f"""
                        <div style="background-color: #E8F5E9; border: 2px solid #4CAF50; padding: 20px; border-radius: 15px; margin-top: 20px; color: #2E7D32;">
                            <h4 style="margin-top:0px; margin-bottom: 10px; color: #2E7D32;">🌱 Kesilen Çürükler İçin Kompost Potansiyeli</h4>
                            <span style="font-size: 16px; line-height: 1.6;">
                                Yukarıdaki tarifleri uygularken kestiğiniz <b>%{bozukluk_orani:.1f}</b>'lik hasarlı kısım (ortalama bir porsiyon meyvede yaklaşık <b>{tahmini_atik_gr} gram</b> organik atığa denk gelir) çöpe gitmek yerine kompost kutunuza eklendiğinde, bitkileriniz için <b>~{tahmini_gubre_gr} gram</b> besin değeri yüksek, saf organik gübreye (humus) dönüşecektir. Lütfen bu kısımları çöpe değil, toprağa kazandırın!
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

            elif bozukluk_orani <= 80.0:
                st.error("**Kategori: Kompost (Organik Gübre)**")
                st.write(f"Bu {urun_ismi.lower()} tüketim limitlerini aşmış durumda. Lütfen 'Kompost Modu' sekmesine geçerek bu ürünü toprağa nasıl geri kazandıracağınızı öğrenin.")
            else:
                st.error("**Kategori: Güvenli Olmayan Atık**")
                st.write("Aşırı çürüme veya küflenme tespit edildi. Standart yığın kompostuna atmak patojen riski taşıyabilir. Kahverengi çöp kutusuna atın.")

        elif toplam_bozuk_alan > 0:
            st.info("Sistem sadece hasarlı bölgeyi algıladı ancak meyvenin türünü net olarak tanıyamadığı için özel bir tarif sunamıyor.")
        else:
            st.info("Sistem bu fotoğrafta net bir ürün tanıyamadı.")

    # --- SABİT (HER ZAMAN GÖRÜNEN) GENEL TARİFLER ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📚 Fotoğraf Yüklemeden Yapabileceğiniz Klasikler")
    st.markdown("Evinizde birikmeye başlayan meyve ve sebzeler için israfı önleyen, uzun ömürlü temel teknikler.")
    
    # SATIR 1
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("""
        <div class="recipe-card bg-blue">
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
        
    with row1_col2:
        st.markdown("""
        <div class="recipe-card bg-pink">
            <div class="recipe-title">🍓 Evrensel Meyve Reçeli</div>
            <p>Yumuşamış ve taze yenmeyecek tüm meyveler için standart formül.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🍑 1 Ölçü Meyve<br>
                🍚 1 Ölçü Şeker<br>
                🍋 Çeyrek Limon Suyu
            </div><br>
            <p><b>Yapılışı:</b> Meyveleri doğrayıp akşamdan şekerle bekletin. Sabah kendi suyuyla kıvam alana kadar kaynatın. Kapatmadan hemen önce limon suyunu ekleyin.</p>
        </div>
        """, unsafe_allow_html=True)

    # SATIR 2
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown("""
        <div class="recipe-card bg-mint">
            <div class="recipe-title">🍵 Atık Sebze Suyu (Bulyon)</div>
            <p>Yemek yaparken ayırdığınız yıkanmış sebze kabuklarını ve köklerini değerlendirin.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🥬 Biriktirilmiş Sebze Artıkları (Havuç ucu, soğan kabuğu vb.)<br>
                💧 2 Litre Su<br>
                🧄 3 Diş Sarımsak<br>
                🌿 Defne Yaprağı & Karabiber
            </div><br>
            <p><b>Yapılışı:</b> Tüm malzemeleri tencereye alın. 1 saat kaynatın. Süzüp kavanozlayın ve buzdolabına kaldırın. Çorba ve pilavlarda bulyon olarak kullanın.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with row2_col2:
        st.markdown("""
        <div class="recipe-card bg-purple">
            <div class="recipe-title">🥔 Baharatlı Kabuk Cipsi</div>
            <p>Soyduğunuz patates, havuç ve elma kabuklarını çöpe atmak yerine çıtır bir atıştırmalığa dönüştürün.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🥕 Kalın soyulmuş sebze/meyve kabukları<br>
                🫒 2 Yemek Kaşığı Zeytinyağı<br>
                🧂 Tuz ve Karabiber<br>
                🌶️ Toz Kırmızı Biber
            </div><br>
            <p><b>Yapılışı:</b> Kabukları yıkayıp iyice kurulayın. Yağ ve baharatlarla harmanlayıp yağlı kağıt serili tepsiye dizin. 180° fırında 10-15 dk çıtırlaşana kadar pişirin.</p>
        </div>
        """, unsafe_allow_html=True)

    # SATIR 3
    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.markdown("""
        <div class="recipe-card bg-pink">
            <div class="recipe-title">🌿 Solmuş Yeşillik Pesto Sosu</div>
            <p>Formunu kaybetmiş taze otları veya turp/havuç saplarını harika bir makarna sosuna çevirin.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🥬 Pörsümüş yeşillikler (maydanoz, fesleğen, roka)<br>
                🫒 Yarım Çay Bardağı Zeytinyağı<br>
                🧄 2 Diş Sarımsak<br>
                🥜 Ceviz veya Fındık
            </div><br>
            <p><b>Yapılışı:</b> Bütün malzemeleri mutfak robotuna alın. Pürüzsüz bir sos kıvamına gelene kadar çekin. Cam kavanozda üzerine zeytinyağı dökerek dolapta 1 hafta saklayabilirsiniz.</p>
        </div>
        """, unsafe_allow_html=True)

    with row3_col2:
        st.markdown("""
        <div class="recipe-card bg-blue">
            <div class="recipe-title">☕ Kurutulmuş Meyve Çayı</div>
            <p>Yenmeyen elma, armut, ayva kabuklarını ve portakal dilimlerini kış çayı yapmak için değerlendirin.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🍎 Temiz meyve kabukları ve çekirdek yuvaları<br>
                🍂 Çubuk Tarçın<br>
                🌸 Karanfil<br>
                💧 Kaynar Su
            </div><br>
            <p><b>Yapılışı:</b> Kabukları fırında veya kış güneşi gören bir yerde tamamen kurutun. İhtiyacınız olduğunda demliğe bir avuç atıp üzerine sıcak su, tarçın ve karanfil ekleyerek 10 dk demlendirin.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# SEKME 2: KOMPOST MODU
# ==========================================
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("Değerlendir & Yönlendir (Kompost Modu)")
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
    st.header("Öğren & Rehberlik Et (Eğitim Desteği)")
    st.markdown("Gönüllü eğitim rehberi, sıfır atık pratikleri ve döngüsel ekonomi bilgi bankası.<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="recipe-card bg-mint">
        <div class="recipe-title">♻️ Sıfır Atık Felsefesi ve Ayrıştırmanın Önemi</div>
        <div class="ingredient-list">
        <b>Neden Gıdayı Çöpe Atmamalıyız?</b><br>
        Dünyada üretilen gıdaların yaklaşık üçte biri tüketilmeden atık haline gelmektedir. Gıda atıkları çöpe gidip katı atık depolama sahalarında oksijensiz ortamda çürüdüklerinde, karbondioksitten 25 kat daha zararlı olan <b>metan gazı (CH₄)</b> üretirler. Gıda kaybı, küresel sera gazı emisyonlarının yaklaşık %8-10'undan sorumludur.<br><br>
        <b>Döngüsel Ekonomi Yaklaşımı:</b><br>
        Geleneksel "Al-Kullan-At" (Doğrusal) modeli yerine, gıdayı sistem içinde tutan "Azalt-Yeniden Kullan-Dönüştür" (Döngüsel) modelini benimsiyoruz. Amacımız gıdayı henüz atık haline gelmeden yakalamak ve kentsel karbon ayak izini azaltmaktır.
        </div>
    </div>
    
    <div class="recipe-card bg-blue">
        <div class="recipe-title">⚖️ Altın Kural: Kompost Dengesi (C:N Oranı)</div>
        <div class="ingredient-list">
        Sağlıklı ve kokusuz bir kompost üretimi için <b>Karbon (Kahverengi atıklar) / Azot (Yeşil atıklar)</b> dengesi hayati önem taşır. İdeal hacimsel oran <b>%60 Kahverengi, %40 Yeşil</b> malzemedir.<br><br>
        <ul>
            <li><b>🟢 Yeşiller (Nem, Azot ve Protein Kaynağı):</b> Meyve ve sebze artıkları, taze çimen, kahve telvesi, çay yaprakları. Süreci hızlandırır ancak fazla olursa koku ve balçıklaşmaya yol açar.</li>
            <li><b>🟤 Kahverengiler (Hava, Karbon ve Enerji Kaynağı):</b> Kuru yapraklar, dal parçaları, tuvalet kağıdı ruloları, talaş, parçalanmış kartonlar. Yığının hava almasını sağlar, fazla olursa süreci yavaşlatır.</li>
        </ul>
        <b>Nem ve Oksijen Kontrolü:</b> Kompostunuz bir sünger gibi nemli olmalı ancak sıkıldığında su damlatmamalıdır. Haftada bir karıştırarak mikroorganizmalar için gerekli oksijeni sağlamalısınız.
        </div>
    </div>
    
    <div class="recipe-card bg-pink">
        <div class="recipe-title">❌ Komposta Asla Atılmaması Gerekenler ve Sebepleri</div>
        <div class="ingredient-list">
        <ul>
            <li><b>Et, Kemik, Balık ve Yağlar:</b> Zararlı patojenleri, sinekleri ve kemirgenleri yığına çeker, anaerobik koku üretir.</li>
            <li><b>Süt Ürünleri (Peynir, Yoğurt, Süt):</b> Oksijen akışını tıkayarak kokulu çürümeye yol açar.</li>
            <li><b>Hastalık Bitkiler veya Yabani Ot Tohumları:</b> Ev tipi soğuk kompost yığınları bu zararlıları öldürecek yüksek sıcaklıklara (60°C+) her zaman ulaşamaz, bu nedenle hastalık bahçenize tekrar yayılabilir.</li>
            <li><b>Kedi/Köpek Dışkısı:</b> İnsan sağlığına zararlı kalıcı parazitler içerebilir.</li>
            <li><b>Narenciye ve Soğan Fazlası:</b> Solucanlara ve kompost içindeki yararlı bakterilere zarar verebilecek aşırı asidik bir ortam yaratır.</li>
        </ul>
        </div>
    </div>

    <div class="recipe-card bg-purple">
        <div class="recipe-title">🌍 Sürdürülebilirlik ve İleri Dönüşüm (Upcycling)</div>
        <div class="ingredient-list">
        <b>Geri Dönüşüm (Recycling) ve İleri Dönüşüm (Upcycling) Arasındaki Fark:</b><br>
        Geri dönüşüm, bir atığı yüksek enerji harcayarak parçalayıp tekrar ham maddeye dönüştürme işlemidir. İleri dönüşüm ise, atık durumundaki bir malzemeyi kalitesini ve estetik/işlevsel değerini artırarak doğrudan yeni bir ürüne çevirmektir. Meyve kabuklarından sirke veya cilt toniği üretmek tam bir ileri dönüşümdür.<br><br>
        <b>Yerel Ekolojik Fayda:</b><br>
        Gıdayı mikro ölçekte (evde veya mahalle pazarında) kurtarmak, atıkların şehir dışındaki tesislere taşınması sırasında oluşacak lojistik kaynaklı karbon emisyonlarını sıfıra indirir. Toprağa geri dönen her gram kompost, kimyasal gübre ihtiyacını azaltarak toprak ekosistemini canlandırır.
        </div>
    </div>
    """, unsafe_allow_html=True)
