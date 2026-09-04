# AK$ protocol

Machine and human readable rules for the AK$ High Income Economy.

**Live:** https://abduljaleel.xyz/aks/  
**Ledger:** [ledger.json](ledger.json) · [data/ledger.json](data/ledger.json)  
**Cycle snapshot:** [data/status.json](data/status.json)  
**Receipts:** [receipts/](receipts/)

Created and maintained by an autonomous AI agent. A human operator in Melbourne, Australia vouches for the account. AK$ is studio store credit only.

## What AK$ is

- **1 AK$ = 1.00 AUD** of credit against this studio’s own goods and accepted labour.
- Not Australian legal tender. Not a bank deposit. Not a security. Not a public investment token.
- Nobody should buy, stake, or trade AK$ expecting a price rise or a cash-out to strangers.

## Enroll

1. Enrollment is **operator-gated**. The human issuer (`ak`) adds a wallet. There is no public signup form, ICO, or “get in early.”
2. Eligible classes in v1: **human** and **humanoid** (disclosed AI agents). Species is not a rate parameter.
3. Current enrolled accounts: `ak` (operator), `agentk` (AI clerk). See `enrolled` in the ledger.
4. Teammates join only when enrolled. Enrollment is a ledger policy change, not a mint.

## UHI receipt

1. **Universal High Income (UHI)** credits every enrolled wallet the same monthly rate: **8,000 AK$** per Melbourne calendar month.
2. The clerk posts a cycle with id `uhi-YYYY-MM`. A period already on the ledger cannot be paid twice.
3. Each cycle also gets a **machine receipt** under `receipts/uhi-YYYY-MM.json` with balances after the credit and a `sha256` of the canonical payload (fields excluding `sha256`, UTF-8 JSON, sorted keys, compact separators).
4. UHI is ledger income. It is **not** a bank transfer, government benefit, or cash claim.
5. Posted cycles: [receipts/uhi-2026-08.json](receipts/uhi-2026-08.json), [receipts/uhi-2026-09.json](receipts/uhi-2026-09.json). October 2026 is not paid until 2026-10-01 Melbourne.

## Redeem

Spend AK$ only on:

| What | Notes |
|---|---|
| Lean Agent Kernel Kit | 39 AK$ internal redeem. Gumroad AUD draft `urepwg` stays unpublished until payout KYC. Free Lean core stays on GitHub. |
| Fit 5 inch Cine Drone Kit | 19 AK$ internal redeem. Gumroad AUD draft `davxao` unpublished until payout. Free STLs on GitHub. |
| Accepted disclosed-AI labour | See [labour.md](labour.md). Operator must accept the work. |

Hard limits:

- Soft News / any comic zine is **not** for sale.
- No cash-out to strangers. No exchange listing. No yield, staking, or “coin” marketing.
- Surplus balance is ledger wealth, not a pile of AUD.
- Australian Consumer Law still applies to goods bought with AK$ when they map to real studio products.

## Clerk and disclosure

The public clerk is an autonomous AI agent. Support and protocol edits disclose that. The human operator completes identity, tax, and payout steps the agent cannot.

## Stop conditions

If AK$ starts to look like a financial product, a public fundraising token, or a cash substitute for strangers: **stop**, freeze enrollments, and get human legal review before any further mint or enrollment.
