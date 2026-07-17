# Changelog

All notable changes to this repository will be documented in this file.

## 2026-07-17

### Added
- Added `idempotency_uuid` (field 19, optional string) to `PaymentInitiationRequest` in `com/kodypay/grpc/ecom/v1/ecom.proto`, mirroring `CreateTokenRequest.idempotency_uuid`. Required by the server when `tokenise_card` is true — it's the dedup key for the card-tokenisation record, distinct from `payer_reference`. Without it, `InitiatePayment` calls with `tokenise_card=true` fail server-side validation ("Idempotency key is required for card tokenization requests"), since `PaymentInitiationRequest` had no field to carry it.

## 2026-07-16

### Changed
- Un-deprecated `PaymentInitiationRequest.tokenise_card` in `com/kodypay/grpc/ecom/v1/ecom.proto` and added `payer_reference` (field 17) and `recurring_processing_model` (field 18), mirroring the equivalent fields on `CreateTokenRequest`. This lets `InitiatePayment` tokenise the card used for a real, non-zero-amount payment in one call, instead of requiring a separate zero-amount `CreateCardToken` request first. `payer_reference` is required by the server when `tokenise_card` is true (see kp-core's mapping change for the request-level validation).

### Added
- Added `card_expiry_date` (field 12, optional string, format `MM/yyyy`) to `GetCardTokenResponse.Response` in `com/kodypay/grpc/ecom/v1/ecom.proto`. The tokenised card's expiry date was already stored server-side but never exposed on this response; this closes that gap for OPI's Pay-by-Link `TransToken` flow, which requires an `ExpiryDate` alongside the token.

## 2026-05-15

### Added
- Added the initial `com/kodypay/grpc/pci/v1/pci.proto` contract for `com.kodypay.grpc.pci.v1.PciTokenService`, including `TokeniseCard` and `DetokeniseCard`, store-scoped idempotent requests, `payer_reference`, `TokenUsage`, `DetokeniseReason`, `payment_token` responses aligned with the existing token-payment and pre-authorisation namespace, `oneof result` envelopes, shared `CardDetails` with required `holder_name`, and masked `CardSummary` metadata.

## 2026-04-29

### Added
- Added `CreateTokenRequest.expiry` to `com/kodypay/grpc/ecom/v1/ecom.proto` so `CreateCardToken` callers can set tokenisation URL expiry settings while preserving the existing default TTL behaviour.
