# SPK-07-gpg-restore-drill - Can an archive be restored from its GPG key?

Status: done
Decision unblocked: APR-0010 archive
Owner: CEO
Date run: 2026-10-18

## Environment
- Host: Oracle A1 class VM, Ubuntu. gpg version: to be recorded (run gpg --version).
- Tools: gpg (symmetric and asymmetric), sha256sum.

## Question
Can an encrypted archive be restored from its passphrase alone, and can the VM encrypt without holding the restore secret?

## Pass criterion (written before running)
Part A: restored SHA-256 equals the reference hash saved before the original was deleted; a wrong passphrase fails with nonzero exit and writes no output.
Part B: VM encrypts with a public key without a prompt; VM cannot decrypt; CEO key restores with matching SHA-256.

## Method
Runbook guides/vm-spike-runbook.md, step 1 (corrected by fix-31 and fix-32). Earlier attempts recorded these faults, all fixed in the runbook:
- Part A, first run: the gpg-agent passphrase cache made the wrong-passphrase test pass when it should fail. Fixed by gpgconf --kill gpg-agent before each decrypt.
- Part A, hash check: the sha256 files named different files, so a whole-line diff failed. Fixed by comparing the hash value only.
- Part B, first run: the key had no encryption subkey, so encrypt failed with "Unusable public key" and the later steps tested nothing. Fixed by adding the subkey with quick-add-key.

## Result Part A
- Reference SHA-256 of the random test file, recorded before deletion: 45c7eb60... (value in the run log, not repeated here)
- Restore with the correct passphrase: exit 0. Restored hash equal to reference: MATCH.
- Wrong passphrase after clearing the cache: "Bad session key", exit 2, no output file. PASS.

## Result Part B
- Encryption subkey added to the CEO key: [E] present.
- Agent keyring: public key only; no secret keys listed.
- Encrypt with the public key: exit 0, no prompt. PASS.
- Agent decrypt: "No secret key", exit 2. PASS.
- CEO restore with the CEO passphrase: exit 0, restored hash equal to reference: MATCH. PASS.

## Conclusion
Both parts pass. The VM can encrypt archives with a public key and cannot decrypt them; the CEO restores with the private key and passphrase. This supports public-key encryption for the archive. The choice is the CEO's: it should be recorded in APR-0010 or ADR-0012 when decided. The passphrases used in this drill were test-only and are not recorded here.

## Redaction log
- Passphrases: never written to a file or to chat.
- Reference hashes: values of random test files, not sensitive.
- Key fingerprint: test key, not recorded here.
- No hostnames, IPs or account names recorded.
