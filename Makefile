# Makefile for AI Resume Advisor Container Apps Development
# Provides convenient commands for local development and deployment

.PHONY: help build run test deploy clean logs

# Default target
help: ## Show this help message
	@echo "🚀 AI Resume Advisor - Container Apps Development"
	@echo "================================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Local development
build: ## Build Docker image locally
	@echo "🔨 Building Docker image..."
	docker build -f deployment/container-apps/Dockerfile -t airesumeadvisor-api:local .

run: ## Run the application locally using Docker Compose
	@echo "🚀 Starting local development environment..."
	docker-compose -f deployment/container-apps/docker-compose.yml up -d
	@echo "✅ Application running at http://localhost:8000"
	@echo "📊 Health check: curl http://localhost/api/health"

stop: ## Stop local development environment
	@echo "🛑 Stopping local development environment..."
	docker-compose -f deployment/container-apps/docker-compose.yml down

logs: ## Show application logs
	@echo "📋 Application logs:"
	docker-compose -f deployment/container-apps/docker-compose.yml logs -f airesumeadvisor-api

# Testing
test-local: ## Run tests against local Docker environment
	@echo "🧪 Testing local Docker environment..."
	@sleep 5  # Wait for services to start
	./scripts/test-container-apps.sh

test-unit: ## Run unit tests
	@echo "🧪 Running unit tests..."
	./run_precommit_tests.sh --level-2 --parallel

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	./run_precommit_tests.sh --level-3 --parallel

# Azure deployment
deploy-dev: ## Deploy to Azure Container Apps (development)
	@echo "🚀 Deploying to Azure Container Apps..."
	@./deployment/scripts/deploy-container-apps.sh

test-azure: ## Test Azure Container Apps deployment
	@echo "🧪 Testing Azure Container Apps..."
	@echo "⚠️  Make sure to update CONTAINER_APP_URL in deployment/scripts/test-container-apps.sh"
	./deployment/scripts/test-container-apps.sh

# Maintenance
clean: ## Clean up local Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose -f deployment/container-apps/docker-compose.yml down --volumes --remove-orphans
	docker image prune -f
	docker container prune -f

clean-all: ## Deep clean all Docker resources (use with caution)
	@echo "🧹 Deep cleaning Docker resources..."
	docker-compose -f deployment/container-apps/docker-compose.yml down --volumes --remove-orphans
	docker system prune -af --volumes

# Development helpers
shell: ## Open shell in running container
	@echo "🐚 Opening shell in container..."
	docker-compose -f deployment/container-apps/docker-compose.yml exec airesumeadvisor-api /bin/bash

health: ## Check application health
	@echo "🏥 Checking application health..."
	curl -f http://localhost/api/health || curl -f http://localhost:8000/api/health

performance: ## Run performance test against local environment
	@echo "⏱️  Running performance test..."
	@echo "Testing extract-jd-keywords endpoint..."
	time curl -X POST http://localhost/api/v1/extract-jd-keywords \
	  -H "Content-Type: application/json" \
	  -d '{"job_description": "We are looking for a Senior Python Developer with FastAPI experience", "language": "en"}' \
	  -w "\nResponse time: %{time_total}s\n"

# Docker registry
push: ## Push image to Azure Container Registry
	@echo "📦 Pushing to Azure Container Registry..."
	az acr login --name airesumeadvisorregistry
	docker tag airesumeadvisor-api:local airesumeadvisorregistry.azurecr.io/airesumeadvisor-api:latest
	docker push airesumeadvisorregistry.azurecr.io/airesumeadvisor-api:latest

# Branch management
checkout-container: ## Switch to container branch
	@echo "🌿 Switching to container branch..."
	git checkout container

# Environment setup
setup-env: ## Setup environment variables template
	@echo "📝 Creating .env template..."
	@echo "# Azure OpenAI Configuration" > .env.template
	@echo "AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com" >> .env.template
	@echo "AZURE_OPENAI_API_KEY=your-api-key" >> .env.template
	@echo "" >> .env.template
	@echo "# Embedding Configuration" >> .env.template
	@echo "EMBEDDING_ENDPOINT=https://your-embedding-endpoint" >> .env.template
	@echo "EMBEDDING_API_KEY=your-embedding-key" >> .env.template
	@echo "" >> .env.template
	@echo "# Application Insights" >> .env.template
	@echo "APPINSIGHTS_INSTRUMENTATIONKEY=your-instrumentation-key" >> .env.template
	@echo "APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string" >> .env.template
	@echo "✅ .env.template created. Copy to .env and fill in your values."

# Development workflow
dev-workflow: build run ## Complete development workflow: build and run
	@echo "🎉 Development environment ready!"
	@echo "📍 API: http://localhost/api/v1/"
	@echo "🏥 Health: http://localhost/api/health"
	@make health