# Devfolio Submission Details: UNCLUSTER

## Hackathon
**BOSS Battle 2026** (Bitshala Bitcoin & Nostr Open Source Software Hackathon)
- Platform: Devfolio
- URL: https://boss-battle.devfolio.co/
- Track: Bitcoin & Nostr Open Source Software

## Project Info
- **Project Name**: Uncluster
- **Tagline**: Zero-Leakage Pre-Flight Bitcoin UTXO Cluster Firewall & Autonomous Nostr Shield
- **GitHub Repository**: https://github.com/Naveen57990/Uncluster
- **Live Demo / Web Console**: https://uncluster-firewall.vercel.app
- **Video Demo**: https://youtu.be/... (or YouTube URL once uploaded)
- **Track**: Bitcoin / Nostr / Open Source

## Pitch / Project Story

### Inspiration
As Bitcoiners and Nostr users, we constantly advocate for financial sovereignty and self-custody. Yet, modern wallet interfaces operate with dangerous opacity. Wallets routinely co-spend distinct UTXOs simply to aggregate enough satoshis for a payment, inadvertently triggering the Common-Input Ownership Heuristic (CIOH). A single KYC exchange withdrawal co-spent with an isolated CoinJoin output or private mining reward instantly contaminates your entire coin history for blockchain surveillance firms.

Furthermore, autonomous Nostr AI agents and Lightning zap bots frequently leak raw on-chain addresses across public relays, allowing surveillance spiders to correlate Nostr public keys (`npub`) with real-world UTXO clusters. We built **Uncluster** as an air-gapped cryptographic firewall to solve this at the pre-flight stage—before signing or broadcasting.

### What it does
Uncluster is an industrial-grade pre-flight transaction firewall and Nostr privacy shield:
1. **CIOH Violation Interception**: Graph-traverses candidate inputs in unsigned PSBTs or raw hex, flagging cross-cluster co-spending risks between KYC, Mining, P2P, and Cold Storage clusters.
2. **Toxic Change Script Fingerprint Audit**: Flags when change script types mismatch input script types (e.g., Native SegWit inputs creating Legacy P2PKH change), preventing wallet fingerprinting.
3. **BIP-69 Verification**: Enforces strict lexicographical sorting of inputs and outputs so surveillance algorithms cannot deduce change ownership via output index ordering.
4. **Autonomous Sanitized Coin Selection**: Given a target payment satoshi budget, Uncluster isolates contaminated inputs and recalculates clean single-cluster UTXO pools with 0 CIOH merges.
5. **Nostr Agent Shield (NIP-01/04/44/57)**: Audits Nostr events before relay broadcast, catching plaintext Bitcoin address leaks, zap receipt change leaks, and relay gossip correlation risks.
6. **Industrial Cyberdeck Console & CLI**: Operates via a retro-futuristic CRT phosphor terminal web console and a zero-dependency Python CLI for bitcoind RPC pipelines.

### How we built it
- **Core Engine**: Pure Python 3 cryptographic domain models (`crypto_models.py`), deterministic CIOH graph traversal analyzer (`cluster_analyzer.py`), and Nostr event privacy auditor (`nostr_shield.py`).
- **Deterministic Test Suite**: 8/8 comprehensive unit tests running in 0.000s without external dependencies or network telemetry.
- **Cyberdeck Console**: Pure ES2022 JavaScript, Web Audio API synthesizer for tactile mechanical terminal feedback, CRT scanlines, and live ASCII transaction topology diagrams.
- **Deployment**: Live on Vercel Edge (`uncluster-firewall.vercel.app`).

### Challenges we ran into
Modeling deterministic coin selection while balancing change output denominations and fee estimation without introducing change script fingerprinting required deep protocol care. We solved this by implementing strict cluster-isolated knapsack selection and matching change script types directly to the input script standard.

### Accomplishments that we're proud of
- Achieving 0.000s execution time across all 8 deterministic test vectors.
- Building an authentic phosphor cyberdeck terminal that Bitcoiners genuinely enjoy using over generic SaaS dashboards.
- Seamlessly unifying Bitcoin UTXO privacy analysis with Nostr NIP-01/04/57 event auditing.

### What we learned
We learned the subtle nuances of wallet fingerprinting beyond CIOH—specifically how change script mismatches and un-randomized output ordering can completely compromise transactions even when CoinJoins are used.

### What's next for Uncluster
- Direct integration as a Sparrow Wallet and Specter Desktop pre-flight verification plugin.
- Headless bitcoind RPC proxy daemon that automatically rejects any transaction failing the Uncluster firewall threshold.
- NIP-47 Nostr Wallet Connect (NWC) automated pre-flight interceptor for sovereign AI agents.
