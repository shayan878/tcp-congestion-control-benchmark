# Experiment design

## Current scenario

The maintained Tcl scripts each create a six-node dumbbell topology. Two TCP sources send FTP traffic through a shared 100 kb/s bottleneck link. Access links are configured at 100 Mb/s; propagation delays on the source access links are drawn from a uniform random variable between 5 ms and 25 ms. The bottleneck queue limit is 10 packets. Both flows start at simulation time 0 and the simulation ends at 1000 seconds.

The Reno script creates two `Agent/TCP/Reno` senders. The second script creates two `Agent/TCP/Reno/BBR` senders and therefore requires the custom agent to be available in the NS-2 binary.

## What the comparison currently means

These are two separate homogeneous experiments:

1. Reno flow 1 competes with Reno flow 2.
2. Prototype flow 1 competes with prototype flow 2.

This supports an initial comparison of aggregate/individual flow behavior across two separate runs when the environments and parameters are held constant. It does not measure cross-protocol coexistence or fairness between Reno and the prototype in one shared queue. A mixed Reno + prototype scenario should be added before making coexistence claims.

## Randomness and paired runs

Both scripts accept an output directory and seed as positional arguments. The runner passes the same seed to each scenario. This is a first step toward paired comparisons, but the random-variable stream and NS-2 RNG semantics should be verified on the exact simulator version. For robust results, run multiple independent seeds and report mean, standard deviation, and confidence intervals rather than selecting a single run.

## Metrics

The analysis package reports received bytes, average throughput, drops, packet-delivery ratio, and Jain's fairness index across observed flow throughputs. Provide an explicit common measurement duration for cross-run comparisons. The packet-delivery ratio is an event-level approximation because a classic trace's drops and receive records do not necessarily map one-to-one to unique application packets.

## Recommended next experiment

Add three matched scenarios:
- Reno + Reno (baseline)
- Reno + BBR-inspired (coexistence)
- BBR-inspired + BBR-inspired (self-fairness)

Keep topology, queue discipline, bottleneck bandwidth, propagation delay distributions, packet size, FTP start/stop times, and seed schedule fixed. Repeat each scenario over a published seed list and export machine-readable run metadata.
