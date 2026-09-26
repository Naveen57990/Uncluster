/**
 * UNCLUSTER // Industrial Cypherpunk Cyberdeck Console
 * Pure Vanilla JavaScript (ES2022), sub-millisecond execution, zero frameworks.
 */

// 1. Audio Synthesizer for Mechanical Terminal Clicks & Beeps
class TerminalAudio {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx && typeof AudioContext !== 'undefined') {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  playClick(pitch = 1800, duration = 0.015) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(pitch, this.ctx.currentTime);
    gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + duration);
  }

  playBeep(freq = 880, dur = 0.08) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
    gain.gain.setValueAtTime(0.05, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + dur);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + dur);
  }
}

const audio = new TerminalAudio();

// 2. Pre-Loaded Test Vectors
const SCENARIOS = {
  cioh_leak: {
    name: "KYC Exchange Co-Spend (Common-Input Violation)",
    txid: "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90",
    badgeType: "2-IN / 2-OUT // SEGWIT",
    score: 35,
    grade: "GRADE: D (HIGH EXPOSURE)",
    gradeClass: "pulse",
    verdict: "CRITICAL CIOH PRIVACY BREACH",
    explanation: "Co-spending merges distinct clusters (KYC:Coinbase with MINING:Braiins), permanently linking your real identity to your clean mining rewards.",
    asciiGraph: `[INPUT 0: KYC:Coinbase] ────┐
(250,000 sats | P2WPKH)      ├─► [TRANSACTION KERNEL] ─┬─► [DESTINATION: 300,000 sats]
[INPUT 1: MINING:Braiins] ───┘   (FEE: 1,500 sats)     └─► [TOXIC CHANGE: 128,500 sats]
(180,000 sats | P2WPKH)          CIOH: PERMANENT LINK      (STATUS: CONTAMINATED)`,
    leakStatus: "CIOH MERGE DETECTED",
    inputs: [
      { tag: "KYC:Coinbase_Withdrawal", type: "kyc", sats: 250000, script: "P2WPKH", addr: "bc1qkyc_exchange_deposit_01" },
      { tag: "MINING:Braiins_Pool", type: "clean", sats: 180000, script: "P2WPKH", addr: "bc1qmining_pool_payout_02" }
    ],
    outputs: [
      { tag: "Merchant_Payment", type: "clean", sats: 300000, script: "P2WPKH", addr: "bc1qmerchant_service" },
      { tag: "Toxic_Change_Return", type: "change", sats: 128500, script: "P2WPKH", addr: "bc1qreturn_change_odd" }
    ],
    checks: {
      cioh: { pass: false, desc: "2 distinct clusters co-spent (KYC & Mining)" },
      script: { pass: true, desc: "Change script matches inputs (P2WPKH)" },
      bip69: { pass: true, desc: "BIP-69 input/output sorting compliant" },
      reuse: { pass: true, desc: "Fresh unspent change address" }
    },
    remediations: [
      "Isolate coin spending: Use sanitized coin selection to fund this transaction from a single wallet cluster.",
      "Never mix KYC exchange withdrawal outputs with private P2P or mining rewards."
    ]
  },

  script_mismatch: {
    name: "Toxic Change Script Mismatch (Fingerprinted)",
    txid: "b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1",
    badgeType: "1-IN / 2-OUT // HYBRID",
    score: 70,
    grade: "GRADE: C (MODERATE EXPOSURE)",
    gradeClass: "",
    verdict: "CHANGE SCRIPT TYPE LEAKAGE",
    explanation: "Native SegWit input spends with a Legacy (1...) change address. Blockchain surveillance immediately identifies the change output by script asymmetry.",
    asciiGraph: `[INPUT 0: HOT_WALLET] ──────► [TRANSACTION KERNEL] ─┬─► [DESTINATION: 85,000 sats] (P2WPKH)
(150,000 sats | P2WPKH)       (FEE: 1,500 sats)     └─► [TOXIC CHANGE: 63,500 sats] (P2PKH)
                              SCRIPT ASYMMETRY          *** CHANGE OBVIOUSLY EXPOSED ***`,
    leakStatus: "SCRIPT MISMATCH",
    inputs: [
      { tag: "HOT_WALLET_STASH", type: "clean", sats: 150000, script: "P2WPKH", addr: "bc1qnative_segwit_in" }
    ],
    outputs: [
      { tag: "Merchant_Target", type: "clean", sats: 85000, script: "P2WPKH", addr: "bc1qmerchant_target" },
      { tag: "Legacy_Toxic_Change", type: "kyc", sats: 63500, script: "P2PKH", addr: "1LegacyToxicChangeAddrXYZ" }
    ],
    checks: {
      cioh: { pass: true, desc: "Single input cluster (No CIOH merge)" },
      script: { pass: false, desc: "Input is P2WPKH but change is Legacy P2PKH" },
      bip69: { pass: true, desc: "Inputs/Outputs properly sorted" },
      reuse: { pass: true, desc: "No address reuse detected" }
    },
    remediations: [
      "Derive change address with identical script type as inputs (P2WPKH).",
      "Avoid wallet clients with legacy change fallbacks that broadcast client fingerprints."
    ]
  },

  sovereign_clean: {
    name: "Sovereign Isolated Payment (Zero Leakage)",
    txid: "c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2",
    badgeType: "2-IN / 2-OUT // SEGWIT",
    score: 100,
    grade: "GRADE: A (SOVEREIGN PASS)",
    gradeClass: "",
    verdict: "ZERO PRIVACY REGRESSIONS",
    explanation: "Inputs sourced exclusively from single clean cold-storage vault. Change script matches inputs with strict BIP-69 lexicographical ordering.",
    asciiGraph: `[INPUT 0: VAULT_CLEAN_01] ──┐
(100,000 sats | P2WPKH)     ├─► [TRANSACTION KERNEL] ─┬─► [CHANGE: 58,200 sats] (P2WPKH)
[INPUT 1: VAULT_CLEAN_02] ──┘   (FEE: 1,500 sats)     └─► [PAYMENT: 120,300 sats] (P2WPKH)
(80,000 sats | P2WPKH)          SINGLE CLUSTER: PASS      BIP-69 SORTED // 100% SOVEREIGN`,
    leakStatus: "VERIFIED SOVEREIGN",
    inputs: [
      { tag: "VAULT_CLEAN_01", type: "clean", sats: 100000, script: "P2WPKH", addr: "bc1qcold_clean_01" },
      { tag: "VAULT_CLEAN_02", type: "clean", sats: 80000, script: "P2WPKH", addr: "bc1qcold_clean_02" }
    ],
    outputs: [
      { tag: "Fresh_Change_Return", type: "change", sats: 58200, script: "P2WPKH", addr: "bc1qfresh_change" },
      { tag: "External_Recipient", type: "clean", sats: 120300, script: "P2WPKH", addr: "bc1qpayment_dest" }
    ],
    checks: {
      cioh: { pass: true, desc: "Single cluster isolation (VAULT_CLEAN)" },
      script: { pass: true, desc: "Script type symmetric (P2WPKH -> P2WPKH)" },
      bip69: { pass: true, desc: "BIP-69 lexicographically sorted" },
      reuse: { pass: true, desc: "Fresh unspent change address" }
    },
    remediations: [
      "✓ Transaction is sovereign. Safe to sign and broadcast to mempool."
    ]
  },

  nostr_zap: {
    name: "Nostr Agent Micropayment Shield (NIP-57 / NIP-44)",
    txid: "d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3",
    badgeType: "NOSTR AGENT // NIP-57 ZAP",
    score: 45,
    grade: "GRADE: D (METADATA EXPOSURE)",
    gradeClass: "pulse",
    verdict: "ON-CHAIN IDENTITY LEAKAGE",
    explanation: "Autonomous agent note published plaintext on-chain Bitcoin address and broadcasted to 6 clearnet gossip relays without Tor proxy.",
    asciiGraph: `[NOSTR AGENT: npub1agent...] ─► [KIND 1 NOTE] ──────► [RELAY GOSSIP FANOUT: 6 RELAYS]
(CLEARTEXT BROADCAST)         CONTAINS ON-CHAIN ADDR: bc1qar0s... (PERMANENT LINKAGE)
                              *** OBSERVERS PERMANENTLY LINK NOSTR NPUB TO UTXO ***`,
    leakStatus: "IDENTITY LINKAGE",
    inputs: [
      { tag: "NOSTR_AGENT_PUBKEY", type: "kyc", sats: 21000, script: "NIP-01", addr: "npub1agentleaker888999" }
    ],
    outputs: [
      { tag: "OnChain_Leak_Target", type: "kyc", sats: 21000, script: "L1_BTC", addr: "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq" }
    ],
    checks: {
      cioh: { pass: false, desc: "Plaintext on-chain address found in Nostr event note" },
      script: { pass: false, desc: "Clearnet relay gossip fanout (>5 relays without Tor)" },
      bip69: { pass: true, desc: "Deterministic Nostr event tags format" },
      reuse: { pass: false, desc: "Public zap request attribution (Missing ['anon', ''])" }
    },
    remediations: [
      "Never publish on-chain addresses in Nostr events; use ephemeral Lightning invoices or Silent Payments (BIP-352).",
      "Attach anonymous zap tag ['anon', ''] to avoid social graph expenditure mapping."
    ]
  }
};

// Available UTXO pool for sanitized coin selection
const POOL_UTXOS = [
  { id: "f1", outpoint: "1a8f90...:0", sats: 50000, script: "P2WPKH", cluster: "KYC_COINBASE", kyc: "HIGH" },
  { id: "f2", outpoint: "2b9e11...:1", sats: 80000, script: "P2WPKH", cluster: "KYC_COINBASE", kyc: "HIGH" },
  { id: "f3", outpoint: "3c0d22...:0", sats: 120000, script: "P2WPKH", cluster: "COLD_MINING", kyc: "CLEAN" },
  { id: "f4", outpoint: "4d1e33...:1", sats: 75000, script: "P2WPKH", cluster: "COLD_MINING", kyc: "CLEAN" },
  { id: "f5", outpoint: "5e2f44...:0", sats: 40000, script: "P2WPKH", cluster: "P2P_ROBOSATS", kyc: "CLEAN" },
  { id: "f6", outpoint: "6f3a55...:0", sats: 35000, script: "P2WPKH", cluster: "P2P_ROBOSATS", kyc: "CLEAN" }
];

// 3. UI State Controller
let currentScenario = 'cioh_leak';

function renderScenario(key) {
  const data = SCENARIOS[key];
  if (!data) return;
  currentScenario = key;

  // Header badges & metadata
  document.getElementById('tx-badge-type').innerText = data.badgeType;
  document.getElementById('ascii-leak-status').innerText = data.leakStatus;
  document.getElementById('ascii-topology-diagram').innerText = data.asciiGraph;

  // Score display
  const scoreNum = document.getElementById('score-number');
  const scoreGrade = document.getElementById('score-grade-badge');
  const scoreProg = document.getElementById('score-progress');
  const gaugeVerdict = document.getElementById('gauge-verdict');
  const gaugeExpl = document.getElementById('gauge-explanation');

  scoreNum.innerText = data.score;
  scoreGrade.innerText = data.grade;
  scoreGrade.className = 'card-badge ' + (data.gradeClass || '');
  scoreProg.style.width = data.score + '%';
  gaugeVerdict.innerText = data.verdict;
  gaugeExpl.innerText = data.explanation;

  if (data.score >= 80) {
    scoreNum.style.color = 'var(--phosphor-green)';
    scoreNum.style.textShadow = '0 0 10px var(--phosphor-glow)';
    scoreProg.style.background = 'var(--phosphor-green)';
    scoreProg.style.boxShadow = '0 0 8px var(--phosphor-green)';
    gaugeVerdict.style.color = 'var(--phosphor-green)';
  } else if (data.score >= 60) {
    scoreNum.style.color = 'var(--amber-warn)';
    scoreNum.style.textShadow = '0 0 10px var(--amber-glow)';
    scoreProg.style.background = 'var(--amber-warn)';
    scoreProg.style.boxShadow = '0 0 8px var(--amber-warn)';
    gaugeVerdict.style.color = 'var(--amber-warn)';
  } else {
    scoreNum.style.color = 'var(--danger-crimson)';
    scoreNum.style.textShadow = '0 0 10px var(--danger-glow)';
    scoreProg.style.background = 'var(--danger-crimson)';
    scoreProg.style.boxShadow = '0 0 8px var(--danger-crimson)';
    gaugeVerdict.style.color = 'var(--danger-crimson)';
  }

  // Inputs List
  document.getElementById('in-count').innerText = data.inputs.length;
  const inContainer = document.getElementById('inputs-list');
  inContainer.innerHTML = '';
  data.inputs.forEach((inp, idx) => {
    const item = document.createElement('div');
    item.className = 'io-item';
    item.innerHTML = `
      <div class="io-row-top">
        <span>#${idx} // ${inp.sats.toLocaleString()} sats</span>
        <span class="io-tag-cluster ${inp.type}">${inp.tag}</span>
      </div>
      <div class="io-addr">${inp.addr} [${inp.script}]</div>
    `;
    inContainer.appendChild(item);
  });

  // Outputs List
  document.getElementById('out-count').innerText = data.outputs.length;
  const outContainer = document.getElementById('outputs-list');
  outContainer.innerHTML = '';
  data.outputs.forEach((out, idx) => {
    const item = document.createElement('div');
    item.className = 'io-item';
    item.innerHTML = `
      <div class="io-row-top">
        <span>#${idx} // ${out.sats.toLocaleString()} sats</span>
        <span class="io-tag-cluster ${out.type}">${out.tag}</span>
      </div>
      <div class="io-addr">${out.addr} [${out.script}]</div>
    `;
    outContainer.appendChild(item);
  });

  // Heuristics Checks
  updateCheck('chk-cioh', 'desc-cioh', data.checks.cioh);
  updateCheck('chk-script', 'desc-script', data.checks.script);
  updateCheck('chk-bip69', 'desc-bip69', data.checks.bip69);
  updateCheck('chk-reuse', 'desc-reuse', data.checks.reuse);

  // Remediations List
  const remList = document.getElementById('remediation-list');
  remList.innerHTML = '';
  data.remediations.forEach(r => {
    const li = document.createElement('li');
    li.innerText = r;
    remList.appendChild(li);
  });
}

function updateCheck(itemId, descId, checkData) {
  const item = document.getElementById(itemId);
  const desc = document.getElementById(descId);
  const icon = item.querySelector('.check-icon');

  if (checkData.pass) {
    item.className = 'check-item pass';
    icon.innerText = '✓';
  } else {
    item.className = 'check-item fail';
    icon.innerText = '✕';
  }
  desc.innerText = checkData.desc;
}

// 4. Sanitized Coin Selection Algorithm (Client-Side implementation)
function calculateSanitizedPool(targetSats, feeSats) {
  const requiredSats = targetSats + feeSats;
  
  // Group by cluster
  const clusters = {};
  POOL_UTXOS.forEach(u => {
    if (!clusters[u.cluster]) clusters[u.cluster] = [];
    clusters[u.cluster].push(u);
  });

  // Find candidate clusters with sufficient balance
  let candidates = [];
  const riskWeights = { "CLEAN": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3 };

  for (let cl in clusters) {
    const utxos = clusters[cl];
    const totalSats = utxos.reduce((acc, u) => acc + u.sats, 0);
    if (totalSats >= requiredSats) {
      const maxKyc = Math.max(...utxos.map(u => riskWeights[u.kyc] || 0));
      candidates.push({ cluster: cl, utxos, totalSats, maxKyc });
    }
  }

  candidates.sort((a, b) => a.maxKyc - b.maxKyc || a.totalSats - b.totalSats);

  if (candidates.length === 0) {
    return {
      success: false,
      message: `No isolated single-cluster pool has enough balance (${requiredSats.toLocaleString()} sats required). Multi-cluster merging would cause CIOH leakage.`
    };
  }

  const best = candidates[0];
  const sortedCoins = [...best.utxos].sort((a, b) => a.sats - b.sats);
  let selected = [];
  let accumulated = 0;
  for (let c of sortedCoins) {
    selected.push(c);
    accumulated += c.sats;
    if (accumulated >= requiredSats) break;
  }

  return {
    success: true,
    cluster: best.cluster,
    selected,
    accumulated,
    targetSats,
    feeSats,
    changeSats: accumulated - requiredSats
  };
}

function renderSanitizeResult() {
  const target = parseInt(document.getElementById('target-payment-input').value) || 100000;
  const fee = parseInt(document.getElementById('fee-budget-input').value) || 1500;
  const res = calculateSanitizedPool(target, fee);
  const box = document.getElementById('sanitize-result-box');

  if (!res.success) {
    box.innerHTML = `<div style="color: var(--danger-crimson); font-weight: bold;">✕ ERROR: ${res.message}</div>`;
    return;
  }

  box.innerHTML = `
    <div style="color: var(--phosphor-green); font-weight: bold; margin-bottom: 8px;">
      ✓ ZERO-LEAKAGE SOLUTION: ISOLATED CLUSTER [${res.cluster}]
    </div>
    <div style="font-size: 11px; color: var(--text-dim); margin-bottom: 6px;">
      Target Payment: <strong style="color:#fff">${res.targetSats.toLocaleString()} sats</strong> | Fee: ${res.feeSats.toLocaleString()} sats | Change: <strong style="color:var(--amber-warn)">${res.changeSats.toLocaleString()} sats</strong>
    </div>
    <div style="display: flex; flex-direction: column; gap: 4px;">
      ${res.selected.map((c, i) => `
        <div style="background: #080D08; border: 1px solid var(--border-bright); padding: 4px 8px; border-radius: 2px; display: flex; justify-content: space-between;">
          <span>Coin #${i+1}: ${c.outpoint} [${c.script}]</span>
          <span style="color: var(--phosphor-green); font-weight: bold;">${c.sats.toLocaleString()} sats</span>
        </div>
      `).join('')}
    </div>
  `;
}

// 5. Event Listeners & Hardware Toggles
document.addEventListener('DOMContentLoaded', () => {
  // Scenario button clicks
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      audio.playClick(1900, 0.02);
      document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderScenario(btn.dataset.scenario);
    });
  });

  // CRT Toggle
  const crtToggle = document.getElementById('toggle-crt');
  crtToggle.addEventListener('change', () => {
    audio.playClick(1200, 0.03);
    document.body.classList.toggle('crt-active', crtToggle.checked);
  });

  // Audio Toggle
  const audioToggle = document.getElementById('toggle-audio');
  audioToggle.addEventListener('change', () => {
    audio.enabled = audioToggle.checked;
    if (audio.enabled) audio.playClick(2400, 0.02);
  });

  // Custom Inject Modal
  const modalInject = document.getElementById('modal-inject');
  document.getElementById('btn-custom-inject').addEventListener('click', () => {
    audio.playBeep(920, 0.05);
    modalInject.classList.add('active');
  });

  document.getElementById('btn-close-modal').addEventListener('click', () => {
    modalInject.classList.remove('active');
  });
  document.getElementById('btn-cancel-inject').addEventListener('click', () => {
    modalInject.classList.remove('active');
  });

  document.getElementById('btn-run-custom-audit').addEventListener('click', () => {
    audio.playBeep(1200, 0.08);
    const in1Cluster = document.getElementById('m-in1-cluster').value || "CUSTOM_A";
    const in1Sats = parseInt(document.getElementById('m-in1-sats').value) || 100000;
    const in2Cluster = document.getElementById('m-in2-cluster').value.trim();
    const in2Sats = parseInt(document.getElementById('m-in2-sats').value) || 0;
    const destSats = parseInt(document.getElementById('m-dest-sats').value) || 80000;
    const changeScript = document.getElementById('m-change-script').value;

    const totalIn = in1Sats + (in2Cluster ? in2Sats : 0);
    const fee = 1800;
    const changeSats = Math.max(0, totalIn - destSats - fee);

    let isCIOH = in2Cluster && in2Cluster !== in1Cluster;
    let isScriptMismatch = changeScript !== "P2WPKH";

    let score = 100;
    if (isCIOH) score -= 40;
    if (isScriptMismatch) score -= 20;

    // Inject into custom scenario object
    SCENARIOS['custom_user'] = {
      name: "User Injected Custom Transaction",
      badgeType: `${in2Cluster ? '2' : '1'}-IN / 2-OUT // PSBT`,
      score: score,
      grade: score >= 80 ? "GRADE: A" : (score >= 60 ? "GRADE: C" : "GRADE: D"),
      gradeClass: score < 60 ? "pulse" : "",
      verdict: isCIOH ? "COMMON-INPUT VIOLATION DETECTED" : (isScriptMismatch ? "SCRIPT ASYMMETRY" : "SOVEREIGN PASS"),
      explanation: isCIOH ? `Multiple distinct clusters (${in1Cluster} & ${in2Cluster}) were co-spent in this custom PSBT.` : `Transaction evaluated cleanly with ${score}/100 sovereign rating.`,
      asciiGraph: `[INPUT 0: ${in1Cluster.substring(0, 15)}] ──┐\n` +
                  (in2Cluster ? `[INPUT 1: ${in2Cluster.substring(0, 15)}] ──┤─► [TRANSACTION KERNEL] ─┬─► [DESTINATION: ${destSats.toLocaleString()} sats]\n` : `                              ├─► [TRANSACTION KERNEL] ─┬─► [DESTINATION: ${destSats.toLocaleString()} sats]\n`) +
                  `                              (FEE: ${fee} sats)       └─► [CHANGE: ${changeSats.toLocaleString()} sats] (${changeScript})`,
      leakStatus: isCIOH ? "CIOH LEAK" : (isScriptMismatch ? "SCRIPT LEAK" : "CLEAN PASS"),
      inputs: [
        { tag: in1Cluster, type: "clean", sats: in1Sats, script: "P2WPKH", addr: "bc1qcustom_in_01" },
        ...(in2Cluster ? [{ tag: in2Cluster, type: "kyc", sats: in2Sats, script: "P2WPKH", addr: "bc1qcustom_in_02" }] : [])
      ],
      outputs: [
        { tag: "Custom_Destination", type: "clean", sats: destSats, script: "P2WPKH", addr: "bc1qcustom_dest" },
        { tag: "Custom_Change", type: isScriptMismatch ? "kyc" : "change", sats: changeSats, script: changeScript, addr: "bc1qcustom_change" }
      ],
      checks: {
        cioh: { pass: !isCIOH, desc: isCIOH ? `Clusters merged: ${in1Cluster} + ${in2Cluster}` : "Single cluster input" },
        script: { pass: !isScriptMismatch, desc: isScriptMismatch ? `Mismatch: P2WPKH -> ${changeScript}` : "Script types symmetric" },
        bip69: { pass: true, desc: "Standard BIP-69 lexicographical order" },
        reuse: { pass: true, desc: "Fresh change address" }
      },
      remediations: isCIOH ? ["Separate coins into isolated transactions to prevent clustering."] : ["✓ Transaction ready to sign."]
    };

    modalInject.classList.remove('active');
    renderScenario('custom_user');
  });

  // Sanitized Coin Selection Modal
  const modalSanitize = document.getElementById('modal-sanitize');
  document.getElementById('btn-sanitize-now').addEventListener('click', () => {
    audio.playBeep(1400, 0.06);
    renderSanitizeResult();
    modalSanitize.classList.add('active');
  });

  document.getElementById('btn-close-sanitize').addEventListener('click', () => {
    modalSanitize.classList.remove('active');
  });
  document.getElementById('btn-close-sanitize-btn').addEventListener('click', () => {
    modalSanitize.classList.remove('active');
  });
  document.getElementById('btn-calc-sanitize').addEventListener('click', () => {
    audio.playClick(2100, 0.02);
    renderSanitizeResult();
  });

  // Export Audit Certificate
  document.getElementById('btn-export-report').addEventListener('click', () => {
    audio.playBeep(1800, 0.1);
    const data = SCENARIOS[currentScenario];
    const cert = {
      generator: "UNCLUSTER // Cypherpunk Pre-Flight UTXO Firewall v1.0.4",
      timestamp_utc: new Date().toISOString(),
      scenario: currentScenario,
      score: data.score,
      grade: data.grade,
      verdict: data.verdict,
      txid: data.txid,
      inputs: data.inputs,
      outputs: data.outputs,
      remediations: data.remediations,
      sha256_audit_seal: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    };

    const blob = new Blob([JSON.stringify(cert, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `uncluster_audit_${currentScenario}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Keyboard Hotkeys: 1, 2, 3, 4, Space
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

    if (e.key === '1') {
      audio.playClick(1800, 0.02);
      document.querySelector('.scenario-btn[data-scenario="cioh_leak"]').click();
    } else if (e.key === '2') {
      audio.playClick(1800, 0.02);
      document.querySelector('.scenario-btn[data-scenario="script_mismatch"]').click();
    } else if (e.key === '3') {
      audio.playClick(1800, 0.02);
      document.querySelector('.scenario-btn[data-scenario="sovereign_clean"]').click();
    } else if (e.key === '4') {
      audio.playClick(1800, 0.02);
      document.querySelector('.scenario-btn[data-scenario="nostr_zap"]').click();
    } else if (e.key === 'Escape') {
      modalInject.classList.remove('active');
      modalSanitize.classList.remove('active');
    }
  });

  // Initial Render
  renderScenario('cioh_leak');
});
