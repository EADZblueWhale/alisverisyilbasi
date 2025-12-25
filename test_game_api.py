#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test game endpoints with authentication"""
from app import app, db, User
import json

with app.app_context():
    user = User.query.first()
    if not user:
        print("❌ No user found!")
        exit(1)
    
    print("=" * 60)
    print("🎮 GAME API TEST")
    print("=" * 60)
    
    with app.test_client() as client:
        # Test 1: Daily Reward
        print("\n✅ TEST 1: Daily Reward")
        response = client.post('/game/daily-reward')
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"   ⚠️  Redirected to login - session needed")
        else:
            print(f"   Response: {response.json}")
        
        # Test 2: Click Reward
        print("\n✅ TEST 2: Click Reward")
        response = client.post('/game/click-reward')
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"   ⚠️  Redirected to login - session needed")
        else:
            print(f"   Response: {response.json}")
        
        # Test 3: Mini Game
        print("\n✅ TEST 3: Mini Game")
        response = client.post('/game/mini-game', 
            json={'guess': 5},
            content_type='application/json')
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"   ⚠️  Redirected to login - session needed")
        else:
            print(f"   Response: {response.json}")
        
        # Test 4: Crossy Road Score
        print("\n✅ TEST 4: Crossy Road Score")
        response = client.post('/api/crossy-road/score',
            json={'score': 10},
            content_type='application/json')
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"   ⚠️  Redirected to login - session needed")
        else:
            print(f"   Response: {response.json}")
        
        print("\n" + "=" * 60)
        print("ℹ️  Browser session required for full testing")
        print("=" * 60)
