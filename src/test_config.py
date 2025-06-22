#!/usr/bin/env python3
"""
Test script to verify YAML configuration integration with CrewAI
"""

import yaml
import os
from chatbot import ChatBot

def test_yaml_loading():
    """Test that YAML files can be loaded correctly"""
    print("=== Testing YAML Configuration Loading ===")
    
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    
    # Test agents.yaml
    try:
        with open(os.path.join(config_dir, 'agents.yaml'), 'r') as f:
            agents_config = yaml.safe_load(f)
        print("✓ agents.yaml loaded successfully")
        print(f"  - Found agent: {list(agents_config.keys())[0]}")
        print(f"  - Agent role: {agents_config['bora_assistant']['role']}")
    except Exception as e:
        print(f"✗ Error loading agents.yaml: {e}")
        return False
    
    # Test tasks.yaml
    try:
        with open(os.path.join(config_dir, 'tasks.yaml'), 'r') as f:
            tasks_config = yaml.safe_load(f)
        print("✓ tasks.yaml loaded successfully")
        print(f"  - Found task: {list(tasks_config.keys())[0]}")
        print(f"  - Task agent: {tasks_config['chat_response']['agent']}")
    except Exception as e:
        print(f"✗ Error loading tasks.yaml: {e}")
        return False
    
    return True

def test_chatbot_initialization():
    """Test that ChatBot can be initialized with YAML configs"""
    print("\n=== Testing ChatBot Initialization ===")
    
    try:
        chatbot = ChatBot()
        print("✓ ChatBot initialized successfully")
        print(f"  - Agent created: {type(chatbot.bora_assistant).__name__}")
        print(f"  - Agent role: {chatbot.bora_assistant.role}")
        print(f"  - Agent goal: {chatbot.bora_assistant.goal}")
        return True
    except Exception as e:
        print(f"✗ Error initializing ChatBot: {e}")
        return False

def test_task_creation():
    """Test that tasks can be created using YAML config"""
    print("\n=== Testing Task Creation ===")
    
    try:
        chatbot = ChatBot()
        
        # Test task creation
        task = chatbot.chat_response("Hello, what's your name?")
        print("✓ Task created successfully")
        print(f"  - Task description length: {len(task.description)} chars")
        print(f"  - Task agent: {task.agent.role}")
        print(f"  - Using YAML config: {'description_template' in chatbot.tasks_config['chat_response']}")
        return True
    except Exception as e:
        print(f"✗ Error creating task: {e}")
        return False

def test_crew_structure():
    """Test that Crew can be created with the configured agent and task"""
    print("\n=== Testing Crew Structure ===")
    
    try:
        chatbot = ChatBot()
        
        # Create a simple task
        task = chatbot.chat_response("Hello")
        
        # Test crew creation (without running it)
        from crewai import Crew
        crew = Crew(
            agents=[chatbot.bora_assistant],
            tasks=[task],
            verbose=False
        )
        print("✓ Crew structure created successfully")
        print(f"  - Number of agents: {len(crew.agents)}")
        print(f"  - Number of tasks: {len(crew.tasks)}")
        print(f"  - Agent in crew: {crew.agents[0].role}")
        return True
    except Exception as e:
        print(f"✗ Error creating crew structure: {e}")
        return False

def main():
    """Run all configuration tests"""
    print("Testing YAML Configuration Integration with CrewAI\n")
    
    tests = [
        test_yaml_loading,
        test_chatbot_initialization,
        test_task_creation,
        test_crew_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! YAML configurations are properly connected.")
    else:
        print("❌ Some tests failed. Please check the configuration.")

if __name__ == "__main__":
    main() 