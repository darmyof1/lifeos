# Hardware for a local model

Status: draft proposal, written 2026-11-01 under APR-0112 (read-only measurements on the VM; prices from public pages found by web search on 2026-11-01). The decision is the CEO's.

## What the VM has now (measured, read-only)
| Item | Value |
|---|---|
| CPU | 4 cores, aarch64 (Neoverse-N1), one thread per core, virtual machine (KVM) |
| Memory | 23 GiB total; about 20 GiB available when idle |
| Disk | 193 GB, 30 percent used |
| GPU | none (lspci shows no graphics or compute device; nvidia-smi absent) |
| Network | one network interface plus a VPN tunnel; the address is not recorded here |
| Local models installed | two small ones in Ollama (about 1 GB and 4.9 GB) |
| Measured speed | SPK-06: llama3.1:8b generated 3.68 tokens per second on this CPU. A routing answer of about 60 tokens takes about 20 seconds; the design assumed under 1 second (research/spikes/SPK-06-local-model-on-vm.md, P-14) |
Conclusion from the measurement: a local model on this VM is too slow for triage and too small to answer high-privacy requests well.

## Why it matters for the gate
The privacy gate (src/lifeos/router/gate.py) denies cloud models for high-privacy requests. Without a local model that is usable, a high-privacy request has nowhere to go: it can be stored, not answered. A usable local model is what lets the CEO's health, finance and family requests be handled at all. Triage (ADR-0004) also needs a local model that answers in about a second.

## Options
| Option | What it is | Rough monthly cost | What it can run (expectation, not measured here) | What it means for the gate |
|---|---|---|---|---|
| A. Keep the VM, add nothing | The current 4-core ARM VM | Current VM cost (not recorded in the repo; Oracle's Ampere A1 price page did not show numbers in the search result, so unknown) | Models up to about 3B to 8B at a few tokens per second; fine for nothing interactive | The gate would deny every high-privacy request in practice. Triage stays slow (about 20 s) or uses rules only (the prefilter in ADR-0004) |
| B. Rent a GPU instance in the cloud (on demand or a small dedicated box) | For example a 24 GB consumer-class GPU (RTX 4090 class) or an L4 at a GPU marketplace; or a small dedicated GPU server | On demand, if used 100 hours a month: RTX 4090 about 0.34 to 0.89 USD per hour, so about 34 to 89 USD; L4 about 0.44 to 0.80 USD per hour, about 44 to 80 USD. Always on (730 hours): about 250 to 650 USD. A dedicated Hetzner GEX44 (20 GB GPU) was 184 EUR per month plus 79 EUR setup, but one source says it can no longer be ordered (unknown) | 7B to 14B models at tens of tokens per second; 30B-class with 4-bit weights on 24 GB | Local for the gate only if the cloud instance is under our control and the data never goes to a third-party model API. It is still someone else's machine, so high-privacy data leaves the home VM. The CEO would have to accept that as "local" or not (a decision, not mine) |
| C. A local box at the CEO's home | For example a Mac mini M4 Pro with 48 GB memory (about 1,999 USD new, 1,869 USD lowest recorded), or a PC with a 16 to 24 GB GPU | One-time about 1,900 to 2,000 USD for the Mac mini, plus power (low); no monthly fee | Up to about 32B models comfortably; a 70B 4-bit model fits in 48 GB but runs at single-digit tokens per second (published figures range from 4 to 9, one outlier at 18) | The best fit for "local": the data stays in the CEO's home. Needs a secure link from the VM to the box (a decision), backups, and someone to keep it running |

## Recommendation (a proposal for the CEO)
Start with option C in a small way, after the gate is wired: buy or borrow one home machine in the 32B class for the high-privacy path only, keep the cloud model for low-privacy requests, and keep the VM for the agents. Until then, treat high-privacy data as not allowed in the system (the gate is not wired; the data stays synthetic). If a purchase is not wanted yet, option B on demand is the cheapest way to measure real speed: rent one GPU for a few hours and run the triage and one high-privacy scenario on synthetic data, then decide. Option A alone does not meet the gate's purpose.

## Sources (searched 2026-11-01; third-party pages, prices change; check before buying)
- GPU hourly prices: Hostinger, "Cloud GPU pricing compared": https://www.hostinger.com/tutorials/?p=158956 ; io.net, "Rent NVIDIA GPUs": https://io.net/p/rent-nvidia-gpus-for-ai-h100-a100-and-rtx-4090-pricing-comparison ; Jarvislabs: https://jarvislabs.ai/blog/a100-price . Sources disagree on the RTX 4090 figure (0.34 and 0.74 to 0.89 USD per hour on one provider); the L4 range is 0.44 to 0.80 USD per hour.
- Hetzner GEX44: launch price 184 EUR plus 79 EUR setup, RTX 4000 SFF Ada with 20 GB: https://www.hetzner.com/pressroom/new-gpu-server/ ; availability doubtful: https://wz-it.com/en/blog/hetzner-gpu-server-comparison/
- Mac mini M4 Pro 48 GB: price tracker https://www.macprices.net/macmini.shtml ; deal listing https://slickdeals.net/f/20106486-apple-mac-mini-m4-pro-48gb-ram-512gb-ssd-1999 ; speed figures for 70B models: https://computingforgeeks.com/mac-mini-vs-mini-pc-vs-gpu-local-llm/ , https://willitrunai.com/can-run/llama-3.3-70b-on-m4-mini-64gb , https://llmrun.dev/device/mac-mini-m4-pro-64gb
- Oracle Ampere A1 pricing page (numbers not shown in the search result, so the VM's own cost is unknown here): https://www.oracle.com/cloud/compute/arm/pricing
