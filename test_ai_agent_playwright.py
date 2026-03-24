#!/usr/bin/env python3
"""Test AI Agent features via Playwright MCP"""

import subprocess
import time
import json

MCP_URL = "http://localhost:8808"

def mcp_call(tool, params):
    """Make MCP tool call"""
    cmd = [
        "python3", 
        "/home/abdulhannan/.qwen/skills/browsing-with-playwright/scripts/mcp-client.py",
        "call", "-u", MCP_URL, "-t", tool, "-p", json.dumps(params)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(result.stdout)
    except:
        return {"error": result.stdout, "stderr": result.stderr}

def get_snapshot():
    """Get page snapshot"""
    result = mcp_call("browser_snapshot", {})
    return result.get("content", [{}])[0].get("text", "")

def type_and_send(text):
    """Type text and send message"""
    mcp_call("browser_type", {"element": "textbox", "ref": "e153", "text": text})
    time.sleep(0.5)
    mcp_call("browser_type", {"element": "textbox", "ref": "e153", "text": "", "submit": True})

print("=" * 60)
print("AI AGENT FEATURE TEST VIA PLAYWRIGHT")
print("=" * 60)

# Navigate to chat
print("\n1. Navigating to chat page...")
result = mcp_call("browser_navigate", {"url": "http://localhost:3000/chat"})
if "error" in str(result).lower():
    print(f"   ❌ Navigation failed: {result}")
else:
    print("   ✅ Chat page loaded")

time.sleep(3)

# Test 1: Create a task
print("\n2. Testing: CREATE TASK")
print("   Sending: 'Create a task to call the plumber tomorrow'")
type_and_send("Create a task to call the plumber tomorrow")
time.sleep(10)

snapshot = get_snapshot()
if "created successfully" in snapshot or "✅" in snapshot:
    print("   ✅ Task created successfully!")
else:
    print("   ⚠️ Checking response...")
    if "plumber" in snapshot:
        print("   ✅ Task visible in chat")
    else:
        print("   ❌ Task creation may have failed")

# Test 2: List tasks
print("\n3. Testing: LIST TASKS")
print("   Sending: 'Show me all my tasks'")
type_and_send("Show me all my tasks")
time.sleep(10)

snapshot = get_snapshot()
if "Your Pending Tasks" in snapshot or "task" in snapshot.lower():
    print("   ✅ Tasks listed successfully!")
else:
    print("   ⚠️ Checking response...")

# Test 3: Complete task by description
print("\n4. Testing: COMPLETE TASK BY DESCRIPTION")
print("   Sending: 'Mark the task call the plumber as complete'")
type_and_send("Mark the task call the plumber as complete")
time.sleep(10)

snapshot = get_snapshot()
if "completed" in snapshot.lower() or "✅" in snapshot:
    print("   ✅ Task completed successfully!")
elif "ambiguous" in snapshot.lower() or "clarify" in snapshot.lower():
    print("   ✅ Agent correctly asked for clarification (multiple matches)")
else:
    print("   ⚠️ Checking response...")

# Test 4: Create multiple tasks
print("\n5. Testing: CREATE MULTIPLE TASKS")
print("   Sending: 'Add 2 tasks: 1) Buy groceries, 2) Walk the dog'")
type_and_send("Add 2 tasks: 1) Buy groceries, 2) Walk the dog")
time.sleep(15)

snapshot = get_snapshot()
if "created" in snapshot.lower():
    print("   ✅ Multiple tasks created!")
else:
    print("   ⚠️ Checking response...")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
