# Changelog

All notable changes to this repository will be documented in this file.

## 2026-04-29

### Added
- Added `CreateTokenRequest.expiry` to `com/kodypay/grpc/ecom/v1/ecom.proto` so `CreateCardToken` callers can set tokenisation URL expiry settings while preserving the existing default TTL behaviour.

### Changed
- Added label-driven stable release automation with a shared version resolver, PR release preview workflow, and merge-to-main auto-tag workflow.
