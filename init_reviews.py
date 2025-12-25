"""
Initialize product reviews for Büyülü Sepet
Run this once to add initial reviews with different ratings and comments
"""
from app import app, db, User, Review
from datetime import datetime, timedelta

# Örnek yorum verileri (ürün_id, yıldız_sayısı, yorum)
REVIEWS_DATA = {
    1: [  # Sihirli Kar Küresi
        (5, "Gerçekten muhteşem! Kar taneleri çok güzel dans ediyor. Çok beğendik! ⭐⭐⭐⭐⭐"),
        (5, "Yılbaşı decorasyon aradığımız tüm şeyi içeriyor. Tavsiye ederim! ✨"),
        (4, "Çok güzel ürün, biraz daha büyük olsaydı daha iyi olurdu."),
        (5, "Hediyelik almıştım, alan kişi çok mutlu oldu!"),
    ],
    2: [  # Peri Işığı Lambası
        (5, "Odanın dekorasyonunu tamamladı! Perilerinin ışığı çok zarif. 🔮"),
        (4, "Güzel bir ürün ama biraz pahalı geldi. Yine de kalitesi iyi."),
        (5, "Geceleyin mükemmel bir ambiyans yaratıyor. Çok hoşuma gitti!"),
        (5, "Çocuğumun odası birer fantastik cennet haline geldi!"),
    ],
    3: [  # Elfler İçin El Yapımı Atkı
        (5, "Çok yumuşak ve konforlu! Çocuğumun favori atkısı oldu. 🧣"),
        (5, "Yılbaşı stiline çok uygun. Herkesten iyileştirme soruları alıyorum!"),
        (4, "Kalitesi güzel ama rengi fotoğrafdakinden biraz farklı çıktı."),
    ],
    4: [  # Çam Kozalağı Süs Seti
        (5, "Yılbaşı ağacım şimdi gerçekten özel görünüyor! 🌲✨"),
        (5, "12'li set tamamen yetmedi, bir tane daha almak istiyorum!"),
        (4, "Güzel bir dekorasyon ürünü. Altın tozu biraz daha sprey olabilirdi."),
    ],
    5: [  # Geyik Peluş Oyuncak
        (5, "Çocuğumuz bunu hiç bırakmıyor! Çok sevimli bir hediye. 🦌"),
        (5, "Kalitesi çok iyi, çok dakikette yapılmış, tavırları gerçekten tatlı."),
        (5, "Rudolf'un küçük kardeşi dediğiniz anda çocuğumuz hemen seçti!"),
    ],
    6: [  # Yıldız Tozlu Mum Seti
        (5, "Ev kokunun harika ve mum ışığı çok ılık. Tüm odaya yayılıyor! 🕯️"),
        (4, "Kokular güzel ama mumlar biraz hızlı yandı. Yine de güzel."),
        (5, "Hediye paketi açtığımızda aroma tüm evi saracak şekilde hoştu."),
    ],
    7: [  # Büyülü Sepet Çayı
        (5, "Bu çay gerçekten sihirli! Rahatlayıcı ve lezzetli. ☕"),
        (5, "Ormanın nefesi gibi kokuyor. Çok hoşuma gitti!"),
        (4, "Güzel bir çay ama biraz daha tatlı olabilirdi."),
    ],
    8: [  # Sincap Peluş Ailesi
        (5, "Tüm aile oyuncakları çok tatarlı ve yumuşak! Çocuklar bayılıyor. 🐿️"),
        (5, "Anne, baba ve bebek sincaplar birbirinden güzel!"),
        (5, "Peluş kalitesi mükemmel, dış dikişler çok itinalı."),
    ],
    9: [  # Ahşap Kulübe Müzik Kutusu
        (5, "Müzik kutusu açılırken kulübenin görüntüsü çok etkileyici! 🎵"),
        (5, "Yılbaşı melodileri çok tatlı ve nostalji yapıyor."),
        (4, "Harika bir ürün ama müzik şarkısı bir tane daha olabilirdi."),
    ],
    10: [  # Kar Tanesi Küpe Seti
        (5, "Zarif ve hassas tasarım! Gerçek kar tanesi desenli. 💎"),
        (5, "Gümüş rengini çok sevdim, kristallerle ışıldıyor!"),
        (5, "Hediye olarak almanız için ideal bir ürün!"),
    ],
    11: [  # Orman Ninnileri Kitabı
        (5, "Çocuğumun yatış rutinine çok yardımcı oldu! 📖"),
        (5, "Yaşlı çınar ağacının masalları çok güzel anlatılmış."),
        (4, "İllüstrasyonlar güzel ama biraz daha renkli olabilirdi."),
    ],
    12: [  # Büyülü Teraryum
        (5, "İçinde minyatür bir orman! Büyüyor ve canlanıyor. 🌿"),
        (5, "Bakımı kolay ve çok dekoratif bir ürün."),
        (5, "Masanın üstünde bir canlı bitki gibi davranıyor!"),
    ],
    13: [  # Kristal Yıldız Kolye
        (5, "Gökyüzünden düşmüş gibi görünüyor! Çok mistik ve güzel. ⭐"),
        (5, "Kolye uzunluğu tam uygun, kristal çok belirgin ışıldar."),
        (4, "Harika bir ürün ama zincir biraz kalın gibi geldi."),
    ],
    14: [  # Sihirli Mantar Lamba
        (5, "RGB renkleri çok güzel, dokunmatik kontrol çok kolay! 🍄"),
        (5, "Mantarın şekli gerçekten adeta oymalı ve detaylı."),
        (5, "Çocuğumun gece lambası oldu, her gecesi berbat ışıklar seçiyor!"),
    ],
    15: [  # Orman Eldiveni Seti
        (5, "Eldiveler çok yumuşak ve parmak uçları gerçekten ışıldar! ✨"),
        (5, "Kar oynarken çok sıcak tuttular, soğuktan hiç etkilenmiyorum."),
        (4, "Eldiveler biraz dar geldi, bir numara büyük tavsiyesi var."),
    ],
    16: [  # Noel Baba Kapı Süsü
        (5, "Kapımda Noel Baba açık kapıdan selamlaşmış gibi görünüyor! 🎅"),
        (5, "Müziği çok sevimli ve ışıklar gerçekten parlak!"),
        (5, "Konuklar ilk bakışta çok beğeniyorlar!"),
    ],
    17: [  # Büyülü Çikolata Kutusu
        (5, "24 çeşit çikolata! Hepsi çok lezzetli ve sihirli tadında. 🍫"),
        (5, "Tur hediye paketi gerçekten çok güzel ve ışıldar."),
        (4, "Çikolatalar çok güzel ama bir kaçı eritilmiş geldi."),
    ],
    18: [  # Kardan Adam Peluş
        (5, "Asla erimese de, çok sıcak gülümsemesi var! ⛄"),
        (5, "Dev kardan adamı sevimli hale getirmişler!"),
        (5, "Koleksiyonuma eklediğim en tatarlı peluş!"),
    ],
    19: [  # Yılbaşı Ağacı Topper Yıldız
        (5, "Uzaktan kumandayla kontrol edebilmek çok pratik! 🌟"),
        (5, "LED ışıkları çok parlak, ağacı gerçekten aydınlatiyor."),
        (4, "Dönüş mekanizması güzel ama biraz sesli dönüyor."),
    ],
    20: [  # Peri Kanatlı Yastık
        (5, "Rüyalarımda peri kanatları taşıyor gibi hissettim! 🦋"),
        (5, "Kanat şekli çok dekoratif ve yastık gerçekten yumuşak."),
        (5, "Başımı koymak için ideal bir yastık!"),
    ],
    21: [  # Elf Şapkası
        (5, "Çıngırakları çok sevimli! Çocuğumuz şarkı söyleyerek gidiyor. 🎩"),
        (5, "Renkleri çok canlı kırmızı ve yeşil kombinasyonu harika!"),
        (4, "Şapka biraz büyük geldi ama çoğunluk için ideal."),
    ],
    22: [  # Orman Hikayeleri Seti
        (5, "5 kitaplık set harika! Ses kitap özelliği çok çok kullanışlı. 📚"),
        (5, "Masalları her akşam dinliyoruz, çocuğumuz çok seviyor!"),
        (5, "Seslendirme çok profesyonel ve etkileyici."),
    ],
    23: [  # Mini Çam Ağacı
        (5, "Saksısında kendi kendine büyüyüp işık saçan bir ağaç! 🌲"),
        (5, "Mini fakat gerçekten canlı ve yeşil görünüyor."),
        (4, "Bakımı basit ama biraz dikkat gerektiriyor."),
    ],
    24: [  # Işıklı Geyik Figürü
        (5, "Bahçe dekorasyonunun yıldızı oldu! Çok etkileyici. 🦌"),
        (5, "LED ışıkları çok parlak, akşam çok göze çarpmıyor."),
        (5, "Komşular haber görmek için soruyorlar!"),
    ],
}

def init_reviews():
    """Initialize reviews for all products"""
    with app.app_context():
        # Dummy test user'ı kontrol et
        test_user = User.query.filter_by(email='musteri@orneg.com').first()
        
        # Eğer yoksa oluştur
        if not test_user:
            test_user = User(
                name='Müşteri Örneği',
                email='musteri@orneg.com'
            )
            test_user.set_password('sifre123')
            db.session.add(test_user)
            db.session.commit()
        
        # Mevcut yorumları kontrol et
        existing_reviews = Review.query.first()
        if existing_reviews:
            print("⚠️ Yorumlar zaten mevcut! İşlem iptal edildi.")
            return
        
        # Tüm yorumları ekle
        total_reviews = 0
        for product_id, reviews in REVIEWS_DATA.items():
            for idx, (rating, comment) in enumerate(reviews):
                review = Review(
                    user_id=test_user.id,
                    product_id=product_id,
                    rating=rating,
                    comment=comment,
                    created_at=datetime.utcnow() - timedelta(days=30-idx)  # Tarihlerini değiştir
                )
                db.session.add(review)
                total_reviews += 1
        
        db.session.commit()
        print(f"✅ {total_reviews} yorum başarıyla eklendi!")
        print(f"✅ Test kullanıcı: {test_user.email}")

if __name__ == '__main__':
    init_reviews()
