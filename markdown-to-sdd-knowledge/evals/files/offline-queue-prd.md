# Feature Request: Offline Queue for Inventory Scanner

**Author**: Sarah (PM, Warehouse Systems)
**Date**: 2026-06-15
**Priority**: P1

## Problem
Our warehouse workers use the Inventory Scanner app in Zone C (the cold storage area) where WiFi drops constantly. When connectivity is lost mid-scan, scanned items are lost and workers have to rescan everything once they're back in range. This causes ~45 minutes of lost productivity per worker per shift.

## Proposed Solution
Add an offline queue that automatically stores scans when the device has no network connectivity, then syncs them when the connection is restored.

## User Stories
- As a warehouse worker, I want my scans to be saved locally when the network is down so that I don't lose my work.
- As a shift supervisor, I want to see which scans are pending sync so that I know when it's safe to move stock.

## Functional Requirements
1. The app must detect network connectivity state in real time
2. When offline, scanned barcodes must be saved to local storage immediately
3. When connectivity returns, queued scans must sync automatically in FIFO order
4. The sync must be retried up to 3 times on failure, with exponential backoff (1s, 4s, 16s)
5. The UI must show a persistent banner: "Offline — 12 scans pending sync" with the count updating live
6. Users must be able to manually trigger a sync via a "Sync Now" button in the banner
7. Scans that fail after all retries must be marked as "failed" and surfaced in a separate "Failed Scans" review screen
8. The queue must survive app restarts and device reboots

## Non-Functional Requirements
- Scan save latency: < 50ms to local storage
- Queue capacity: must handle up to 10,000 pending scans without performance degradation
- Storage: use Room database for persistence
- The offline banner must be accessible (announced by TalkBack) and meet WCAG 2.1 AA contrast ratios

## Edge Cases
- What happens if the user force-kills the app during a sync? → The sync must be atomic per scan; partial sync of a batch is acceptable but individual scans must not be corrupted
- What happens if the device runs out of storage? → Show a warning banner and stop accepting new scans; existing queued scans must not be lost
- What if the server rejects a scan (e.g., invalid barcode format)? → Mark as failed after retries, do not retry indefinitely

## Tech Notes
- We use Kotlin + Jetpack Compose with Room for local DB
- The project already has a ConnectivityManager wrapper in `util/NetworkMonitor.kt`
- Current scan data model is in `model/ScanItem.kt` — it has fields: barcode, timestamp, locationCode, workerId
- The warehouse API endpoint for submitting scans is `POST /api/v2/scans` — we use Retrofit with a `ScanApiService` interface in `network/ScanApiService.kt`

## Out of Scope
- Real-time inventory deduction (handled by backend)
- Barcode validation logic (handled by `BarcodeValidator` which already exists)
- Multi-device conflict resolution

## Timeline
- Target: end of Q3 (September 30, 2026)
- Sarah from Warehouse Ops is the stakeholder reviewer
