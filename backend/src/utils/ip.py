from flask import request

def get_client_ip():
    xff = request.headers.get("X-Forwarded-For", "")
    ip = xff.split(",")[0].strip() if xff else None
    if not ip:
        ip = request.headers.get("X-Real-IP")
    if not ip:
        ip = request.remote_addr
    if ip in ("::1", "127.0.0.1") or ip.startswith(("10.", "172.", "192.168.")):
        ip = None
    return ip