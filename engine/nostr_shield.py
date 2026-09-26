"""
Uncluster Nostr Agent Shield
Analyzes Nostr protocol events (NIP-01, NIP-19, NIP-44, NIP-57 Zaps)
for metadata leakage, relay gossip exposure, and on-chain identity linkage.
Pure Python, zero external dependencies.
"""

from typing import List, Dict, Any, Optional
import re
from .crypto_models import NostrEvent


class NostrAuditResult:
    def __init__(self):
        self.privacy_score: int = 100
        self.exposure_level: str = "LOW"
        self.flags: List[str] = []
        self.leaks_detected: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []

    def compute_exposure(self):
        self.privacy_score = max(0, min(100, self.privacy_score))
        if self.privacy_score >= 85:
            self.exposure_level = "SOVEREIGN (SHIELDED)"
        elif self.privacy_score >= 60:
            self.exposure_level = "MODERATE (PARTIAL EXPOSURE)"
        elif self.privacy_score >= 40:
            self.exposure_level = "HIGH (METADATA LEAKAGE)"
        else:
            self.exposure_level = "CRITICAL (DIRECT IDENTITY LINKAGE)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "privacy_score": self.privacy_score,
            "exposure_level": self.exposure_level,
            "flags": self.flags,
            "leaks_detected": self.leaks_detected,
            "recommendations": self.recommendations,
        }


class NostrShieldAnalyzer:
    """
    Evaluates Nostr events emitted by autonomous agents and users.
    """

    # Known surveillance or high-traffic corporate relays
    HIGH_SURVEILLANCE_RELAYS = [
        "relay.damus.io",
        "nos.lol",
        "relay.snort.social",
        "eden.nostr.land"
    ]

    def audit_event(self, event: NostrEvent) -> NostrAuditResult:
        result = NostrAuditResult()

        # 1. Kind 4 Legacy Encrypted DM check (NIP-04 vs NIP-44)
        if event.kind == 4:
            penalty = 25
            result.privacy_score -= penalty
            result.flags.append("NIP04_LEGACY_ENCRYPTION")
            result.leaks_detected.append({
                "category": "LEGACY_CRYPTO_VULNERABILITY",
                "penalty": penalty,
                "detail": "Event uses deprecated NIP-04 CBC encryption instead of NIP-44 ChaCha20-Poly1305. NIP-04 leaks payload length and lacks authenticated padding."
            })
            result.recommendations.append("Upgrade agent communication to NIP-44 authenticated encryption with deterministic payload padding.")

        # 2. Check for On-Chain Bitcoin Address or TxID Leakage in event content or tags
        btc_addr_pattern = r"\b(bc1[a-z0-9]{38,59}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b"
        matches = re.findall(btc_addr_pattern, event.content)
        for tag in event.tags:
            for val in tag:
                matches.extend(re.findall(btc_addr_pattern, val))

        if matches:
            penalty = 40
            result.privacy_score -= penalty
            result.flags.append("ONCHAIN_ADDRESS_EXPOSURE")
            result.leaks_detected.append({
                "category": "ONCHAIN_IDENTITY_CORRELATION",
                "penalty": penalty,
                "detail": f"Plaintext Bitcoin on-chain address found in Nostr event: {matches[0][:12]}... Gossip relays permanently link your npub to this UTXO."
            })
            result.recommendations.append("Never publish on-chain addresses in unencrypted Nostr events; use ephemeral Lightning invoices or Silent Payments (BIP-352).")

        # 3. NIP-57 Zap Request Anonymity Check
        if event.kind == 9734:
            has_anon_tag = any(tag[0] == "anon" for tag in event.tags if len(tag) > 0)
            if not has_anon_tag:
                penalty = 15
                result.privacy_score -= penalty
                result.flags.append("PUBLIC_ZAP_ATTRIBUTION")
                result.leaks_detected.append({
                    "category": "ECONOMIC_GRAPH_LEAKAGE",
                    "penalty": penalty,
                    "detail": "Zap request includes public sender signature. Observers can map your spending habits and financial relationships."
                })
                result.recommendations.append("Use NIP-57 anonymous zap tag ['anon', ''] for private peer-to-peer microtransactions.")

        # 4. Relay Gossip Fanout Audit
        cleartext_relays = [r for r in event.relays if not r.startswith("onion://") and not ".onion" in r]
        if len(cleartext_relays) > 5:
            penalty = 15
            result.privacy_score -= penalty
            result.flags.append("EXCESSIVE_CLEARNET_FANOUT")
            result.leaks_detected.append({
                "category": "TRAFFIC_CORRELATION_RISK",
                "penalty": penalty,
                "detail": f"Broadcasting simultaneously to {len(cleartext_relays)} clearnet relays enables ISP/timing correlation attacks."
            })
            result.recommendations.append("Limit broadcasting to 2-3 trusted private relays or route gossip over Tor/I2P onion endpoints.")

        result.compute_exposure()
        return result
