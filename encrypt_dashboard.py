#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把看板HTML加密为带密码门的index.html（AES-256-GCM + PBKDF2-SHA256）
用法: python3 encrypt_dashboard.py <看板html路径> [输出路径,默认同目录index.html]
密码从本目录 .password 文件读取（首行）。该文件已被.gitignore排除，绝不入库。
"""
import sys, os, base64, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

HERE = os.path.dirname(os.path.abspath(__file__))
ITER = 310000

def main():
    if len(sys.argv) < 2:
        print("用法: python3 encrypt_dashboard.py <看板html路径> [输出路径]"); sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "index.html")
    pw_file = os.path.join(HERE, ".password")
    if not os.path.exists(pw_file):
        print("缺少 .password 文件"); sys.exit(1)
    pw = open(pw_file, encoding="utf-8").readline().strip()
    if not pw or "CHANGE" in pw.upper():
        print("请先把 .password 改成真正的家庭密码（当前是占位符），拒绝发布"); sys.exit(1)
    html = open(src, encoding="utf-8").read()
    if "cb_temp" not in html and "SEED_ROWS" not in html:
        print("警告：输入文件不像看板HTML，拒绝发布"); sys.exit(1)

    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
    key = kdf.derive(pw.encode())
    ct = AESGCM(key).encrypt(iv, html.encode(), None)
    b64 = lambda b: base64.b64encode(b).decode()

    gate = GATE_TEMPLATE.replace("__SALT__", b64(salt)).replace("__IV__", b64(iv)) \
                        .replace("__ITER__", str(ITER)).replace("__CT__", b64(ct))
    open(out, "w", encoding="utf-8").write(gate)
    print(f"已加密发布 → {out}  (密文 {len(ct)//1024}KB)")

GATE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>转债温度计 · 家庭版</title>
<style>
:root{color-scheme:light}
body{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f4f5f7;display:flex;min-height:100vh;align-items:center;justify-content:center}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:34px 30px;width:300px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,.06)}
h3{margin:0 0 4px;font-size:18px}
.sub{color:#6b7280;font-size:12px;margin-bottom:18px}
input[type=password]{width:100%;box-sizing:border-box;padding:11px 12px;border:1px solid #e5e7eb;border-radius:9px;font-size:15px;text-align:center}
label{display:block;font-size:12px;color:#6b7280;margin:10px 0}
button{width:100%;padding:11px;border:none;border-radius:9px;background:#1a1d23;color:#fff;font-size:14px;cursor:pointer;margin-top:2px}
#err{color:#dc2626;font-size:12px;margin-top:10px;min-height:16px}
</style>
</head>
<body>
<div class="card" id="g">
<h3>转债温度计</h3>
<div class="sub">家庭版 · 请输入访问密码</div>
<input type="password" id="pw" autocomplete="current-password">
<label><input type="checkbox" id="rm" checked> 在这台设备上记住密码</label>
<button id="btn">进入</button>
<div id="err"></div>
</div>
<script>
const SALT="__SALT__",IV="__IV__",CT="__CT__",ITER=__ITER__;
function b64d(s){const b=atob(s);const a=new Uint8Array(b.length);for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a;}
async function derive(pw){
  const km=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
  return crypto.subtle.deriveKey({name:"PBKDF2",salt:b64d(SALT),iterations:ITER,hash:"SHA-256"},km,{name:"AES-GCM",length:256},false,["decrypt"]);
}
async function tryOpen(pw,remember){
  try{
    const k=await derive(pw);
    const pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:b64d(IV)},k,b64d(CT));
    if(remember)localStorage.setItem("fam_gate_pw",pw);
    const html=new TextDecoder().decode(pt);
    document.open();document.write(html);document.close();
    return true;
  }catch(e){return false;}
}
document.getElementById("btn").onclick=async()=>{
  const ok=await tryOpen(document.getElementById("pw").value,document.getElementById("rm").checked);
  if(!ok)document.getElementById("err").textContent="密码不对，再试试";
};
document.getElementById("pw").addEventListener("keydown",e=>{if(e.key==="Enter")document.getElementById("btn").click();});
(async()=>{const s=localStorage.getItem("fam_gate_pw");if(s){if(!await tryOpen(s,false))localStorage.removeItem("fam_gate_pw");}})();
</script>
</body>
</html>"""

if __name__ == "__main__":
    main()
