# Incident INC-2026-0001: Callback Service Timeout

- Service: Callback Service
- Priority: P1
- Incident Manager: Monjur
- Middleware Lead: Rasel

## Summary

On 2026-06-14 at 09:42 UTC the Callback Service began returning HTTP 504
timeouts for roughly 38% of requests. Customer-facing payment confirmations
were delayed by up to 12 minutes.

## Timeline

- 09:42 UTC - Alerting fired on elevated p99 latency for the Callback Service.
- 09:51 UTC - On-call confirmed a connection pool exhaustion on the middleware tier.
- 10:05 UTC - A recent deploy raised the default database connection timeout
  from 2s to 30s, causing worker threads to block and the pool to saturate.
- 10:18 UTC - The change was rolled back to the previous release.
- 10:26 UTC - Error rate returned to baseline and the incident was resolved.

## Root Cause

A configuration change in release 4.7.0 increased the database connection
timeout to 30 seconds. Under load, slow queries held connections far longer,
exhausting the fixed-size connection pool and blocking new callbacks.

## Resolution

Rolled back release 4.7.0 and restored the 2 second connection timeout. The
connection pool recovered within eight minutes.

## Action Items

- Add a circuit breaker around the database connection pool.
- Add an alert on connection pool utilization above 80%.
- Require load testing for any change to connection timeout settings.
