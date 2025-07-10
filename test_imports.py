#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
This helps identify any import issues before running the main application.
"""

def test_imports():
    """Test all critical imports to ensure they work correctly."""
    try:
        print("Testing imports...")
        
        # Test core imports
        print("✓ Testing core imports...")
        from core.config import settings
        print(f"  - Settings loaded: debug={settings.debug}")
        
        # Test database imports
        print("✓ Testing database imports...")
        from db.session import database, models_registry
        print(f"  - Database URL: {database.url}")
        print(f"  - Registry created: {models_registry is not None}")
        
        # Test model imports
        print("✓ Testing model imports...")
        from apps.todo.models import List, Task, ShoppingItem
        print(f"  - List model: {List}")
        print(f"  - Task model: {Task}")
        print(f"  - ShoppingItem model: {ShoppingItem}")
        
        # Test schema imports
        print("✓ Testing schema imports...")
        from apps.todo.schemas import ListResponse, TaskResponse, ShoppingItemResponse
        print(f"  - ListResponse schema: {ListResponse}")
        print(f"  - TaskResponse schema: {TaskResponse}")
        print(f"  - ShoppingItemResponse schema: {ShoppingItemResponse}")
        
        # Test service imports
        print("✓ Testing service imports...")
        from apps.todo.services import ListService, TaskService, ShoppingItemService
        print(f"  - ListService: {ListService}")
        print(f"  - TaskService: {TaskService}")
        print(f"  - ShoppingItemService: {ShoppingItemService}")
        
        # Test endpoint imports
        print("✓ Testing endpoint imports...")
        from apps.todo.endpoints import get_lists, create_list, get_tasks
        print(f"  - get_lists function: {get_lists}")
        print(f"  - create_list function: {create_list}")
        print(f"  - get_tasks function: {get_tasks}")
        
        # Test main app import
        print("✓ Testing main app import...")
        from main import app
        print(f"  - Main app: {app}")
        print(f"  - App title: {app.title}")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1) 