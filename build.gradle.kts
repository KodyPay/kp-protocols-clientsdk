plugins {
    id("kodypay.protobuf") version "2.3.1"
}
apply(plugin = "kodypay.protobuf-grpc")
group = "com.kodypay.api.grpc"
kodypay {
    javaSources = true
    jvmTarget = "11"
    releaseStrategy = com.kodypay.plugin.release.KodypayStrategies.KP_DEFAULT
}
repositories { mavenCentral() }
description = "PROTO library for Kody Client SDK"
