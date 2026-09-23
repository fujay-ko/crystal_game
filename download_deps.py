"""下載網頁版所需的前端函式庫到 lib/ 資料夾。

注意：lib/ 已隨專案附上，通常不需要執行此腳本。
只有在 lib/ 缺檔時才需要執行。
"""
import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, 'lib')
os.makedirs(LIB_DIR, exist_ok=True)

# 定義要下載的檔案清單
files = {
    'skulpt.min.js': 'https://cdn.jsdelivr.net/npm/skulpt@1.2.0/dist/skulpt.min.js',
    'skulpt-stdlib.js': 'https://cdn.jsdelivr.net/npm/skulpt@1.2.0/dist/skulpt-stdlib.js',
    'codemirror.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js',
    'codemirror.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css',
    'dracula.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/dracula.min.css',
    'python.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.min.js'
}

print("正在檢查必要檔案，請稍候...")

failed = []
for filename, url in files.items():
    dest = os.path.join(LIB_DIR, filename)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"Skip {filename} (已存在)")
        continue
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, dest)
        if os.path.getsize(dest) == 0:
            raise IOError("下載的檔案是空的")
        print("OK!")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        failed.append(filename)

if failed:
    print("以下檔案下載失敗：" + ", ".join(failed))
    sys.exit(1)
print("所有檔案齊全！")
