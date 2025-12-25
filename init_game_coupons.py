"""
Initialize game coupons for Büyülü Sepet
Run this once to add initial game reward coupons to the database
"""
from app import app, db, Coupon
from datetime import datetime, timedelta

with app.app_context():
    # Check if coupons already exist
    existing = Coupon.query.filter_by(code='GAME10-WELCOME').first()
    
    if not existing:
        # Create some initial coupons that can be earned through the game
        initial_coupons = [
            {
                'code': 'GAME10-WELCOME',
                'discount_percent': 10,
                'min_purchase': 0,
                'max_uses': 100,
                'valid_until': datetime.utcnow() + timedelta(days=365),
                'is_active': True
            },
            {
                'code': 'YILBASI2024',
                'discount_percent': 20,
                'min_purchase': 100,
                'max_uses': 50,
                'valid_until': datetime.utcnow() + timedelta(days=30),
                'is_active': True
            },
            {
                'code': 'BUYULU50',
                'discount_percent': 50,
                'min_purchase': 500,
                'max_uses': 10,
                'valid_until': datetime.utcnow() + timedelta(days=7),
                'is_active': True
            }
        ]
        
        for coupon_data in initial_coupons:
            coupon = Coupon(**coupon_data)
            db.session.add(coupon)
        
        db.session.commit()
        print("✅ Başlangıç kuponları oluşturuldu!")
        print("- GAME10-WELCOME (10% indirim)")
        print("- YILBASI2024 (20% indirim, min 100₺)")
        print("- BUYULU50 (50% indirim, min 500₺)")
    else:
        print("ℹ️ Kuponlar zaten mevcut.")

print("\n🎮 Oyun sistemi hazır!")
print("📝 Kullanıcılar oyun oynayarak coin kazanıp ödül satın alabilirler.")
print("🎁 Ödüller: İndirim kuponları, hediye çekleri ve ürünler")
