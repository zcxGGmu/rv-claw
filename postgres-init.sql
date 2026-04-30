-- PostgreSQL 初始化脚本
-- 创建 rv_checkpoints 数据库（如果 docker-compose 已设置则可省略）
-- 创建 rv 用户并授权

-- 确保数据库存在
SELECT 'CREATE DATABASE rv_checkpoints'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rv_checkpoints')\gexec

-- 为 rv 用户授权（Docker Compose 中已通过环境变量创建）
-- 此脚本主要确保 LangGraph checkpointer 表可在首次启动时自动创建

-- 扩展（可选）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
