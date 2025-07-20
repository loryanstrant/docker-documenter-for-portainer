#!/bin/bash

# Portainer Documenter - Development and Test Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

print_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install     Install Python dependencies"
    echo "  test        Run basic tests and validation"
    echo "  build       Build Docker image"
    echo "  demo        Run a demo with example Portainer URL"
    echo "  run         Run the tool with provided arguments"
    echo "  clean       Clean up Docker images and generated files"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install"
    echo "  $0 build"
    echo "  $0 run --url https://portainer.example.com --token abc123"
    echo "  $0 demo"
}

install_deps() {
    print_color $BLUE "Installing Python dependencies..."
    pip install -r requirements.txt
    print_color $GREEN "Dependencies installed successfully!"
}

run_tests() {
    print_color $BLUE "Running basic validation tests..."
    
    # Test Python import
    python -c "import sys; sys.path.insert(0, 'src'); from portainer_documenter import __version__; print(f'Version: {__version__}')"
    
    # Test CLI help
    python main.py --help > /dev/null
    
    # Test Docker build (if Docker is available)
    if command -v docker &> /dev/null; then
        print_color $BLUE "Testing Docker build..."
        docker build -t portainer-documenter:test . > /dev/null
        docker run --rm portainer-documenter:test --help > /dev/null
        print_color $GREEN "Docker build test passed!"
    else
        print_color $YELLOW "Docker not available, skipping Docker tests"
    fi
    
    print_color $GREEN "All tests passed!"
}

build_docker() {
    print_color $BLUE "Building Docker image..."
    docker build -t portainer-documenter:latest .
    print_color $GREEN "Docker image built successfully!"
    
    print_color $BLUE "Testing Docker image..."
    docker run --rm portainer-documenter:latest --help
    print_color $GREEN "Docker image test passed!"
}

run_demo() {
    print_color $BLUE "Running demo with mock Portainer instance..."
    print_color $YELLOW "This will show error handling as no real Portainer is available"
    
    python main.py \
        --url https://demo.portainer.io \
        --token demo-token \
        --verbose \
        --output /tmp/demo-docs.md || true
    
    print_color $GREEN "Demo completed! Check the error handling above."
}

run_tool() {
    print_color $BLUE "Running Portainer Documenter..."
    python main.py "$@"
}

clean_up() {
    print_color $BLUE "Cleaning up..."
    
    # Remove Docker images
    if command -v docker &> /dev/null; then
        docker rmi portainer-documenter:test 2>/dev/null || true
        docker rmi portainer-documenter:latest 2>/dev/null || true
    fi
    
    # Remove generated files (but keep examples)
    find . -name "*.md" -not -name "README.md" -delete 2>/dev/null || true
    find . -name "*.json" -not -name "config.example.json" -delete 2>/dev/null || true
    rm -f /tmp/demo-docs.md 2>/dev/null || true
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    print_color $GREEN "Cleanup completed!"
}

# Main script logic
case "${1:-help}" in
    install)
        install_deps
        ;;
    test)
        run_tests
        ;;
    build)
        build_docker
        ;;
    demo)
        run_demo
        ;;
    run)
        shift
        run_tool "$@"
        ;;
    clean)
        clean_up
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        print_color $RED "Unknown command: $1"
        print_usage
        exit 1
        ;;
esac