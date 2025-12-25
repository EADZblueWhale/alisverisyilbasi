# 🎮 Büyülü Sepet - Oyun Sistemi Rehberi

## 🌟 Genel Bakış

Büyülü Sepet artık tamamen işlevsel bir **gamification (oyunlaştırma) sistemi** ile geliyor! Kullanıcılar oyun oynayarak XP ve Coin kazanabilir, seviye atlayabilir ve gerçek ödüller kazanabilirler.

---

## 🎯 Oyun Sistemine Erişim

### Gizli Buton (Easter Egg)
Ana sayfanın footer kısmında **"Büyülü Orman v2.0 🌲"** yazısına **5 kez tıklayın**!
- Her tıklamada emoji değişir
- 5. tıklamada confetti animasyonu ile birlikte **🎮 Gizli Oyun Merkezi** butonu belirir
- Butona tıklayarak oyun sayfasına gidebilirsiniz

**Alternatif:** Giriş yaptıktan sonra direkt `/game` URL'ini ziyaret edin.

---

## 📊 Oyun Mekanikleri

### XP (Deneyim Puanı) Sistemi
- **Seviye Sistemi:** Her 100 XP = 1 seviye
- **Seviye Atladığınızda:** Seviye başına 50 bonus coin
- **İlerleme Çubuğu:** Bir sonraki seviyeye ne kadar yakın olduğunuzu gösterir

### Coin (Oyun Parası) Sistemi
- Coinler ile ödül mağazasından ödül satın alabilirsiniz
- Ödüller: İndirim kuponları, hediye çekleri, ürünler

---

## 🎲 Oyunlar ve Aktiviteler

### 1. 🎁 Günlük Ödül
- **Kazanç:** 50 XP + 25 Coin
- **Cooldown:** Günde 1 kez (her gün 00:00'da sıfırlanır)
- **Nasıl:** "Günlük Ödülü Al" butonuna tıklayın

### 2. 🖱️ Tıklama Oyunu
- **Kazanç:** 5-15 XP + 2-8 Coin (rastgele)
- **Cooldown:** 5 saniye
- **Nasıl:** Parlayan yıldıza tıklayın

### 3. 🎲 Sayı Tahmin Oyunu (Mini Game)
- **Mekanik:** 1-10 arası rastgele bir sayı tahmin edin
- **Kazandınız:** 30 XP + 20 Coin
- **Kaybettiniz:** 5 XP (teselli ödülü)
- **Cooldown:** 30 saniye
- **Nasıl:** Sayı butonlarından birine tıklayın

---

## 🏪 Ödül Mağazası

### 🎟️ İndirim Kuponları
| Ödül | Coin Maliyeti | İndirim |
|------|--------------|---------|
| 10₺ İndirim Kuponu | 100 Coin | 10₺ |
| 25₺ İndirim Kuponu | 250 Coin | 25₺ |
| 50₺ İndirim Kuponu | 500 Coin | 50₺ |

### 💳 Hediye Çekleri
| Ödül | Coin Maliyeti | Değer |
|------|--------------|-------|
| 100₺ Hediye Çeki | 1000 Coin | 100₺ |
| 250₺ Hediye Çeki | 2500 Coin | 250₺ |

### 🎁 Ürünler (Merch)
| Ödül | Coin Maliyeti |
|------|--------------|
| Büyülü Sepet Tişört | 750 Coin |
| Büyülü Sepet Kupa | 400 Coin |
| Büyülü Sepet Çanta | 600 Coin |

---

## 🎫 Kupon Kullanımı

1. Ödül mağazasından kupon satın alın
2. "Kazandığın Ödüller" bölümünde kupon kodunuzu görün
3. Sepet sayfasında kupon kodunu girin
4. İndiriminiz otomatik uygulanır!

**Örnek Kupon Kodu:** `GAME25-A3F8B2E1`

---

## 📈 İpuçları ve Stratejiler

### Hızlı XP Kazanma
1. **Her gün giriş yapın** → 50 XP günlük ödül
2. **Mini oyunu oynayın** → Kazanırsanız 30 XP
3. **Tıklama oyununu** 5 saniyede bir oynayın → 5-15 XP
4. **Seviye atlayın** → Her seviye 50 bonus coin

### Coin Yönetimi
- İlk 100 coin'i hemen harcamayın
- Günlük ödülleri biriktirin (25 coin/gün)
- Mini oyunu kazanmak için şansınızı deneyin (20 coin)
- Hedef belirleyin (örn: 500 coin → 50₺ kupon)

### Optimal Strateji
1. **Gün 1-3:** Günlük ödül + Tıklama oyunu → ~200 coin
2. **Gün 4:** İlk ödülü alın (100 coin → 10₺ kupon)
3. **Gün 5-10:** 500 coin hedefleyin → 50₺ kupon
4. **Uzun vade:** 2500 coin → 250₺ hediye çeki!

---

## 🛠️ Teknik Bilgiler (Geliştiriciler İçin)

### Database Modelleri
- **User:** `game_xp`, `game_level`, `game_coins` alanları eklendi
- **GameReward:** Kullanıcıların kazandığı ödüller
- **GameActivity:** Oyun aktivitelerinin kaydı
- **Coupon:** Kupon kodu sistemi

### API Endpoints
```
POST /game/daily-reward     # Günlük ödül al
POST /game/click-reward     # Tıklama ödülü
POST /game/mini-game        # Mini oyun oyna
POST /game/buy-reward/<id>  # Ödül satın al
GET  /game                  # Oyun ana sayfası
```

### İlk Kurulum
```bash
# Başlangıç kuponlarını oluştur
python init_game_coupons.py
```

---

## 🎨 Görsel Özellikler

- **Gradient arka planlar** (mor-pembe tonları)
- **Glassmorphism** efektleri
- **Confetti animasyonu** (easter egg açıldığında)
- **Pulse animasyonları** (oyun butonu)
- **Progress bar** (seviye ilerlemesi)
- **Real-time bildirimler** (ödül kazanıldığında)

---

## 🐛 Bilinen Özellikler

### Cooldown Sistemi
- **Günlük ödül:** Server-side kontrol (veritabanı)
- **Tıklama:** Client + Server-side (5 saniye)
- **Mini oyun:** Server-side (30 saniye)

### Spam Önleme
- Aynı aktiviteyi çok hızlı yapamazsınız
- Cooldown süreleri server tarafında kontrol edilir
- Frontend butonları devre dışı kalır

---

## 🎯 Gelecek Özellikler (İsteğe Bağlı)

- [ ] Liderlik tablosu (en yüksek seviye, en çok coin)
- [ ] Başarımlar (achievements) sistemi
- [ ] Daha fazla mini oyun çeşidi
- [ ] Arkadaş davet sistemi (bonus XP)
- [ ] Haftalık/aylık turnuvalar
- [ ] Özel etkinlik kuponları

---

## 📞 Destek

Oyun sistemi ile ilgili sorunlar için:
- Müşteri destek: support@buyulusepet.com
- Canlı destek: Site içi chatbot

---

## 🎄 Oyunun Tadını Çıkarın!

Büyülü Sepet oyun sistemi tamamen ücretsizdir ve gerçek ödüller kazanmanızı sağlar. Eğlenceli vakit geçirin! ✨

**Not:** I cannot generate actual AI images, but I've added beautiful Unsplash placeholder images for all 24 products. The images are themed (Christmas, winter, gifts, decorations, etc.) and will load automatically from Unsplash's CDN.
