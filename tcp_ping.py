from argparse import ArgumentParser
from ipaddress import ip_address
from signal import signal, SIGINT
from socket import socket, AF_INET, SOCK_STREAM, timeout, SHUT_RD, IPPROTO_TCP, TCP_NODELAY
from time import time_ns, sleep

parser = ArgumentParser()

parser.add_argument("host", nargs="?", help="Remote address and port")
parser.add_argument("-n", help="Number of requests to send", type=int, default=4)
parser.add_argument("-w", help="Delay in milliseconds to use in between requests", type=int, default=450)
parser.add_argument("-o", help="Timeout in milliseconds to wait for each reply", type=int, default=5000)
args = parser.parse_args()

sent, dropped, latencies = 0, 0, []


def finalise(_, __):
    print()
    if sent or dropped:
        request_statistics = f"Received: {sent}/{sent + dropped} requests"

        if not sent:
            request_statistics.join(f"100% loss)")
        else:
            request_statistics.join(f"{round(dropped / sent, 2)}% loss)")
        print(request_statistics)

        if latencies:
            latency_statistics = f"Min: {min(latencies)}ms, Max: {max(latencies)}ms, Avg: {round(sum(latencies) / len(latencies), 3)}ms"
            print(latency_statistics)
        
    exit(0)


signal(SIGINT, finalise)


def input_is_valid(address: str, port: int) -> bool:
    try:
        ip_address(address)
    except (OverflowError, OSError, ValueError):
        return False
    else:
        return 0 < port <= 65535


def main():
    if not args.host:
        return print("Host address not provided")

    host = args.host.split(":")
    if len(host) != 2:
        return print("Invalid host:port format provided")

    address, port = host[0], int(host[1])
    if not input_is_valid(address, port):
        return print("Host address or port range invalid")

    global sent, dropped, latencies

    TIMEOUT, WAIT = args.o / 1000, args.w / 1000

    print("\n----------- TCP Ping 1.1 -----------\n"
          f"Initialising connection to {address}:{port}\n")
    for sequence in range(1, args.n + 1):
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.settimeout(TIMEOUT)
        tcp_socket.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        sleep(WAIT)

        t1 = time_ns()
        try:
            tcp_socket.connect((address, port))
        except timeout:
            print(f"Sequence {sequence}: Timed out ({args.o}ms)")
            dropped += 1
        except OSError as exception:
            print(f"Sequence {sequence}: Generic error ({exception})")
            dropped += 1
        else:
            latency = (time_ns() - t1) / 1000000
            print(f"Sequence {sequence}: Connected in {latency}ms")
            tcp_socket.shutdown(SHUT_RD)
            sent += 1
            latencies.append(latency)

    finalise(None, None)


if __name__ == "__main__":
    main()
