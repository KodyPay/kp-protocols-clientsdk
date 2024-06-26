@file:Suppress("UnstableApiUsage")
rootProject.name = "kp-protocols-clientsdk"

pluginManagement {
    repositories {
        mavenLocal()
        gradlePluginPortal()
        mavenCentral()
        maven {
            url = uri("https://maven.pkg.github.com/KodyPay/kp-gradle-plugins")
            credentials {
                username = ""
                password = System.getenv("GITHUB_TOKEN")
            }
        }
    }
    resolutionStrategy {
        eachPlugin {
            val reg = Regex("""kodypay.(\w+)""")
            if (reg.matches(requested.id.id)) {
                val name = reg.find(requested.id.id)!!.groupValues[1]
                useModule("com.kodypay.gradle.plugins:${name}-plugin:${requested.version}")
            }
        }
    }
}
plugins {
    id("com.gradle.enterprise").version("3.11.1")
}
gradleEnterprise {
    buildScan {
        termsOfServiceUrl = "https://gradle.com/terms-of-service"
        termsOfServiceAgree = "yes"
    }
}
