# Changelog

All notable changes to this repository will be documented in this file.

## 2026-05-15

### Added
- Added the initial `com/kodypay/grpc/pci/v1/pci.proto` contract for `com.kodypay.grpc.pci.v1.PciTokenService`, including `TokeniseCard` and `DetokeniseCard`, store-scoped idempotent requests, `payer_reference`, `TokenUsage`, `DetokeniseReason`, `payment_token` responses aligned with the existing token-payment and pre-authorisation namespace, `oneof result` envelopes, shared `CardDetails` with required `holder_name`, and masked `CardSummary` metadata.

## 2026-04-29

### Added
- Added `CreateTokenRequest.expiry` to `com/kodypay/grpc/ecom/v1/ecom.proto` so `CreateCardToken` callers can set tokenisation URL expiry settings while preserving the existing default TTL behaviour.
