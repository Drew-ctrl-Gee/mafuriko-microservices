"""
MafurikoAI - API Gateway with Monitoring
Routes requests + provides system-wide monitoring
"""
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import os
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Service URLs
AUTH_SERVICE = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
WEATHER_SERVICE = os.getenv('WEATHER_SERVICE_URL', 'http://localhost:5002')
ML_SERVICE = os.getenv('ML_SERVICE_URL', 'http://localhost:5003')
CHATBOT_SERVICE = os.getenv('CHATBOT_SERVICE_URL', 'http://localhost:5004')

# Metrics tracking
gateway_metrics = {
    "total_requests": 0,
    "requests_by_service": {"auth": 0, "weather": 0, "ml": 0, "chatbot": 0},
    "total_errors": 0,
    "total_response_time": 0,
    "started_at": datetime.now().isoformat()
}


@app.route('/', methods=['GET'])
def home():
    """API Gateway home"""
    return jsonify({
        "service": "MafurikoAI API Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "dashboard": "/dashboard",
            "auth": "/api/auth/*",
            "weather": "/api/weather/<city>",
            "ml_predict": "/api/predict",
            "ml_batch": "/api/predict/batch",
            "chat": "/api/chat"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Comprehensive health check with response times"""
    services = {
        'auth': AUTH_SERVICE,
        'weather': WEATHER_SERVICE,
        'ml': ML_SERVICE,
        'chatbot': CHATBOT_SERVICE
    }
    
    status = {}
    total_healthy = 0
    
    for name, url in services.items():
        start = time.time()
        try:
            resp = requests.get(f"{url}/health", timeout=5)
            response_time = round((time.time() - start) * 1000, 2)
            
            if resp.status_code == 200:
                status[name] = {
                    "status": "✅ healthy",
                    "response_time_ms": response_time,
                    "details": resp.json()
                }
                total_healthy += 1
            else:
                status[name] = {
                    "status": "⚠️ unhealthy",
                    "response_time_ms": response_time
                }
        except Exception as e:
            status[name] = {
                "status": "🔴 unreachable",
                "error": str(e)[:100]
            }
    
    return jsonify({
        "gateway": "✅ healthy",
        "services_healthy": f"{total_healthy}/{len(services)}",
        "overall_health": "healthy" if total_healthy == len(services) else "degraded",
        "services": status,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/metrics', methods=['GET'])
def system_metrics():
    """System-wide metrics from all services"""
    metrics_data = {
        "gateway": {
            "total_requests": gateway_metrics["total_requests"],
            "total_errors": gateway_metrics["total_errors"],
            "requests_by_service": gateway_metrics["requests_by_service"],
            "avg_response_time_ms": round(
                (gateway_metrics["total_response_time"] / gateway_metrics["total_requests"] * 1000)
                if gateway_metrics["total_requests"] > 0 else 0, 2
            ),
            "uptime_seconds": int(
                (datetime.now() - datetime.fromisoformat(gateway_metrics["started_at"])).total_seconds()
            )
        },
        "services": {}
    }
    
    # Get metrics from ML service
    try:
        ml_resp = requests.get(f"{ML_SERVICE}/metrics", timeout=3)
        if ml_resp.status_code == 200:
            metrics_data["services"]["ml"] = ml_resp.json()
    except:
        metrics_data["services"]["ml"] = {"status": "unavailable"}
    
    return jsonify(metrics_data)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """HTML monitoring dashboard"""
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MafurikoAI - System Monitoring</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                color: white;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { text-align: center; margin-bottom: 30px; }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: rgba(255,255,255,0.15);
                backdrop-filter: blur(10px);
                padding: 25px;
                border-radius: 15px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .stat-value {
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }
            .stat-label { opacity: 0.9; }
            .service-status {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                margin-bottom: 10px;
            }
            .healthy { color: #4ade80; }
            .unhealthy { color: #ef4444; }
            .refresh-btn {
                background: #22c55e;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌧️ MafurikoAI Monitoring Dashboard</h1>
            
            <div class="stats-grid" id="stats">
                <div class="stat-card">
                    <div class="stat-label">Total Requests</div>
                    <div class="stat-value" id="totalRequests">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Response Time</div>
                    <div class="stat-value" id="avgResponseTime">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Services Healthy</div>
                    <div class="stat-value" id="servicesHealthy">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Uptime</div>
                    <div class="stat-value" id="uptime">-</div>
                </div>
            </div>
            
            <h2>📊 Service Status</h2>
            <div id="services"></div>
            
            <div style="text-align: center;">
                <button class="refresh-btn" onclick="refresh()">🔄 Refresh</button>
                <button class="refresh-btn" onclick="autoRefresh()" id="autoBtn">▶️ Auto-Refresh</button>
            </div>
        </div>
        
        <script>
            let autoRefreshInterval = null;
            
            async function refresh() {
                try {
                    const health = await fetch('/health').then(r => r.json());
                    const metrics = await fetch('/metrics').then(r => r.json());
                    
                    document.getElementById('totalRequests').textContent = metrics.gateway.total_requests;
                    document.getElementById('avgResponseTime').textContent = metrics.gateway.avg_response_time_ms + 'ms';
                    document.getElementById('servicesHealthy').textContent = health.services_healthy;
                    document.getElementById('uptime').textContent = formatUptime(metrics.gateway.uptime_seconds);
                    
                    let servicesHtml = '';
                    for (const [name, info] of Object.entries(health.services)) {
                        const isHealthy = info.status.includes('healthy');
                        servicesHtml += `
                            <div class="service-status">
                                <div>
                                    <strong>${name.toUpperCase()}</strong>
                                    <div style="opacity:0.8">${info.status}</div>
                                </div>
                                <div>${info.response_time_ms || 'N/A'}ms</div>
                            </div>
                        `;
                    }
                    document.getElementById('services').innerHTML = servicesHtml;
                    
                } catch (e) {
                    console.error(e);
                }
            }
            
            function formatUptime(seconds) {
                const hours = Math.floor(seconds / 3600);
                const minutes = Math.floor((seconds % 3600) / 60);
                return `${hours}h ${minutes}m`;
            }
            
            function autoRefresh() {
                const btn = document.getElementById('autoBtn');
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                    btn.textContent = '▶️ Auto-Refresh';
                } else {
                    autoRefreshInterval = setInterval(refresh, 5000);
                    btn.textContent = '⏸️ Stop Auto';
                }
            }
            
            refresh();
        </script>
    </body>
    </html>
    """
    return dashboard_html


@app.route('/api/auth/<path:path>', methods=['GET', 'POST'])
def proxy_auth(path):
    return proxy_request(AUTH_SERVICE, f'/api/auth/{path}', 'auth')


@app.route('/api/weather/<path:path>', methods=['GET'])
def proxy_weather(path):
    return proxy_request(WEATHER_SERVICE, f'/api/weather/{path}', 'weather')


@app.route('/api/predict', methods=['POST'])
def proxy_ml():
    return proxy_request(ML_SERVICE, '/api/predict', 'ml')


@app.route('/api/predict/batch', methods=['POST'])
def proxy_ml_batch():
    return proxy_request(ML_SERVICE, '/api/predict/batch', 'ml')


@app.route('/api/chat', methods=['POST'])
def proxy_chat():
    return proxy_request(CHATBOT_SERVICE, '/api/chat', 'chatbot')


def proxy_request(service_url, path, service_name):
    """Forward request and track metrics"""
    start_time = time.time()
    gateway_metrics["total_requests"] += 1
    gateway_metrics["requests_by_service"][service_name] += 1
    
    try:
        url = f"{service_url}{path}"
        
        if request.method == 'GET':
            response = requests.get(url, params=request.args, timeout=30)
        else:
            response = requests.post(url, json=request.get_json(), timeout=30)
        
        gateway_metrics["total_response_time"] += (time.time() - start_time)
        
        return Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        gateway_metrics["total_errors"] += 1
        return jsonify({"error": f"Service unavailable: {str(e)}"}), 503


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚪 API Gateway with Monitoring starting on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}/dashboard")
    app.run(host='0.0.0.0', port=port, debug=False)