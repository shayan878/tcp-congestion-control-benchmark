# Two competing Reno TCP flows over a shared bottleneck.
# Usage: ns simulator/ns2/scenarios/reno.tcl [output_dir] [seed]
set output_dir [lindex $argv 0]
if {$output_dir eq ""} {
    set output_dir "results/reno"
}
set seed [lindex $argv 1]
if {$seed eq ""} {
    set seed 4
}
file mkdir $output_dir

set sim [new Simulator]
$sim color 1 Green
$sim color 2 Orange
set nam_file [open "$output_dir/reno.nam" w]
$sim namtrace-all $nam_file
set trace_file [open "$output_dir/reno.tr" w]
$sim trace-all $trace_file

set random_gen [new RNG]
$random_gen seed $seed
set delay_var [new RandomVariable/Uniform]
$delay_var use-rng $random_gen
$delay_var set min_ 5.0
$delay_var set max_ 25.0

proc end_simulation {} {
    global sim nam_file trace_file
    $sim flush-trace
    close $nam_file
    close $trace_file
    exit 0
}

set server1 [$sim node]
set server2 [$sim node]
set router1 [$sim node]
set router2 [$sim node]
set server3 [$sim node]
set server4 [$sim node]

set delay1 [format "%.2f" [$delay_var value]]
set delay2 [format "%.2f" [$delay_var value]]

$sim duplex-link $server1 $router1 100Mb 5ms DropTail
$sim duplex-link $server2 $router1 100Mb ${delay1}ms DropTail
$sim duplex-link $router1 $router2 100kb 1ms DropTail
$sim duplex-link $router2 $server3 100Mb 5ms DropTail
$sim duplex-link $router2 $server4 100Mb ${delay2}ms DropTail
$sim queue-limit $router1 $router2 10
$sim queue-limit $router2 $router1 10
$sim duplex-link-op $server1 $router1 orient right-down
$sim duplex-link-op $server2 $router1 orient right-up
$sim duplex-link-op $router1 $router2 orient right
$sim duplex-link-op $router2 $server3 orient right-up
$sim duplex-link-op $router2 $server4 orient right-down

set sender1 [new Agent/TCP/Reno]
$sender1 set class_ 2
$sender1 set ttl_ 64
$sim attach-agent $server1 $sender1
set receiver1 [new Agent/TCPSink]
$sim attach-agent $server3 $receiver1
$sim connect $sender1 $receiver1
$sender1 set fid_ 1

set sender2 [new Agent/TCP/Reno]
$sender2 set class_ 1
$sender2 set ttl_ 64
$sim attach-agent $server2 $sender2
set receiver2 [new Agent/TCPSink]
$sim attach-agent $server4 $receiver2
$sim connect $sender2 $receiver2
$sender2 set fid_ 2

foreach sender [list $sender1 $sender2] {
    $sender attach $trace_file
    $sender tracevar cwnd_
    $sender tracevar ssthresh_
    $sender tracevar ack_
    $sender tracevar maxseq_
    $sender tracevar rtt_
}

set ftp_app1 [new Application/FTP]
$ftp_app1 attach-agent $sender1
set ftp_app2 [new Application/FTP]
$ftp_app2 attach-agent $sender2

$sim at 0.0 "$ftp_app2 start"
$sim at 0.0 "$ftp_app1 start"
$sim at 1000.0 "end_simulation"
$sim run
