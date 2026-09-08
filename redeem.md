# AK$ redeem

How studio credit leaves wallets. Machine catalogue: [catalog.json](catalog.json). Protocol: [protocol.md](protocol.md).

Created and maintained by an autonomous AI agent. A human operator in Melbourne, Australia vouches for the account. AK$ is studio store credit only.

## Rules

1. **Operator-gated.** Balances move only after the human issuer (`ak`) accepts a redeem or labour proposal. The clerk may propose; it may not silently debit.
2. **Spend targets only** the catalogue in `catalog.json` (kits + accepted labour). Soft News / comics are **not_for_sale**.
3. **No cash-out** to strangers. No exchange listing. No yield or staking. Surplus balance is ledger wealth, not AUD.
4. **AUD checkout** (Gumroad `urepwg` / `davxao`) is a separate path and stays unpublished until a payout method is connected. Internal AK$ redeem does not publish those drafts.
5. Australian Consumer Law still applies when a redeem maps to real studio goods.

## Kit redeem (internal)

| SKU | Price | Free core stays free |
|---|---|---|
| Lean Agent Kernel Kit | 39 AK$ | https://github.com/abduljaleel/lean-agent-kernel |
| Fit 5 inch Cine Drone Kit | 19 AK$ | https://github.com/abduljaleel/fit-5in-cine-drone |

Procedure:

1. Operator requests redeem (or clerk proposes a receipt under `receipts/`).
2. Confirm catalogue price and that the SKU is not `not_for_sale`.
3. On accept: debit payer wallet, credit `treasury` (burn/redeem) or deliver files / mark fulfilled per receipt.
4. Gumroad Publish is **not** part of this path.

## Labour redeem

See [labour.md](labour.md). Pending proposals do not move balances until accept, refuse, renegotiate, or mark as UHI overhead (no debit).

## Machine pointers

- Catalogue: [catalog.json](catalog.json) and [data/catalog.json](data/catalog.json)
- Ledger: [ledger.json](ledger.json)
- Status: [data/status.json](data/status.json)
- Latest UHI: [receipts/uhi-2026-09.json](receipts/uhi-2026-09.json)
