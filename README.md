# IP查询工具

一个基于Python Flask的IP地址查询工具，支持多种IP数据库查询，包括GeoLite2、db-ip、ip2location和ip2region。

## 功能特性

- ✅ 支持最多10个IP地址的批量查询
- ✅ 支持IPv4和IPv6地址查询
- ✅ 集成4种IP数据库：GeoLite2、db-ip、ip2location、ip2region
- ✅ 现代化的响应式UI设计
- ✅ 清晰的查询结果展示
- ✅ 支持部署到特定路径

## 技术栈

- **后端框架**: Flask
- **IP数据库**: 
  - GeoLite2
  - db-ip
  - ip2location
  - ip2region
- **前端**: HTML5 + CSS3

## 项目结构

```
ip/
├── app.py              # 主应用程序
├── requirements.txt    # 依赖列表
├── db/                 # IP数据库目录
│   ├── GeoLite2/       # GeoLite2数据库
│   ├── db-ip/          # db-ip数据库
│   ├── ip2location/    # ip2location数据库
│   └── ip2region/      # ip2region数据库
└── venv/               # Python虚拟环境
```

## 安装和运行

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

应用将运行在 `http://127.0.0.1:5001/ip`

## 使用方法

1. 在浏览器中访问 `http://127.0.0.1:5001/ip`
2. 在文本框中输入IP地址，每行一个，最多10个
3. 点击"查询"按钮查看结果
4. 查询结果将按数据库分类显示

## 查询结果说明

### GeoLite2
- 城市
- 国家
- 地区
- 纬度
- 经度
- ASN
- ISP

### db-ip
- 城市
- 国家
- 地区
- 纬度
- 经度

### ip2location
- 城市
- 国家
- 地区
- 邮编

### ip2region
- 国家
- 地区
- 城市
- ISP

## 部署说明

### 部署到特定路径

应用默认运行在 `/ip` 路径下，如需修改，请修改 `app.py` 中的路由装饰器：

```python
@app.route('/your-path', methods=['GET', 'POST'])
def index():
    # ...
```

同时修改HTML表单的action属性：

```html
<form method="post" action="/your-path">
    <!-- ... -->
</form>
```

### 使用Nginx反向代理

```nginx
location /ip {
    proxy_pass http://localhost:5001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 依赖列表

- Flask
- maxminddb
- IP2Location
- requests
- ip2region (从Gitee安装)

## 许可证

MIT License

## 作者

Timo & TRAE

GitHub: https://github.com/timoseven/dividend-ranker