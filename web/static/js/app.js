// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        // Update active tab
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Update active pane
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Load reports if switching to reports tab
        if (tabName === 'reports') {
            loadReports();
        }
    });
});

// Check health status
async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        const statusText = document.getElementById('status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (data.status === 'healthy') {
            statusText.textContent = 'Ollama 已连接';
            statusDot.style.background = '#10b981';
        } else {
            statusText.textContent = 'Ollama 未连接';
            statusDot.style.background = '#ef4444';
        }
    } catch (error) {
        document.getElementById('status-text').textContent = '连接失败';
        document.querySelector('.status-dot').style.background = '#ef4444';
    }
}

// Analyze code
document.getElementById('analyze-btn').addEventListener('click', async () => {
    const code = document.getElementById('code-input').value;
    const language = document.getElementById('language').value;
    
    if (!code.trim()) {
        alert('请输入代码！');
        return;
    }
    
    const btn = document.getElementById('analyze-btn');
    const btnText = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.spinner');
    
    // Show loading state
    btn.disabled = true;
    btnText.textContent = '分析中...';
    spinner.style.display = 'inline-block';
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                language: language,
                type: 'basic'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show result
            const resultContainer = document.getElementById('analysis-result');
            const resultContent = document.getElementById('analysis-content');
            
            resultContent.innerHTML = data.html;
            resultContainer.style.display = 'block';
            
            // Scroll to result
            resultContainer.scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('分析失败: ' + data.error);
        }
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        // Reset button state
        btn.disabled = false;
        btnText.textContent = '开始分析';
        spinner.style.display = 'none';
    }
});

// Load reports
async function loadReports() {
    const reportsList = document.getElementById('reports-list');
    reportsList.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        const response = await fetch('/reports');
        const reports = await response.json();
        
        if (reports.length === 0) {
            reportsList.innerHTML = '<div class="loading">暂无报告</div>';
            return;
        }
        
        reportsList.innerHTML = '';
        reports.forEach(report => {
            const item = document.createElement('div');
            item.className = 'report-item';
            item.innerHTML = `
                <h4>${report.name}</h4>
                <div class="report-meta">
                    <span class="report-badge badge-${report.type}">${getTypeLabel(report.type)}</span>
                    <span>📅 ${report.modified}</span>
                    <span>📦 ${formatSize(report.size)}</span>
                </div>
            `;
            item.addEventListener('click', () => viewReport(report.path));
            reportsList.appendChild(item);
        });
    } catch (error) {
        reportsList.innerHTML = '<div class="loading">加载失败</div>';
    }
}

// View report
async function viewReport(path) {
    const modal = document.getElementById('report-modal');
    const title = document.getElementById('report-title');
    const content = document.getElementById('report-content');
    
    modal.classList.add('active');
    title.textContent = path;
    content.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        const response = await fetch(`/report/${path}`);
        const data = await response.json();
        
        if (data.html) {
            content.innerHTML = data.html;
        } else {
            content.innerHTML = '<div class="loading">加载失败</div>';
        }
    } catch (error) {
        content.innerHTML = '<div class="loading">加载失败: ' + error.message + '</div>';
    }
}

// Close modal
document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('report-modal').classList.remove('active');
});

// Close modal on outside click
document.getElementById('report-modal').addEventListener('click', (e) => {
    if (e.target.id === 'report-modal') {
        e.target.classList.remove('active');
    }
});

// Scan repository
document.getElementById('scan-repo-btn').addEventListener('click', async () => {
    const repoPath = document.getElementById('repo-path').value;
    
    if (!repoPath.trim()) {
        alert('请输入仓库路径！');
        return;
    }
    
    const btn = document.getElementById('scan-repo-btn');
    const btnText = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.spinner');
    
    btn.disabled = true;
    btnText.textContent = '扫描中...';
    spinner.style.display = 'inline-block';
    
    try {
        const response = await fetch('/analyze-repo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                repo_path: repoPath
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const filesContainer = document.getElementById('repo-files');
            const filesContent = document.getElementById('files-content');
            
            filesContent.innerHTML = '';
            data.files.forEach(file => {
                const item = document.createElement('div');
                item.className = 'file-item';
                item.textContent = file;
                filesContent.appendChild(item);
            });
            
            if (data.total > data.files.length) {
                const more = document.createElement('div');
                more.className = 'file-item';
                more.textContent = `... 还有 ${data.total - data.files.length} 个文件`;
                filesContent.appendChild(more);
            }
            
            filesContainer.style.display = 'block';
        } else {
            alert('扫描失败: ' + data.error);
        }
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        btn.disabled = false;
        btnText.textContent = '扫描仓库';
        spinner.style.display = 'none';
    }
});

// Search reports
document.getElementById('search-reports').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    document.querySelectorAll('.report-item').forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? 'block' : 'none';
    });
});

// Filter reports by type
document.getElementById('filter-type').addEventListener('change', (e) => {
    const type = e.target.value;
    document.querySelectorAll('.report-item').forEach(item => {
        const badge = item.querySelector('.report-badge');
        if (type === 'all' || badge.classList.contains(`badge-${type}`)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
});

// Helper functions
function getTypeLabel(type) {
    const labels = {
        'quality': '质量报告',
        'impact': '影响分析',
        'analysis': '代码分析'
    };
    return labels[type] || type;
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Initialize
checkHealth();
setInterval(checkHealth, 30000); // Check every 30 seconds
