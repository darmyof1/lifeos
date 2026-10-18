# SPK-07-gpg-restore-drill - Can an archive be restored from its GPG key?

Status: partial
Decision unblocked: APR-0010 archive
Owner: CEO
Date run: 2026-10-18 (Part A, first and second runs). Part B pending.

## Environment
- Host: Oracle A1 class VM. OS and gpg version: to be recorded (run gpg --version).
- Tools: gpg (symmetric and asymmetric), sha256sum.

## Question
Can an encrypted archive be restored from its passphrase alone, and can the VM encrypt without holding the restore secret?

## Pass criterion (written before running)
Part A: restored SHA-256 equals the reference hash saved before the original was deleted; a wrong passphrase fails with nonzero exit and writes no output.
Part B: VM encrypts with a public key without a prompt; VM cannot decrypt; CEO key restores with matching SHA-256.

## Method
Runbook guides/vm-spike-runbook.md, step 1. The first run had an invalid wrong-passphrase test: gpg-agent cached the passphrase, so the decrypt did not prompt and exited 0. The runbook now clears the cache with gpgconf --kill gpg-agent before each decrypt.

## Result (Part A so far)
- Reference SHA-256 of the random test file, recorded before deletion: 45c7eb60... (full value kept in the run log, not here)
- Restore with the correct passphrase: exit 0. Restored file's SHA-256 printed as 45c7eb60... in both runs. The MATCH comparison is pending the rerun.
- Wrong passphrase after clearing the cache: "Bad session key", exit 2, no output file. PASS.
- Part A status: pass pending MATCH line.

## Result (Part B)
Pending.

## Conclusion
Pending Part A MATCH and Part B. Part B tests whether the VM can encrypt archives with a public key, so it never holds the restore secret. This is the design proposed for the archive (APR-0010 and ADR-0012 to confirm).

## Redaction log
- Passphrases: never written to a file or to chat.
- Reference hash: value of a random test file, not sensitive.
- No hostnames, IPs or account names recorded.
