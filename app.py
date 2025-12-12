from flask import Flask, request, render_template_string
import maxminddb
import IP2Location
import os
import socket
from ip2region.searcher import new_with_file_only
from ip2region.util import load_header_from_file, version_from_header

app = Flask(__name__)

# 定义IP库路径
DB_PATH = {
    'geolite2_city': './db/GeoLite2/GeoLite2-City.mmdb',
    'geolite2_country': './db/GeoLite2/GeoLite2-Country.mmdb',
    'geolite2_asn': './db/GeoLite2/GeoLite2-ASN.mmdb',
    'dbip_city': './db/db-ip/dbip-city-lite-2025-12.mmdb',
    'ip2location_v4': './db/ip2location/IP2LOCATION-LITE-DB11.BIN',
    'ip2location_v6': './db/ip2location/IP2LOCATION-LITE-DB11.IPV6.BIN',
    'ip2region_v4': './db/ip2region/ip2region_v4.xdb',
    'ip2region_v6': './db/ip2region/ip2region_v6.xdb'
}

# 初始化IP库读取器
readers = {}

# 初始化GeoLite2和db-ip的mmdb读取器
try:
    readers['geolite2_city'] = maxminddb.open_database(DB_PATH['geolite2_city'])
    readers['geolite2_country'] = maxminddb.open_database(DB_PATH['geolite2_country'])
    readers['geolite2_asn'] = maxminddb.open_database(DB_PATH['geolite2_asn'])
    readers['dbip_city'] = maxminddb.open_database(DB_PATH['dbip_city'])
except Exception as e:
    print(f"Error opening MMDB files: {e}")

# 初始化ip2location读取器
try:
    readers['ip2location_v4'] = IP2Location.IP2Location(DB_PATH['ip2location_v4'])
    readers['ip2location_v6'] = IP2Location.IP2Location(DB_PATH['ip2location_v6'])
except Exception as e:
    print(f"Error opening IP2Location files: {e}")

# 初始化ip2region读取器
try:
    # 加载IPv4数据库
    header_v4 = load_header_from_file(DB_PATH['ip2region_v4'])
    version_v4 = version_from_header(header_v4)
    readers['ip2region_v4'] = new_with_file_only(version_v4, DB_PATH['ip2region_v4'])
    
    # 加载IPv6数据库
    header_v6 = load_header_from_file(DB_PATH['ip2region_v6'])
    version_v6 = version_from_header(header_v6)
    readers['ip2region_v6'] = new_with_file_only(version_v6, DB_PATH['ip2region_v6'])
    
except Exception as e:
    print(f"Error opening ip2region files: {e}")

@app.route('/ip', methods=['GET', 'POST'])
def index():
    result = {}
    
    if request.method == 'POST':
        # 处理表单提交的IP
        ips = request.form.get('ips', '').strip().split('\n')
        ips = [ip.strip() for ip in ips if ip.strip()]
        ips = ips[:10]  # 最多处理10个IP
        
        for ip in ips:
            result[ip] = {
                'geolite2': query_geolite2(ip),
                'dbip': query_dbip(ip),
                'ip2location': query_ip2location(ip),
                'ip2region': query_ip2region(ip)
            }
    else:
        # 默认访问时，显示用户当前IP
        # 获取用户真实IP
        user_ip = request.remote_addr
        if not user_ip or user_ip == '127.0.0.1' or user_ip == '::1':
            # 尝试从X-Forwarded-For等头信息获取真实IP
            user_ip = request.headers.get('X-Real-IP') or request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or user_ip
        
        # 查询用户IP信息
        result[user_ip] = {
            'geolite2': query_geolite2(user_ip),
            'dbip': query_dbip(user_ip),
            'ip2location': query_ip2location(user_ip),
            'ip2region': query_ip2region(user_ip)
        }
    
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>IP查询工具 - Timo Tools</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 30px rgba(0, 0, 100, 0.1);
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    min-height: calc(100vh - 40px);
                }
                
                header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }
                
                header h1 {
                    font-size: 28px;
                    margin-bottom: 10px;
                    font-weight: 600;
                }
                
                header p {
                    font-size: 16px;
                    opacity: 0.9;
                }
                
                main {
                    flex: 1;
                    padding: 30px;
                }
                
                .input-section {
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    border: 1px solid #e9ecef;
                }
                
                .input-section h2 {
                    font-size: 20px;
                    color: #343a40;
                    margin-bottom: 15px;
                    font-weight: 600;
                }
                
                textarea {
                    width: 100%;
                    padding: 15px;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    font-size: 16px;
                    min-height: 180px;
                    resize: vertical;
                    font-family: inherit;
                    transition: all 0.3s ease;
                    background: white;
                }
                
                textarea:focus {
                    outline: none;
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }
                
                button {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 30px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    margin-top: 15px;
                }
                
                button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }
                
                button:active {
                    transform: translateY(0);
                }
                
                .result-section {
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 8px;
                    border: 1px solid #e9ecef;
                }
                
                .result-section h2 {
                    font-size: 20px;
                    color: #343a40;
                    margin-bottom: 20px;
                    font-weight: 600;
                }
                
                .ip-result {
                    background: white;
                    margin-bottom: 20px;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                    border: 1px solid #e9ecef;
                    transition: all 0.3s ease;
                }
                
                .ip-result:hover {
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }
                
                .ip-title {
                    font-size: 20px;
                    font-weight: 600;
                    margin-bottom: 20px;
                    color: #343a40;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #e9ecef;
                }
                
                .database-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                }
                
                .database-result {
                    background: #f8f9fa;
                    padding: 18px;
                    border-radius: 6px;
                    border: 1px solid #e9ecef;
                }
                
                .database-name {
                    font-weight: 600;
                    color: #667eea;
                    margin-bottom: 12px;
                    font-size: 16px;
                }
                
                .info-list {
                    list-style: none;
                }
                
                .info-item {
                    font-size: 14px;
                    color: #555;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                }
                
                .info-item:last-child {
                    margin-bottom: 0;
                }
                
                .info-label {
                    font-weight: 500;
                    color: #666;
                    margin-right: 8px;
                    min-width: 60px;
                }
                
                .error {
                    color: #dc3545;
                    font-size: 14px;
                    padding: 10px;
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    margin-top: 10px;
                }
                
                footer {
                    background: #343a40;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                    margin-top: auto;
                }
                
                footer a {
                    color: #667eea;
                    text-decoration: none;
                    transition: color 0.3s ease;
                }
                
                footer a:hover {
                    color: #764ba2;
                    text-decoration: underline;
                }
                
                .footer-content {
                    max-width: 1200px;
                    margin: 0 auto;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 10px;
                }
                
                .footer-info {
                    text-align: center;
                }
                
                .footer-info p {
                    margin: 2px 0;
                    color: white;
                    opacity: 0.9;
                    line-height: 1.4;
                }
                
                .footer-info a {
                    color: #667eea;
                    text-decoration: none;
                    transition: color 0.3s ease;
                }
                
                .footer-info a:hover {
                    color: #764ba2;
                    text-decoration: underline;
                }
                
                @media (max-width: 768px) {
                    body {
                        padding: 10px;
                    }
                    
                    .container {
                        min-height: calc(100vh - 20px);
                    }
                    
                    header, main {
                        padding: 20px;
                    }
                    
                    header h1 {
                        font-size: 24px;
                    }
                    
                    .database-container {
                        grid-template-columns: 1fr;
                    }
                    
                    .footer-links {
                        flex-direction: column;
                        gap: 10px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>IP查询工具</h1>
                    <p>支持最多10个IP地址的批量查询，包括IPv4和IPv6</p>
                    {% if request.method == 'GET' and result %}
                    <p style="margin-top: 10px; font-weight: 600;">你的IP是: {% for ip in result.keys() %}{{ ip }}{% endfor %}</p>
                    {% endif %}
                </header>
                
                <main>
                    <div class="input-section">
                        <h2>输入IP地址</h2>
                        <form method="post" action="/ip">
                            <textarea name="ips" placeholder="请输入IP地址，每行一个，最多10个">{{ request.form.get('ips', '') }}</textarea>
                            <br>
                            <button type="submit">查询</button>
                        </form>
                    </div>
                    
                    {% if result %}
                    <div class="result-section">
                        <h2>查询结果</h2>
                        {% for ip, data in result.items() %}
                        <div class="ip-result">
                            <div class="ip-title">IP: {{ ip }}</div>
                            
                            <div class="database-container">
                                <!-- GeoLite2 -->
                                <div class="database-result">
                                    <div class="database-name">1. GeoLite2</div>
                                    {% if data.geolite2.error %}
                                    <div class="error">{{ data.geolite2.error }}</div>
                                    {% else %}
                                    <ul class="info-list">
                                        {% if data.geolite2.country %}
                                        <li class="info-item"><span class="info-label">国家:</span> {{ data.geolite2.country }}</li>
                                        {% endif %}
                                        {% if data.geolite2.region %}
                                        <li class="info-item"><span class="info-label">地区:</span> {{ data.geolite2.region }}</li>
                                        {% endif %}
                                        {% if data.geolite2.city %}
                                        <li class="info-item"><span class="info-label">城市:</span> {{ data.geolite2.city }}</li>
                                        {% endif %}
                                        {% if data.geolite2.latitude %}
                                        <li class="info-item"><span class="info-label">纬度:</span> {{ data.geolite2.latitude }}</li>
                                        {% endif %}
                                        {% if data.geolite2.longitude %}
                                        <li class="info-item"><span class="info-label">经度:</span> {{ data.geolite2.longitude }}</li>
                                        {% endif %}
                                        {% if data.geolite2.asn %}
                                        <li class="info-item"><span class="info-label">ASN:</span> {{ data.geolite2.asn }}</li>
                                        {% endif %}
                                        {% if data.geolite2.isp %}
                                        <li class="info-item"><span class="info-label">ISP:</span> {{ data.geolite2.isp }}</li>
                                        {% endif %}
                                    </ul>
                                    {% endif %}
                                </div>
                                
                                <!-- db-ip -->
                                <div class="database-result">
                                    <div class="database-name">2. db-ip</div>
                                    {% if data.dbip.error %}
                                    <div class="error">{{ data.dbip.error }}</div>
                                    {% else %}
                                    <ul class="info-list">
                                        {% if data.dbip.country %}
                                        <li class="info-item"><span class="info-label">国家:</span> {{ data.dbip.country }}</li>
                                        {% endif %}
                                        {% if data.dbip.region %}
                                        <li class="info-item"><span class="info-label">地区:</span> {{ data.dbip.region }}</li>
                                        {% endif %}
                                        {% if data.dbip.city %}
                                        <li class="info-item"><span class="info-label">城市:</span> {{ data.dbip.city }}</li>
                                        {% endif %}
                                        {% if data.dbip.latitude %}
                                        <li class="info-item"><span class="info-label">纬度:</span> {{ data.dbip.latitude }}</li>
                                        {% endif %}
                                        {% if data.dbip.longitude %}
                                        <li class="info-item"><span class="info-label">经度:</span> {{ data.dbip.longitude }}</li>
                                        {% endif %}
                                    </ul>
                                    {% endif %}
                                </div>
                                
                                <!-- ip2location -->
                                <div class="database-result">
                                    <div class="database-name">3. ip2location</div>
                                    {% if data.ip2location.error %}
                                    <div class="error">{{ data.ip2location.error }}</div>
                                    {% else %}
                                    <ul class="info-list">
                                        {% if data.ip2location.country %}
                                        <li class="info-item"><span class="info-label">国家:</span> {{ data.ip2location.country }}</li>
                                        {% endif %}
                                        {% if data.ip2location.region %}
                                        <li class="info-item"><span class="info-label">地区:</span> {{ data.ip2location.region }}</li>
                                        {% endif %}
                                        {% if data.ip2location.city %}
                                        <li class="info-item"><span class="info-label">城市:</span> {{ data.ip2location.city }}</li>
                                        {% endif %}
                                        {% if data.ip2location.zipcode %}
                                        <li class="info-item"><span class="info-label">邮编:</span> {{ data.ip2location.zipcode }}</li>
                                        {% endif %}
                                    </ul>
                                    {% endif %}
                                </div>
                                
                                <!-- ip2region -->
                                <div class="database-result">
                                    <div class="database-name">4. ip2region</div>
                                    {% if data.ip2region.error %}
                                    <div class="error">{{ data.ip2region.error }}</div>
                                    {% else %}
                                    <ul class="info-list">
                                        {% if data.ip2region.country %}
                                        <li class="info-item"><span class="info-label">国家:</span> {{ data.ip2region.country }}</li>
                                        {% endif %}
                                        {% if data.ip2region.region %}
                                        <li class="info-item"><span class="info-label">地区:</span> {{ data.ip2region.region }}</li>
                                        {% endif %}
                                        {% if data.ip2region.city %}
                                        <li class="info-item"><span class="info-label">城市:</span> {{ data.ip2region.city }}</li>
                                        {% endif %}
                                        {% if data.ip2region.isp %}
                                        <li class="info-item"><span class="info-label">ISP:</span> {{ data.ip2region.isp }}</li>
                                        {% endif %}
                                    </ul>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                </main>
                
                <footer>
                    <div class="footer-content">
                        <div class="footer-info">
                            <p>Author：Timo & TRAE</p>
                            <p>GitHub：<a href="https://github.com/timoseven/ip" target="_blank">https://github.com/timoseven/ip</a></p>
                        </div>
                    </div>
                </footer>
            </div>
        </body>
        </html>
    ''', result=result)

def query_geolite2(ip):
    """使用GeoLite2查询IP信息，同时查询city、country、asn三个数据库"""
    try:
        result = {}
        
        # 查询city数据库
        if 'geolite2_city' in readers:
            city_data = readers['geolite2_city'].get(ip)
            if city_data:
                # 1. 处理国家信息
                country_data = city_data.get('registered_country') or city_data.get('country')
                if country_data and 'names' in country_data:
                    result['country'] = country_data['names'].get('zh-CN', country_data['names'].get('en', ''))
                
                # 2. 处理城市信息，优先从subdivisions获取，再从city获取
                city_name = ''
                
                # 尝试从subdivisions获取地区信息（可能包含城市或省份）
                if 'subdivisions' in city_data and city_data['subdivisions']:
                    result['region'] = city_data['subdivisions'][0]['names'].get('zh-CN', city_data['subdivisions'][0]['names'].get('en', ''))
                    # 使用地区信息作为城市名的备选
                    city_name = result['region']
                
                # 尝试从city字段获取城市信息
                if 'city' in city_data and 'names' in city_data['city']:
                    city_from_city = city_data['city']['names'].get('zh-CN', city_data['city']['names'].get('en', ''))
                    if city_from_city:
                        city_name = city_from_city
                
                # 3. 处理经纬度信息
                if 'location' in city_data:
                    if 'latitude' in city_data['location']:
                        result['latitude'] = city_data['location']['latitude']
                    if 'longitude' in city_data['location']:
                        result['longitude'] = city_data['location']['longitude']
                
                # 4. 如果仍然没有城市信息，使用国家名作为城市名
                if not city_name and 'country' in result:
                    city_name = result['country']
                
                # 添加城市信息
                result['city'] = city_name
        
        # 查询asn数据库
        if 'geolite2_asn' in readers:
            asn_data = readers['geolite2_asn'].get(ip)
            if asn_data:
                if 'autonomous_system_number' in asn_data:
                    result['asn'] = asn_data['autonomous_system_number']
                if 'autonomous_system_organization' in asn_data:
                    result['isp'] = asn_data['autonomous_system_organization']
        
        # 查询country数据库作为补充
        if 'geolite2_country' in readers and 'country' not in result:
            country_data = readers['geolite2_country'].get(ip)
            if country_data:
                country_info = country_data.get('registered_country') or country_data.get('country')
                if country_info and 'names' in country_info:
                    country_name = country_info['names'].get('zh-CN', country_info['names'].get('en', ''))
                    result['country'] = country_name
                    # 补充城市信息
                    if 'city' not in result:
                        result['city'] = country_name
        
        return result if result else {'error': '未找到信息'}
    except Exception as e:
        return {'error': str(e)}

def query_dbip(ip):
    """使用db-ip查询IP信息"""
    try:
        if 'dbip_city' not in readers:
            return {'error': 'db-ip数据库未加载'}
        
        data = readers['dbip_city'].get(ip)
        if not data:
            return {'error': '未找到信息'}
        
        result = {}
        if 'city' in data and 'names' in data['city']:
            result['city'] = data['city']['names'].get('zh-CN', data['city']['names'].get('en', ''))
        
        if 'country' in data and 'names' in data['country']:
            result['country'] = data['country']['names'].get('zh-CN', data['country']['names'].get('en', ''))
        
        if 'subdivisions' in data and data['subdivisions']:
            result['region'] = data['subdivisions'][0]['names'].get('zh-CN', data['subdivisions'][0]['names'].get('en', ''))
        
        if 'location' in data:
            if 'latitude' in data['location']:
                result['latitude'] = data['location']['latitude']
            if 'longitude' in data['location']:
                result['longitude'] = data['location']['longitude']
        
        return result
    except Exception as e:
        return {'error': str(e)}

def query_ip2location(ip):
    """使用ip2location查询IP信息"""
    try:
        # 判断IP类型
        is_ipv6 = False
        try:
            socket.inet_aton(ip)
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip)
                is_ipv6 = True
            except socket.error:
                return {'error': '无效的IP地址'}
        
        # 选择对应的数据库
        reader_key = 'ip2location_v6' if is_ipv6 else 'ip2location_v4'
        if reader_key not in readers:
            return {'error': f'ip2location {"IPv6" if is_ipv6 else "IPv4"}数据库未加载'}
        
        rec = readers[reader_key].get_all(ip)
        if not rec:
            return {'error': '未找到信息'}
        
        result = {}
        if rec.city:
            result['city'] = rec.city
        if rec.country_long:
            result['country'] = rec.country_long
        if rec.region:
            result['region'] = rec.region
        if rec.isp:
            result['isp'] = rec.isp
        if rec.domain:
            result['domain'] = rec.domain
        if rec.zipcode:
            result['zipcode'] = rec.zipcode
        
        return result
    except Exception as e:
        return {'error': str(e)}

def query_ip2region(ip):
    """使用ip2region查询IP信息，返回更准确的结果"""
    try:
        # 判断IP类型
        is_ipv6 = False
        try:
            socket.inet_aton(ip)
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip)
                is_ipv6 = True
            except socket.error:
                return {'error': '无效的IP地址'}
        
        # 选择对应的数据库
        reader_key = 'ip2region_v6' if is_ipv6 else 'ip2region_v4'
        if reader_key not in readers:
            return {'error': f'ip2region {"IPv6" if is_ipv6 else "IPv4"}数据库未加载'}
        
        # 使用官方库查询
        region_str = readers[reader_key].search(ip)
        if not region_str:
            return {'error': '未找到信息'}
        
        # 解析结果，格式为：国家|省份|城市|ISP
        parts = region_str.split('|')
        if len(parts) < 4:
            return {'error': '未找到信息'}
        
        # 构建结果
        result = {
            'country': parts[0],
            'region': parts[1],
            'city': parts[2],
            'isp': parts[3]
        }
        
        return result
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
