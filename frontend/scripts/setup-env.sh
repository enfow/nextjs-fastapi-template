#!/bin/bash

# Setup Environment Files for NextAuth
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔧 Setting up environment files for NextAuth..."

# Generate a secure secret
generate_secret() {
    if command -v openssl &> /dev/null; then
        openssl rand -base64 32
    else
        # Fallback for systems without openssl
        node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
    fi
}

# Create development .env.local
create_dev_env() {
    local env_file="$FRONTEND_DIR/.env.local"
    local secret=$(generate_secret)
    
    if [ ! -f "$env_file" ]; then
        cat > "$env_file" << EOF
# NextAuth Configuration (Development)
NEXTAUTH_SECRET=$secret
NEXTAUTH_URL=http://localhost:3000

# Development settings
NODE_ENV=development
NEXT_TELEMETRY_DISABLED=1

# Application settings
APP_NAME="Next.js FastAPI Template"
APP_DESCRIPTION="A modern web application template"

# Demo credentials for development
DEMO_USERNAME=admin
DEMO_PASSWORD=password1
EOF
        echo "✅ Created development environment file: $env_file"
    else
        echo "ℹ️  Development environment file already exists: $env_file"
    fi
}

# Create production .env.production.example
create_prod_example() {
    local env_file="$FRONTEND_DIR/.env.production.example"
    
    cat > "$env_file" << EOF
# Production NextAuth Configuration
# CRITICAL: Generate a strong secret for production!
# Generate: openssl rand -base64 32 or yarn generate-secret
NEXTAUTH_SECRET=REPLACE_WITH_STRONG_SECRET_IN_PRODUCTION
NEXTAUTH_URL=https://your-domain.com

# Database (recommended for production)
# DATABASE_URL=postgresql://user:password@db-host:5432/production_db

# OAuth Providers (production keys)
# GOOGLE_CLIENT_ID=your-production-google-client-id
# GOOGLE_CLIENT_SECRET=your-production-google-client-secret
# GITHUB_CLIENT_ID=your-production-github-client-id
# GITHUB_CLIENT_SECRET=your-production-github-client-secret

# Production settings
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1

# Security settings (for container networking)
# NEXTAUTH_URL_INTERNAL=http://localhost:3000

# Application settings
APP_NAME="Next.js FastAPI Template"
APP_DESCRIPTION="A modern web application template"

# Production credentials (replace with your auth system)
# ADMIN_USERNAME=your-admin-username
# ADMIN_PASSWORD_HASH=your-hashed-password
EOF
    echo "✅ Created production example file: $env_file"
}

# Create development .env.example
create_dev_example() {
    local env_file="$FRONTEND_DIR/.env.example"
    
    cat > "$env_file" << EOF
# NextAuth Configuration (Development Template)
# Generate a secret: openssl rand -base64 32
NEXTAUTH_SECRET=your-super-secret-jwt-secret-here-change-in-production
NEXTAUTH_URL=http://localhost:3000

# Database (if using database sessions)
# DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# OAuth Providers (examples)
# GOOGLE_CLIENT_ID=your-google-client-id
# GOOGLE_CLIENT_SECRET=your-google-client-secret
# GITHUB_CLIENT_ID=your-github-client-id
# GITHUB_CLIENT_SECRET=your-github-client-secret

# Development settings
NODE_ENV=development
NEXT_TELEMETRY_DISABLED=1

# Application settings
APP_NAME="Next.js FastAPI Template"
APP_DESCRIPTION="A modern web application template"

# Demo credentials for development
DEMO_USERNAME=admin
DEMO_PASSWORD=password1
EOF
    echo "✅ Created development example file: $env_file"
}

# Main execution
main() {
    echo "📍 Working in: $FRONTEND_DIR"
    
    # Create environment files
    create_dev_env
    create_dev_example
    create_prod_example
    
    echo ""
    echo "🎉 Environment setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Review the generated .env.local file"
    echo "   2. For production, copy .env.production.example to .env.production"
    echo "   3. Replace NEXTAUTH_SECRET with a secure secret in production"
    echo "   4. Update NEXTAUTH_URL with your production domain"
    echo ""
    echo "🔐 Generate a new secret anytime with:"
    echo "   openssl rand -base64 32"
}

main "$@" 