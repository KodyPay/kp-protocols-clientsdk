# kp-protocols-clientsdk

gRPC protocols for client-sdk.

## Release Process

### New Version Release
1. Create a Pull Request (PR) to the `main` branch for review.
2. Once the PR is approved and merged, manually tag the version based on the changes made and current version of the previous head of main branch:
    - **Patch**: For bug fixes or small changes.
    - **Minor**: For backward-compatible feature additions.
    - **Major**: For breaking changes.
3. Use the tag to run the release action from the respective SDK repositories to release SDKs in different languages.

### Testing Release
1. Tag the version in your development branch, appending -alpha or -beta to the end of the version based on the nature of the changes (e.g., 1.0.0-alpha for early testing or 1.0.0-beta for more stable pre-release testing).
2. Use the tag to run the release action from the respective SDK repositories to release SDKs in different languages.

## Active SDK Repositories
Below is the list of active SDK repositories for different languages, most are public:
- **Java**: [kp-clientsdk-java](https://github.com/KodyPay/kody-clientsdk-java)
- **PHP**: [kody-clientsdk-php](https://github.com/KodyPay/kody-clientsdk-php)
- **Dotnet**: [kp-clientsdk-dotnet](https://github.com/KodyPay/kody-clientsdk-dotnet)
- **Python**: [kody-clientsdk-python](https://github.com/KodyPay/kody-clientsdk-python)
- **Kotlin**: [kp-clientsdk-kotlin](https://github.com/KodyPay/kody-clientsdk-kotlin)


**Note**: The SDK from [kody-clientsdk-java6](http://github.com/KodyPay/kody-clientsdk-java6) does not follow the same approach. It is fully manual and requires code changes to use the latest protocol.
