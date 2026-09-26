"""
Uncluster Cryptographic Data Models
Pure Python representations of UTXOs, Bitcoin Transactions, and Nostr Protocol Events.
Zero external dependencies, 100% deterministic and portable.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import hashlib
import json


@dataclass
class UTXO:
    txid: str
    vout: int
    amount_sats: int
    address: str
    script_type: str  # P2WPKH, P2TR, P2SH-P2WPKH, P2PKH
    cluster_label: str  # e.g., "KYC_EXCHANGE", "MINING_POOL", "P2P_TRADE", "CLEAN_COINJOIN"
    kyc_risk: str  # "HIGH", "MEDIUM", "LOW", "CLEAN"
    confirmations: int = 144

    def outpoint(self) -> str:
        return f"{self.txid}:{self.vout}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "txid": self.txid,
            "vout": self.vout,
            "outpoint": self.outpoint(),
            "amount_sats": self.amount_sats,
            "amount_btc": round(self.amount_sats / 100_000_000, 8),
            "address": self.address,
            "script_type": self.script_type,
            "cluster_label": self.cluster_label,
            "kyc_risk": self.kyc_risk,
            "confirmations": self.confirmations,
        }


@dataclass
class TransactionInput:
    prev_txid: str
    prev_vout: int
    address: str
    amount_sats: int
    script_type: str
    cluster_label: str
    kyc_risk: str

    def outpoint(self) -> str:
        return f"{self.prev_txid}:{self.prev_vout}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prev_txid": self.prev_txid,
            "prev_vout": self.prev_vout,
            "outpoint": self.outpoint(),
            "address": self.address,
            "amount_sats": self.amount_sats,
            "script_type": self.script_type,
            "cluster_label": self.cluster_label,
            "kyc_risk": self.kyc_risk,
        }


@dataclass
class TransactionOutput:
    address: str
    amount_sats: int
    script_type: str
    is_change: bool = False
    target_label: str = "Destination"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": self.address,
            "amount_sats": self.amount_sats,
            "amount_btc": round(self.amount_sats / 100_000_000, 8),
            "script_type": self.script_type,
            "is_change": self.is_change,
            "target_label": self.target_label,
        }


@dataclass
class BitcoinTransaction:
    txid: str
    inputs: List[TransactionInput]
    outputs: List[TransactionOutput]
    locktime: int = 0
    version: int = 2

    @property
    def total_input_sats(self) -> int:
        return sum(i.amount_sats for i in self.inputs)

    @property
    def total_output_sats(self) -> int:
        return sum(o.amount_sats for o in self.outputs)

    @property
    def fee_sats(self) -> int:
        return max(0, self.total_input_sats - self.total_output_sats)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "txid": self.txid,
            "version": self.version,
            "locktime": self.locktime,
            "total_input_sats": self.total_input_sats,
            "total_output_sats": self.total_output_sats,
            "fee_sats": self.fee_sats,
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
        }


@dataclass
class NostrEvent:
    id: str
    pubkey: str
    created_at: int
    kind: int
    tags: List[List[str]] = field(default_factory=list)
    content: str = ""
    sig: str = ""
    relays: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pubkey": self.pubkey,
            "created_at": self.created_at,
            "kind": self.kind,
            "tags": self.tags,
            "content": self.content,
            "sig": self.sig,
            "relays": self.relays,
        }
