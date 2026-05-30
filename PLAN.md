# Order API -- build plan

## Phase 1 -- Core order lifecycle (complete)

- [x] Create order endpoint (`POST /orders`)
- [x] List orders endpoint (`GET /orders`)
- [x] Get single order endpoint (`GET /orders/<id>`)
- [x] JWT authentication on all protected routes

## Phase 2 -- Order management (in progress)

- [ ] Order cancellation (`POST /orders/<id>/cancel`)
- [ ] Bulk import endpoint (`POST /orders/import`)
- [ ] Order status update webhook

## Phase 3 -- Observability and operations

- [ ] Structured logging for all order state transitions
- [ ] Prometheus metrics for order volume and error rates
- [ ] Health check endpoint with dependency status

## Phase 4 -- Maintenance

- [ ] Dependency audit and update cycle
- [ ] CVE scan and remediation
