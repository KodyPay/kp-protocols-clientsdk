import com.google.protobuf.gradle.*

plugins {
    id("java")
    id("idea")
    id("com.google.protobuf") version "0.9.4"
}

repositories {
    mavenCentral()
}

val protbufVersion = "4.28.2"
val grpcVersion = "1.68.0"
val javaxAnnotationsVersion = "1.3.2"

dependencies {
    implementation("com.google.protobuf:protobuf-java:$protbufVersion")
    implementation("io.grpc:grpc-stub:$grpcVersion")
    implementation("io.grpc:grpc-protobuf:$grpcVersion")
    implementation("javax.annotation:javax.annotation-api:$javaxAnnotationsVersion")
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:$protbufVersion"
    }
    plugins {
        id("grpc") { artifact = "io.grpc:protoc-gen-grpc-java:$grpcVersion" }
    }
    generateProtoTasks {
        ofSourceSet("main").forEach {
            it.plugins {
                id("grpc") { }
            }
        }
    }
}
