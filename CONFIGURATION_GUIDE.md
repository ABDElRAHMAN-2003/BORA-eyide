# CrewAI Configuration Guide

This guide explains how the YAML configuration files are connected to the CrewAI structure and how to maintain them properly.

## 📁 Configuration Files Structure

```
src/config/
├── agents.yaml      # Agent definitions and configurations
└── tasks.yaml       # Task definitions and templates
```

## 🔧 Agents Configuration (`agents.yaml`)

The `agents.yaml` file defines all AI agents used in the system. Each agent has specific attributes that CrewAI uses to create Agent instances.

### Required Fields

- **`role`**: The agent's role/title (e.g., "AI Assistant (Jarvis-like)")
- **`goal`**: What the agent aims to achieve
- **`backstory`**: Detailed description of the agent's personality and capabilities

### Optional Fields

- **`verbose`**: Whether the agent should be verbose in its operations (default: false)
- **`memory`**: Whether the agent should maintain memory (default: true)
- **`allow_delegation`**: Whether the agent can delegate tasks (default: false)
- **`tools`**: List of tools the agent can use (default: [])

### Example Structure

```yaml
bora_assistant:
  role: AI Assistant (Jarvis-like)
  goal: Be a helpful, conversational AI assistant that can chat naturally and provide information when needed
  backstory: >
    You are Bora, an advanced AI assistant inspired by Jarvis from Iron Man...
  verbose: false
  memory: true
  allow_delegation: false
  tools: []
```

## 📋 Tasks Configuration (`tasks.yaml`)

The `tasks.yaml` file defines tasks that agents can perform. Each task has a template that gets populated with dynamic data.

### Required Fields

- **`description_template`**: Template string for the task description (supports Python string formatting)
- **`expected_output`**: What the task should produce
- **`agent`**: Reference to the agent that will perform this task (must exist in `agents.yaml`)

### Example Structure

```yaml
chat_response:
  description_template: >
    Respond to the user's input in a natural, conversational way...
    
    RELEVANT DATA FOR THIS QUERY:
    {relevant_data}
    
    Use this data to provide specific, accurate responses...
  expected_output: >
    A natural, conversational response that directly addresses what the user said or asked...
  agent: bora_assistant
```

## 🔗 How Configuration Connects to CrewAI

### 1. Agent Creation

In `chatbot.py`, agents are created using the YAML configuration:

```python
# Load agent config from YAML
with open(os.path.join(config_dir, 'agents.yaml'), 'r') as f:
    self.agents_config = yaml.safe_load(f)

# Create agent with YAML config + additional CrewAI requirements
agent_config = self.agents_config['bora_assistant'].copy()
agent_config['llm'] = completion  # Add required CrewAI parameter
self.bora_assistant = Agent(**agent_config)
```

### 2. Task Creation

Tasks are created using the YAML template:

```python
# Use task configuration from YAML
task_config = self.tasks_config['chat_response']
description = task_config['description_template'].format(relevant_data=relevant_data)

return Task(
    description=description,
    expected_output=task_config['expected_output'],
    agent=self.bora_assistant
)
```

### 3. Crew Assembly

The Crew is assembled using the configured agent and task:

```python
crew = Crew(
    agents=[self.bora_assistant],  # Agent from YAML config
    tasks=[self.chat_response(user_input)],  # Task using YAML template
    verbose=True
)
```

## ✅ Validation and Testing

### Running Configuration Tests

```bash
# Test basic configuration loading and CrewAI integration
python src/test_config.py

# Validate YAML structure and consistency
python src/validate_config.py
```

### What the Tests Check

1. **YAML Syntax**: Valid YAML format
2. **Required Fields**: All necessary fields are present
3. **Agent References**: Tasks reference valid agents
4. **CrewAI Integration**: Agents and tasks can be created successfully
5. **Configuration Consistency**: No orphaned agents or missing references

## 🛠️ Maintenance Guidelines

### Adding New Agents

1. Add agent definition to `agents.yaml`:
```yaml
new_agent:
  role: "New Agent Role"
  goal: "Agent's goal"
  backstory: "Agent's backstory..."
  verbose: false
  memory: true
  allow_delegation: false
  tools: []
```

2. Update `chatbot.py` to create the new agent:
```python
self.new_agent = Agent(**self.agents_config['new_agent'])
```

### Adding New Tasks

1. Add task definition to `tasks.yaml`:
```yaml
new_task:
  description_template: "Task description with {variables}..."
  expected_output: "Expected output description"
  agent: "agent_name_from_agents_yaml"
```

2. Create a method in `chatbot.py` to use the task:
```python
def new_task_method(self, data):
    task_config = self.tasks_config['new_task']
    description = task_config['description_template'].format(variables=data)
    
    return Task(
        description=description,
        expected_output=task_config['expected_output'],
        agent=self.agent_name
    )
```

### Modifying Existing Configurations

1. **Agent Modifications**: Update fields in `agents.yaml` and restart the application
2. **Task Modifications**: Update templates in `tasks.yaml` - changes take effect immediately
3. **Always run validation** after making changes: `python src/validate_config.py`

## 🚨 Common Issues and Solutions

### Issue: "Agent not found" error
**Solution**: Ensure the agent name in `tasks.yaml` matches exactly with the key in `agents.yaml`

### Issue: YAML syntax errors
**Solution**: Use a YAML validator or run `python src/validate_config.py` to identify syntax issues

### Issue: Missing required fields
**Solution**: Check that all required fields (`role`, `goal`, `backstory` for agents; `description_template`, `expected_output`, `agent` for tasks) are present

### Issue: Template formatting errors
**Solution**: Ensure all variables in `description_template` are properly formatted with `{variable_name}` and that the `.format()` call provides all required variables

## 📊 Configuration Best Practices

1. **Keep it DRY**: Use templates for repeated patterns
2. **Validate Early**: Run validation scripts after any changes
3. **Document Changes**: Update this guide when adding new agents or tasks
4. **Test Thoroughly**: Always test new configurations before deployment
5. **Use Meaningful Names**: Choose descriptive names for agents and tasks
6. **Maintain Consistency**: Follow the established naming conventions

## 🔍 Debugging Configuration Issues

### Enable Debug Output

Add debug prints to see how configurations are being used:

```python
print(f"Agent config: {self.agents_config}")
print(f"Task config: {self.tasks_config}")
```

### Check Configuration Loading

Verify that files are being loaded correctly:

```python
print(f"Config directory: {config_dir}")
print(f"Agents file exists: {os.path.exists(os.path.join(config_dir, 'agents.yaml'))}")
```

### Validate CrewAI Integration

Test that CrewAI can create objects with your configuration:

```python
try:
    agent = Agent(**agent_config)
    print("✓ Agent created successfully")
except Exception as e:
    print(f"✗ Agent creation failed: {e}")
```

This configuration system ensures that your CrewAI setup is maintainable, testable, and properly structured for future enhancements. 