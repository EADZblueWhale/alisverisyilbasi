#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ürünleri emoji'leriyle beraber veritabanına ekle"""

from app import app, db, Product, URUNLER

with app.app_context():
    # Veritabanı tablosunu kontrol et ve gerekirse oluştur
    db.create_all()
    
    # Mevcut ürünleri temizle
    Product.query.delete()
    
    # Her ürünü veritabanına ekle
    for urun in URUNLER:
        product = Product(
            id=urun['id'],
            name=urun['isim'],
            description=urun['aciklama'],
            price=urun['fiyat'],
            category=urun['kategori'],
            image_url=urun['resim'],
            icon=urun.get('emoji', '✨'),
            stock=100
        )
        db.session.add(product)
        print(f"✓ Ürün eklendi: {urun['isim']} ({urun.get('emoji', '✨')})")
    
    db.session.commit()
    print("\n✓ Tüm ürünler veritabanına emoji'leriyle beraber eklendi!")

