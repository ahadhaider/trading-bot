# Android Release APK Compilation & Signing Guide

### Step 1: Generate a Production Upload Keystore
Run the following keytool command in your terminal to create your release signing key:

```bash
keytool -genkey -v -keystore android/app/upload-keystore.jks \
        -alias anime-studio-key -keyalg RSA -keysize 2048 -validity 10000
```

### Step 2: Configure `android/key.properties`
Create a file at `android/key.properties` with your secret credentials (ensure this is added to `.gitignore`):

```properties
storePassword=YourKeystorePasswordHere
keyPassword=YourKeyPasswordHere
keyAlias=anime-studio-key
storeFile=../upload-keystore.jks
```

### Step 3: Configure `android/app/build.gradle`
Ensure your `android/app/build.gradle` includes:

```groovy
plugins {
    id "com.android.application"
    id "kotlin-android"
    id "dev.flutter.flutter-gradle-plugin"
}

def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    namespace "com.animestudio.aivideomaker"
    compileSdk 34
    ndkVersion "25.1.8937393"

    defaultConfig {
        applicationId "com.animestudio.aivideomaker"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0.0"
        multiDexEnabled true
    }

    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### Step 4: ProGuard Rules (`android/app/proguard-rules.pro`)
Prevent code minification from breaking AdMob and Razorpay SDKs:

```proguard
# Google Mobile Ads
-keep class com.google.android.gms.ads.** { *; }
-keep class com.google.ads.** { *; }

# Razorpay
-keep class com.razorpay.** { *; }
-dontwarn com.razorpay.**

# ExoPlayer / Video
-keep class com.google.android.exoplayer2.** { *; }
```

### Step 5: Build Release APK & App Bundle (AAB)

```bash
# 1. Clean Flutter build cache
flutter clean && flutter pub get

# 2. Compile Universal Release APK
flutter build apk --release --split-per-abi

# Output files located at:
# build/app/outputs/flutter-apk/app-armeabi-v7a-release.apk
# build/app/outputs/flutter-apk/app-arm64-v8a-release.apk

# 3. Compile Google Play Store AAB Bundle
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### Step 6: Automated GitHub Actions CI/CD Pipeline
Place this workflow in `.github/workflows/build-apk.yml` to automatically generate APK releases on push:

```yaml
name: Build Anime Studio Android APK
on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v3
        with:
          distribution: 'zulu'
          java-version: '17'
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.19.x'
          channel: 'stable'
      - run: flutter pub get
      - run: flutter build apk --release
      - uses: actions/upload-artifact@v4
        with:
          name: Anime-AI-Video-Studio-APK
          path: build/app/outputs/flutter-apk/app-release.apk
```