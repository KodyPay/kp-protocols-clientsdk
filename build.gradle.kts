import build.buf.gradle.BUF_BUILD_DIR
import build.buf.gradle.ImageFormat

plugins {
    java
    id("idea")
    id("build.buf") version "0.10.0"
}

repositories {
    mavenCentral()
    maven {
        url = uri("https://buf.build/gen/maven")
    }
}
group = "com.kodypay.api.grpc"
defaultTasks("clean", "build")

val protbufVersion = "4.28.2"
val grpcVersion = "1.68.0"
val javaxAnnotationsVersion = "1.3.2"

dependencies {
    implementation("com.google.protobuf:protobuf-java:$protbufVersion")
    implementation("io.grpc:grpc-stub:$grpcVersion")
    implementation("io.grpc:grpc-protobuf:$grpcVersion")
    implementation("javax.annotation:javax.annotation-api:$javaxAnnotationsVersion")
}

// Add a task dependency for compilation
tasks.named("compileJava").configure {
    dependsOn("bufGenerate")
    dependsOn("bufBuild")
}

// Add the generated code to the main source set
sourceSets["main"].java {
    srcDir("${layout.buildDirectory}/$BUF_BUILD_DIR/java")
}

buf {
    configFileLocation = rootProject.file("buf.yaml")
    generate {
        includeImports = true
    }
    build {
        imageFormat = ImageFormat.BINPB
    }
}
