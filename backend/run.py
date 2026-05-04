import sys
import os

# 添加本地包路径到最前面
packages_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'packages')
if packages_dir not in sys.path:
    sys.path.insert(0, packages_dir)

import uvicorn

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
