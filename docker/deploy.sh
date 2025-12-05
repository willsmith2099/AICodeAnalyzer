#!/bin/bash

# Code Analyzer Docker 部署脚本
# 使用方法: ./deploy.sh [start|stop|restart|logs|status]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_info "Docker 和 Docker Compose 已就绪"
}

# 函数：启动服务
start_services() {
    print_info "启动 Code Analyzer 服务..."
    
    # 创建必要的目录
    mkdir -p api_reports web_reports impact_reports analysis_results
    
    # 启动服务
    docker-compose up -d
    
    print_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        print_info "服务启动成功！"
        
        # 检查 Ollama 模型
        print_info "检查 Ollama 模型..."
        if docker-compose exec -T ollama ollama list | grep -q "qwen2.5:0.5b"; then
            print_info "Ollama 模型已安装"
        else
            print_warn "Ollama 模型未安装，正在拉取 qwen2.5:0.5b..."
            docker-compose exec -T ollama ollama pull qwen2.5:0.5b
            print_info "模型拉取完成"
        fi
        
        echo ""
        print_info "服务访问地址："
        echo "  - Web 界面: http://localhost:5001"
        echo "  - API 服务: http://localhost:8000"
        echo "  - Ollama:   http://localhost:11434"
        echo ""
    else
        print_error "服务启动失败，请查看日志"
        docker-compose logs
        exit 1
    fi
}

# 函数：停止服务
stop_services() {
    print_info "停止 Code Analyzer 服务..."
    docker-compose down
    print_info "服务已停止"
}

# 函数：重启服务
restart_services() {
    print_info "重启 Code Analyzer 服务..."
    docker-compose restart
    print_info "服务已重启"
}

# 函数：查看日志
view_logs() {
    print_info "查看服务日志（按 Ctrl+C 退出）..."
    docker-compose logs -f --tail=100
}

# 函数：查看状态
check_status() {
    print_info "服务状态："
    docker-compose ps
    
    echo ""
    print_info "健康检查："
    
    # 检查 API
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "  API:    ${GREEN}✓ 健康${NC}"
    else
        echo -e "  API:    ${RED}✗ 不健康${NC}"
    fi
    
    # 检查 Web
    if curl -sf http://localhost:5001/health > /dev/null 2>&1; then
        echo -e "  Web:    ${GREEN}✓ 健康${NC}"
    else
        echo -e "  Web:    ${RED}✗ 不健康${NC}"
    fi
    
    # 检查 Ollama
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "  Ollama: ${GREEN}✓ 健康${NC}"
    else
        echo -e "  Ollama: ${RED}✗ 不健康${NC}"
    fi
}

# 函数：清理资源
cleanup() {
    print_warn "这将删除所有容器、卷和网络"
    read -p "确认删除？(y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        print_info "清理资源..."
        docker-compose down -v
        print_info "清理完成"
    else
        print_info "取消清理"
    fi
}

# 函数：更新服务
update_services() {
    print_info "更新 Code Analyzer 服务..."
    
    # 拉取最新代码（如果是 git 仓库）
    if [ -d .git ]; then
        print_info "拉取最新代码..."
        git pull
    fi
    
    # 重新构建并启动
    print_info "重新构建镜像..."
    docker-compose build --no-cache
    
    print_info "重启服务..."
    docker-compose up -d
    
    print_info "更新完成"
}

# 主函数
main() {
    echo "================================"
    echo "Code Analyzer Docker 部署工具"
    echo "================================"
    echo ""
    
    check_docker
    
    case "${1:-}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            view_logs
            ;;
        status)
            check_status
            ;;
        cleanup)
            cleanup
            ;;
        update)
            update_services
            ;;
        *)
            echo "使用方法: $0 {start|stop|restart|logs|status|cleanup|update}"
            echo ""
            echo "命令说明："
            echo "  start   - 启动所有服务"
            echo "  stop    - 停止所有服务"
            echo "  restart - 重启所有服务"
            echo "  logs    - 查看服务日志"
            echo "  status  - 查看服务状态"
            echo "  cleanup - 清理所有资源"
            echo "  update  - 更新并重启服务"
            exit 1
            ;;
    esac
}

main "$@"
