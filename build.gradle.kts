plugins {
    kotlin("jvm") version "2.0.20"
    id("kodypay.core") version "3.0.14"
    id("kodypay.protobuf") version "3.0.14"
}
kodyProtobuf {
    useGrpc = true
    protobufVersion = "4.28.2"
    grpcVersion = "1.68.0"
    coroutinesVersion = "1.9.0"
    grpcKotlinVersion = "1.4.1"
}
kodypay {
    jvmTarget = "11"
    withSources()
    release { fixedStrategy = false }
}
