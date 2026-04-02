"""
Script to initialize database tables and create admin user.
Run this once after deploying to create all tables in the database.
"""
import asyncio
import os
import sys

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(__file__))


async def init():
    from app.core.config import settings
    from app.db.session import engine
    from app.models.base import Base

    # Import all models so they are registered with Base.metadata
    import app.models.user  # noqa
    import app.models.tenant  # noqa
    import app.models.account  # noqa
    import app.models.transaction  # noqa
    import app.models.category  # noqa
    import app.models.goal  # noqa
    import app.models.invoice  # noqa
    import app.models.plan  # noqa
    import app.models.recurrence  # noqa
    import app.models.notification  # noqa
    import app.models.audit_log  # noqa
    import app.models.webhook_log  # noqa

    print(f"Database URL: {settings.DATABASE_URL[:30]}...")
    print("Creating all tables...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("Tables created successfully!")

        # Add missing columns to existing tables (create_all won't do this)
        async with engine.begin() as conn:
            await conn.execute(
                __import__("sqlalchemy").text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS has_completed_onboarding BOOLEAN NOT NULL DEFAULT FALSE"
                )
            )
        print("Schema migrations applied!")

        # Create admin user if not exists
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import select
        from app.models.user import User
        from app.models.tenant import Tenant
        from app.core.security import hash_password

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            # Check if admin already exists
            result = await session.execute(
                select(User).where(User.email == "admin@fincontrol.com")
            )
            existing = result.scalar_one_or_none()

            if existing:
                print("Admin user already exists!")
            else:
                tenant = Tenant(
                    name="Admin Corp",
                    slug="admin-corp",
                    plan="premium",
                    subscription_status="active",
                    max_connections=999,
                )
                session.add(tenant)
                await session.flush()

                user = User(
                    email="admin@fincontrol.com",
                    cpf="12345678909",
                    full_name="Administrador",
                    hashed_password=hash_password("admin123"),
                    tenant_id=tenant.id,
                    is_active=True,
                    is_verified=True,
                    is_admin=True,
                )
                session.add(user)
                await session.commit()
                print("Admin user created: admin@fincontrol.com / admin123")

        await engine.dispose()
        print("Done!")
    except Exception as e:
        print(f"WARNING: init_db failed: {e}")
        print("The server will start anyway. Tables may need to be created manually.")
        try:
            await engine.dispose()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(init())
