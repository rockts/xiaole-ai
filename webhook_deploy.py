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

    # 验证签名
    if not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 403

    payload = request.json

    # 只处理 push 到 main 分支的事件
    if payload.get("ref") != "refs/heads/main":
        return jsonify({"message": "Not main branch, skipped"}), 200

    # 执行部署
    try:
        result = subprocess.run(
            ["bash", DEPLOY_SCRIPT],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )

        return jsonify({
            "message": "Deployment triggered",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
