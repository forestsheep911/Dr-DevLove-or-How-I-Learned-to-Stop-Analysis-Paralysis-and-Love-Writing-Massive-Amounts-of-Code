#!/usr/bin/env python3
"""
HTTP 服务器模块 - 托管静态文件和 JSON 数据
"""
import http.server
import json
import os
import socketserver
import threading
import webbrowser
from pathlib import Path
from typing import Optional
from functools import partial


class StaticHandler(http.server.SimpleHTTPRequestHandler):
    """自定义 HTTP 请求处理器"""
    
    def __init__(self, *args, static_dir: str, data_json: str, **kwargs):
        self.static_dir = static_dir
        self.data_json = data_json
        super().__init__(*args, directory=static_dir, **kwargs)
    
    def do_GET(self):
        # 忽略 favicon 请求，避免 404 噪音
        if self.path == '/favicon.ico' or self.path == '/favicon.ico/':
            self.send_response(204)
            self.end_headers()
            return

        # 处理 /data.json 请求
        if self.path == '/data.json' or self.path == '/data.json/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(self.data_json.encode('utf-8'))
            return
        
        # 处理根路径
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        
        # 静态文件
        return super().do_GET()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"  [{self.log_date_time_string()}] {format % args}")
    
    def end_headers(self):
        # 添加 CORS 头（开发时可能需要）
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


def get_static_dir() -> Path:
    """获取静态文件目录路径"""
    # 优先使用包内的 static 目录
    package_dir = Path(__file__).parent
    static_dir = package_dir / 'static'
    
    if static_dir.exists():
        return static_dir
    
    # 开发模式：使用 web/out 目录
    project_root = package_dir.parent.parent
    dev_static = project_root / 'web' / 'out'
    
    if dev_static.exists():
        return dev_static
    
    raise FileNotFoundError(
        "Static files not found. Please build the web frontend first:\n"
        "  cd web && pnpm build"
    )


def start_server(
    data_json: str,
    port: int = 8080,
    open_browser: bool = True,
    static_dir: Optional[Path] = None,
) -> None:
    """
    启动 HTTP 服务器
    
    Args:
        data_json: JSON 数据字符串
        port: 服务器端口
        open_browser: 是否自动打开浏览器
        static_dir: 静态文件目录（可选，默认自动检测）
    """
    if static_dir is None:
        static_dir = get_static_dir()
    
    # 创建请求处理器
    handler = partial(
        StaticHandler,
        static_dir=str(static_dir),
        data_json=data_json,
    )
    
    # 尝试绑定端口
    server = None
    actual_port = port
    
    for try_port in range(port, port + 10):
        try:
            server = socketserver.TCPServer(("", try_port), handler)
            actual_port = try_port
            break
        except OSError:
            continue
    
    if server is None:
        print(f"Error: Could not find an available port in range {port}-{port+9}")
        return
    
    url = f"http://localhost:{actual_port}"
    
    print(f"\n{'='*50}")
    print(f"  Dr. DevLove Web Dashboard")
    print(f"{'='*50}")
    print(f"  Server running at: {url}")
    print(f"  Static files: {static_dir}")
    print(f"{'='*50}")
    print(f"  Press Ctrl+C to stop the server")
    print(f"{'='*50}\n")
    
    # 自动打开浏览器
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    finally:
        server.shutdown()


def create_fallback_html(data_json: str) -> str:
    """
    创建后备 HTML 页面（当静态文件不存在时）
    
    这是一个简单的 HTML 页面，直接嵌入数据显示基本统计信息
    """
    data = json.loads(data_json)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dr. DevLove - GitHub Stats</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Dr. DevLove 统计报告</h1>
        <p class="text-gray-600 mb-8">
            {data['meta'].get('user', '')} | 
            {data['meta']['dateRange']['since']} ~ {data['meta']['dateRange']['until']}
        </p>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-lg shadow p-4">
                <p class="text-gray-500 text-sm">总提交数</p>
                <p class="text-2xl font-bold">{data['summary']['totalCommits']}</p>
            </div>
            <div class="bg-white rounded-lg shadow p-4">
                <p class="text-gray-500 text-sm">新增行数</p>
                <p class="text-2xl font-bold text-green-600">+{data['summary']['totalAdded']:,}</p>
            </div>
            <div class="bg-white rounded-lg shadow p-4">
                <p class="text-gray-500 text-sm">删除行数</p>
                <p class="text-2xl font-bold text-red-600">-{data['summary']['totalDeleted']:,}</p>
            </div>
            <div class="bg-white rounded-lg shadow p-4">
                <p class="text-gray-500 text-sm">净增长</p>
                <p class="text-2xl font-bold">{data['summary']['netGrowth']:,}</p>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-bold mb-4">仓库统计</h2>
            <table class="w-full">
                <thead>
                    <tr class="text-left text-gray-500 border-b">
                        <th class="pb-2">仓库</th>
                        <th class="pb-2 text-right">提交</th>
                        <th class="pb-2 text-right">新增</th>
                        <th class="pb-2 text-right">删除</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'''
                    <tr class="border-b">
                        <td class="py-2">{repo['name']}</td>
                        <td class="py-2 text-right">{repo['commits']}</td>
                        <td class="py-2 text-right text-green-600">+{repo['added']:,}</td>
                        <td class="py-2 text-right text-red-600">-{repo['deleted']:,}</td>
                    </tr>
                    ''' for repo in data['repos'][:20])}
                </tbody>
            </table>
        </div>
        
        <p class="text-center text-gray-500 text-sm">
            提示：完整的图表功能需要先构建前端。运行 <code class="bg-gray-200 px-1 rounded">cd web && pnpm build</code>
        </p>
    </div>
    
    <script>
        // 数据可以通过 /data.json 获取
        console.log('Stats data available at /data.json');
    </script>
</body>
</html>"""
    
    return html


class FallbackHandler(http.server.BaseHTTPRequestHandler):
    """后备 HTTP 处理器（无静态文件时使用）"""
    
    def __init__(self, *args, data_json: str, **kwargs):
        self.data_json = data_json
        self.fallback_html = create_fallback_html(data_json)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/favicon.ico' or self.path == '/favicon.ico/':
            self.send_response(204)
            self.end_headers()
            return

        if self.path == '/data.json' or self.path == '/data.json/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.data_json.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.fallback_html.encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"  [{self.log_date_time_string()}] {format % args}")


def start_fallback_server(
    data_json: str,
    port: int = 8080,
    open_browser: bool = True,
) -> None:
    """
    启动后备服务器（无静态文件时使用）
    """
    handler = partial(FallbackHandler, data_json=data_json)
    
    server = None
    actual_port = port
    
    for try_port in range(port, port + 10):
        try:
            server = socketserver.TCPServer(("", try_port), handler)
            actual_port = try_port
            break
        except OSError:
            continue
    
    if server is None:
        print(f"Error: Could not find an available port")
        return
    
    url = f"http://localhost:{actual_port}"
    
    print(f"\n{'='*50}")
    print(f"  Dr. DevLove Web Dashboard (Fallback Mode)")
    print(f"{'='*50}")
    print(f"  Server running at: {url}")
    print(f"  Note: Using fallback HTML. Build frontend for full features.")
    print(f"{'='*50}")
    print(f"  Press Ctrl+C to stop the server")
    print(f"{'='*50}\n")
    
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    finally:
        server.shutdown()
