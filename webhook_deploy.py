#!/usr/bin/env python3
"""
GitHub Webhook 自动部署服务
监听 GitHub push 事件,自动拉取代码并重新部署
"""
import os
import hmac
import hashlib
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# 配置
WEBHOOK_SECRET = os.getenv(
    "WEBHOOK_SECRET", "your-secret-key-here")  # 在 .env 中设置
REPO_DIR = "/volume2/docker/xiaole-ai"
DEPLOY_SCRIPT = f"{REPO_DIR}/deploy_prod.sh"


def verify_signature(payload_body, signature_header):
    """验证 GitHub Webhook 签名"""
    if not signature_header:
        return False

    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


@app.route("/webhook", methods=["POST"])
def webhook():
    """处理 GitHub Webhook 请求"""
    signature = request.headers.get("X-Hub-Signature-256")
    
    # 调试日志
    print(f"[DEBUG] Webhook received")
    print(f"[DEBUG] Signature from GitHub: {signature}")
    print(f"[DEBUG] WEBHOOK_SECRET (first 8): {WEBHOOK_SECRET[:8]}...")
    print(f"[DEBUG] WEBHOOK_SECRET (last 8): ...{WEBHOOK_SECRET[-8:]}")
    print(f"[DEBUG] Payload size: {len(request.data)} bytes")

    # 验证签名
    if not verify_signature(request.data, signature):
        print("[DEBUG] ❌ Signature verification FAILED!")
        return jsonify({"error": "Invalid signature"}), 403
    
    print("[DEBUG] ✅ Signature verification SUCCESS!")

    payload = request.json

    # 只处理 push 到 main 分支的事件
    if payload.get("ref") != "refs/heads/main":
        return jsonify({"message": "Not main branch, skipped"}), 200

    # 执行部署(容器内 git pull)
    try:
        # 拉取最新代码
        pull_result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd="/app",
            capture_output=True,
            text=True,
            timeout=60
        )

        # 如果有更新,触发容器重启(通过退出让 Docker 自动重启)
        if "Already up to date" not in pull_result.stdout:
            # 记录日志后退出,Docker restart=always 会自动重启
            subprocess.Popen(["bash", "-c", "sleep 2 && kill 1"])

        return jsonify({
            "message": "Deployment triggered",
            "stdout": pull_result.stdout,
            "stderr": pull_result.stderr,
            "returncode": pull_result.returncode
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
