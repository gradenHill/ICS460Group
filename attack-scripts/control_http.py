import socket
import time

target_ip = "10.0.0.10"
target_port = 80

def main():
    print(f"Sending normal HTTP traffic to {target_ip}:{target_port}")

    for i in range(10):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)

            s.connect((target_ip, target_port))

            request = (
                "GET / HTTP/1.1\r\n"
                f"Host: {target_ip}\r\n"
                "User-Agent: Mozilla/5.0\r\n"
                "Connection: close\r\n\r\n"
            )

            s.send(request.encode())

            data = s.recv(1024)

            print(f"[NORMAL] Request {i+1} successful")

            s.close()

        except Exception as e:
            print(f"Request failed: {e}")

        time.sleep(1)

if __name__ == "__main__":
    main()
