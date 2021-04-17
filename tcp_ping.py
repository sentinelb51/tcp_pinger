from socket import inet_aton, socket, AF_INET, SOCK_STREAM, getservbyport, SHUT_RD, timeout
from sys import argv
from time import time_ns, sleep


def ip_is_valid(address: str) -> bool:
    try:
        inet_aton(address)
    except (OverflowError, OSError, ValueError):
        return False
    else:
        return True

def try_connect(ip_address: str, port: int) -> None:
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.settimeout(0.5)
    # Re-creating a socket every time is expensive but it's to avoid WinError-10053
    t1 = time_ns()
    try:
        tcp_socket.connect((ip_address, port))
    except timeout:
        print(f"Connection to {ip_address} timed out in {(time_ns() - t1) / 1000000}ms")
    except OSError as exception:
        print(f"General error when trying to connect; {exception}")
    else:
        print(f"Connected to {ip_address}; {(time_ns() - t1) / 1000000}ms")
        tcp_socket.shutdown(SHUT_RD)


def main():
    arguments = argv

    if not arguments[1:]:
        raise AttributeError("Insufficient arguments provided")

    if ":" not in arguments[1]:
        raise AttributeError("Invalid format provided, expected IP:PORT")

    ip_address, port = arguments[1].split(":")
    if not ip_is_valid(ip_address):
        raise TypeError("Invalid or illegal IPv4 address provided")

    if not port.isdigit():
        raise TypeError("Port provided is not an integer")

    port = int(port)
    if not 0 < port <= 65535:
        raise ValueError("Port range is out of boundaries")

    try:
        for _ in range(8):
            try_connect(ip_address, port)
            sleep(0.5)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
