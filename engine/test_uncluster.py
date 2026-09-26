"""
Unit Tests for Uncluster Deterministic Engine
Verifies CIOH detection, toxic change identification, BIP-69 compliance,
sanitized coin selection, and Nostr agent exposure auditing.
"""

import unittest
import sys
import os

# Add repo root and parent directory to sys.path for universal portability
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


class TestUnclusterEngine(unittest.TestCase):

    def setUp(self):
        self.analyzer = UTXOClusterAnalyzer()
        self.nostr_shield = NostrShieldAnalyzer()

    def test_single_cluster_clean_transaction(self):
        """Test a clean transaction with inputs from the same cluster and matched script change."""
        tx = BitcoinTransaction(
            txid="11" * 32,
            inputs=[
                TransactionInput(
                    prev_txid="aa" * 32,
                    prev_vout=0,
                    address="bc1qclean01",
                    amount_sats=100_000,
                    script_type="P2WPKH",
                    cluster_label="COLD_STORAGE",
                    kyc_risk="CLEAN"
                ),
                TransactionInput(
                    prev_txid="bb" * 32,
                    prev_vout=1,
                    address="bc1qclean02",
                    amount_sats=50_000,
                    script_type="P2WPKH",
                    cluster_label="COLD_STORAGE",
                    kyc_risk="CLEAN"
                )
            ],
            outputs=[
                TransactionOutput(
                    address="bc1qfreshchange",
                    amount_sats=68_250,
                    script_type="P2WPKH",
                    is_change=True
                ),
                TransactionOutput(
                    address="bc1qmerchant",
                    amount_sats=79_750,
                    script_type="P2WPKH",
                    is_change=False
                )
            ]
        )
        res = self.analyzer.analyze_transaction(tx)
        self.assertEqual(res.overall_score, 100)
        self.assertFalse(res.common_input_violation)
        self.assertFalse(res.toxic_change_detected)
        self.assertIn("A", res.privacy_grade)

    def test_cioh_violation_detection(self):
        """Test detection of Common-Input Ownership Heuristic (merging KYC with private coins)."""
        tx = BitcoinTransaction(
            txid="22" * 32,
            inputs=[
                TransactionInput(
                    prev_txid="cc" * 32,
                    prev_vout=0,
                    address="bc1qkyc_binance",
                    amount_sats=200_000,
                    script_type="P2WPKH",
                    cluster_label="KYC:Binance_Withdrawal",
                    kyc_risk="HIGH"
                ),
                TransactionInput(
                    prev_txid="dd" * 32,
                    prev_vout=0,
                    address="bc1qmining_braiins",
                    amount_sats=150_000,
                    script_type="P2WPKH",
                    cluster_label="MINING:Braiins_Pool",
                    kyc_risk="CLEAN"
                )
            ],
            outputs=[
                TransactionOutput(
                    address="bc1qrecipient",
                    amount_sats=300_000,
                    script_type="P2WPKH",
                    is_change=False
                )
            ]
        )
        res = self.analyzer.analyze_transaction(tx)
        self.assertTrue(res.common_input_violation)
        self.assertLess(res.overall_score, 50)
        self.assertIn("CIOH Violation", res.cluster_leak_details[0])

    def test_toxic_change_script_mismatch(self):
        """Test detection of script type mismatch (spending SegWit, returning change as Legacy)."""
        tx = BitcoinTransaction(
            txid="33" * 32,
            inputs=[
                TransactionInput(
                    prev_txid="ee" * 32,
                    prev_vout=0,
                    address="bc1qsegwit_in",
                    amount_sats=100_000,
                    script_type="P2WPKH",
                    cluster_label="WALLET_A",
                    kyc_risk="LOW"
                )
            ],
            outputs=[
                TransactionOutput(
                    address="bc1qrecipient",
                    amount_sats=40_000,
                    script_type="P2WPKH",
                    is_change=False
                ),
                TransactionOutput(
                    address="1LegacyChangeAddress123",
                    amount_sats=58_000,
                    script_type="P2PKH",
                    is_change=True
                )
            ]
        )
        res = self.analyzer.analyze_transaction(tx)
        self.assertTrue(res.toxic_change_detected)
        self.assertTrue(res.script_mismatch_detected)
        self.assertLess(res.overall_score, 90)

    def test_toxic_change_address_reuse(self):
        """Test detection of address reuse for change."""
        reused_addr = "bc1qreusedaddress"
        tx = BitcoinTransaction(
            txid="44" * 32,
            inputs=[
                TransactionInput(
                    prev_txid="ff" * 32,
                    prev_vout=0,
                    address=reused_addr,
                    amount_sats=80_000,
                    script_type="P2WPKH",
                    cluster_label="WALLET_A",
                    kyc_risk="LOW"
                )
            ],
            outputs=[
                TransactionOutput(
                    address="bc1qtarget",
                    amount_sats=50_000,
                    script_type="P2WPKH",
                    is_change=False
                ),
                TransactionOutput(
                    address=reused_addr,  # Reused!
                    amount_sats=28_000,
                    script_type="P2WPKH",
                    is_change=True
                )
            ]
        )
        res = self.analyzer.analyze_transaction(tx)
        self.assertTrue(res.toxic_change_detected)
        reasons = " ".join(res.toxic_change_reasons)
        self.assertIn("Reuse", reasons)

    def test_bip69_sorting_validation(self):
        """Test detection of non-lexicographical input and output ordering."""
        # Unsorted inputs: 'zz' comes before 'aa'
        tx = BitcoinTransaction(
            txid="55" * 32,
            inputs=[
                TransactionInput(
                    prev_txid="zz" * 32,
                    prev_vout=0,
                    address="bc1qin1",
                    amount_sats=50_000,
                    script_type="P2WPKH",
                    cluster_label="POOL",
                    kyc_risk="CLEAN"
                ),
                TransactionInput(
                    prev_txid="aa" * 32,
                    prev_vout=0,
                    address="bc1qin2",
                    amount_sats=50_000,
                    script_type="P2WPKH",
                    cluster_label="POOL",
                    kyc_risk="CLEAN"
                )
            ],
            outputs=[
                TransactionOutput(address="bc1qout", amount_sats=95_000, script_type="P2WPKH")
            ]
        )
        res = self.analyzer.analyze_transaction(tx)
        self.assertFalse(res.bip69_compliant)

    def test_sanitized_coin_selection(self):
        """Test coin selection picking UTXOs strictly from a single cluster without mixing."""
        utxos = [
            UTXO(txid="11"*32, vout=0, amount_sats=40_000, address="addr1", script_type="P2WPKH", cluster_label="KYC_COINS", kyc_risk="HIGH"),
            UTXO(txid="12"*32, vout=0, amount_sats=30_000, address="addr2", script_type="P2WPKH", cluster_label="KYC_COINS", kyc_risk="HIGH"),
            UTXO(txid="21"*32, vout=0, amount_sats=120_000, address="addr3", script_type="P2WPKH", cluster_label="CLEAN_MINING", kyc_risk="CLEAN"),
            UTXO(txid="22"*32, vout=0, amount_sats=50_000, address="addr4", script_type="P2WPKH", cluster_label="CLEAN_MINING", kyc_risk="CLEAN"),
        ]

        selection = self.analyzer.sanitize_coin_selection(utxos, target_amount_sats=100_000, fee_budget_sats=2_000)
        self.assertTrue(selection["success"])
        self.assertEqual(selection["cluster_used"], "CLEAN_MINING")
        self.assertGreaterEqual(selection["total_selected_sats"], 102_000)

    def test_nostr_shield_onchain_leak(self):
        """Test Nostr shield detecting plaintext on-chain Bitcoin address in event content."""
        event = NostrEvent(
            id="event123",
            pubkey="npub1testagent",
            created_at=1720000000,
            kind=1,
            content="Please pay our agent invoice to bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq immediately.",
            relays=["wss://nos.lol"]
        )
        audit = self.nostr_shield.audit_event(event)
        self.assertIn("ONCHAIN_ADDRESS_EXPOSURE", audit.flags)
        self.assertLess(audit.privacy_score, 70)

    def test_nostr_shield_nip04_warning(self):
        """Test Nostr shield warning about legacy NIP-04 encryption."""
        event = NostrEvent(
            id="event456",
            pubkey="npub1agent2",
            created_at=1720000000,
            kind=4,  # Kind 4 is legacy NIP-04 DM
            content="?iv=1234567890abcdef==?ciphertext",
            relays=["wss://nos.lol"]
        )
        audit = self.nostr_shield.audit_event(event)
        self.assertIn("NIP04_LEGACY_ENCRYPTION", audit.flags)


if __name__ == "__main__":
    unittest.main()
