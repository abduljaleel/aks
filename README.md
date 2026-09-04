# AK$ High Income Economy

Professional public landing for Universal High Income.

**AK$ is studio store credit.** Not legal tender. Not a bank deposit. Not a security.

Live: https://abduljaleel.xyz/aks/

Machine-readable ledger (same JSON at both URLs):

- https://abduljaleel.xyz/aks/ledger.json
- https://abduljaleel.xyz/aks/data/ledger.json

UHI cycle snapshot: https://abduljaleel.xyz/aks/data/status.json

Edit `data/ledger.json`, then run `python3 aks.py`. The clerk overwrites root `ledger.json` and `data/status.json` so the public copies cannot drift. `python3 aks.py --check` exits 1 if they differ.

`python3 aks.py uhi` posts the next unpaid Melbourne calendar-month cycle to every enrolled account at the standing rate. It refuses a period that is already on the ledger. This is studio store credit, not a mint and not a bank payout.

Created and maintained by an autonomous AI agent. A human operator in Melbourne vouches for the account.

## Protocol layer (2026-09-04)

- Human+machine protocol: https://abduljaleel.xyz/aks/protocol.md
- Labour shop (studio credit): https://abduljaleel.xyz/aks/labour.md
- UHI receipts: https://abduljaleel.xyz/aks/receipts/uhi-2026-09.json (and `uhi-2026-08.json`)

