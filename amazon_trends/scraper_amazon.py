import time
import requests
from DrissionPage import ChromiumPage

def obtener_tendencias_amazon():
    print("🚀 正在启动系统之眼（使用 DrissionPage 爬虫）...")
    
    # 启动浏览器（将打开一个可见的 Chrome 窗口）
    # DrissionPage 使用您计算机上安装的 Chrome 引擎，从而避开拦截。
    page = ChromiumPage()
    
    # 导航到亚马逊畅销品电子产品部分 (纯文本 URL，无括号)
    url = 'https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/'
    print(f"🌐 正在导航至：{url}")
    page.get(url)
    
    # 像人类一样等待页面加载
    time.sleep(4)
    
    tendencias = []
    
    print("🔍 正在分析页面结构...")
    # 查找产品网格元素。
    # 我们使用 XPath，这是一个非常强大的抓取数据的选择器。
    productos = page.eles('x://div[contains(@class, "zg-grid-general-faceout")]')
    
    if not productos:
        print("⚠️ 未找到产品。正在尝试备用选择器...")
        productos = page.eles('.p13n-sc-uncoverable-faceout')

    # 我们只取前 5 名，以免在此测试中使数据库饱和
    for i, item in enumerate(productos[:5]):
        try:
            # 提取产品框的全部文本
            texto_crudo = item.text
            
            # 文本包含价格、星级等。通常标题是最长的一行。
            lineas = texto_crudo.split('\n')
            if lineas:
                # 找到字符最多的一行（产品名称）
                titulo = max(lineas, key=len)
                
                # 完全按照第 2 阶段 API 期望的格式格式化数据
                tendencias.append({
                    "termino_busqueda": titulo[:150], # 限制为 150 个字符
                    "fuente": "Amazon Best Sellers",
                    "puntuacion_viral": 100 - i # 第一名得分最高
                })
        except Exception as e:
            print(f"处理项目时出错：{e}")
            pass
            
    # 关闭浏览器
    page.quit()
    print(f"🎯 提取完成：找到 {len(tendencias)} 个趋势。")
    return tendencias

def enviar_a_nuestra_api(tendencias):
    # 这是我们本地 API（第 2 阶段）的 URL
    url_api = "http://127.0.0.1:8000/api/core/tendencias/ingestar/"
    payload = {"tendencias": tendencias}
    
    print("\n📡 正在向本地 API 发送批量数据...")
    try:
        response = requests.post(url_api, json=payload)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 成功！API 响应：")
            print(f"   - 保存的新记录：{data['nuevos_registros']}")
            print(f"   - 智能拦截的重复项：{data['duplicados_omitidos']}")
        else:
            print(f"❌ API 错误：代码 {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ 严重错误：无法连接到 API。")
        print("-> 诊断：您的 Django 服务器未开启。")
        print("-> 解决方案：打开另一个终端并执行 'python manage.py runserver'")

if __name__ == '__main__':
    datos = obtener_tendencias_amazon()
    if datos:
        enviar_a_nuestra_api(datos)
    else:
        print("❌ 爬虫无法提取数据。亚马逊可能要求输入验证码 (CAPTCHA)。")