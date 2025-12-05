# Code Analyzer REST API 文档

## 基本信息

- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **API Version**: v1

## 端点列表

### 1. 健康检查

#### GET `/health`

检查 API 服务和 Ollama 连接状态。

**响应示例**:
```json
{
  "status": "healthy",
  "version": "v1",
  "timestamp": "2025-12-05T20:00:00",
  "ollama": "connected"
}
```

### 2. 状态信息

#### GET `/status`

获取 API 状态和统计信息。

**响应示例**:
```json
{
  "version": "v1",
  "timestamp": "2025-12-05T20:00:00",
  "reports_directory": "/path/to/reports",
  "total_reports": 42,
  "supported_languages": ["java", "python", "javascript", "typescript"],
  "endpoints": { ... }
}
```

### 3. 代码分析

#### POST `/analyze`

分析代码片段。

**请求体**:
```json
{
  "code": "public class Test { ... }",
  "language": "java",
  "save": false
}
```

**参数说明**:
- `code` (required): 要分析的代码
- `language` (optional): 编程语言，默认 "java"
- `save` (optional): 是否保存报告，默认 false

**响应示例**:
```json
{
  "success": true,
  "language": "java",
  "analysis": "...",
  "report_id": "analysis_20251205_200000.md",
  "timestamp": "2025-12-05T20:00:00"
}
```

### 4. 文件分析

#### POST `/analyze/file`

分析代码文件。

**请求体**:
```json
{
  "file_path": "/path/to/file.java",
  "language": "java"
}
```

**参数说明**:
- `file_path` (required): 文件路径
- `language` (optional): 编程语言，自动检测

**响应示例**:
```json
{
  "success": true,
  "file_path": "/path/to/file.java",
  "language": "java",
  "analysis": "...",
  "report_id": "file_analysis_20251205_200000.md",
  "timestamp": "2025-12-05T20:00:00"
}
```

### 5. 仓库分析

#### POST `/analyze/repo`

分析 Git 仓库。

**请求体**:
```json
{
  "repo_path": "/path/to/repo",
  "max_files": 20
}
```

**参数说明**:
- `repo_path` (required): 仓库路径
- `max_files` (optional): 最大文件数，默认 20

**响应示例**:
```json
{
  "success": true,
  "repo_path": "/path/to/repo",
  "files_found": 15,
  "files": ["file1.java", "file2.py", ...],
  "commits_analyzed": 10,
  "timestamp": "2025-12-05T20:00:00"
}
```

### 6. 影响分析

#### POST `/impact`

执行完整的影响分析（代码分析 + 影响分析 + 质量报告）。

**请求体**:
```json
{
  "file_path": "/path/to/file.java",
  "repo_path": "."
}
```

**参数说明**:
- `file_path` (required): 文件路径
- `repo_path` (optional): 仓库路径，默认当前目录

**响应示例**:
```json
{
  "success": true,
  "file_path": "/path/to/file.java",
  "code_analysis": "...",
  "impact_analysis": "...",
  "quality_report": "...",
  "reports": {
    "code_analysis": "file_code_analysis_20251205_200000.md",
    "impact_analysis": "file_impact_analysis_20251205_200000.md",
    "quality_report": "file_quality_report_20251205_200000.md"
  },
  "git_commits_analyzed": 5,
  "timestamp": "2025-12-05T20:00:00"
}
```

### 7. 报告列表

#### GET `/reports?type=quality&limit=50`

获取报告列表。

**查询参数**:
- `type` (optional): 报告类型 (quality/impact/analysis)
- `limit` (optional): 最大数量，默认 50

**响应示例**:
```json
{
  "success": true,
  "total": 10,
  "reports": [
    {
      "id": "report_20251205_200000.md",
      "type": "quality",
      "size": 2048,
      "created": "2025-12-05T20:00:00",
      "path": "report_20251205_200000.md"
    }
  ],
  "timestamp": "2025-12-05T20:00:00"
}
```

### 8. 获取报告

#### GET `/reports/<report_id>`

获取特定报告内容。

**响应示例**:
```json
{
  "success": true,
  "id": "report_20251205_200000.md",
  "content": "# Report Content...",
  "timestamp": "2025-12-05T20:00:00"
}
```

### 9. 删除报告

#### DELETE `/reports/<report_id>`

删除特定报告。

**响应示例**:
```json
{
  "success": true,
  "message": "Report deleted",
  "id": "report_20251205_200000.md",
  "timestamp": "2025-12-05T20:00:00"
}
```

## 错误响应

所有错误响应遵循以下格式：

```json
{
  "error": "Error message description"
}
```

**HTTP 状态码**:
- `200`: 成功
- `400`: 请求错误
- `404`: 资源未找到
- `405`: 方法不允许
- `500`: 服务器错误
- `503`: 服务不可用

## 使用示例

### cURL

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 分析代码
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "public class Test { public static void main(String[] args) { System.out.println(\"Hello\"); } }",
    "language": "java",
    "save": true
  }'

# 获取报告列表
curl http://localhost:8000/api/v1/reports?type=quality&limit=10
```

### Python

```python
import requests

# 健康检查
response = requests.get('http://localhost:8000/api/v1/health')
print(response.json())

# 分析代码
data = {
    'code': 'public class Test { ... }',
    'language': 'java',
    'save': True
}
response = requests.post('http://localhost:8000/api/v1/analyze', json=data)
print(response.json())

# 影响分析
data = {
    'file_path': '/path/to/file.java',
    'repo_path': '.'
}
response = requests.post('http://localhost:8000/api/v1/impact', json=data)
print(response.json())
```

### JavaScript

```javascript
// 健康检查
fetch('http://localhost:8000/api/v1/health')
  .then(res => res.json())
  .then(data => console.log(data));

// 分析代码
fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: 'public class Test { ... }',
    language: 'java',
    save: true
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## 速率限制

当前版本无速率限制。生产环境建议添加速率限制。

## 认证

当前版本无需认证。生产环境建议添加 API Key 或 OAuth 认证。
