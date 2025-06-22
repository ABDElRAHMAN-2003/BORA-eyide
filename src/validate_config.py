#!/usr/bin/env python3
"""
Configuration validation script for CrewAI YAML files
"""

import yaml
import os
from typing import Dict, Any, List

class ConfigValidator:
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), 'config')
        self.errors = []
        self.warnings = []
    
    def validate_agents_yaml(self) -> bool:
        """Validate agents.yaml structure and required fields"""
        print("=== Validating agents.yaml ===")
        
        try:
            with open(os.path.join(self.config_dir, 'agents.yaml'), 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to load agents.yaml: {e}")
            return False
        
        # Check if config is a dictionary
        if not isinstance(config, dict):
            self.errors.append("agents.yaml must be a dictionary")
            return False
        
        # Check for at least one agent
        if not config:
            self.errors.append("agents.yaml must contain at least one agent")
            return False
        
        # Validate each agent
        for agent_name, agent_config in config.items():
            print(f"  Validating agent: {agent_name}")
            
            if not isinstance(agent_config, dict):
                self.errors.append(f"Agent '{agent_name}' must be a dictionary")
                continue
            
            # Required fields for CrewAI Agent
            required_fields = ['role', 'goal', 'backstory']
            for field in required_fields:
                if field not in agent_config:
                    self.errors.append(f"Agent '{agent_name}' missing required field: {field}")
                elif not agent_config[field]:
                    self.warnings.append(f"Agent '{agent_name}' has empty {field}")
            
            # Optional but recommended fields
            optional_fields = ['verbose', 'memory', 'allow_delegation', 'tools']
            for field in optional_fields:
                if field in agent_config:
                    print(f"    ✓ {field}: {agent_config[field]}")
                else:
                    print(f"    ⚠ {field}: not specified (will use default)")
        
        return len(self.errors) == 0
    
    def validate_tasks_yaml(self) -> bool:
        """Validate tasks.yaml structure and required fields"""
        print("\n=== Validating tasks.yaml ===")
        
        try:
            with open(os.path.join(self.config_dir, 'tasks.yaml'), 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to load tasks.yaml: {e}")
            return False
        
        # Check if config is a dictionary
        if not isinstance(config, dict):
            self.errors.append("tasks.yaml must be a dictionary")
            return False
        
        # Check for at least one task
        if not config:
            self.errors.append("tasks.yaml must contain at least one task")
            return False
        
        # Validate each task
        for task_name, task_config in config.items():
            print(f"  Validating task: {task_name}")
            
            if not isinstance(task_config, dict):
                self.errors.append(f"Task '{task_name}' must be a dictionary")
                continue
            
            # Required fields for CrewAI Task
            required_fields = ['description_template', 'expected_output', 'agent']
            for field in required_fields:
                if field not in task_config:
                    self.errors.append(f"Task '{task_name}' missing required field: {field}")
                elif not task_config[field]:
                    self.warnings.append(f"Task '{task_name}' has empty {field}")
            
            # Check if agent reference exists in agents.yaml
            if 'agent' in task_config:
                agent_name = task_config['agent']
                agents_file = os.path.join(self.config_dir, 'agents.yaml')
                try:
                    with open(agents_file, 'r') as f:
                        agents_config = yaml.safe_load(f)
                    if agent_name not in agents_config:
                        self.errors.append(f"Task '{task_name}' references non-existent agent: {agent_name}")
                    else:
                        print(f"    ✓ agent: {agent_name} (exists in agents.yaml)")
                except Exception:
                    self.warnings.append(f"Could not verify agent reference: {agent_name}")
        
        return len(self.errors) == 0
    
    def validate_yaml_syntax(self) -> bool:
        """Validate YAML syntax for all config files"""
        print("\n=== Validating YAML Syntax ===")
        
        config_files = ['agents.yaml', 'tasks.yaml']
        
        for filename in config_files:
            filepath = os.path.join(self.config_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    yaml.safe_load(f)
                print(f"  ✓ {filename}: Valid YAML syntax")
            except yaml.YAMLError as e:
                self.errors.append(f"{filename}: Invalid YAML syntax - {e}")
            except FileNotFoundError:
                self.errors.append(f"{filename}: File not found")
        
        return len(self.errors) == 0
    
    def validate_config_consistency(self) -> bool:
        """Validate consistency between agents.yaml and tasks.yaml"""
        print("\n=== Validating Configuration Consistency ===")
        
        try:
            # Load both configs
            with open(os.path.join(self.config_dir, 'agents.yaml'), 'r') as f:
                agents_config = yaml.safe_load(f)
            with open(os.path.join(self.config_dir, 'tasks.yaml'), 'r') as f:
                tasks_config = yaml.safe_load(f)
            
            # Check agent references in tasks
            available_agents = set(agents_config.keys())
            referenced_agents = set()
            
            for task_name, task_config in tasks_config.items():
                if 'agent' in task_config:
                    referenced_agents.add(task_config['agent'])
            
            # Check for unreferenced agents
            unreferenced = available_agents - referenced_agents
            if unreferenced:
                self.warnings.append(f"Unreferenced agents in tasks.yaml: {', '.join(unreferenced)}")
            
            # Check for missing agents
            missing = referenced_agents - available_agents
            if missing:
                self.errors.append(f"Tasks reference non-existent agents: {', '.join(missing)}")
            
            print(f"  ✓ Available agents: {', '.join(available_agents)}")
            print(f"  ✓ Referenced agents: {', '.join(referenced_agents)}")
            
        except Exception as e:
            self.errors.append(f"Error checking consistency: {e}")
        
        return len(self.errors) == 0
    
    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        print("🔍 CrewAI Configuration Validator\n")
        
        validations = [
            self.validate_yaml_syntax,
            self.validate_agents_yaml,
            self.validate_tasks_yaml,
            self.validate_config_consistency
        ]
        
        all_passed = True
        for validation in validations:
            if not validation():
                all_passed = False
        
        # Print results
        print("\n" + "="*50)
        print("VALIDATION RESULTS")
        print("="*50)
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validations passed! Configuration is correct.")
        elif not self.errors:
            print("\n✅ Configuration is valid with warnings.")
        else:
            print("\n❌ Configuration has errors that need to be fixed.")
        
        return all_passed

def main():
    """Run configuration validation"""
    validator = ConfigValidator()
    success = validator.run_all_validations()
    
    if success:
        print("\n🎉 Your YAML configurations are properly connected to CrewAI!")
    else:
        print("\n🔧 Please fix the errors above before using the chatbot.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 