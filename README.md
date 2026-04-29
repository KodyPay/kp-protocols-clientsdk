# kp-protocols-clientsdk

gRPC protocols for client-sdk.

## Release Process

### New Version Release
1. Create a Pull Request (PR) to the `main` branch for review.
2. Add exactly one release label before merge:
    - **`release:patch`**: For bug fixes or small protocol changes that still require a stable release.
    - **`release:minor`**: For backward-compatible feature additions.
    - **`release:major`**: For breaking changes.
    - **`release:none`**: For docs, CI, or internal automation changes that should not create a stable tag.
3. The `release_preview` workflow validates that exactly one release label is present and shows the next stable tag that would be created after merge.
4. Once the PR is merged into protected `main`, the `release_on_main` workflow creates the annotated stable tag and a GitHub Release automatically.
5. Use the stable tag to run the release action from the respective SDK repositories to release SDKs in different languages.

### Testing Release
1. Pre-release tags in development branches remain manual and must use a suffix such as `-alpha.N` or `-beta.N`.
2. Pre-release tags do not participate in the next stable version calculation.
3. Use the pre-release tag to run the release action from the respective SDK repositories when branch-level validation is needed.

## Active SDK Repositories
Below is the list of active SDK repositories for different languages, most are public:
- **Java**: [kp-clientsdk-java](https://github.com/KodyPay/kody-clientsdk-java)
- **PHP**: [kody-clientsdk-php](https://github.com/KodyPay/kody-clientsdk-php)
- **Dotnet**: [kp-clientsdk-dotnet](https://github.com/KodyPay/kody-clientsdk-dotnet)
- **Python**: [kody-clientsdk-python](https://github.com/KodyPay/kody-clientsdk-python)
- **Kotlin**: [kp-clientsdk-kotlin](https://github.com/KodyPay/kody-clientsdk-kotlin)


**Note**: The SDK from [kody-clientsdk-java6](http://github.com/KodyPay/kody-clientsdk-java6) does not follow the same approach. It is fully manual and requires code changes to use the latest protocol.
