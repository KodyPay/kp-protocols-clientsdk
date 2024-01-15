plugins {
    id("kodypay.protobuf") version "2.0.0"
}
apply(plugin = "kodypay.protobuf-grpc")
group = "com.kodypay.sdk"
kodypay {
    javaSources = true
    jvmTarget = "21"
    releaseStrategy = com.kodypay.plugin.release.KodypayStrategies.KP_DEFAULT
}
repositories { mavenCentral() }
description = "PROTO library for Kody Client SDK"
