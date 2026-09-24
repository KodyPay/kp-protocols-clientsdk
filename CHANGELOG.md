# Changelog

All notable changes to this repository will be documented in this file.

## 2026-09-25

### Changed
- `GetPaymentTransactionList` in `com/kodypay/grpc/ecom/v1/ecom.proto` is no longer limited to the three completed calendar days before today (INS-1448). `filter.transaction_date` may now be any day, with no lower or upper limit, and it is now required: a request without it is `INVALID_ARGUMENT` instead of returning the three-day window. Today and future dates are no longer rejected: today returns what has happened so far, and a future day has no rows.

  Comments only: no field, number or type changes, so this is wire- and source-compatible. `filter` and `transaction_date` stay `optional` in the schema, and presence is enforced by the server, which returns `INVALID_ARGUMENT` when either is missing. The only caller-visible behaviour change is for requests that omit the date: they previously returned three days and are now rejected.

## 2026-09-24

### Changed
- `GetPaymentTransactionListRequest.Filter.transaction_date` in `com/kodypay/grpc/ecom/v1/ecom.proto` changes type from `google.type.Date` to `optional string`, an ISO 8601 / RFC 3339 full-date (`"2026-09-16"`) (INS-1448). It keeps field number 1, and the `google/type/date.proto` import is gone.

  `google.type.Date` is not one of protobuf's well-known types: it ships with googleapis (`proto-google-common-protos` / `googleapis-common-protos`), which none of the language SDKs had depended on until now. v1.8.10 broke each SDK's release in its own way - the Kotlin and Java builds failed with `cannot access GeneratedMessageV3` on their protobuf versions, and Python's protoc could not find `google/type/date.proto` - and every SDK would also have had to pass the extra dependency on to merchants. A full-date string is how date-only values are written elsewhere (Adyen's `format: date`, OpenAPI's `date`), needs nothing beyond protobuf, and keeps the semantics unchanged: a calendar day with no time and no offset, read in the store's timezone.

  The rpc is new and still in development - published in v1.8.10 on 2026-09-22, served on staging only (kp-core v5.0.1630), never in production - so the field is retyped in place rather than moved to a new number. A client built on v1.8.10 that sets the old `Date` value will have its request rejected (it does not parse as a UTF-8 string) rather than silently misread.

## 2026-09-18

### Changed
- Six enum-typed fields become `optional`, so that an unset field is no longer read as a real value (BAM-987):

  | file | field | zero value read when unset |
  | :--- | :--- | :--- |
  | `ecom/v1/ecom.proto` | `PaymentDetailsResponse.PaymentData.payment_method` | `VISA` |
  | `ecom/v1/ecom.proto` | `GetCardTokenResponse.Response.payment_method` | `VISA` |
  | `pay/v1/token.proto` | `TokenDetailsResponse.CardInfo.payment_method` | `VISA` |
  | `preauth/v1/preauth.proto` | `PaymentCard.payment_method` | `VISA` |
  | `pay/v1/pay.proto` | `CloseBatchResponse.status` | `SUCCESS` |
  | `pay/v1/pay.proto` | `PayResponse.PaymentData.payment_method_type` | `CARD` |

  `PaymentMethods` starts at `VISA = 0`, so a `PaymentData` with nothing set and one with `payment_method` explicitly set to Visa were byte-identical — both empty. A caller could not tell "the server said Visa" from "the server said nothing", and a successful WeChat payment whose `payment_method` had not yet been written read as a Visa card. `CloseBatchStatus` starts at `SUCCESS = 0`, which defaults an unreported batch closure to a successful one. `PaymentMethodType` starts at `CARD = 0`.

  Renumbering those enums would silently reinterpret the bytes of every already-published client, so the zero values stay where they are and the fields gain presence instead. Notes on the `PaymentMethods` enums record this, and point at `payment_method_variant` (a string, where empty is unambiguous) as the signal for SDKs generated before the presence existed.

  Wire-compatible and source-compatible: field numbers and types are unchanged, generated getters keep returning the enum, and a `hasX()` accessor is added alongside. Explicit presence on a scalar changes the accessor shape only in generators that switch to pointers (Go — no Go SDK here); C#, Java/Kotlin, Python, PHP and Ruby keep the value accessor.

  One behavioural note for servers: a field explicitly set to its zero value now serialises as present-and-zero (two bytes rather than none), which is the intended meaning. Servers must set these fields explicitly for the presence to carry information.

  `PayRequest.PaymentMethods` is deliberately not changed: it is only carried by `repeated` fields, which encode each element explicitly and so already distinguish a one-element `[VISA]` list from an empty one.

## 2026-09-09

### Changed
- `amount_refunded_minor_units` and `fully_refunded` on `PaymentDetailsResponse.PaymentDetails` in `com/kodypay/grpc/ecom/v1/ecom.proto` are now `optional`, so a caller can tell "the server did not report this" from "nothing was refunded" (BAM-962).

  Without explicit presence, a `uint64` and a `bool` come back as `0` and `false` whether or not the server filled them in. Staging verification on 2026-09-09 found that `GetPayments` returns this message without populating the refund fields, so a fully refunded payment read there as one that was never refunded — and no client could detect the difference. The terminal side already had both fields optional; this brings ecom into line.

  The two are also documented as not populated by every endpoint returning `PaymentDetails`, and `refunds` now records that `GetPayments` leaves them unset. Note that `repeated refunds` has no presence of its own and cannot express the distinction — hence relying on the two aggregates for it.

  Wire-compatible and source-compatible: the field numbers and types are unchanged, generated getters keep returning `uint64` / `bool`, and a `hasX()` accessor is added alongside. This contract already uses `optional` on scalars extensively (77 such fields across `ecom.proto` and `pay.proto`), so it is not a new pattern for any language SDK.

## 2026-09-05

### Added
- Added `Refund.Status` — a refund's own lifecycle — carried on `RefundDetails.status` in both `com/kodypay/grpc/ecom/v1/ecom.proto` and `com/kodypay/grpc/pay/v1/pay.proto` (BAM-843). Whether a refund completed could not be expressed anywhere before. `CANCELLED` covers a refund taken as a void, where the payer is never charged rather than charged and refunded.
- Added `repeated RefundDetails refunds`, `amount_refunded_minor_units` and `fully_refunded` to `PaymentDetailsResponse.PaymentDetails` in `ecom.proto` (BAM-842). ecom query responses carried no refund information at all. One change covers `PaymentDetails`, `PaymentDetailsStream` and `GetTokenPaymentDetails`, which all return `PaymentDetailsResponse`.
- Added `status` (field 7) to `PayResponse.RefundDetails`, plus `amount_refunded` and `fully_refunded` on `PayResponse`, in `pay.proto` (BAM-842). The terminal API returned refunds with no status, so a caller could only infer the outcome from whether `refund_psp_reference` was set — which indicates acceptance, not success.

The aggregates are server-derived from the same rows as `refunds`, so they cannot disagree with it — which is why they are worth carrying rather than making every caller sum a list. ecom uses minor units and terminal a BigDecimal string, each following its own service's existing convention. `fully_refunded` is deliberately named for what it means: it is false while a payment is only partially refunded.

### Removed
- Removed `psp_reference` from ecom `RefundRequest` (field 4) and terminal `VoidPaymentRequest` (field 1), and reserved both the numbers and the name. Refunding or voiding by psp reference is no longer supported; use `payment_id`. Verified beforehand that no request in the previous 90 days used either field.

  Removal is wire-safe: a client still sending the field has it treated as an unknown field and skipped, which leaves the request with no identifier, so it is rejected rather than acting on the wrong thing. Both messages keep their `oneof` with a single member, so `payment_id` presence and the `IdCase` / `IdsCase` accessors generated code already uses are unchanged, and a future identifier can be added without reshaping anything.

  `reserved` is the important half: without it, field 4 / field 1 or the name `psp_reference` could later be reused for something with different meaning, and old clients still sending the old value would have it silently interpreted as the new field.

### Deprecated
- `PaymentStatus.REFUND_PENDING` and `PaymentStatus.REFUND_REQUESTED` in `pay.proto`. Refund state does not belong on the payment's status — the payment stays successful whether or not it was later refunded, and how much came back belongs in `refunds` / `amount_refunded`. These two predate that decision and are still emitted for compatibility. ecom's `PaymentStatus` never had refund values, so it is already the shape both services should have.

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
