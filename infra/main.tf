terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "fincontrol-terraform-state"
    key            = "infra/terraform.tfstate"
    region         = "sa-east-1"
    encrypt        = true
    dynamodb_table = "fincontrol-terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region
}

# --- Variables ---

variable "aws_region" {
  default = "sa-east-1"
}

variable "environment" {
  default = "production"
}

variable "db_password" {
  sensitive = true
}

variable "app_domain" {
  default = "app.fincontrol.com.br"
}

# --- VPC ---

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "fincontrol-${var.environment}"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  tags = {
    Environment = var.environment
    Project     = "fincontrol"
  }
}

# --- RDS PostgreSQL ---

resource "aws_db_subnet_group" "main" {
  name       = "fincontrol-${var.environment}"
  subnet_ids = module.vpc.private_subnets

  tags = { Name = "fincontrol-db-subnet" }
}

resource "aws_security_group" "db" {
  name_prefix = "fincontrol-db-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "main" {
  identifier     = "fincontrol-${var.environment}"
  engine         = "postgres"
  engine_version = "16.4"
  instance_class = "db.t4g.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true

  db_name  = "fincontrol"
  username = "fincontrol_admin"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  multi_az            = false
  skip_final_snapshot = false
  final_snapshot_identifier = "fincontrol-${var.environment}-final"

  tags = {
    Environment = var.environment
    Project     = "fincontrol"
  }
}

# --- ElastiCache Redis ---

resource "aws_elasticache_subnet_group" "main" {
  name       = "fincontrol-${var.environment}"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name_prefix = "fincontrol-redis-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "fincontrol-${var.environment}"
  description          = "FinControl Redis"
  node_type            = "cache.t4g.micro"
  num_cache_clusters   = 1

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  automatic_failover_enabled = false

  tags = {
    Environment = var.environment
    Project     = "fincontrol"
  }
}

# --- ECS Cluster ---

resource "aws_security_group" "app" {
  name_prefix = "fincontrol-app-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_cluster" "main" {
  name = "fincontrol-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
    Project     = "fincontrol"
  }
}

resource "aws_ecr_repository" "api" {
  name                 = "fincontrol-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = "fincontrol"
  }
}

# --- Secrets Manager ---

resource "aws_secretsmanager_secret" "app_secrets" {
  name = "fincontrol/${var.environment}/app"

  tags = {
    Environment = var.environment
    Project     = "fincontrol"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    DATABASE_URL          = "postgresql+asyncpg://${aws_db_instance.main.username}:${var.db_password}@${aws_db_instance.main.endpoint}/fincontrol"
    REDIS_URL             = "rediss://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
    SECRET_KEY            = "CHANGE_ME"
    STRIPE_SECRET_KEY     = ""
    STRIPE_WEBHOOK_SECRET = ""
    SENTRY_DSN            = ""
  })
}

# --- S3 Bucket for exports ---

resource "aws_s3_bucket" "exports" {
  bucket = "fincontrol-exports-${var.environment}"

  tags = {
    Environment = var.environment
    Project     = "fincontrol"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "exports" {
  bucket = aws_s3_bucket.exports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "exports" {
  bucket = aws_s3_bucket.exports.id

  rule {
    id     = "expire-old-exports"
    status = "Enabled"

    expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_public_access_block" "exports" {
  bucket = aws_s3_bucket.exports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- Outputs ---

output "db_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}
