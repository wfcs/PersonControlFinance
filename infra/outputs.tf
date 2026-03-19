output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "public_subnets" {
  value = module.vpc.public_subnets
}

output "database_url" {
  value     = "postgresql+asyncpg://${aws_db_instance.main.username}:${var.db_password}@${aws_db_instance.main.endpoint}/fincontrol"
  sensitive = true
}

output "redis_url" {
  value = "rediss://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0"
}
