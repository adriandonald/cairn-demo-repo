# cairn-demo-repo

Demo target repository for the [Cairn AI governance harness](https://github.com/adriandonald/cairn).

This repository is a realistic Python microservice used to demonstrate Cairn's four governance outcomes:

| PR | Scenario | Expected outcome |
|---|---|---|
| #1 | Clean feature PR — well-structured, fully typed, documented | AI approved |
| #2 | Feature with observability gap — missing logging on error paths | AI approved with warning |
| #3 | Auth change — modifies token validation in a high-risk code path | Escalated to human |
| #4 | Dependency update — clean version bumps, no new packages | AI approved (high confidence) |

## About this service

A minimal order processing API built with Flask. It is not a production system — it exists to provide a realistic codebase for Cairn's analysis engine to evaluate.
