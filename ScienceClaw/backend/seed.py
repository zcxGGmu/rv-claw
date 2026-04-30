"""种子数据 — 初始化数据库."""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime

from backend.mongodb.db import db
from backend.config import settings


async def seed_users() -> None:
    """初始化默认用户."""
    users_col = db.get_collection("users")

    # 检查是否已有管理员
    admin_exists = await users_col.find_one({"role": "admin"})
    if admin_exists:
        return

    # 创建默认管理员
    admin_id = str(uuid.uuid4())
    now = int(datetime.utcnow().timestamp())

    import bcrypt
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(
        settings.bootstrap_admin_password.encode(),
        salt,
    ).decode()

    admin = {
        "_id": admin_id,
        "username": settings.bootstrap_admin_username,
        "email": f"{settings.bootstrap_admin_username}@localhost",
        "password_hash": password_hash,
        "fullname": "Administrator",
        "role": "admin",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
    }

    await users_col.insert_one(admin)
    print(f"[seed] Created admin user: {settings.bootstrap_admin_username}")


async def seed_feature_flags() -> None:
    """初始化功能开关."""
    flags_col = db.get_collection("feature_flags")

    default_flags = [
        {
            "_id": "pipeline_enabled",
            "name": "Pipeline Mode",
            "description": "Enable Pipeline execution mode",
            "enabled": False,
            "updated_at": datetime.utcnow().isoformat(),
        },
        {
            "_id": "chat_enabled",
            "name": "Chat Mode",
            "description": "Enable Chat execution mode",
            "enabled": True,
            "updated_at": datetime.utcnow().isoformat(),
        },
        {
            "_id": "human_gate_required",
            "name": "Human-in-the-Loop",
            "description": "Require human approval at each stage",
            "enabled": True,
            "updated_at": datetime.utcnow().isoformat(),
        },
    ]

    for flag in default_flags:
        exists = await flags_col.find_one({"_id": flag["_id"]})
        if not exists:
            await flags_col.insert_one(flag)
            print(f"[seed] Created feature flag: {flag['_id']}")


async def seed_system_config() -> None:
    """初始化系统配置."""
    config_col = db.get_collection("system_config")

    defaults = {
        "_id": "default",
        "max_review_iterations": 3,
        "max_agent_turns": 50,
        "cost_budget_daily_usd": 50.0,
        "max_concurrent_cases": 3,
        "default_target_repo": "linux",
        "created_at": datetime.utcnow().isoformat(),
    }

    exists = await config_col.find_one({"_id": "default"})
    if not exists:
        await config_col.insert_one(defaults)
        print("[seed] Created system config")


async def run_seed() -> None:
    """运行所有种子数据初始化."""
    print("[seed] Starting database seeding...")

    await seed_users()
    await seed_feature_flags()
    await seed_system_config()

    print("[seed] Database seeding completed")


if __name__ == "__main__":
    # 允许直接运行此文件进行初始化
    from backend.main import init_db

    async def main():
        await init_db()
        await run_seed()

    asyncio.run(main())
