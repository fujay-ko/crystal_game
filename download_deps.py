import os
import urllib.request

# 建立 lib 資料夾
if not os.path.exists('lib'):
    os.makedirs('lib')

# 定義要下載的檔案清單
files = {
    'skulpt.min.js': 'https://cdn.jsdelivr.net/npm/skulpt@1.2.0/dist/skulpt.min.js',
    'skulpt-stdlib.js': 'https://cdn.jsdelivr.net/npm/skulpt@1.2.0/dist/skulpt-stdlib.js',
    'codemirror.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js',
    'codemirror.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css',
    'dracula.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/dracula.min.css',
    'python.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.min.js'
}

print("正在下載必要檔案，請稍候...")

for filename, url in files.items():
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, f'lib/{filename}')
        print(f"OK!")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

print("所有檔案下載完成！")
