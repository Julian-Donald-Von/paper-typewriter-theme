# -*- coding: utf-8 -*-
"""把 paper-follow.js 注入 Typora 窗口 —— 不修改 Typora 本体。

原理：Typora 是 Electron 应用，启动时带上 --remote-debugging-port=9333 后，
就能用 Chrome DevTools 协议连上它的窗口。本脚本：
  1. 立即注入一次（当前页面生效）
  2. 注册 Page.addScriptToEvaluateOnNewDocument（窗口重载后自动再生效）

用法：
  python inject.py            # 默认端口 9333
  python inject.py 9444       # 指定端口
前置：Typora 需以 --remote-debugging-port 启动（见 同目录 启动随动.bat）。
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

try:
    import websocket  # websocket-client
except ImportError:
    print("缺少依赖：pip install websocket-client")
    sys.exit(2)

HERE = Path(__file__).resolve().parent
JS_FILE = HERE / "paper-follow.js"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9333


def fetch(path):
    url = f"http://127.0.0.1:{PORT}{path}"
    with urllib.request.urlopen(url, timeout=4) as r:
        return json.load(r)


def pick_target(targets):
    pages = [t for t in targets if t.get("type") == "page" and t.get("webSocketDebuggerUrl")]
    for t in pages:
        url = (t.get("url") or "").lower()
        if "window.html" in url or "typora" in url:
            return t
    return pages[0] if pages else None


def main():
    if not JS_FILE.exists():
        print(f"找不到 {JS_FILE}")
        return 2
    source = JS_FILE.read_text(encoding="utf-8")

    # 等 Typora 起来
    targets = []
    for _ in range(20):
        try:
            targets = fetch("/json/list")
            break
        except Exception:
            time.sleep(0.5)
    if not targets:
        print(f"连不上 127.0.0.1:{PORT} —— 请用「启动随动.bat」启动 Typora（需带调试端口）")
        return 1

    target = pick_target(targets)
    if target is None:
        print("没有找到 Typora 窗口页面")
        return 1

    print(f"目标窗口: {target.get('title', '')} — {target.get('url', '')}")
    ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=8)

    def send(msg_id, method, params=None):
        payload = {"id": msg_id, "method": method}
        if params:
            payload["params"] = params
        ws.send(json.dumps(payload))

    # 1) 立即注入
    send(1, "Runtime.evaluate", {"expression": source})
    # 2) 重载后自动再生效
    send(2, "Page.addScriptToEvaluateOnNewDocument", {"source": source})

    # 等回执
    got = set()
    deadline = time.time() + 5
    while len(got) < 2 and time.time() < deadline:
        ws.settimeout(max(0.2, deadline - time.time()))
        try:
            msg = json.loads(ws.recv())
        except Exception:
            continue
        if msg.get("id") in (1, 2):
            err = msg.get("error")
            got.add(msg["id"])
            print(("  ✓ " if not err else "  ✗ ") + msg.get("method", str(msg["id"])) +
                  ("" if not err else f" — {err}"))

    # 3) 验证注入结果
    ws.settimeout(4)
    send(3, "Runtime.evaluate", {
        "expression": "String(window.__paperFollowInstalled)",
        "returnByValue": True,
    })
    ok = False
    deadline = time.time() + 4
    while time.time() < deadline:
        try:
            msg = json.loads(ws.recv())
        except Exception:
            break
        if msg.get("id") == 3:
            val = msg.get("result", {}).get("result", {}).get("value")
            ok = val == "true"
            break
    print("注入状态:", "已生效 ✓" if ok else "未生效 ✗")
    ws.close()
    print("提示：窗口重载（Ctrl+R）后随动仍会自动恢复。")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
