plugins {
    id("kodypay.protobuf") version "3.0.8"
}
kodyProtobuf {
    useGrpc = true
}
repositories { mavenCentral() }
description = "PROTO library for Kody Client SDK"
