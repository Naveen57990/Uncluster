#!/usr/bin/env python3
"""
Uncluster - Developer CLI
Zero-Leakage Pre-Flight Bitcoin UTXO Cluster Analyzer & Autonomous Nostr Shield
Pure Python 3, zero external dependencies.
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any

# Ensure project root is in python path
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_parent_root = os.path.abspath(os.path.join(_repo_root, ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
if _parent_root not in sys.path:
    sys.path.insert(0, _parent_root)

try:
    from engine.crypto_models import UTXO, TransactionInput, TransactionOutput, BitcoinTransaction, NostrEvent
    from engine.cluster_analyzer import UTXOClusterAnalyzer
    from engine.nostr_shield import NostrShieldAnalyzer
except ImportError:
    from uncluster.engine.crypto_models import UTXO, TransactionInput, TransactionOutput, BitcoinTransaction, NostrEvent
    from uncluster.engine.cluster_analyzer import UTXOClusterAnalyzer
    from uncluster.engine.nostr_shield import NostrShieldAnalyzer


# Built-in reference test scenarios
SAMPLE_SCENARIOS = {
    "cioh_leak": BitcoinTransaction(
        txid="a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90",
        inputs=[
            TransactionInput(
                prev_txid="7f3c4e1a"*8,
                prev_vout=0,
                address="bc1qkyc_exchange_deposit_01",
                amount_sats=250_000,
                script_type="P2WPKH",
                cluster_label="KYC:Coinbase_Withdrawal",
                kyc_risk="HIGH"
            ),
            TransactionInput(
                prev_txid="9e2d1c0b"*8,
                prev_vout=1,
                address="bc1qmining_pool_payout_02",
                amount_sats=180_000,
                script_type="P2WPKH",
                cluster_label="MINING:Braiins_Pool",
                kyc_risk="CLEAN"
            )
        ],
        outputs=[
            TransactionOutput(
                address="bc1qmerchant_service",
                amount_sats=300_000,
                script_type="P2WPKH",
                is_change=False,
                target_label="External_Payment"
            ),
            TransactionOutput(
                address="bc1qreturn_change_odd",
                amount_sats=128_500,
                script_type="P2WPKH",
                is_change=True,
                target_label="Change_Return"
            )
        ]
    ),
    "script_mismatch": BitcoinTransaction(
        txid="b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1",
        inputs=[
            TransactionInput(
                prev_txid="11223344"*8,
                prev_vout=0,
                address="bc1qnative_segwit_in",
                amount_sats=150_000,
                script_type="P2WPKH",
                cluster_label="WALLET_HOT",
                kyc_risk="LOW"
            )
        ],
        outputs=[
            TransactionOutput(
                address="bc1qmerchant_target",
                amount_sats=85_000,
                script_type="P2WPKH",
                is_change=False
            ),
            TransactionOutput(
                address="1LegacyToxicChangeAddrXYZ",
                amount_sats=63_500,
                script_type="P2PKH",  # Mismatch!
                is_change=True
            )
        ]
    ),
    "sovereign_clean": BitcoinTransaction(
        txid="c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2",
        inputs=[
            TransactionInput(
                prev_txid="aa11bb22"*8,
                prev_vout=0,
                address="bc1qcold_clean_01",
                amount_sats=100_000,
                script_type="P2WPKH",
                cluster_label="VAULT_CLEAN",
                kyc_risk="CLEAN"
            ),
            TransactionInput(
                prev_txid="cc33dd44"*8,
                prev_vout=0,
                address="bc1qcold_clean_02",
                amount_sats=80_000,
                script_type="P2WPKH",
                cluster_label="VAULT_CLEAN",
                kyc_risk="CLEAN"
            )
        ],
        outputs=[
            TransactionOutput(
                address="bc1qfresh_change",
                amount_sats=58_200,
                script_type="P2WPKH",
                is_change=True
            ),
            TransactionOutput(
                address="bc1qpayment_dest",
                amount_sats=120_300,
                script_type="P2WPKH",
                is_change=False
            )
        ]
    )
}

SAMPLE_UTXO_POOL = [
    UTXO(txid="f1"*32, vout=0, amount_sats=50_000, address="bc1qkyc1", script_type="P2WPKH", cluster_label="KYC_EXCHANGE", kyc_risk="HIGH"),
    UTXO(txid="f2"*32, vout=1, amount_sats=80_000, address="bc1qkyc2", script_type="P2WPKH", cluster_label="KYC_EXCHANGE", kyc_risk="HIGH"),
    UTXO(txid="f3"*32, vout=0, amount_sats=120_000, address="bc1qclean1", script_type="P2WPKH", cluster_label="COLD_MINING", kyc_risk="CLEAN"),
    UTXO(txid="f4"*32, vout=1, amount_sats=75_000, address="bc1qclean2", script_type="P2WPKH", cluster_label="COLD_MINING", kyc_risk="CLEAN"),
    UTXO(txid="f5"*32, vout=0, amount_sats=40_000, address="bc1qp2p1", script_type="P2WPKH", cluster_label="P2P_ROBOSATS", kyc_risk="CLEAN"),
]


def render_ascii_header():
    print(r"""
╔═══════════════════════════════════════════════════════════════════════════╗
║   █  █ █▄ █ ▄▀▀ █   █ █ ▄▀▀ ▀█▀ █▀▀ █▀▄   ░▒▓ UNCLUSTER WORKBENCH ▓▒░    ║
║   ▀▄▄▀ █ ▀█ ▀▄▄ █▄▄ ▀▄█ ▄██  █  ██▄ █▀▄   Zero-Leakage Bitcoin Pre-Flight║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)


def format_table_output(tx: BitcoinTransaction, res: Any):
    print(f"TRANSACTION ID : {tx.txid[:24]}...")
    print(f"TOTAL INPUTS   : {len(tx.inputs)} ({tx.total_input_sats:,} sats)")
    print(f"TOTAL OUTPUTS  : {len(tx.outputs)} ({tx.total_output_sats:,} sats | Fee: {tx.fee_sats:,} sats)")
    print("-" * 75)
    print(f"PRIVACY SCORE  : [{res.overall_score}/100]  GRADE: {res.privacy_grade}")
    print(f"CIOH VIOLATION : {'YES (CRITICAL)' if res.common_input_violation else 'NO (CLEAN)'}")
    print(f"TOXIC CHANGE   : {'DETECTED' if res.toxic_change_detected else 'NONE'}")
    print(f"BIP-69 SORTED  : {'COMPLIANT' if res.bip69_compliant else 'NON-COMPLIANT'}")
    print("=" * 75)

    if res.deductions:
        print("EXPOSURE VULNERABILITIES DETECTED:")
        for idx, d in enumerate(res.deductions, 1):
            print(f"  [{idx}] -{d['penalty']} pts | {d['category']}:")
            print(f"      Reason: {d['reason']}")
    else:
        print("✓ Zero privacy regressions detected. Transaction is sovereign.")

    if res.recommendations:
        print("\nRECOMMENDED ACTIONS:")
        for r in res.recommendations:
            print(f"  • {r}")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Uncluster - Zero-Leakage Pre-Flight Bitcoin UTXO Cluster Analyzer")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: audit
    audit_parser = subparsers.add_parser("audit", help="Audit pending transaction or PSBT for cluster leakage")
    audit_parser.add_argument("--scenario", choices=["cioh_leak", "script_mismatch", "sovereign_clean"], default="cioh_leak", help="Built-in test scenario")
    audit_parser.add_argument("--format", choices=["table", "json", "markdown"], default="table", help="Output format")

    # Command: sanitize
    sanitize_parser = subparsers.add_parser("sanitize", help="Compute unclustered coin selection from UTXO pool")
    sanitize_parser.add_argument("--amount", type=int, default=100_000, help="Target payment amount in satoshis")
    sanitize_parser.add_argument("--fee", type=int, default=2_000, help="Fee budget in satoshis")

    # Command: nostr
    nostr_parser = subparsers.add_parser("nostr-check", help="Audit Nostr agent event for metadata and identity leaks")
    nostr_parser.add_argument("--leak", action="store_true", help="Audit sample event with on-chain address leak")

    args = parser.parse_args()
    analyzer = UTXOClusterAnalyzer()

    if args.command == "audit" or not args.command:
        scenario_key = getattr(args, "scenario", "cioh_leak")
        tx = SAMPLE_SCENARIOS[scenario_key]
        res = analyzer.analyze_transaction(tx)

        if getattr(args, "format", "table") == "json":
            out = {
                "transaction": tx.to_dict(),
                "audit": res.to_dict()
            }
            print(json.dumps(out, indent=2))
        elif getattr(args, "format", "table") == "markdown":
            print(f"# Uncluster Audit Report: {tx.txid[:16]}...\n")
            print(f"- **Score**: {res.overall_score}/100 ({res.privacy_grade})")
            print(f"- **CIOH Violation**: {res.common_input_violation}")
            print(f"- **Toxic Change**: {res.toxic_change_detected}")
            print(f"- **BIP-69 Compliant**: {res.bip69_compliant}\n")
            print("### Deductions")
            for d in res.deductions:
                print(f"- `- {d['penalty']} pts`: {d['category']} — {d['reason']}")
        else:
            render_ascii_header()
            format_table_output(tx, res)

        sys.exit(0 if res.overall_score >= 75 else 1)

    elif args.command == "sanitize":
        render_ascii_header()
        res = analyzer.sanitize_coin_selection(SAMPLE_UTXO_POOL, args.amount, args.fee)
        print(f"TARGET PAYMENT : {args.amount:,} sats (Fee: {args.fee:,} sats)")
        print("-" * 75)
        if res["success"]:
            print(f"STATUS         : SUCCESS — ZERO CLUSTER MERGING")
            print(f"ISOLATED CLUSTER: {res['cluster_used']}")
            print(f"SELECTED UTXOS : {len(res['selected_utxos'])} coins (Total: {res['total_selected_sats']:,} sats)")
            print(f"CHANGE RETURN  : {res['change_sats']:,} sats")
            print("-" * 75)
            for idx, u in enumerate(res["selected_utxos"], 1):
                print(f"  Coin #{idx}: {u['outpoint'][:20]}... | {u['amount_sats']:,} sats [{u['script_type']}]")
        else:
            print(f"STATUS : FAILED — {res['error']}")
        print("=" * 75)
        sys.exit(0 if res["success"] else 1)

    elif args.command == "nostr-check":
        render_ascii_header()
        shield = NostrShieldAnalyzer()
        if args.leak:
            event = NostrEvent(
                id="event_leaky_99",
                pubkey="npub1agentleaker888",
                created_at=1727390000,
                kind=1,
                content="Please settle our agent consulting fee to bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq on L1.",
                relays=["wss://nos.lol", "wss://relay.damus.io"]
            )
        else:
            event = NostrEvent(
                id="event_sovereign_01",
                pubkey="npub1sovereignagent007",
                created_at=1727390000,
                kind=1,
                content="Autonomous settlement verified via ChaCha20 authenticated envelope.",
                relays=["wss://relay.nostr.band"]
            )
        res = shield.audit_event(event)
        print(f"NOSTR EVENT ID : {event.id}")
        print(f"PUBKEY         : {event.pubkey}")
        print(f"PRIVACY SCORE  : [{res.privacy_score}/100]  EXPOSURE: {res.exposure_level}")
        print("-" * 75)
        if res.leaks_detected:
            for l in res.leaks_detected:
                print(f"  ! {l['category']} (-{l['penalty']} pts): {l['detail']}")
        else:
            print("✓ Zero metadata or on-chain identity linkage detected in Nostr event.")
        print("=" * 75)


if __name__ == "__main__":
    main()
