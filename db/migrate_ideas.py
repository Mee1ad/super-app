# Migration script for ideas app
import asyncio
import sys
import os
import platform

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix Windows event loop issue
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from db.session import database
from apps.ideas.models import Category, Idea
from apps.ideas.schemas import CategoryCreate


async def create_ideas_tables():
    """Create tables for the ideas app"""
    print("Creating ideas app tables...")
    
    # Create tables using the registry
    from db.session import models_registry
    await models_registry.create_all()
    print("✅ Tables created successfully")


async def seed_categories():
    """Seed initial categories"""
    print("Seeding initial categories...")
    
    # Initial categories from the requirements
    initial_categories = [
        CategoryCreate(
            id="project",
            name="Project",
            emoji="🚀"
        ),
        CategoryCreate(
            id="article",
            name="Article", 
            emoji="📝"
        ),
        CategoryCreate(
            id="shopping",
            name="Shopping",
            emoji="🛒"
        ),
        CategoryCreate(
            id="learning",
            name="Learning",
            emoji="📚"
        ),
        CategoryCreate(
            id="personal",
            name="Personal",
            emoji="👤"
        ),
        CategoryCreate(
            id="work",
            name="Work",
            emoji="💼"
        )
    ]
    
    # Check if categories already exist
    existing_categories = await Category.query.all()
    if existing_categories:
        print("Categories already exist, skipping seed...")
        return
    
    # Create categories
    for category_data in initial_categories:
        await Category.query.create(**category_data.model_dump())
    
    print("✅ Categories seeded successfully")


async def seed_sample_ideas():
    """Seed sample ideas"""
    print("Seeding sample ideas...")
    
    # Check if ideas already exist
    existing_ideas = await Idea.query.all()
    if existing_ideas:
        print("Ideas already exist, skipping seed...")
        return
    
    # Sample ideas from the requirements
    sample_ideas = [
        {
            "title": "Build a habit tracker app",
            "description": "Simple app to track daily habits with streaks and analytics",
            "category": "project",
            "tags": ["react", "typescript", "productivity"]
        },
        {
            "title": "Write about AI in education",
            "description": "Article exploring how AI can personalize learning experiences",
            "category": "article", 
            "tags": ["ai", "education", "writing"]
        }
    ]
    
    # Create ideas
    for idea_data in sample_ideas:
        await Idea.query.create(**idea_data)
    
    print("✅ Sample ideas seeded successfully")


async def main():
    """Run the complete migration"""
    try:
        await create_ideas_tables()
        await seed_categories()
        await seed_sample_ideas()
        print("🎉 Ideas app migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await database.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 