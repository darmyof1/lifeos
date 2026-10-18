# SPK-01-egress-interception - Can the host block outbound calls per process?

Status: done
Decision unblocked: ADR-0003 / security design
Owner: CEO
Date run: 2026-10-18

## Environment
- Host: Oracle A1 class VM, Ubuntu. iptables v1.8.10 (nf_tables backend). Default policies ACCEPT on INPUT, FORWARD, OUTPUT before the test.
- Test user: a system user created for the test and removed afterwards.

## Question
Can the VM block outbound network access for one user, while the same user still reaches the local model on loopback?

## Pass criterion (written before running)
The test user cannot reach a public host (curl exit nonzero), can reach the local model on 127.0.0.1 (exit 0), and an ordinary user still reaches a public host (exit 0).

## Method
Runbook guides/vm-spike-runbook.md, step 2. Rule: iptables OUTPUT, owner match on the test user, all destinations except loopback, action REJECT. Cleanup removed the rule and the user.

## Result
- Test user, public host: curl exit 7 (failed to connect). PASS.
- Test user, local model 127.0.0.1:11434: exit 0. PASS.
- Ordinary user, public host: exit 0. PASS.
- Pass against the criterion: yes.
- Baseline before the change: iptables OUTPUT policy ACCEPT, no other rules.
- After cleanup: rules back to the baseline; test user removed.

## Limits (what this spike does not prove)
1. The block was tested for a test user. It was not tested on an OpenClaw agent process. The agents must each run under their own user for this to protect them. That check belongs in SPK-03 or a follow-up.
2. The rule is not persistent. It was removed by cleanup. A reboot would also clear it. A boot-time rule needs its own test.
3. The VM image has an InstanceServices chain with no references. The rule was added to OUTPUT and did not depend on it.

## Conclusion
The kernel can block outbound traffic per user on this VM, and the block leaves loopback open for the local model. This supports a per-agent user design for egress control. The design choice (per-agent users, persistent rules) is the CEO's and belongs in ADR-0003 or the security design when written. Limits 1 and 2 must be closed before the design is relied on.

## Evidence
### Commands and exit codes (redacted)
    sudo iptables -S OUTPUT                       # baseline: -P OUTPUT ACCEPT only
    sudo useradd --system --no-create-home --shell /usr/sbin/nologin <test-user>
    sudo iptables -I OUTPUT 1 -m owner --uid-owner <test-user> ! -o lo -j REJECT
    sudo -u <test-user> curl -sS -m 10 <public-host> -o /dev/null; echo "internet exit=$?"    # 7
    sudo -u <test-user> curl -sS -m 10 http://127.0.0.1:11434/api/tags -o /dev/null; echo "local exit=$?"   # 0
    curl -sS -m 10 <public-host> -o /dev/null; echo "normal user exit=$?"                      # 0
    sudo iptables -D OUTPUT -m owner --uid-owner <test-user> ! -o lo -j REJECT
    sudo userdel <test-user>

## Redaction log
- Public test host name and the test user name: replaced with placeholders.
- No IPs, account names, or VPN or process names recorded.
