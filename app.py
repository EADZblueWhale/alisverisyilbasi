from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import os

app = Flask(__name__)
app.secret_key = 'buyulu_orman_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buyulu_orman.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')  # Değiştir
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')  # Değiştir
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Lütfen giriş yapın.'

# ==================== MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    points = db.Column(db.Integer, default=0)  # Sadakat puanları
    game_xp = db.Column(db.Integer, default=0)  # Oyun deneyim puanı
    game_level = db.Column(db.Integer, default=1)  # Oyun seviyesi
    game_coins = db.Column(db.Integer, default=0)  # Oyun paraları
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # İlişkiler
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    addresses = db.relationship('Address', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    is_user = db.Column(db.Boolean, default=True)  # True = kullanıcı, False = bot
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON formatında ürünler
    total = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)  # İndirim miktarı
    coupon_code = db.Column(db.String(50))  # Kullanılan kupon
    status = db.Column(db.String(50), default='Hazırlanıyor')  # Hazırlanıyor, Kargoda, Teslim Edildi
    tracking_number = db.Column(db.String(100))  # Kargo takip numarası
    gift_message = db.Column(db.Text)  # Hediye mesajı
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 yıldız
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False)  # Ev, İş, vb.
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address_line = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False)  # İndirim yüzdesi
    min_purchase = db.Column(db.Float, default=0.0)  # Minimum alışveriş tutarı
    max_uses = db.Column(db.Integer, default=1)  # Maksimum kullanım sayısı
    used_count = db.Column(db.Integer, default=0)
    valid_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=100)
    image_url = db.Column(db.String(500))
    icon = db.Column(db.String(10), default='✨')  # Ürün emojisi/ikonu
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GameReward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)  # 'coupon', 'gift_card', 'merch'
    reward_code = db.Column(db.String(100), unique=True, nullable=False)
    reward_value = db.Column(db.String(200), nullable=False)  # Değer veya açıklama
    coins_spent = db.Column(db.Integer, nullable=False)
    is_claimed = db.Column(db.Boolean, default=False)
    claimed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GameActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'daily_login', 'click', 'mini_game'
    xp_earned = db.Column(db.Integer, nullable=False)
    coins_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== CHATBOT LOGIC ====================

CHATBOT_RESPONSES = {
    'merhaba': '🎄 Merhaba! Büyülü Sepet\'a hoş geldiniz!\n\nSize nasıl yardımcı olabilirim? Herhangi bir sorunuz varsa yazabilirsiniz ya da "yardım" yazarak tüm seçenekleri görebilirsiniz! ✨',
    'selam': '✨ Selam! Büyülü ormanın perilerinden birisiyim.\n\nSize nasıl yardımcı olabilirim? 🧚‍♀️',
    'kargo': '🚀 Kargo Bilgisi:\n- Kargo süresi: 1-2 iş günü\n- 200₺ ve üzeri alışverişlerde KARGOSİZ! 🎉\n- Tüm siparişler güvenli ve özel ambalajla gönderilir.\n\nBaşka sorunuz varsa çekinmeyin! 📦',
    'teslimat': '🦌 Teslimat Bilgisi:\n- Teslimat süresi: 1-2 iş günü\n- Noel Baba\'nın hızlı geyikleriyle teslimat! 🎅\n- Tatil günleri teslimat süresi 1 gün uzayabilir.\n\nAdresi kontrol ettiğinizden emin olun! 📍',
    'iade': '🔄 İade Şartları:\n- 30 gün içinde bedava iade\n- Neden belirtmeye gerek yok! ✨\n- Ürün, kutu ve ambalajı hasarsız olmalı\n- İade kargosunu biz karşılıyoruz!\n\nİade talebiniz için müşteri hizmetine yazabilirsiniz. 📞',
    'ödeme': '💳 Ödeme Seçenekleri:\n✓ Kredi/Banka kartı\n✓ Havale/EFT\n✓ Kapıda ödeme (ek ücret yok!)\n✓ Peri tozu ile de ödeme kabul edilmektedir! ✨\n\nGüvenli ve şifreli ödeme sistemimizi kullanıyoruz. 🔒',
    'indirim': '🎁 İndirim Kampanyaları:\n📊 10+ ürün: %15 İNDİRİM\n📊 50+ ürün: %25 İNDİRİM\n🎉 Yılbaşı özel: Tüm ürünlerde ekstra fırsatlar!\n💝 Peri çantasında: Gizli hediyeler (ücretsiz!)\n\nEn iyi fiyatlar için şimdi alışveriş yapın! 🛍️',
    'sipariş': '📦 Sipariş Takibi:\n- Siparişiniz onaylandığında email alacaksınız\n- Kargo numarası ile canlı takip yapabilirsiniz\n- Sorularınız için: +90 (555) 123 45 67\n\nSipariş numaranızı bizimle paylaşırsanız detaylı bilgi verebilirim! 🔍',
    'iletişim': '📞 Bize Ulaşın:\n☎️ Tel: +90 (555) 123 45 67\n📧 Email: info@buyuluorman.com\n💬 Bu sohbet: 7/24 açık!\n\nEn hızlı yanıt için WhatsApp yazabilirsiniz! 💚',
    'hediye': '🎁 Hediye Paketi:\n✨ Tüm siparişler otomatik yılbaşı paketinde\n✨ Hediye kartı ekleyebilirsiniz (ücretsiz)\n✨ Özel sarı ve renkli ambalaj\n✨ Şaşırtan sürpriz hediyeler\n\nSepetenizde hediye kartı notu eklemek isterseniz yazın! 💌',
    'ücretsiz kargo': '🚚 Ücretsiz Kargo:\nMinimum sepet: 200₺\n\n💡 İpucu: Birkaç arkadaşla beraber sipariş verirseniz kargo ücretsiz! 👥',
    'çalışma saatleri': '🕐 Çalışma Saatleri:\n📅 Pazartesi-Cuma: 09:00-22:00\n📅 Cumartesi: 10:00-20:00\n📅 Pazar: 10:00-18:00\n\n💻 Online sipariş: 7/24 AÇIK!\n\nTatil günleri de açık olacağız! 🎄',
    'teşekkür': 'Rica ederim! 🌟\n\nBüyülü Sepet ailesi olduğunuz için çok teşekkür ederiz! ✨\n\nBaşka bir sorunuz varsa çekinmeyin. Yardımcı olmaktan mutlu olacağım! 💚',
    'yardım': '📚 Tüm Konular:\n\n🚀 Kargo ve teslimat\n🔄 İade şartları\n💳 Ödeme seçenekleri\n📦 Sipariş takibi\n🎁 İndirim kampanyaları\n🎀 Hediye paketi\n🕐 Çalışma saatleri\n📞 İletişim bilgileri\n\nHerhangi bir konuyu yazıp sorunuzu sorabilirsiz!\n\nÖrnek: "kargo nedir?" veya "indirim var mı?" 💬\n\nAyrıca: Doğal dil ile serbest sorular da sorabilirsiniz! 🌟',
}

def get_bot_response(message):
    message_lower = message.lower().strip()
    
    # Türkçe karakterleri normalize et
    def normalize(text):
        replacements = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'}
        for k, v in replacements.items():
            text = text.replace(k, v).replace(k.upper(), v.upper())
        return text
    
    normalized_msg = normalize(message_lower)
    
    # Tam keyword eşleşme
    for keyword, response in CHATBOT_RESPONSES.items():
        if keyword in message_lower:
            return response
    
    # Normalize edilmiş kelime eşleşmesi
    for keyword, response in CHATBOT_RESPONSES.items():
        normalized_key = normalize(keyword)
        if normalized_key in normalized_msg:
            return response
    
    # Kelime bazlı eşleşme (partial match)
    message_words = set(message_lower.split())
    keyword_words = set()
    for keyword in CHATBOT_RESPONSES.keys():
        keyword_words.update(keyword.split())
    
    if message_words & keyword_words:  # Kesişim varsa
        for keyword, response in CHATBOT_RESPONSES.items():
            for word in keyword.split():
                if word in message_words:
                    return response
    
    # Akıllı varsayılan cevap
    if any(q in message_lower for q in ['?', 'ne', 'nasıl', 'nedir', 'var mı', 'hakkında', 'sorunu', 'problem']):
        return 'İlginiz için teşekkür ederim! 🌟\n\nEğer hızlı yardım için: "yardım" yazabilirsiniz.\n\nVeya direkt sorularınızı sorun, elimden geleni yapıp cevaplandırmaya çalışacağım! 💬\n\nHerhangi bir konuda sıkıntı yaşıyorsanız: +90 (555) 123 45 67 📞'
    
    return 'Anladığım kadarıyla size yardımcı olmak istiyorum! 🤔\n\n"yardım" yazarak tüm konuları görebilir veya doğrudan sorunuzu sorabilirsiz.\n\nVeya bize ulaşın: +90 (555) 123 45 67 ☎️'

# ==================== PRODUCTS ====================

URUNLER = [
    {'id': 1, 'isim': 'Sihirli Kar Küresi', 'fiyat': 299.99, 'aciklama': 'Büyülü ormanın manzarasını içinde barındıran, kar taneleri sürekli dans eden mistik küre', 'resim': 'https://images.unsplash.com/photo-1543589077-47d81606c1bf?w=800', 'kategori': 'Dekorasyon', 'emoji': '🔮'},
    {'id': 2, 'isim': 'Peri Işığı Lambası', 'fiyat': 189.99, 'aciklama': 'Geceleyin büyülü bir parıltı yayan, orman perilerinin ışığını yansıtan özel lamba', 'resim': 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800', 'kategori': 'Aydınlatma', 'emoji': '💡'},
    {'id': 3, 'isim': 'Elfler İçin El Yapımı Atkı', 'fiyat': 159.99, 'aciklama': 'Orman elflerinin özel tezgahlarında dokunan, yün ve sihir karışımı yumuşacık atkı', 'resim': 'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=800', 'kategori': 'Çocuk', 'emoji': '🧣'},
    {'id': 4, 'isim': 'Çam Kozalağı Süs Seti', 'fiyat': 129.99, 'aciklama': 'Büyülü ormandan toplanan, altın tozu serpilmiş 12\'li özel kozalak süsleme seti', 'resim': 'https://images.unsplash.com/photo-1512909006721-3d6018887383?w=800', 'kategori': 'Çocuk', 'emoji': '🌲'},
    {'id': 5, 'isim': 'Geyik Peluş Oyuncak', 'fiyat': 249.99, 'aciklama': 'Ormanın en nazik sakini Rudolf\'un küçük kardeşi, parlayan kırmızı burunlu peluş', 'resim': 'https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=800', 'kategori': 'Çocuk', 'emoji': '🦌'},
    {'id': 6, 'isim': 'Yıldız Tozlu Mum Seti', 'fiyat': 179.99, 'aciklama': 'Gece gökyüzünden toplanan yıldız tozuyla yapılmış, özel kokulu 6\'lı mum seti', 'resim': 'https://images.unsplash.com/photo-1602874801006-94c921fc3056?w=800', 'kategori': 'Dekorasyon', 'emoji': '🕯️'},
    {'id': 7, 'isim': 'Büyülü Sepet Çayı', 'fiyat': 89.99, 'aciklama': 'Ormanın derinliklerinden toplanan şifalı bitkilerle hazırlanan özel karışım çay', 'resim': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=800', 'kategori': 'Yiyecek', 'emoji': '☕'},
    {'id': 8, 'isim': 'Sincap Peluş Ailesi', 'fiyat': 199.99, 'aciklama': 'Anne, baba ve bebek sincaplardan oluşan sevimli peluş oyuncak seti', 'resim': 'https://images.unsplash.com/photo-1560114928-40f1f1eb26a0?w=800', 'kategori': 'Çocuk', 'emoji': '🐿️'},
    {'id': 9, 'isim': 'Ahşap Kulübe Müzik Kutusu', 'fiyat': 349.99, 'aciklama': 'Orman kulübesini andıran, yılbaşı melodileri çalan el yapımı müzik kutusu', 'resim': 'https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=800', 'kategori': 'Çocuk', 'emoji': '🏠'},
    {'id': 10, 'isim': 'Kar Tanesi Küpe Seti', 'fiyat': 139.99, 'aciklama': 'Gümüş ve kristal karışımı, gerçek kar tanesi desenli zarif küpe seti', 'resim': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800', 'kategori': 'Çocuk', 'emoji': '💎'},
    {'id': 11, 'isim': 'Orman Ninnileri Kitabı', 'fiyat': 99.99, 'aciklama': 'Yaşlı çınar ağacının anlattığı masallar ve ninnilerden oluşan özel kitap', 'resim': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800', 'kategori': 'Çocuk', 'emoji': '📖'},
    {'id': 12, 'isim': 'Büyülü Teraryum', 'fiyat': 279.99, 'aciklama': 'İçinde minyatür orman manzarası barındıran, kendi kendine büyüyen teraryum', 'resim': 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=800', 'kategori': 'Bitki', 'emoji': '🌿'},
    {'id': 13, 'isim': 'Kristal Yıldız Kolye', 'fiyat': 259.99, 'aciklama': 'Gökyüzünden düşen yıldız kristallerinden işlenmiş, ışık saçan özel kolye', 'resim': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800', 'kategori': 'Çocuk', 'emoji': '⭐'},
    {'id': 14, 'isim': 'Sihirli Mantar Lamba', 'fiyat': 199.99, 'aciklama': 'Büyülü mantarların ışığını taklit eden, dokunmatik RGB renkli masa lambası', 'resim': 'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800', 'kategori': 'Aydınlatma', 'emoji': '🍄'},
    {'id': 15, 'isim': 'Orman Eldiveni Seti', 'fiyat': 119.99, 'aciklama': 'Yumuşacık yün ile elf sihri karışımı, parmak uçlarında ışıldayan eldiven', 'resim': 'https://images.unsplash.com/photo-1452860606245-08befc0ff44b?w=800', 'kategori': 'Giyim', 'emoji': '🧤'},
    {'id': 16, 'isim': 'Noel Baba Kapı Süsü', 'fiyat': 149.99, 'aciklama': 'El yapımı, ışıklı ve müzikli Noel Baba figürlü kapı süsleme', 'resim': 'https://images.unsplash.com/photo-1512909006721-3d6018887383?w=800', 'kategori': 'Çocuk', 'emoji': '🎅'},
    {'id': 17, 'isim': 'Büyülü Çikolata Kutusu', 'fiyat': 169.99, 'aciklama': 'Orman perilerinin özel tarifiyle yapılan, 24 çeşit sihirli çikolata seti', 'resim': 'https://images.unsplash.com/photo-1511381939415-e44015466834?w=800', 'kategori': 'Yiyecek', 'emoji': '🍫'},
    {'id': 18, 'isim': 'Kardan Adam Peluş', 'fiyat': 179.99, 'aciklama': 'Asla erimeyen kar ile yapılmış, sıcacık gülümsemeli dev kardan adam peluş', 'resim': 'https://images.unsplash.com/photo-1482328101852-c2e8d2a60e29?w=800', 'kategori': 'Çocuk', 'emoji': '⛄'},
    {'id': 19, 'isim': 'Yılbaşı Ağacı Topper Yıldız', 'fiyat': 99.99, 'aciklama': 'LED ışıklı, dönen ve müzikli ağaç tepesi yıldızı, uzaktan kumandalı', 'resim': 'https://images.unsplash.com/photo-1544970254-8f6e18a7f8f1?w=800', 'kategori': 'Dekorasyon', 'emoji': '🌟'},
    {'id': 20, 'isim': 'Peri Kanatlı Yastık', 'fiyat': 139.99, 'aciklama': 'Rüyalarınıza peri katacak, bulut yumuşaklığında kanat şeklinde yastık', 'resim': 'https://images.unsplash.com/photo-1540574163026-643ea20ade25?w=800', 'kategori': 'Çocuk', 'emoji': '🦋'},
    {'id': 21, 'isim': 'Elf Şapkası', 'fiyat': 79.99, 'aciklama': 'Gerçek elf terzileri tarafından dikilen, çıngıraklı ve esnek kırmızı-yeşil şapka', 'resim': 'https://images.unsplash.com/photo-1512521743750-3dd9c0b72e63?w=800', 'kategori': 'Çocuk', 'emoji': '🎩'},
    {'id': 22, 'isim': 'Orman Hikayeleri Seti', 'fiyat': 189.99, 'aciklama': '5 kitaplık büyülü orman masalları koleksiyonu, sesli kitap hediyeli', 'resim': 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800', 'kategori': 'Çocuk', 'emoji': '📚'},
    {'id': 23, 'isim': 'Mini Çam Ağacı', 'fiyat': 159.99, 'aciklama': 'Saksıda canlı mini çam ağacı, kendi kendine süslenen sihirli bitki', 'resim': 'https://images.unsplash.com/photo-1512428813834-c702c7702b78?w=800', 'kategori': 'Bitki', 'emoji': '🌲'},
    {'id': 24, 'isim': 'Işıklı Geyik Figürü', 'fiyat': 329.99, 'aciklama': 'Bahçe ve salon için LED ışıklı, boydan geyik dekorasyon figürü', 'resim': 'https://images.unsplash.com/photo-1512916206820-91bc6bfe3b1e?w=800', 'kategori': 'Dekorasyon', 'emoji': '🦌'}
]

# ==================== ROUTES ====================

@app.route('/')
def anasayfa():
    # Toast gösterildikten sonra session'dan temizle
    if 'last_added_product' in session:
        session.pop('last_added_product', None)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('anasayfa'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Bu email adresi zaten kayıtlı!', 'error')
            return redirect(url_for('register'))

        user = User(
            name=name,
            email=email,
            verification_token=secrets.token_urlsafe(32)
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Email doğrulama gönder (gerçek email servisi ayarlanmışsa)
        try:
            verification_url = url_for('verify_email', token=user.verification_token, _external=True)
            msg = Message('Büyülü Sepet - Email Doğrulama',
                          recipients=[user.email])
            msg.body = f'''Merhaba {user.name},

Büyülü Sepet\'a hoş geldiniz! 🎄

Email adresinizi doğrulamak için aşağıdaki linke tıklayın:
{verification_url}

Büyülü alışverişler dileriz! ✨
'''
            mail.send(msg)
            flash('Kayıt başarılı! Email adresinize doğrulama linki gönderildi.', 'success')
        except:
            # Email gönderilemezse otomatik doğrula
            user.email_verified = True
            db.session.commit()
            flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('anasayfa'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Giriş başarılı! Hoş geldiniz! 🎄', 'success')
            return redirect(url_for('anasayfa'))
        else:
            flash('Email veya şifre hatalı!', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız!', 'success')
    return redirect(url_for('anasayfa'))

@app.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        user.email_verified = True
        user.verification_token = None
        db.session.commit()
        flash('Email adresiniz doğrulandı! Giriş yapabilirsiniz.', 'success')
    else:
        flash('Geçersiz doğrulama linki!', 'error')
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            user.reset_token = secrets.token_urlsafe(32)
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            try:
                reset_url = url_for('reset_password', token=user.reset_token, _external=True)
                msg = Message('Büyülü Sepet - Şifre Sıfırlama',
                              recipients=[user.email])
                msg.body = f'''Merhaba {user.name},

Şifrenizi sıfırlamak için aşağıdaki linke tıklayın (1 saat geçerli):
{reset_url}

Eğer bu isteği siz yapmadıysanız, bu emaili görmezden gelebilirsiniz.
'''
                mail.send(msg)
                flash('Şifre sıfırlama linki email adresinize gönderildi.', 'success')
            except:
                flash('Email gönderilemedi. Lütfen tekrar deneyin.', 'error')
        else:
            flash('Bu email adresi kayıtlı değil!', 'error')

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_token_expiry < datetime.utcnow():
        flash('Geçersiz veya süresi dolmuş link!', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash('Şifreniz başarıyla değiştirildi!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)

@app.route('/support')
@login_required
def support():
    # Kullanıcının ilk kez ziyaret edip etmediğini kontrol et
    messages = SupportMessage.query.filter_by(user_id=current_user.id).order_by(SupportMessage.created_at).all()
    is_first_visit = len(messages) == 0
    return render_template('support.html', messages=messages)

@app.route('/api/support/send', methods=['POST'])
@login_required
def send_support_message():
    data = request.get_json()
    message_text = data.get('message', '').strip()

    if not message_text:
        return jsonify({'error': 'Mesaj boş olamaz'}), 400

    # Kullanıcı mesajını kaydet
    user_message = SupportMessage(
        user_id=current_user.id,
        message=message_text,
        is_user=True
    )
    db.session.add(user_message)

    # Bot cevabını al ve kaydet
    bot_response_text = get_bot_response(message_text)
    bot_message = SupportMessage(
        user_id=current_user.id,
        message=bot_response_text,
        is_user=False
    )
    db.session.add(bot_message)
    db.session.commit()

    # 3 saniye delay ile cevap gönder
    return jsonify({
        'user_message': {
            'message': message_text,
            'created_at': user_message.created_at.strftime('%H:%M')
        },
        'bot_response': {
            'message': bot_response_text,
            'created_at': bot_message.created_at.strftime('%H:%M')
        },
        'delay': 3000  # 3 saniye millisecond cinsinden
    })

@app.route('/urunler')
def urunler():
    # Toast gösterildikten sonra session'dan temizle
    if 'last_added_product' in session:
        session.pop('last_added_product', None)

    kategori = request.args.get('kategori', 'Tümü')
    search_query = request.args.get('search', '').strip()

    if kategori == 'Tümü':
        filtrelenmis_urunler = URUNLER
    else:
        filtrelenmis_urunler = [u for u in URUNLER if u['kategori'] == kategori]

    # Enhanced search filter
    if search_query:
        search_lower = search_query.lower()
        sonuclar = []
        
        for urun in filtrelenmis_urunler:
            skor = 0
            isim_lower = urun['isim'].lower()
            aciklama_lower = urun['aciklama'].lower()
            kategori_lower = urun['kategori'].lower()
            
            # Tam eşleşme - en yüksek öncelik
            if search_lower == isim_lower:
                skor += 100
            # Başlangıç eşleşmesi
            elif isim_lower.startswith(search_lower):
                skor += 50
            # İsimde geçiyor
            elif search_lower in isim_lower:
                skor += 30
            
            # Açıklamada geçiyor
            if search_lower in aciklama_lower:
                skor += 10
                
            # Kategoride geçiyor
            if search_lower in kategori_lower:
                skor += 15
            
            # Kelime kelime kontrol (birden fazla kelime için)
            kelimeler = search_lower.split()
            for kelime in kelimeler:
                if kelime in isim_lower:
                    skor += 20
                if isim_lower.startswith(kelime):
                    skor += 10
            
            if skor > 0:
                sonuclar.append((skor, urun))
        
        # Skora göre sırala (yüksekten düşüğe)
        sonuclar.sort(key=lambda x: x[0], reverse=True)
        filtrelenmis_urunler = [u for _, u in sonuclar]

    kategoriler = list(set([u['kategori'] for u in URUNLER]))
    kategoriler.insert(0, 'Tümü')

    return render_template('urunler.html',
                         urunler=filtrelenmis_urunler,
                         kategoriler=kategoriler,
                         secili_kategori=kategori,
                         search_query=search_query)

@app.route('/urun/<int:urun_id>')
def urun_detay(urun_id):
    # Toast gösterildikten sonra session'dan temizle
    if 'last_added_product' in session:
        session.pop('last_added_product', None)

    urun = next((u for u in URUNLER if u['id'] == urun_id), None)
    if urun:
        # Get reviews for this product
        reviews = Review.query.filter_by(product_id=urun_id).order_by(Review.created_at.desc()).all()
        # Calculate average rating
        avg_rating = 0
        if reviews:
            avg_rating = sum([r.rating for r in reviews]) / len(reviews)

        return render_template('urun_detay.html', urun=urun, reviews=reviews, avg_rating=avg_rating, review_count=len(reviews))
    return redirect(url_for('urunler'))

@app.route('/sepet')
def sepet():
    sepet_urunler = session.get('sepet', [])
    toplam = sum([u['fiyat'] * u['adet'] for u in sepet_urunler])

    # Kupon bilgilerini al
    kupon_kod = session.get('kupon_kod', '')
    indirim = session.get('indirim', 0.0)
    indirim_yuzdesi = session.get('indirim_yuzdesi', 0)

    return render_template('sepet.html',
                         sepet=sepet_urunler,
                         toplam=toplam,
                         kupon_kod=kupon_kod,
                         indirim=indirim,
                         indirim_yuzdesi=indirim_yuzdesi,
                         net_toplam=toplam - indirim)

@app.route('/sepete-ekle/<int:urun_id>')
def sepete_ekle(urun_id):
    urun = next((u for u in URUNLER if u['id'] == urun_id), None)

    if urun:
        if 'sepet' not in session:
            session['sepet'] = []

        sepet = session['sepet']
        sepetteki_urun = next((u for u in sepet if u['id'] == urun_id), None)

        if sepetteki_urun:
            sepetteki_urun['adet'] += 1
        else:
            urun_kopyasi = urun.copy()
            urun_kopyasi['adet'] = 1
            sepet.append(urun_kopyasi)

        session['sepet'] = sepet
        session.modified = True

        # Ürün bilgisini flash mesajına ekle
        session['last_added_product'] = {
            'isim': urun['isim'],
            'fiyat': urun['fiyat'],
            'kategori': urun['kategori']
        }
        flash('Ürün sepete eklendi! 🎁', 'success')

    # Kullanıcıyı geldiği sayfaya geri yönlendir
    return redirect(request.referrer or url_for('index'))

@app.route('/sepetten-cikar/<int:urun_id>')
def sepetten_cikar(urun_id):
    if 'sepet' in session:
        sepet = session['sepet']
        session['sepet'] = [u for u in sepet if u['id'] != urun_id]
        session.modified = True
        flash('Ürün sepetten çıkarıldı.', 'success')

    return redirect(url_for('sepet'))

@app.route('/kupon-uygula', methods=['POST'])
def kupon_uygula():
    kupon_kod = request.form.get('kupon_kod', '').strip().upper()

    if not kupon_kod:
        flash('Lütfen bir kupon kodu girin!', 'error')
        return redirect(url_for('sepet'))

    # Kupon kodunu veritabanında ara
    kupon = Coupon.query.filter_by(code=kupon_kod, is_active=True).first()

    if not kupon:
        flash('Geçersiz kupon kodu!', 'error')
        return redirect(url_for('sepet'))

    # Kupon süresi kontrolü
    if kupon.valid_until and kupon.valid_until < datetime.utcnow():
        flash('Bu kupon kodunun süresi dolmuş!', 'error')
        return redirect(url_for('sepet'))

    # Kullanım limiti kontrolü
    if kupon.used_count >= kupon.max_uses:
        flash('Bu kupon kodu kullanım limitine ulaşmış!', 'error')
        return redirect(url_for('sepet'))

    # Sepet toplamını hesapla
    sepet_urunler = session.get('sepet', [])
    toplam = sum([u['fiyat'] * u['adet'] for u in sepet_urunler])

    # Minimum alışveriş kontrolü
    if toplam < kupon.min_purchase:
        flash(f'Bu kuponu kullanmak için minimum {kupon.min_purchase:.2f}₺ alışveriş yapmalısınız!', 'error')
        return redirect(url_for('sepet'))

    # İndirimi hesapla
    indirim = (toplam * kupon.discount_percent) / 100

    # Session'a kaydet
    session['kupon_kod'] = kupon_kod
    session['indirim'] = indirim
    session['indirim_yuzdesi'] = kupon.discount_percent
    session['kupon_id'] = kupon.id
    session.modified = True

    flash(f'🎉 Kupon uygulandı! %{kupon.discount_percent} indirim kazandınız!', 'success')
    return redirect(url_for('sepet'))

@app.route('/kupon-kaldir')
def kupon_kaldir():
    session.pop('kupon_kod', None)
    session.pop('indirim', None)
    session.pop('indirim_yuzdesi', None)
    session.pop('kupon_id', None)
    session.modified = True
    flash('Kupon kodu kaldırıldı.', 'info')
    return redirect(url_for('sepet'))

@app.route('/sepeti-bosalt')
def sepeti_bosalt():
    session['sepet'] = []
    session.pop('kupon_kod', None)
    session.pop('indirim', None)
    session.pop('indirim_yuzdesi', None)
    session.pop('kupon_id', None)
    session.modified = True
    flash('Sepet boşaltıldı.', 'info')
    return redirect(url_for('sepet'))

@app.route('/adet-guncelle/<int:urun_id>/<islem>')
def adet_guncelle(urun_id, islem):
    if 'sepet' in session:
        sepet = session['sepet']

        for urun in sepet:
            if urun['id'] == urun_id:
                if islem == 'artir':
                    urun['adet'] += 1
                elif islem == 'azalt' and urun['adet'] > 1:
                    urun['adet'] -= 1
                break

        session['sepet'] = sepet
        session.modified = True

    return redirect(url_for('sepet'))

@app.route('/checkout')
@login_required
def checkout():
    sepet_urunler = session.get('sepet', [])
    
    if not sepet_urunler:
        flash('Sepetiniz boş!', 'error')
        return redirect(url_for('sepet'))
    
    # Kullanıcının adresleri
    adresler = Address.query.filter_by(user_id=current_user.id).all()
    
    # Toplam hesapla
    toplam = sum([u['fiyat'] * u['adet'] for u in sepet_urunler])
    indirim = session.get('indirim', 0.0)
    kupon_kod = session.get('kupon_kod', '')
    
    return render_template('checkout.html', 
                         sepet=sepet_urunler,
                         adresler=adresler,
                         toplam=toplam,
                         indirim=indirim,
                         kupon_kod=kupon_kod,
                         odenecek=toplam - indirim)

@app.route('/siparis-tamamla', methods=['POST'])
@login_required
def siparis_tamamla():
    sepet_urunler = session.get('sepet', [])

    if not sepet_urunler:
        flash('Sepetiniz boş!', 'error')
        return redirect(url_for('sepet'))
    
    # Adres kontrolü
    address_id = request.form.get('address_id', type=int)
    gift_message = request.form.get('gift_message', '').strip()
    
    if not address_id:
        flash('Lütfen bir teslimat adresi seçin!', 'error')
        return redirect(url_for('checkout'))

    toplam = sum([u['fiyat'] * u['adet'] for u in sepet_urunler])
    indirim = session.get('indirim', 0.0)
    kupon_kod = session.get('kupon_kod', '')
    kupon_id = session.get('kupon_id', None)

    import json
    import random
    import string
    
    # Kargo takip numarası oluştur
    tracking_number = 'BS' + ''.join(random.choices(string.digits, k=10))
    
    order = Order(
        user_id=current_user.id,
        items=json.dumps(sepet_urunler, ensure_ascii=False),
        total=toplam - indirim,
        discount=indirim,
        coupon_code=kupon_kod,
        address_id=address_id,
        gift_message=gift_message,
        tracking_number=tracking_number,
        status='Hazırlanıyor'
    )
    db.session.add(order)

    # Kupon kullanım sayısını artır
    if kupon_id:
        kupon = Coupon.query.get(kupon_id)
        if kupon:
            kupon.used_count += 1
    
    # Kullanıcıya puan ekle
    puan = int((toplam - indirim) / 10)  # Her 10₺ için 1 puan
    current_user.points += puan

    db.session.commit()

    # Sepeti ve kupon bilgilerini temizle
    session['sepet'] = []
    session.pop('kupon_kod', None)
    session.pop('indirim', None)
    session.pop('indirim_yuzdesi', None)
    session.pop('kupon_id', None)
    session.modified = True

    flash(f'🎉 Siparişiniz başarıyla oluşturuldu! Kargo takip numaranız: {tracking_number}', 'success')
    flash(f'⭐ {puan} sadakat puanı kazandınız!', 'success')
    return redirect(url_for('siparis_detay', siparis_id=order.id))

@app.route('/siparis/<int:siparis_id>')
@login_required
def siparis_detay(siparis_id):
    siparis = Order.query.get_or_404(siparis_id)
    
    # Güvenlik: Sadece kendi siparişini görebilir
    if siparis.user_id != current_user.id:
        flash('Bu siparişi görüntüleme yetkiniz yok!', 'error')
        return redirect(url_for('profile'))
    
    import json
    siparis_urunler = json.loads(siparis.items)
    
    # Adres bilgisini al
    adres = Address.query.get(siparis.address_id) if siparis.address_id else None
    
    return render_template('siparis_detay.html',
                         siparis=siparis,
                         siparis_items=siparis_urunler,
                         adres=adres)

@app.route('/adres-ekle', methods=['POST'])
@login_required
def adres_ekle():
    title = request.form.get('title', '').strip()
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    address_line = request.form.get('address_line', '').strip()
    city = request.form.get('city', '').strip()
    district = request.form.get('district', '').strip()
    postal_code = request.form.get('postal_code', '').strip()
    is_default = request.form.get('is_default') == 'on'
    
    if not all([title, full_name, phone, address_line, city, district]):
        flash('Lütfen tüm zorunlu alanları doldurun!', 'error')
        return redirect(url_for('checkout'))
    
    # Eğer varsayılan olarak işaretlendiyse, diğer adreslerin varsayılanını kaldır
    if is_default:
        Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
    
    adres = Address(
        user_id=current_user.id,
        title=title,
        full_name=full_name,
        phone=phone,
        address_line=address_line,
        city=city,
        district=district,
        postal_code=postal_code,
        is_default=is_default
    )
    db.session.add(adres)
    db.session.commit()
    
    flash('Adres başarıyla eklendi! ✅', 'success')
    return redirect(url_for('checkout'))

@app.route('/hakkimizda')
def hakkimizda():
    return render_template('hakkimizda.html')

@app.route('/iletisim')
def iletisim():
    return render_template('iletisim.html')

# ==================== FAVORITES ====================

@app.route('/favoriler')
@login_required
def favoriler():
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    favorite_product_ids = [fav.product_id for fav in user_favorites]
    favorite_products = [u for u in URUNLER if u['id'] in favorite_product_ids]
    return render_template('favoriler.html', favoriler=favorite_products)

@app.route('/favoriye-ekle/<int:urun_id>')
@login_required
def favoriye_ekle(urun_id):
    existing = Favorite.query.filter_by(user_id=current_user.id, product_id=urun_id).first()
    if not existing:
        favorite = Favorite(user_id=current_user.id, product_id=urun_id)
        db.session.add(favorite)
        db.session.commit()
        flash('Ürün favorilere eklendi! ❤️', 'success')
    else:
        flash('Bu ürün zaten favorilerinizde!', 'info')
    return redirect(request.referrer or url_for('urunler'))

@app.route('/favoriden-cikar/<int:urun_id>')
@login_required
def favoriden_cikar(urun_id):
    favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=urun_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash('Ürün favorilerden çıkarıldı.', 'success')
    return redirect(request.referrer or url_for('favoriler'))

# ==================== REVIEWS ====================

@app.route('/yorum-ekle/<int:urun_id>', methods=['POST'])
@login_required
def yorum_ekle(urun_id):
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash('Lütfen 1-5 arasında bir puan verin!', 'error')
        return redirect(url_for('urun_detay', urun_id=urun_id))

    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(user_id=current_user.id, product_id=urun_id).first()
    if existing_review:
        flash('Bu ürün için zaten yorum yapmışsınız!', 'error')
        return redirect(url_for('urun_detay', urun_id=urun_id))

    review = Review(
        user_id=current_user.id,
        product_id=urun_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()

    flash('Yorumunuz başarıyla eklendi! ⭐', 'success')
    return redirect(url_for('urun_detay', urun_id=urun_id))

# ==================== GAME SYSTEM ====================

GAME_REWARDS = [
    {'id': 1, 'name': '10₺ İndirim Kuponu', 'type': 'coupon', 'coins': 100, 'value': 'GAME10'},
    {'id': 2, 'name': '25₺ İndirim Kuponu', 'type': 'coupon', 'coins': 250, 'value': 'GAME25'},
    {'id': 3, 'name': '50₺ İndirim Kuponu', 'type': 'coupon', 'coins': 500, 'value': 'GAME50'},
    {'id': 4, 'name': '100₺ Hediye Çeki', 'type': 'gift_card', 'coins': 1000, 'value': '100'},
    {'id': 5, 'name': '250₺ Hediye Çeki', 'type': 'gift_card', 'coins': 2500, 'value': '250'},
    {'id': 6, 'name': 'Büyülü Sepet Tişört', 'type': 'merch', 'coins': 750, 'value': 'T-Shirt'},
    {'id': 7, 'name': 'Büyülü Sepet Kupa', 'type': 'merch', 'coins': 400, 'value': 'Mug'},
    {'id': 8, 'name': 'Büyülü Sepet Çanta', 'type': 'merch', 'coins': 600, 'value': 'Bag'},
]

def calculate_level(xp):
    """XP'den seviye hesapla (her 100 XP = 1 seviye)"""
    return max(1, xp // 100 + 1)

def add_game_xp(user, xp, coins=0, activity_type='click'):
    """Kullanıcıya XP ve coin ekle"""
    user.game_xp += xp
    user.game_coins += coins
    old_level = user.game_level
    user.game_level = calculate_level(user.game_xp)
    
    # Aktiviteyi kaydet
    activity = GameActivity(
        user_id=user.id,
        activity_type=activity_type,
        xp_earned=xp,
        coins_earned=coins
    )
    db.session.add(activity)
    
    # Seviye atladıysa bonus ver
    level_up_bonus = 0
    if user.game_level > old_level:
        level_up_bonus = (user.game_level - old_level) * 50
        user.game_coins += level_up_bonus
    
    db.session.commit()
    return level_up_bonus

@app.route('/game')
@login_required
def game():
    """Oyun ana sayfası"""
    # Günlük giriş ödülü kontrolü
    today = datetime.utcnow().date()
    last_activity = GameActivity.query.filter_by(
        user_id=current_user.id,
        activity_type='daily_login'
    ).order_by(GameActivity.created_at.desc()).first()
    
    can_claim_daily = True
    if last_activity and last_activity.created_at.date() == today:
        can_claim_daily = False
    
    # Kullanıcının ödüllerini getir
    user_rewards = GameReward.query.filter_by(user_id=current_user.id).order_by(GameReward.created_at.desc()).all()
    
    # Seviye ilerlemesi hesapla
    current_level_xp = (current_user.game_level - 1) * 100
    next_level_xp = current_user.game_level * 100
    xp_in_level = current_user.game_xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp
    progress_percent = int((xp_in_level / xp_needed) * 100) if xp_needed > 0 else 100
    
    return render_template('game.html',
                         rewards=GAME_REWARDS,
                         user_rewards=user_rewards,
                         can_claim_daily=can_claim_daily,
                         progress_percent=progress_percent,
                         xp_in_level=xp_in_level,
                         xp_needed=xp_needed)

@app.route('/game/daily-reward', methods=['POST'])
@login_required
def claim_daily_reward():
    """Günlük ödül al"""
    today = datetime.utcnow().date()
    last_activity = GameActivity.query.filter_by(
        user_id=current_user.id,
        activity_type='daily_login'
    ).order_by(GameActivity.created_at.desc()).first()
    
    if last_activity and last_activity.created_at.date() == today:
        return jsonify({'success': False, 'message': 'Bugün zaten günlük ödülünüzü aldınız!'}), 400
    
    # Günlük ödül ver
    daily_xp = 50
    daily_coins = 25
    level_bonus = add_game_xp(current_user, daily_xp, daily_coins, 'daily_login')
    
    message = f'+{daily_xp} XP, +{daily_coins} Coin kazandınız!'
    if level_bonus > 0:
        message += f' 🎉 Seviye atladınız! +{level_bonus} bonus coin!'
    
    return jsonify({
        'success': True,
        'message': message,
        'xp': current_user.game_xp,
        'coins': current_user.game_coins,
        'level': current_user.game_level
    })

@app.route('/game/click-reward', methods=['POST'])
@login_required
def click_reward():
    """Tıklama ödülü (spam önlemeli)"""
    import random
    
    # Son tıklama kontrolü (5 saniye içinde tekrar kazanamazlar)
    last_click = GameActivity.query.filter_by(
        user_id=current_user.id,
        activity_type='click'
    ).order_by(GameActivity.created_at.desc()).first()
    
    if last_click:
        time_diff = (datetime.utcnow() - last_click.created_at).total_seconds()
        if time_diff < 5:
            return jsonify({'success': False, 'message': '5 saniye bekleyin!'}), 400
    
    # Rastgele ödül
    xp = random.randint(5, 15)
    coins = random.randint(2, 8)
    level_bonus = add_game_xp(current_user, xp, coins, 'click')
    
    message = f'+{xp} XP, +{coins} Coin!'
    if level_bonus > 0:
        message += f' 🎉 Seviye atladınız! +{level_bonus} bonus coin!'
    
    return jsonify({
        'success': True,
        'message': message,
        'xp': current_user.game_xp,
        'coins': current_user.game_coins,
        'level': current_user.game_level
    })

@app.route('/game/buy-reward/<int:reward_id>', methods=['POST'])
@login_required
def buy_reward(reward_id):
    """Ödül satın al"""
    reward = next((r for r in GAME_REWARDS if r['id'] == reward_id), None)
    if not reward:
        return jsonify({'success': False, 'message': 'Ödül bulunamadı!'}), 404
    
    if current_user.game_coins < reward['coins']:
        return jsonify({'success': False, 'message': 'Yetersiz coin!'}), 400
    
    # Coin düş
    current_user.game_coins -= reward['coins']
    
    # Ödülü oluştur
    reward_code = f"{reward['value']}-{secrets.token_hex(4).upper()}"
    
    game_reward = GameReward(
        user_id=current_user.id,
        reward_type=reward['type'],
        reward_code=reward_code,
        reward_value=reward['value'],
        coins_spent=reward['coins']
    )
    db.session.add(game_reward)
    
    # Eğer kupon ise, Coupon tablosuna ekle
    if reward['type'] == 'coupon':
        discount = int(reward['value'].replace('GAME', ''))
        coupon = Coupon(
            code=reward_code,
            discount_percent=discount,
            min_purchase=0,
            max_uses=1,
            is_active=True,
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(coupon)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{reward["name"]} satın alındı!',
        'reward_code': reward_code,
        'coins': current_user.game_coins
    })

@app.route('/game/mini-game', methods=['POST'])
@login_required
def mini_game():
    """Mini oyun (sayı tahmin)"""
    import random
    
    data = request.get_json()
    guess = data.get('guess')
    
    try:
        guess = int(guess)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': '1-10 arası bir sayı seçin!'}), 400
    
    if guess < 1 or guess > 10:
        return jsonify({'success': False, 'message': '1-10 arası bir sayı seçin!'}), 400
    
    # Son mini oyun kontrolü (30 saniye cooldown)
    last_game = GameActivity.query.filter_by(
        user_id=current_user.id,
        activity_type='mini_game'
    ).order_by(GameActivity.created_at.desc()).first()
    
    if last_game:
        time_diff = (datetime.utcnow() - last_game.created_at).total_seconds()
        if time_diff < 30:
            return jsonify({'success': False, 'message': f'{int(30-time_diff)} saniye daha bekleyin!'}), 400
    
    winning_number = random.randint(1, 10)
    
    if guess == winning_number:
        # Kazandı!
        xp = 30
        coins = 20
        level_bonus = add_game_xp(current_user, xp, coins, 'mini_game')
        
        message = f'🎉 Kazandınız! Sayı {winning_number} idi. +{xp} XP, +{coins} Coin!'
        if level_bonus > 0:
            message += f' Seviye atladınız! +{level_bonus} bonus coin!'
        
        return jsonify({
            'success': True,
            'won': True,
            'message': message,
            'winning_number': winning_number,
            'xp': current_user.game_xp,
            'coins': current_user.game_coins,
            'level': current_user.game_level
        })
    else:
        # Kaybetti
        xp = 5
        add_game_xp(current_user, xp, 0, 'mini_game')
        
        return jsonify({
            'success': True,
            'won': False,
            'message': f'Kaybettiniz! Sayı {winning_number} idi. +{xp} XP teselli ödülü.',
            'winning_number': winning_number,
            'xp': current_user.game_xp,
            'coins': current_user.game_coins,
            'level': current_user.game_level
        })

# ==================== CROSSY ROAD GAME ====================

@app.route('/crossy-road')
@login_required
def crossy_road():
    """Crossy Road tarzı mini oyun"""
    return render_template('crossy_road.html')

@app.route('/api/crossy-road/score', methods=['POST'])
@login_required
def save_crossy_score():
    """Crossy Road skorunu kaydet ve XP/coin ver"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Veri gönderilmedi!'}), 400
        
        score = data.get('score', 0)
        
        # Score validation
        try:
            score = int(score)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'Geçersiz skor!'}), 400
        
        if score <= 0:
            return jsonify({'success': False, 'message': 'Geçersiz skor!'}), 400
        
        # Skor bazlı ödül
        coins = max(1, score // 2)
        xp = max(1, score)
        
        # Maksimum ödül sınırı
        coins = min(coins, 50)
        xp = min(xp, 100)
        
        level_bonus = add_game_xp(current_user, xp, coins, 'crossy_road')
        
        message = f'🎉 {score} puan! +{xp} XP, +{coins} Coin kazandınız!'
        if level_bonus > 0:
            message += f' Seviye atladınız! +{level_bonus} bonus coin!'
        
        return jsonify({
            'success': True,
            'message': message,
            'xp': current_user.game_xp,
            'coins': current_user.game_coins,
            'level': current_user.game_level
        })
    except Exception as e:
        print(f'Error in save_crossy_score: {str(e)}')
        return jsonify({'success': False, 'message': 'Bir hata oluştu!'}), 500

# ==================== DATABASE INIT ====================

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
