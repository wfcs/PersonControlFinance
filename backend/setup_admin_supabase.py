import asyncio
import os
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import hash_password

async def setup():
    db_url = "postgresql+asyncpg://postgres:HtlZ7JWj6y&t#H@db.ycdowmrdiafflqlnbvfl.supabase.co:5432/postgres"
    engine = create_async_engine(db_url)
    
    # 1. Add columns if not exist
    async def add_column_safely(sql):
        async with engine.begin() as conn:
            try:
                await conn.execute(text(sql))
                print(f"Executed: {sql}")
            except Exception as e:
                print(f"Skipped (already exists?): {sql}")

    await add_column_safely("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL")
    await add_column_safely("ALTER TABLE tenants ADD COLUMN stripe_customer_id VARCHAR(255)")
    await add_column_safely("ALTER TABLE tenants ADD COLUMN stripe_subscription_id VARCHAR(255)")

    # 2. Create admin user
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        t_id = str(uuid.uuid4())
        u_id = str(uuid.uuid4())
        
        tenant = Tenant(
            id=t_id, 
            name="Admin Corp", 
            slug="admin-corp", 
            plan="premium", 
            subscription_status="active", 
            max_connections=999
        )
        
        user = User(
            id=u_id, 
            email="admin@fincontrol.com", 
            cpf="12345678909", 
            full_name="Administrador", 
            hashed_password=hash_password("admin123"), 
            tenant_id=t_id, 
            is_active=True, 
            is_verified=True, 
            is_admin=True
        )
        
        session.add(tenant)
        session.add(user)
        await session.commit()
        print("Admin user created successfully")

if __name__ == "__main__":
    asyncio.run(setup())
