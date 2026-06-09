# UNILIS Extensions

**Three new systems built on the ZeroEdge foundation**  
BCT 2406 | Quinter Maru Jelimo | SCT212-0068/2021 | JKUAT | 2026

[![CI](https://github.com/MARU-Quinter/unilis-extensions/actions/workflows/ci.yml/badge.svg)](https://github.com/MARU-Quinter/unilis-extensions/actions/workflows/ci.yml)

| Suite | Tests | Status |
|---|---|---|
| PulseProof — ZK time-bound attendance | 12 / 12 | ✅ |
| GhostGrade — AI grading integrity | 10 / 10 | ✅ |
| PrivacyPool — Federated k-anonymity | 11 / 11 | ✅ |
| **Total** | **33 / 33** | **✅ 0 failures** |

---

## Systems overview

| System | What it does | Key novelty | Constraints |
|---|---|---|---|
| PulseProof | ZK anonymous attendance | Time-bound presence proof | ~516 R1CS |
| GhostGrade | ZK AI grading integrity | Commitment: model × input × output | ECDSA scheme |
| PrivacyPool | Cross-institution anonymity | Federated depth-18 Merkle tree | ~461 R1CS |

All three share the ZeroEdge cryptographic stack: Groth16, Poseidon, Yjs CRDT, Polygon zkEVM.

---

## PulseProof

**ZK time-bound attendance — prove presence without identity**

Circuit: `pulseproof/circuits/pulseproof_main.circom`  
Contract: `pulseproof/contracts/PulseProof.sol`  
Frontend: `pulseproof/frontend/src/components/AttendanceForm.jsx`

### What it proves
- Student is enrolled (Merkle membership, same as ZeroEdge)
- Student generated the proof during the attendance window (time-bound constraint)
- Student was within the classroom radius (location commitment)

### Privacy guarantees
- Identity: only `attendanceNullifier = Poseidon(privKey, lectureID)` stored on-chain
- Location: only `Poseidon(lat, lng)` stored — exact coordinates never leave device
- Time: only that proof was generated within the window — exact time not revealed

### Hillary IoT integration
Hillary publishes a `unilis/labs/ready` MQTT event when the lab is available.  
The event-service subscribes and calls `PulseProof.createLecture()` automatically.

### Quick start
```bash
npm run build:pulseproof     # compile circuit
npm run test:pulseproof      # run contract tests
npm run deploy:pulseproof    # deploy to Polygon Amoy
npm run dev:pulseproof       # frontend dev server
```

---

## GhostGrade

**ZK-verified AI grading integrity**

Contract: `ghostgrade/contracts/GhostGrade.sol`  
Newton module: `ghostgrade/crdt/newton_signing.js`  
Frontend: `ghostgrade/frontend/src/components/GradeVerifier.jsx`

### What it proves
- A specific registered AI model (identified by keccak256 weight hash) graded the submission
- The model graded the correct IPFS content (input CID binding)
- The grade feedback is genuinely from that model run (output CID binding)
- The same model was used for all students in the cohort (fairness guarantee)

### What it does NOT prove (documented limitation)
- It does NOT prove the computation was correct (that requires zkML circuits — future work)
- It proves Newton signed the triple (model, input, output) with an ECDSA key
- A compromised Newton key would invalidate proofs retroactively

### Commitment scheme
```
gradeCommitment = Poseidon(modelHash_as_field, inputCID, outputCID)
signature       = ECDSA.sign(gradeCommitment, newtonKey)
```
Both `gradeCommitment` and `signature` are stored on-chain.  
Anyone can verify: `ECDSA.recover(gradeCommitment) === newtonSigner`

### Quick start
```bash
npm run test:ghostgrade       # run contract tests
npm run deploy:ghostgrade     # deploy to Polygon Amoy
```

---

## PrivacyPool

**Federated anonymity across EAC universities**

Circuit: `privacypool/circuits/privacypool_main.circom`  
Tree builder: `privacypool/circuits/federated_tree.js`  
Contract: `privacypool/contracts/PrivacyPool.sol`

### Privacy amplification theorem

Let *k* = number of students in the federated pool.  
An adversary with full blockchain access can identify a specific submitter with probability:

```
P(identify) ≤ 1/k
```

For *k* = 262,144 (full pool): `P ≤ 3.8 × 10⁻⁶`  
vs ZeroEdge single-university (200 students): `P ≤ 5 × 10⁻³`  
**Privacy amplification: 1,310× stronger**

### Federated root computation
```
subRoot_i = MerkleRoot(institution_i.students)  // computed locally by each institution

l16[j] = Poseidon(subRoot_{2j}, subRoot_{2j+1})  // on-chain
l17[j] = Poseidon(l16_{2j}, l16_{2j+1})           // on-chain
federatedRoot = Poseidon(l17[0], l17[1])            // on-chain
```

Each institution contributes its sub-root independently.  
No institution learns another's student list.  
The federated root is derived from all sub-roots on-chain.

### Member institutions (simulated for prototype)
| ID | Institution | Country | Students |
|---|---|---|---|
| 1 | JKUAT | Kenya | Real |
| 2 | University of Nairobi | Kenya | Simulated |
| 3 | Kenyatta University | Kenya | Simulated |
| 4 | Mount Kenya University | Kenya | Simulated |
| 5–8 | TUK, MMUST, KCA, USIU | Kenya | Simulated |

### Quick start
```bash
npm run test:privacypool      # federated tree tests + k-anonymity metrics
npm run build:privacypool     # compile depth-18 circuit
npm run deploy:privacypool    # deploy to Polygon Amoy
```

---

## How all three connect to ZeroEdge

```
Hillary IoT ──MQTT──▶ event-service ──▶ PulseProof.createLecture()
                                    ──▶ ZeroEdge.createAssignment()

Student ──▶ ZeroEdge (submit anonymously)
        ──▶ PulseProof (attend anonymously)
        ──▶ PrivacyPool (submit with EAC-level privacy)

Newton AI ──▶ GhostGrade.commitGrade() (prove AI graded correctly)
          ──▶ ZeroEdge.recordGrade()   (store feedback CID)

Student ──▶ GradeVerifier (verify Newton graded their submission authentically)
```

---

## Budget

| Item | Cost |
|---|---|
| Polygon Amoy testnet (all 3 contracts) | $0 |
| IPFS Pinata free tier | $0 |
| Vercel hosting (all 3 frontends) | $0 |
| Mobile data | $15 |
| **Total** | **$15** |
