# Changelog

All notable changes to this repository will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

### Added
- Added `CreateTokenRequest.expiry` to `com/kodypay/grpc/ecom/v1/ecom.proto` so `CreateCardToken` callers can set tokenisation URL expiry settings while preserving the existing default TTL behaviour.