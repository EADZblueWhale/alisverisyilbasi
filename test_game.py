#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app, db, User, GameActivity, add_game_xp
import json

# Test context
with app.app_context():
    # Check if user exists
    user = User.query.first()
    if user:
        print(f"✓ User found: {user.email}")
        print(f"  Level: {user.game_level}")
        print(f"  XP: {user.game_xp}")
        print(f"  Coins: {user.game_coins}")
        
        # Test add_game_xp function
        print("\nTesting add_game_xp function...")
        initial_coins = user.game_coins
        initial_xp = user.game_xp
        
        bonus = add_game_xp(user, 50, 25, 'test_activity')
        
        print(f"  Initial coins: {initial_coins}")
        print(f"  Added coins: 25")
        print(f"  Current coins: {user.game_coins}")
        print(f"  Level up bonus: {bonus}")
        print(f"  Initial XP: {initial_xp}")
        print(f"  Added XP: 50")
        print(f"  Current XP: {user.game_xp}")
        
        # Test database
        activity = GameActivity.query.filter_by(
            user_id=user.id,
            activity_type='test_activity'
        ).first()
        
        if activity:
            print(f"\n✓ Activity recorded: {activity.activity_type}")
            print(f"  XP earned: {activity.xp_earned}")
            print(f"  Coins earned: {activity.coins_earned}")
        else:
            print("\n✗ Activity not recorded!")
    else:
        print("✗ No user found in database")
        print("Create a user first by registering on the website")
