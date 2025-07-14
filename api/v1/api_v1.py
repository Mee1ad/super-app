from esmerald import Gateway, Include
from apps.todo.endpoints import (
    get_lists, create_list, update_list, delete_list,
    get_tasks, create_task, update_task, delete_task, toggle_task, reorder_tasks,
    get_items, create_item, update_item, delete_item, toggle_item, reorder_items,
    search
)
from apps.ideas.endpoints import (
    get_categories, get_ideas, create_idea, get_idea, update_idea, delete_idea
)
from apps.diary.endpoints import (
    get_moods, get_diary_entries, create_diary_entry, get_diary_entry, 
    update_diary_entry, delete_diary_entry, upload_image
)
from apps.food_planner.endpoints import (
    get_meal_types, get_food_entries, create_food_entry, get_food_entry,
    update_food_entry, delete_food_entry, get_food_summary, get_calendar_data, upload_food_image
)
from apps.auth.endpoints import google_login, refresh_token, get_google_auth_url, google_callback
from apps.changelog.endpoints import (
    get_changelog_entries, get_changelog_entry, get_changelog_summary,
    get_unread_changelog, mark_changelog_viewed, process_new_commits,
    get_available_versions, get_current_version
)

# V1 API Router - All endpoints under /api/v1/
v1_routes = [
    # Auth endpoints
    Gateway(handler=google_login, path="/auth"),
    Gateway(handler=refresh_token, path="/auth"),
    Gateway(handler=get_google_auth_url, path="/auth"),
    Gateway(handler=google_callback, path="/auth/google/callback"),
    
    # Todo endpoints
    Gateway(handler=get_lists, path="/lists"),
    Gateway(handler=create_list, path="/lists"),
    Gateway(handler=update_list, path="/lists/{list_id:uuid}"),
    Gateway(handler=delete_list, path="/lists/{list_id:uuid}"),
    Gateway(handler=get_tasks, path="/lists/{list_id:uuid}/tasks"),
    Gateway(handler=create_task, path="/lists/{list_id:uuid}/tasks"),
    Gateway(handler=update_task, path="/lists/{list_id:uuid}/tasks/{task_id:uuid}"),
    Gateway(handler=delete_task, path="/lists/{list_id:uuid}/tasks/{task_id:uuid}"),
    Gateway(handler=toggle_task, path="/lists/{list_id:uuid}/tasks/{task_id:uuid}/toggle"),
    Gateway(handler=reorder_tasks, path="/lists/{list_id:uuid}/tasks/reorder"),
    Gateway(handler=get_items, path="/lists/{list_id:uuid}/items"),
    Gateway(handler=create_item, path="/lists/{list_id:uuid}/items"),
    Gateway(handler=update_item, path="/lists/{list_id:uuid}/items/{item_id:uuid}"),
    Gateway(handler=delete_item, path="/lists/{list_id:uuid}/items/{item_id:uuid}"),
    Gateway(handler=toggle_item, path="/lists/{list_id:uuid}/items/{item_id:uuid}/toggle"),
    Gateway(handler=reorder_items, path="/lists/{list_id:uuid}/items/reorder"),
    Gateway(handler=search, path="/search"),
    
    # Ideas endpoints
    Gateway(handler=get_categories, path="/categories"),
    Gateway(handler=get_ideas, path="/ideas"),
    Gateway(handler=create_idea, path="/ideas"),
    Gateway(handler=get_idea, path="/ideas/{idea_id:uuid}"),
    Gateway(handler=update_idea, path="/ideas/{idea_id:uuid}"),
    Gateway(handler=delete_idea, path="/ideas/{idea_id:uuid}"),
    
    # Diary endpoints
    Gateway(handler=get_moods, path="/moods"),
    Gateway(handler=get_diary_entries, path="/diary-entries"),
    Gateway(handler=create_diary_entry, path="/diary-entries"),
    Gateway(handler=get_diary_entry, path="/diary-entries/{entry_id:uuid}"),
    Gateway(handler=update_diary_entry, path="/diary-entries/{entry_id:uuid}"),
    Gateway(handler=delete_diary_entry, path="/diary-entries/{entry_id:uuid}"),
    Gateway(handler=upload_image, path="/upload-image"),
    
    # Food Planner endpoints
    Gateway(handler=get_meal_types, path="/meal-types"),
    Gateway(handler=get_food_entries, path="/food-entries"),
    Gateway(handler=create_food_entry, path="/food-entries"),
    Gateway(handler=get_food_entry, path="/food-entries/{entry_id:uuid}"),
    Gateway(handler=update_food_entry, path="/food-entries/{entry_id:uuid}"),
    Gateway(handler=delete_food_entry, path="/food-entries/{entry_id:uuid}"),
    Gateway(handler=get_food_summary, path="/food-entries/summary"),
    Gateway(handler=get_calendar_data, path="/food-entries/calendar"),
    Gateway(handler=upload_food_image, path="/upload-food-image"),
    
    # Changelog endpoints
    Gateway(handler=get_changelog_entries, path="/changelog"),
    Gateway(handler=get_changelog_entry, path="/changelog/{entry_id:uuid}"),
    Gateway(handler=get_changelog_summary, path="/changelog/summary/{version}"),
    Gateway(handler=get_unread_changelog, path="/changelog/unread"),
    Gateway(handler=mark_changelog_viewed, path="/changelog/mark-viewed"),
    Gateway(handler=process_new_commits, path="/changelog/process-commits"),
    Gateway(handler=get_available_versions, path="/changelog/versions"),
    Gateway(handler=get_current_version, path="/changelog/current-version"),
] 