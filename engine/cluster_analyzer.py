"""
Uncluster Deterministic UTXO Cluster Analyzer
Evaluates Bitcoin transactions for Common-Input Ownership Heuristics (CIOH),
toxic change leaks, script fingerprinting, and BIP-69 compliance.
Pure Python, zero external dependencies, 100% deterministic.
"""

from typing import List, Dict, Any, Tuple, Optional
import hashlib
import json
from .crypto_models import UTXO, TransactionInput, TransactionOutput, BitcoinTransaction


class PrivacyScoreResult:
    def __init__(self):
        self.overall_score: int = 100  # 0 to 100 Sovereign Rating
        self.privacy_grade: str = "A"   # A, B, C, D, F
        self.common_input_violation: bool = False
        self.cluster_leak_details: List[str] = []
        self.toxic_change_detected: bool = False
        self.toxic_change_reasons: List[str] = []
        self.bip69_compliant: bool = True
        self.script_mismatch_detected: bool = False
        self.deductions: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []

    def compute_grade(self):
        self.overall_score = max(0, min(100, self.overall_score))
        if self.overall_score >= 90:
            self.privacy_grade = "A (SOVEREIGN)"
        elif self.overall_score >= 75:
            self.privacy_grade = "B (LOW EXPOSURE)"
        elif self.overall_score >= 50:
            self.privacy_grade = "C (MODERATE EXPOSURE)"
        elif self.overall_score >= 30:
            self.privacy_grade = "D (HIGH CLUSTER RISK)"
        else:
            self.privacy_grade = "F (CRITICAL PRIVACY BREACH)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "privacy_grade": self.privacy_grade,
            "common_input_violation": self.common_input_violation,
            "cluster_leak_details": self.cluster_leak_details,
            "toxic_change_detected": self.toxic_change_detected,
            "toxic_change_reasons": self.toxic_change_reasons,
            "bip69_compliant": self.bip69_compliant,
            "script_mismatch_detected": self.script_mismatch_detected,
            "deductions": self.deductions,
            "recommendations": self.recommendations,
        }


class UTXOClusterAnalyzer:
    """
    Deterministic privacy auditor for Bitcoin unspent outputs and pending transactions.
    """

    def analyze_transaction(self, tx: BitcoinTransaction) -> PrivacyScoreResult:
        result = PrivacyScoreResult()

        # 1. Common-Input Ownership Heuristic (CIOH) Analysis
        distinct_clusters = set()
        kyc_taint_count = 0
        for inp in tx.inputs:
            distinct_clusters.add(inp.cluster_label)
            if inp.kyc_risk in ("HIGH", "MEDIUM"):
                kyc_taint_count += 1

        if len(tx.inputs) > 1 and len(distinct_clusters) > 1:
            result.common_input_violation = True
            penalty = 40
            result.overall_score -= penalty
            msg = f"CIOH Violation: {len(distinct_clusters)} distinct wallet clusters co-spent: {', '.join(sorted(distinct_clusters))}"
            result.cluster_leak_details.append(msg)
            result.deductions.append({
                "category": "COMMON_INPUT_HEURISTIC",
                "penalty": penalty,
                "reason": "Co-spending inputs from distinct clusters permanently groups all addresses in chain surveillance databases."
            })
            result.recommendations.append("Isolate coin spending: use coin selection to fund this transaction from a single wallet cluster.")

        if kyc_taint_count > 0 and len(distinct_clusters) > 1:
            penalty = 25
            result.overall_score -= penalty
            result.deductions.append({
                "category": "KYC_TAINT_CONTAMINATION",
                "penalty": penalty,
                "reason": f"KYC-linked input ({kyc_taint_count} inputs) co-spent with private coins, deanonymizing the clean UTXOs."
            })
            result.recommendations.append("Do not mix KYC exchange withdrawal outputs with private P2P or mining rewards.")

        # 2. Change Output Analysis & Script Type Mismatches
        input_scripts = set(i.script_type for i in tx.inputs)
        change_outputs = [o for o in tx.outputs if o.is_change]
        destination_outputs = [o for o in tx.outputs if not o.is_change]

        for change in change_outputs:
            # Check script type mismatch (e.g., spending SegWit, returning change as Legacy)
            if input_scripts and change.script_type not in input_scripts:
                result.script_mismatch_detected = True
                result.toxic_change_detected = True
                penalty = 20
                result.overall_score -= penalty
                reason = f"Script Mismatch: Input uses {list(input_scripts)[0]} but change uses {change.script_type}."
                result.toxic_change_reasons.append(reason)
                result.deductions.append({
                    "category": "SCRIPT_TYPE_MISMATCH",
                    "penalty": penalty,
                    "reason": reason + " Blockchain analytics immediately flags the outlier script as change."
                })
                result.recommendations.append(f"Generate change address with identical script type ({list(input_scripts)[0]}).")

            # Check round-number heuristic on destination vs change
            if destination_outputs:
                dest = destination_outputs[0]
                # If destination amount is round (e.g. 100,000 sats) and change is odd (e.g. 43,210 sats),
                # chain analysis easily identifies change.
                if dest.amount_sats % 10_000 == 0 and change.amount_sats % 10_000 != 0:
                    result.toxic_change_detected = True
                    penalty = 10
                    result.overall_score -= penalty
                    reason = f"Round Payment Fingerprint: Destination ({dest.amount_sats:,} sats) is round, revealing change ({change.amount_sats:,} sats)."
                    result.toxic_change_reasons.append(reason)
                    result.deductions.append({
                        "category": "ROUND_PAYMENT_FINGERPRINT",
                        "penalty": penalty,
                        "reason": reason
                    })

            # Check address reuse between inputs and change
            input_addresses = set(i.address for i in tx.inputs)
            if change.address in input_addresses:
                result.toxic_change_detected = True
                penalty = 30
                result.overall_score -= penalty
                reason = f"Change Address Reuse: Change sent back to input address {change.address[:10]}..."
                result.toxic_change_reasons.append(reason)
                result.deductions.append({
                    "category": "ADDRESS_REUSE_DETECTED",
                    "penalty": penalty,
                    "reason": reason
                })
                result.recommendations.append("Never reuse addresses for change outputs; always derive a fresh key.")

        # 3. BIP-69 Lexicographical Ordering Check
        if len(tx.inputs) > 1:
            sorted_inputs = sorted(tx.inputs, key=lambda x: (x.prev_txid, x.prev_vout))
            if tx.inputs != sorted_inputs:
                result.bip69_compliant = False
                penalty = 10
                result.overall_score -= penalty
                result.deductions.append({
                    "category": "BIP69_INPUT_ORDER_VIOLATION",
                    "penalty": penalty,
                    "reason": "Inputs are not lexicographically sorted per BIP-69, revealing specific non-standard wallet software fingerprints."
                })
                result.recommendations.append("Enable BIP-69 deterministic input sorting in your signing pipeline.")

        if len(tx.outputs) > 1:
            sorted_outputs = sorted(tx.outputs, key=lambda x: (x.amount_sats, x.address))
            if tx.outputs != sorted_outputs:
                result.bip69_compliant = False
                penalty = 10
                result.overall_score -= penalty
                result.deductions.append({
                    "category": "BIP69_OUTPUT_ORDER_VIOLATION",
                    "penalty": penalty,
                    "reason": "Outputs are not lexicographically sorted per BIP-69, leaking change position."
                })
                result.recommendations.append("Sort transaction outputs deterministically per BIP-69.")

        result.compute_grade()
        return result

    def sanitize_coin_selection(self, utxo_pool: List[UTXO], target_amount_sats: int, fee_budget_sats: int = 2000) -> Dict[str, Any]:
        """
        Computes a clean, unclustered coin selection that funds target amount from a SINGLE cluster
        without cross-contamination, picking the minimum necessary UTXOs.
        """
        required_sats = target_amount_sats + fee_budget_sats

        # Group UTXOs by cluster label
        clusters: Dict[str, List[UTXO]] = {}
        for u in utxo_pool:
            clusters.setdefault(u.cluster_label, []).append(u)

        # Prioritize clusters with lowest KYC risk and sufficient funds
        candidates = []
        risk_rank = {"CLEAN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

        for label, utxos in clusters.items():
            total_cluster_sats = sum(u.amount_sats for u in utxos)
            if total_cluster_sats >= required_sats:
                kyc_score = max(risk_rank.get(u.kyc_risk, 2) for u in utxos)
                candidates.append((kyc_score, label, utxos, total_cluster_sats))

        candidates.sort(key=lambda x: (x[0], x[3]))

        if not candidates:
            return {
                "success": False,
                "error": f"No single unclustered pool contains sufficient funds ({required_sats:,} sats). Spending requires multi-cluster merging.",
                "selected_utxos": [],
                "cluster_used": None,
                "total_selected_sats": 0,
                "change_sats": 0,
            }

        best_cluster = candidates[0]
        selected_label = best_cluster[1]
        available_utxos = sorted(best_cluster[2], key=lambda u: u.amount_sats)

        # Greedy selection within single cluster
        selected = []
        accumulated = 0
        for u in available_utxos:
            selected.append(u)
            accumulated += u.amount_sats
            if accumulated >= required_sats:
                break

        change_sats = accumulated - required_sats

        return {
            "success": True,
            "cluster_used": selected_label,
            "kyc_risk_level": best_cluster[0],
            "selected_utxos": [u.to_dict() for u in selected],
            "total_selected_sats": accumulated,
            "target_amount_sats": target_amount_sats,
            "fee_budget_sats": fee_budget_sats,
            "change_sats": change_sats,
            "cluster_leak_risk": "ZERO_LEAKAGE (Isolated to single cluster)",
        }
