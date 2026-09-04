# Changelog

All notable changes to this repository will be documented in this file.

## 2026-09-05

### Added
- Added a new `RefundState` enum and put the refund's real state on **new fields only** — `RefundResponse.refund_state` and `RefundDetails.status` — in both `com/kodypay/grpc/ecom/v1/ecom.proto` and `com/kodypay/grpc/pay/v1/pay.proto` (BAM-843). `RefundStatus` went as far as `REQUESTED`, which means "the acquirer accepted the refund", so **whether a refund actually completed could not be expressed at all**. `REFUND_STATE_CANCELLED` covers a refund taken as a void, where the payer is never charged rather than charged and refunded.
- Added `repeated RefundDetails refunds` to `PaymentDetailsResponse.PaymentDetails` in `ecom.proto` (BAM-842), with a new nested `RefundDetails` mirroring the terminal API's `PayResponse.RefundDetails`. This covers `PaymentDetails`, `PaymentDetailsStream` and `GetTokenPaymentDetails`, which all return `PaymentDetailsResponse`. The refunded total and remaining balance are the sum of these entries and are deliberately **not** also exposed as separate fields — two sources for one number can disagree.
- Added `status` (field 7) to `PayResponse.RefundDetails` in `pay.proto` (BAM-842). The terminal API returned refunds with no status, so a caller could only infer the outcome from whether `refund_psp_reference` was set — which indicates acceptance, not success.

### Unchanged, deliberately
- **`RefundStatus` and `PaymentStatus` gain no values.** Adding to an existing field would land as `UNRECOGNIZED` on clients generated against an older contract, so it would have needed announcing and coordinating. New fields cost nothing instead: proto3 skips unknown fields silently and losslessly, so an old client never sees the new state and a new client reads it from `refund_state` / `RefundDetails.status`. The two paths are independent with no version negotiation.
- A refunded payment therefore still reports `SUCCESS` on `PaymentStatus`. Whether it was refunded, and by how much, is in `refunds`. `REQUESTED` keeps its existing meaning — accepted, not completed — which is all it could ever have meant, since Adyen offers no synchronous refund API.

`RefundState` values carry a `REFUND_STATE_` prefix because proto enum values are siblings of their type within the package, and `PaymentStatus` already occupies `REFUND_PENDING` and `REFUND_REQUESTED`.

## 2026-09-04

### Added
- Added `idempotency_uuid` (field 5, optional string) to `RefundRequest` in `com/kodypay/grpc/ecom/v1/ecom.proto`. Ecom `Refund` was the only money-moving request in the suite without one, so a caller that retried after a slow or lost response necessarily refunded twice — the server had no way to tell a retry from a genuine second partial refund (BAM-942). Terminal Payments' `RefundRequest` has carried this field since BAM-857 was fixed the same way.

### Changed
- Documented what `RefundResponse.paymentTransactionId` identifies, in both `com/kodypay/grpc/ecom/v1/ecom.proto` and `com/kodypay/grpc/pay/v1/pay.proto`. It is **the refund's own id**, not the payment's; the payment stays in `payment_id`. Both services previously returned the payment's transaction id here, so the refund a caller had just created was not identifiable from the response at all. Ecom additionally leaves `payment_id` empty when the refund was requested by `psp_reference`, and terminal's interim `PENDING` message leaves `paymentTransactionId` empty because the refund row does not exist yet.

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
