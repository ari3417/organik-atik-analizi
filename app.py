import streamlit as st
from ultralytics import YOLO
# ... kodun geri kalanı ...
from PIL import Image

# 1. Sayfa Ayarları (Mobil/Web uyumlu ve geniş tasarım)
st.set_page_config(page_title="Rescue Scanner & Coach", page_icon="♻️", layout="centered")

# 2. Ana Başlık ve Açıklama
st.title("📱 DIGITAL PLATFORM: RESCUE SCANNER & COACH")
st.markdown("""
**Rescue Scanner & Coach**, gönüllülere gıda ayırma, yeniden kullanım ve kompost hazırlama süreçlerinde rehberlik eden, fotoğraf tabanlı bir karar destek arayüzüdür.
""")

# Modeli yükleme
@st.cache_resource
def load_model():
    return YOLO('best.pt')

model = load_model()

# 3. Sekmelerin (Tabs) Oluşturulması
tab1, tab2, tab3 = st.tabs(["📸 Ayrıştırma ve Değerlendirme", "🍂 Kompost Modu", "📖 Eğitim Desteği"])

# ==========================================
# SEKME 1: AYRIŞTIRMA VE DEĞERLENDİRME
# ==========================================
with tab1:
    st.header("Scan & Sort")
    st.markdown("Malzemeleri tanımlayın ve doğrudan yeniden dağıtım, yenilebilir geri kazanım veya kompost seçeneklerini görün.")
    
    uploaded_file = st.file_uploader("Analiz etmek istediğiniz ürünün fotoğrafını yükleyin", type=["jpg", "jpeg", "png"], key="scanner")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        st.write("🔄 Yapay zeka görüntüyü işliyor...")
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
                
                
                if sinif_adi == BOZUK_ETIKETI:
                    toplam_bozuk_alan += alan
                else:
                    toplam_meyve_alani += alan
                    if sinif_adi not in tespit_edilen_urunler:
                        tespit_edilen_urunler.append(sinif_adi)
            
            if len(tespit_edilen_urunler) > 0:
                urun_ismi = ", ".join(tespit_edilen_urunler).upper()
                bozukluk_orani = (toplam_bozuk_alan / toplam_meyve_alani) * 100 if toplam_meyve_alani > 0 else 100
                if bozukluk_orani > 100: bozukluk_orani = 100.0
                
                # --- GÖRSEL ANALİZ ---
                st.markdown("---")
                st.write(f"🔍 **Yapay Zeka Tespit Görüntüsü:** Lütfen kırmızı/işaretli kutu ile belirtilen bozuk bölgeyi keserek ayırın.")
                res_plotted = result.plot()[:, :, ::-1]
                st.image(res_plotted, caption=f"Tespit Edilen: {urun_ismi} | Hasar: %{bozukluk_orani:.1f}", use_column_width=True)

                # --- SINIFLANDIRMA VE TARİFLER ---
                st.markdown("### 📋 Aksiyon Planı")
                
                if bozukluk_orani <= 5.0:
                    st.success("**Kategori: Doğrudan Yeniden Dağıtım (Taze Tüketim)**")
                    st.write("Ürün kusursuz veya kusura çok yakın. Taze olarak tüketime veya gıda bankalarına gönderilmeye tamamen uygundur.")
                
                elif bozukluk_orani <= 45.0:
                    st.warning("**Kategori: Yenilebilir Geri Kazanım (Sıfır Atık İleri Dönüşüm)**")
                    st.write("Hasarlı kısımları kestikten sonra kalan temiz bölümlerle maksimum verim elde edebileceğiniz tarifler:")
                    
                    # Tarif Sözlüğü
                    tarifler = {
                        "portakal": "**🍊 Portakal:**\n- *Kabuklar:* İnce ince dilimleyip kaynatarak sıfır atık portakal kabuğu reçeli yapabilir veya sirke içine atarak doğal yüzey temizleyici elde edebilirsiniz.\n- *İç Kısım:* Taze portakal suyu olarak sıkılabilir veya posası keklerde kullanılabilir.\n🔗 [YouTube'da Sıfır Atık Portakal Tarifleri](https://www.youtube.com/results?search_query=sifir+atik+portakal+kabugu+tarifi)",
                        "muz": "**🍌 Muz:**\n- *Kararmış İç:* Püre haline getirip şekersiz muzlu ekmek (banana bread) yapımında kullanın veya dondurup vegan dondurma yapın.\n- *Kabuklar:* Suda 24 saat bekleterek bitkileriniz için potasyum zengini sıvı gübre elde edin.\n🔗 [YouTube'da Sıfır Atık Muz Tarifleri](https://www.youtube.com/results?search_query=kararmis+muz+degerlendirme)",
                        "elma": "**🍏 Elma:**\n- *Kabuk ve Çekirdekler:* Bir kavanoza su ve biraz şeker ile koyarak ev yapımı elma sirkesi fermente edin.\n- *Yumuşamış İç:* Tarçınla fırınlayarak elma cipsi veya ezerek şekersiz elma püresi yapın.\n🔗 [YouTube'da Sıfır Atık Elma Tarifleri](https://www.youtube.com/results?search_query=elma+kabugu+sirkesi+tarifi)",
                        "salatalık": "**🥒 Salatalık:**\n- *İç Kısım:* Dilimleyip limon ve nane ile detoks suyuna ekleyin veya hızlı turşu kurun.\n- *Kabuklar ve Uçlar:* Blenderdan geçirip göz altı maskesi veya ferahlatıcı cilt toniği olarak kullanın.\n🔗 [YouTube'da Sıfır Atık Salatalık Tarifleri](https://www.youtube.com/results?search_query=salatalik+degerlendirme+tarifleri)",
                        "domates": "**🍅 Domates:**\n- *Genel Kullanım:* Yumuşamış domatesler taze tüketim için iyi olmasa da, kaynatılarak menemenlik sos, salça veya domates püresi yapmak için en lezzetli formundadır.\n🔗 [YouTube'da Yumuşamış Domates Değerlendirme](https://www.youtube.com/results?search_query=yumusamis+domates+degerlendirme)"
                    }
                    
                    for urun in tespit_edilen_urunler:
                        if urun in tarifler:
                            st.info(tarifler[urun])
                            
                elif bozukluk_orani <= 80.0:
                    st.error("**Kategori: Kompost (Organik Gübre)**")
                    st.write(f"Bu {urun_ismi.lower()} tüketim limitlerini aşmış durumda. Lütfen doğrudan 'Kompost Modu' sekmesine geçerek bu ürünü toprağa nasıl geri kazandıracağınızı öğrenin.")
                
                else:
                    st.error("**Kategori: Güvenli Olmayan Atık**")
                    st.write("Aşırı çürüme veya küflenme tespit edildi. Eğer ev tipi Bokashi kompostu yapmıyorsanız, standart yığın kompostuna atmak patojen riski taşıyabilir. Kahverengi çöp kutusuna atın.")

            elif toplam_bozuk_alan > 0:
                st.info("Sadece hasarlı bölge algılandı, ana ürün tespit edilemedi.")
            else:
                st.info("Sistem bu fotoğrafta net bir ürün tanıyamadı.")

# ==========================================
# SEKME 2: KOMPOST MODU
# ==========================================
with tab2:
    st.header("Evaluate & Redirect (Kompost Modu)")
    st.markdown("Kompost dengenizi kontrol edin ve organik atıklarınızın olgunlaşma durumunu analiz edin.")
    
    st.markdown("### 🌡️ Kompost Üretim Aşaması Hesaplayıcı")
    atilan_malzeme = st.selectbox("Komposta eklenecek ağırlıklı malzeme türü nedir?", ["Meyve/Sebze Kabukları (Yeşil - Azot)", "Kuru Yaprak/Karton (Kahverengi - Karbon)", "Kahve Telvesi (Yeşil - Azot)"])
    
    if "Yeşil" in atilan_malzeme:
        st.warning("Hızlı çürüyen 'Yeşil' malzeme ekliyorsunuz. Dengeyi sağlamak için üzerine mutlaka talaş, kuru yaprak veya parçalanmış karton gibi 'Kahverengi' malzeme eklemelisiniz.")
    else:
        st.success("Kuru 'Kahverengi' malzeme ekliyorsunuz. Bu, kompostun hava almasını ve koku yapmamasını sağlayacaktır.")
        
    st.write("**Tahmini Bekleme Süresi:** Ev tipi soğuk kompost için düzenli karıştırma ile yaklaşık **3 ila 6 ay** arası beklemeniz gerekmektedir.")
    
    st.markdown("---")
    st.markdown("### 📸 Kompost Gelişim Analizi (Prototip)")
    compost_file = st.file_uploader("Kompostunuzun son durumunu fotoğraflayın", type=["jpg", "jpeg", "png"], key="compost")
    
    if compost_file is not None:
        c_image = Image.open(compost_file)
        st.image(c_image, caption="Yüklenen Kompost Görseli", use_column_width=True)
        st.info("""
        *Sistem Notu: Mevcut yapay zeka modelimiz taze gıda kurtarma üzerine eğitilmiştir. Kompostun olgunluk seviyesini, karbon/azot rengini ve nem oranını piksel tabanlı analiz edecek 'Kompost Görüntü İşleme Modeli (v2.0)' geliştirme aşamasındadır. Olgunlaşmış kompost koyu kahverengi, topraksı kokulu ve ilk atılan malzemelerin tanınmadığı bir dokuda olmalıdır.*
        """)

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
