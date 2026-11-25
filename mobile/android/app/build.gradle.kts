plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    // [Sessão 43] package trocado de com.example.rumo_mobile -> br.com.rumo.app
    namespace = "br.com.rumo.app"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        // [Sessão 43] applicationId trocado; TODO do Flutter removido (era o pedido de troca)
        applicationId = "br.com.rumo.app"
        // You can update the following values to match your application needs.
        // For more information, see: [flutter.dev](https://flutter.dev/to/review-gradle-config)
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        release {
            // TODO: Add your own signing config for the release build.
            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

flutter {
    source = "../.."
}

 kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}