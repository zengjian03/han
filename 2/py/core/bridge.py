#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import pickle
import socket
import struct
import sys

HOST = "127.0.0.1"
PORT = 57570
MAX_MSG_SIZE = 10 * 1024 * 1024
TIMEOUT = 30

def send_packet(sock, obj: dict):
    payload = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    if len(payload) > MAX_MSG_SIZE:
        raise ValueError("payload too large")
    sock.sendall(struct.pack(">I", len(payload)))
    sock.sendall(payload)

def recv_exact(sock, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("peer closed")
        data += chunk
    return data

def recv_packet(sock) -> dict:
    header = recv_exact(sock, 4)
    (length,) = struct.unpack(">I", header)
    if length <= 0 or length > MAX_MSG_SIZE:
        raise ValueError("invalid length")
    payload = recv_exact(sock, length)
    return pickle.loads(payload)

def main():
    p = argparse.ArgumentParser(description="T4 CLI bridge")
    p.add_argument("--script-path", required=True, help="Spider脚本路径或模块名")
    p.add_argument("--method-name", required=True, help="要调用的方法名")
    p.add_argument("--env", default="", help="JSON字符串（可包含 proxyUrl/ext）或普通字符串")
    p.add_argument("--arg", action="append", default=[], help="方法参数；可多次传入。每个参数若可解析为JSON则按JSON，否则按字符串")
    p.add_argument("--host", default=HOST, help="守护进程主机（默认127.0.0.1）")
    p.add_argument("--port", type=int, default=PORT, help="守护进程端口（默认57570）")
    p.add_argument("--timeout", type=int, default=TIMEOUT, help="超时秒数（默认30）")
    args = p.parse_args()

    req = {
        "script_path": args.script_path,
        "method_name": args.method_name,
        "env": args.env,
        "args": args.arg,
    }

    try:
        with socket.create_connection((args.host, args.port), timeout=args.timeout) as s:
            s.settimeout(args.timeout)
            send_packet(s, req)
            resp = recv_packet(s)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)

    # 统一以 JSON 打印到 stdout，便于脚本链路消费
    print(json.dumps(resp, ensure_ascii=False))
    # 非0退出码用于指示错误，方便shell判断
    sys.exit(0 if resp.get("success") else 1)

if __name__ == "__main__":
    main()
