/*
 * Experimental BBR-inspired congestion-control agent for NS-2.
 *
 * IMPORTANT: This is a research prototype, not a faithful implementation of
 * Google's production BBR algorithm. The current implementation modifies a
 * Reno-derived congestion window, but does not wire pacing_rate_ into NS-2's
 * packet scheduler and does not implement BBR's complete round-based bandwidth
 * filters, ACK aggregation handling, or full ProbeBW/ProbeRTT state machine.
 *
 * Keep these limitations explicit in published comparisons. See
 * docs/implementation-limitations.md.
 */

#ifndef lint
static const char rcsid[] =
    "@(#) experimental BBR-inspired TCP agent for NS-2";
#endif

#include <algorithm>
#include <cmath>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>

#include "ip.h"
#include "tcp.h"
#include "tcp-reno.h"
#include "flags.h"

class BBRRenoTcpAgent : public RenoTcpAgent {
public:
    BBRRenoTcpAgent();
    void recv(Packet *pkt, Handler *);
    void timeout(int tno);

protected:
    double bottleneck_bandwidth_;
    double min_rtt_;
    double pacing_rate_;
    double send_rate_;
    double last_ack_bytes_;
    double last_time_;
    double startup_full_bandwidth_;
    double startup_last_check_;
    int startup_no_growth_count_;
    int state_;

    enum BBRState { STARTUP, DRAIN, PROBE_BW, PROBE_RTT };

    void update_bandwidth(double ack_bytes, double current_time);
    void update_rtt(double current_rtt);
    void adjust_pacing_rate();
    void adjust_congestion_window();
};

BBRRenoTcpAgent::BBRRenoTcpAgent()
    : RenoTcpAgent(),
      bottleneck_bandwidth_(0.0),
      min_rtt_(1e9),
      pacing_rate_(0.0),
      send_rate_(1.0),
      last_ack_bytes_(0.0),
      last_time_(0.0),
      startup_full_bandwidth_(0.0),
      startup_last_check_(0.0),
      startup_no_growth_count_(0),
      state_(STARTUP) {}

void BBRRenoTcpAgent::recv(Packet *pkt, Handler *h) {
    hdr_tcp *tcph = hdr_tcp::access(pkt);

    if (tcph->ts() < lastreset_) {
        Packet::free(pkt);
        return;
    }

    /*
     * NS-2's Reno-derived agent still owns retransmission and ACK processing.
     * The custom estimate below is therefore deliberately treated as an
     * experimental signal, not as a complete ACK-clock replacement.
     */
    double ack_bytes = static_cast<double>(tcph->ackno());
    double current_time = Scheduler::instance().clock();

    update_bandwidth(ack_bytes, current_time);

    double current_rtt = std::max(current_time - tcph->ts(), 0.001);
    update_rtt(current_rtt);

    adjust_pacing_rate();
    adjust_congestion_window();

    RenoTcpAgent::recv(pkt, h);
}

void BBRRenoTcpAgent::update_bandwidth(double ack_bytes, double current_time) {
    if (last_time_ > 0.0) {
        double interval = current_time - last_time_;
        if (interval > 0.0 && ack_bytes >= last_ack_bytes_) {
            double current_bandwidth = (ack_bytes - last_ack_bytes_) / interval;
            bottleneck_bandwidth_ =
                std::max(bottleneck_bandwidth_, current_bandwidth);
        }
    }

    last_ack_bytes_ = ack_bytes;
    last_time_ = current_time;

    /*
     * Approximate startup plateau detection. These checks are time-window
     * based, not the packet-round accounting used by the reference BBR design.
     */
    if (state_ == STARTUP && current_time - startup_last_check_ >=
                                 std::max(min_rtt_, 0.01)) {
        if (bottleneck_bandwidth_ >= startup_full_bandwidth_ * 1.25) {
            startup_full_bandwidth_ = bottleneck_bandwidth_;
            startup_no_growth_count_ = 0;
        } else {
            ++startup_no_growth_count_;
        }
        startup_last_check_ = current_time;

        if (startup_no_growth_count_ >= 3) {
            state_ = DRAIN;
        }
    }
}

void BBRRenoTcpAgent::update_rtt(double current_rtt) {
    if (current_rtt > 0.0) {
        min_rtt_ = std::min(min_rtt_, current_rtt);
    }
}

void BBRRenoTcpAgent::adjust_pacing_rate() {
    switch (state_) {
    case STARTUP:
        pacing_rate_ = bottleneck_bandwidth_ * 2.0;
        break;

    case DRAIN:
        pacing_rate_ = bottleneck_bandwidth_;
        if (pacing_rate_ * min_rtt_ <= cwnd_) {
            state_ = PROBE_BW;
        }
        break;

    case PROBE_BW:
        pacing_rate_ =
            bottleneck_bandwidth_ *
            (1.0 + 0.05 * std::sin(Scheduler::instance().clock()));
        if (Scheduler::instance().clock() - startup_last_check_ >
            5.0 * min_rtt_) {
            state_ = PROBE_RTT;
        }
        break;

    case PROBE_RTT:
        pacing_rate_ = bottleneck_bandwidth_ * 0.75;
        if (Scheduler::instance().clock() - startup_last_check_ > min_rtt_) {
            state_ = PROBE_BW;
        }
        break;
    }

    /*
     * The value is retained for instrumentation only: this source does not
     * connect it to NS-2's send timer, so it must not be presented as pacing.
     */
    send_rate_ = pacing_rate_;
}

void BBRRenoTcpAgent::adjust_congestion_window() {
    cwnd_ = std::max(1.0, pacing_rate_ * min_rtt_);
}

void BBRRenoTcpAgent::timeout(int tno) {
    if (tno == TCP_TIMER_RTX) {
        state_ = STARTUP;
        bottleneck_bandwidth_ *= 0.5;
        pacing_rate_ = 0.0;
        send_rate_ = 1.0;
        last_ack_bytes_ = 0.0;
        last_time_ = 0.0;
        startup_full_bandwidth_ = 0.0;
        startup_last_check_ = Scheduler::instance().clock();
        startup_no_growth_count_ = 0;
    }
    RenoTcpAgent::timeout(tno);
}

static class BBRRenoTcpClass : public TclClass {
public:
    BBRRenoTcpClass() : TclClass("Agent/TCP/Reno/BBR") {}

    TclObject *create(int, const char *const *) {
        return new BBRRenoTcpAgent();
    }
} class_bbr_reno;
