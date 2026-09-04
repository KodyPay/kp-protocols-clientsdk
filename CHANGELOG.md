# Changelog

All notable changes to this repository will be documented in this file.

## 2026-09-05

### Added
- Added `Refund.Status` — a refund's own lifecycle — carried on `RefundDetails.status` in both `com/kodypay/grpc/ecom/v1/ecom.proto` and `com/kodypay/grpc/pay/v1/pay.proto` (BAM-843). Whether a refund completed could not be expressed anywhere before. `CANCELLED` covers a refund taken as a void, where the payer is never charged rather than charged and refunded.
- Added `repeated RefundDetails refunds`, `amount_refunded_minor_units` and `fully_refunded` to `PaymentDetailsResponse.PaymentDetails` in `ecom.proto` (BAM-842). ecom query responses carried no refund information at all. One change covers `PaymentDetails`, `PaymentDetailsStream` and `GetTokenPaymentDetails`, which all return `PaymentDetailsResponse`.
- Added `status` (field 7) to `PayResponse.RefundDetails`, plus `amount_refunded` and `fully_refunded` on `PayResponse`, in `pay.proto` (BAM-842). The terminal API returned refunds with no status, so a caller could only infer the outcome from whether `refund_psp_reference` was set — which indicates acceptance, not success.

The aggregates follow Stripe, whose `Charge` carries `refunds`, `amount_refunded` and `refunded` together. They are server-derived from the same rows as `refunds`, so they cannot disagree with it. ecom uses minor units and terminal a BigDecimal string, each following its own service's existing convention.

### Deprecated
- `PaymentStatus.REFUND_PENDING` and `PaymentStatus.REFUND_REQUESTED` in `pay.proto`. Refund state does not belong on the payment's status: Stripe's `Charge.status` is only `succeeded` / `pending` / `failed`, and a refunded charge stays `succeeded`. These two predate that decision and are still emitted for compatibility. ecom's `PaymentStatus` never had refund values, so it is already the shape both services should have.

### Unchanged, deliberately
- **`RefundStatus` gains no values, and needs none.** It describes whether the refund *request* was accepted, which is all a synchronous response can say — Adyen's refund endpoint returns `status: received` and nothing more. A refund's outcome is only knowable later, so it lives on `refunds[].status` and nowhere else. There is deliberately **no** second status field on `RefundResponse`: one concept, one field.
- **`PaymentStatus` gains no values.** Adding to an existing field would land as `UNRECOGNIZED` on clients generated against an older contract. Every new field here is genuinely new, and proto3 skips unknown fields silently, so an old client is unaffected and a new client reads the new surface. No version negotiation, nothing to announce.
- **No `REVERSED` value.** Adyen documents a `REFUNDED_REVERSED` webhook, but it is not enabled for our merchant accounts, so the state is unreachable. Adding a value we never emit would be worse than adding it later if that changes.

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
