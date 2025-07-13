#!/usr/bin/env python3
"""
Test script for the Ideas API endpoints
"""
import asyncio
import sys
import os
import platform

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Fix Windows event loop issue
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from db.session import database
from apps.ideas.models import Category, Idea
from apps.ideas.schemas import CategoryCreate, IdeaCreate


async def test_ideas_api():
    """Test the ideas API functionality"""
    try:
        print("🔧 Testing Ideas API...")
        
        # Connect to database
        await database.connect()
        print("✅ Database connected")
        
        # Test 1: Create categories
        print("\n📝 Test 1: Creating categories...")
        categories_data = [
            CategoryCreate(id="project", name="Project", emoji="🚀"),
            CategoryCreate(id="article", name="Article", emoji="📝"),
            CategoryCreate(id="shopping", name="Shopping", emoji="🛒"),
            CategoryCreate(id="learning", name="Learning", emoji="📚"),
            CategoryCreate(id="personal", name="Personal", emoji="👤"),
            CategoryCreate(id="work", name="Work", emoji="💼")
        ]
        
        for cat_data in categories_data:
            try:
                await Category.query.create(**cat_data.model_dump())
                print(f"  ✅ Created category: {cat_data.name}")
            except Exception as e:
                print(f"  ⚠️  Category {cat_data.name} already exists: {e}")
        
        # Test 2: Create sample ideas
        print("\n💡 Test 2: Creating sample ideas...")
        ideas_data = [
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
        
        for idea_data in ideas_data:
            try:
                await Idea.query.create(**idea_data)
                print(f"  ✅ Created idea: {idea_data['title']}")
            except Exception as e:
                print(f"  ⚠️  Idea {idea_data['title']} already exists: {e}")
        
        # Test 3: Query categories
        print("\n📋 Test 3: Querying categories...")
        categories = await Category.query.all().order_by("name")
        print(f"  📊 Found {len(categories)} categories:")
        for cat in categories:
            print(f"    - {cat.emoji} {cat.name} (ID: {cat.id})")
        
        # Test 4: Query ideas
        print("\n💭 Test 4: Querying ideas...")
        ideas = await Idea.query.all().order_by("-created_at")
        print(f"  📊 Found {len(ideas)} ideas:")
        for idea in ideas:
            print(f"    - {idea.title} (Category: {idea.category})")
        
        # Test 5: Test filtering
        print("\n🔍 Test 5: Testing filters...")
        project_ideas = await Idea.query.filter(category="project").all()
        print(f"  📊 Found {len(project_ideas)} project ideas:")
        for idea in project_ideas:
            print(f"    - {idea.title}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        await database.disconnect()
        print("🔌 Database disconnected")


if __name__ == "__main__":
    asyncio.run(test_ideas_api()) 