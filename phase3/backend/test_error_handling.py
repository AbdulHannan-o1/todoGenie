 #!/usr/bin/env python3
"""
Test script to verify error handling for invalid task IDs in voice operations
"""
import asyncio
import uuid
import sys
import os

# Add the backend directory to the path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from phase3.backend.src.services.task_operations import TaskOperationsService
from phase3.backend.src.services.voice_processor import voice_processor_service


async def test_invalid_task_id_error_handling():
    """Test that invalid task IDs are properly handled with appropriate error messages"""

    print("Testing error handling for invalid task IDs...")

    # Test 1: Invalid UUID format
    print("\n1. Testing invalid UUID format:")
    invalid_task_id = "invalid-task-id"
    result = TaskOperationsService.update_task(
        task_id=invalid_task_id,
        title="Test Update"
    )
    print(f"   Result: {result}")
    assert result["status"] == "error"
    assert "Invalid task ID format" in result["message"]
    print("   ✓ Invalid UUID format properly handled")

    # Test 2: Valid UUID format but non-existent task
    print("\n2. Testing valid UUID format but non-existent task:")
    non_existent_task_id = str(uuid.uuid4())
    result = TaskOperationsService.update_task(
        task_id=non_existent_task_id,
        title="Test Update"
    )
    print(f"   Result: {result}")
    assert result["status"] == "error"
    assert "not found" in result["message"]
    print("   ✓ Non-existent task properly handled")

    # Test 3: Invalid status value
    print("\n3. Testing invalid status value:")
    result = TaskOperationsService.update_task(
        task_id=non_existent_task_id,  # This will fail before status validation
        status="invalid_status"
    )
    print(f"   Result: {result}")
    # This should fail with "not found" before reaching status validation

    # Test 4: Test with a valid format but non-existent task for delete
    print("\n4. Testing delete with non-existent task:")
    result = TaskOperationsService.delete_task(task_id=non_existent_task_id)
    print(f"   Result: {result}")
    assert result["status"] == "error"
    assert "not found" in result["message"]
    print("   ✓ Delete with non-existent task properly handled")

    # Test 5: Test with a valid format but non-existent task for complete
    print("\n5. Testing complete with non-existent task:")
    result = TaskOperationsService.complete_task(task_id=non_existent_task_id)
    print(f"   Result: {result}")
    assert result["status"] == "error"
    assert "not found" in result["message"]
    print("   ✓ Complete with non-existent task properly handled")


async def test_voice_command_validation():
    """Test voice command validation functionality"""

    print("\n\nTesting voice command validation...")

    # Test 1: Valid task command
    print("\n1. Testing valid task command:")
    result = await voice_processor_service.validate_voice_command("Add a task to buy groceries")
    print(f"   Result: {result}")
    assert result["is_valid_task_command"] == True
    assert result["is_task_related"] == True
    print("   ✓ Valid task command properly validated")

    # Test 2: Valid command with task ID
    print("\n2. Testing command with task ID:")
    result = await voice_processor_service.validate_voice_command("Mark task 3 as done")
    print(f"   Result: {result}")
    assert result["is_valid_task_command"] == True
    assert result["detected_task_ids"] == ["3"]
    print("   ✓ Command with task ID properly detected")

    # Test 3: Invalid command
    print("\n3. Testing invalid task command:")
    result = await voice_processor_service.validate_voice_command("What's the weather like today?")
    print(f"   Result: {result}")
    assert result["is_valid_task_command"] == False
    assert result["is_task_related"] == False
    assert len(result["suggestions"]) > 0
    print("   ✓ Invalid task command properly identified with suggestions")

    # Test 4: Audio format validation
    print("\n4. Testing audio format validation:")
    result = await voice_processor_service.validate_audio_format("mp3")
    print(f"   Result: {result}")
    assert result["valid"] == True
    print("   ✓ Valid audio format properly validated")

    result = await voice_processor_service.validate_audio_format("invalid_format")
    print(f"   Result: {result}")
    assert result["valid"] == False
    print("   ✓ Invalid audio format properly rejected")


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing Error Handling and Validation Features")
    print("=" * 60)

    try:
        await test_invalid_task_id_error_handling()
        await test_voice_command_validation()

        print("\n" + "=" * 60)
        print("✅ All tests passed! Error handling and validation working correctly.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())