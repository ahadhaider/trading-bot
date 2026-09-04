# Anime AI Video Generator - Production Architecture

├── mobile_app_flutter/               # Android & iOS Flutter Application
│   ├── android/
│   │   ├── app/
│   │   │   ├── build.gradle          # Keystore signing, NDK, ProGuard, AdMob metadata
│   │   │   ├── proguard-rules.pro    # Obfuscation rules for Google Mobile Ads & Razorpay
│   │   │   └── src/main/AndroidManifest.xml
│   │   ├── build.gradle
│   │   └── key.properties            # Secret store credentials (ignored in git)
│   ├── lib/
│   │   ├── main.dart                 # Entry point, Firebase init & AdMob preload
│   │   ├── config/
│   │   │   ├── admob_config.dart     # Dynamic Ad Unit IDs & Remote Config handler
│   │   │   └── theme.dart            # Anime Cyberpunk Dark/Light Palette
│   │   ├── models/
│   │   │   ├── user_model.dart       # Credits, Tier, Daily Quota
│   │   │   ├── video_project.dart    # Scenes, Prompts, TTS & Audio timestamps
│   │   │   └── subscription.dart
│   │   ├── services/
│   │   │   ├── api_service.dart      # HTTP Client with JWT interceptor
│   │   │   ├── admob_service.dart    # App Open, Banner, Interstitial & Rewarded Ads
│   │   │   ├── razorpay_service.dart # Native Razorpay / UPI SDK bridge
│   │   │   └── tts_player_service.dart
│   │   └── screens/
│   │       ├── home_screen.dart      # Mode selector (Prompt, Image, Script, Auto-Story)
│   │       ├── video_creator_screen.dart # Interactive Canvas, Timeline & Scene editor
│   │       ├── paywall_modal.dart    # Tiered Razorpay INR checkout
│   │       └── player_export_screen.dart
│   └── pubspec.yaml                  # google_mobile_ads, razorpay_flutter, firebase_auth
│
├── backend_fastapi/                  # High-Performance Asynchronous Video Engine
│   ├── app/
│   │   ├── main.py                   # FastAPI Application Entry point & CORS
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic Settings (.env validator)
│   │   │   └── security.py           # JWT & Razorpay HMAC-SHA256 verification
│   │   ├── db/
│   │   │   ├── database.py           # Async SQLAlchemy / Supabase Pool
│   │   │   └── models.py             # PostgreSQL Tables
│   │   ├── api/v1/
│   │   │   ├── generate.py           # Gemini 3.7 Auto-Script & Prompt Enhancer
│   │   │   ├── render.py             # Task Dispatcher to Celery Queue
│   │   │   ├── admob.py              # Dynamic Remote Config & SSV Reward Callback
│   │   │   └── webhooks.py           # Razorpay Signature Verification & Credit Ledger
│   │   ├── pipeline/
│   │   │   ├── ffmpeg_stitcher.py    # Multi-scene crossfades, Subtitles & Audio Ducking
│   │   │   ├── tts_synthesizer.py    # Voiceover generation & phoneme alignment
│   │   │   └── cloudflare_r2.py      # S3-compatible asset upload & CDN streaming
│   │   └── tasks/
│   │       ├── celery_app.py         # Celery Redis Worker configuration
│   │       └── video_tasks.py        # Distributed video rendering jobs
│   ├── Dockerfile
│   └── requirements.txt
└── devops/
    ├── docker-compose.yml            # FastAPI + Redis + Celery + FFmpeg container
    └── github-actions-release.yml    # Automated Android Release APK CI/CD pipeline