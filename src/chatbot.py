import yaml
import os
import re
from litellm import completion


class ChatBot:
    def __init__(self):
        # Load agent and task configs from YAML files
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        with open(os.path.join(config_dir, 'agents.yaml'), 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open(os.path.join(config_dir, 'tasks.yaml'), 'r') as f:
            self.tasks_config = yaml.safe_load(f)

        # Load all data files once and store in memory
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.data_files = {}
        data_file_names = [
            'fraud_data.txt', 'fraud_response.txt',
            'market_data.txt', 'market_response.txt',
            'revenue_data.txt', 'revenue_response.txt',
            'userPref.txt'
        ]

        print("Loading data files into memory...")
        for filename in data_file_names:
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.data_files[filename.replace('.txt', '')] = content
                    print(f"✓ Loaded {filename}: {len(content)} characters")
            except FileNotFoundError:
                print(f"✗ Warning: {filename} not found in data directory")
                self.data_files[filename.replace('.txt', '')] = "Data not available"

        # Initialize conversation memory
        self.conversation_memory = []

    def detect_intent(self, user_input):
        """Detect what type of data the user is asking about"""
        user_input_lower = user_input.lower()

        # Identity questions
        if any(word in user_input_lower for word in ['name', 'who are you', 'who built you', 'created by']):
            return 'identity'

        # Business data questions
        if any(word in user_input_lower for word in ['fraud', 'fraudulent', 'suspicious', 'security', 
                                                    'market', 'trend', 'stock', 'trading', 'price',
                                                    'revenue', 'income', 'profit', 'financial', 'money', 'earnings',
                                                    'business', 'summary', 'overview', 'data', 'metrics']):
            return 'business_data'

        # Greetings
        if any(word in user_input_lower for word in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']):
            return 'greeting'

        return 'general'

    def get_relevant_data(self, intent, user_input):
        """Get relevant data based on user intent and input"""
        if intent == 'identity':
            return ""

        elif intent == 'business_data':
            user_input_lower = user_input.lower()
            
            if any(word in user_input_lower for word in ['fraud', 'fraudulent', 'suspicious', 'security']):
                return f"""
                FRAUD DATA:
                {self.data_files.get('fraud_data', 'Not available')[:500]}...

                FRAUD ANALYSIS:
                {self.data_files.get('fraud_response', 'Not available')[:800]}...
                """
            
            elif any(word in user_input_lower for word in ['market', 'trend', 'stock', 'trading', 'price']):
                return f"""
                MARKET DATA SUMMARY:
                {self.data_files.get('market_data', 'Not available')[:800]}...

                MARKET ANALYSIS:
                {self.data_files.get('market_response', 'Not available')[:800]}...
                """
            
            elif any(word in user_input_lower for word in ['revenue', 'income', 'profit', 'financial', 'money', 'earnings']):
                return f"""
                REVENUE DATA:
                {self.data_files.get('revenue_data', 'Not available')[:500]}...

                REVENUE ANALYSIS:
                {self.data_files.get('revenue_response', 'Not available')[:800]}...
                """
            
            else:
                # General business query
                return f"""
                BUSINESS SUMMARY:

                FRAUD: {self.data_files.get('fraud_response', 'Not available')[:200]}...
                MARKET: {self.data_files.get('market_response', 'Not available')[:200]}...
                REVENUE: {self.data_files.get('revenue_response', 'Not available')[:200]}...
                USER PREFERENCES: {self.data_files.get('userPref', 'Not available')}
                """

        return ""

    def create_system_prompt(self, intent, relevant_data):
        """Create system prompt using agent configuration from YAML"""
        # Get agent configuration from YAML
        agent_config = self.agents_config['bora_assistant']
        task_config = self.tasks_config['chat_response']
        
        # Build the system prompt using agent configuration
        system_prompt = f"""
        ROLE: {agent_config['role']}
        GOAL: {agent_config['goal']}
        BACKSTORY: {agent_config['backstory']}
        
        TASK DESCRIPTION:
        {task_config['description_template'].format(relevant_data=relevant_data)}
        
        EXPECTED OUTPUT: {task_config['expected_output']}
        """
        
        return system_prompt

    def process_input(self, user_input):
        """Process user input and return response"""
        # Detect user intent
        intent = self.detect_intent(user_input)

        # Add to conversation memory
        self.conversation_memory.append({
            'user_input': user_input,
            'intent': intent,
            'timestamp': 'now'
        })

        # Get relevant data if needed
        relevant_data = self.get_relevant_data(intent, user_input)

        # Get agent configuration from YAML
        agent_config = self.agents_config['bora_assistant']
        task_config = self.tasks_config['chat_response']
        
        # Create system prompt using agent configuration from YAML
        system_prompt = f"""
        ROLE: {agent_config['role']}
        GOAL: {agent_config['goal']}
        BACKSTORY: {agent_config['backstory']}
        
        TASK DESCRIPTION:
        {task_config['description_template'].format(relevant_data=relevant_data)}
        
        EXPECTED OUTPUT: {task_config['expected_output']}
        """

        # Debug: Show intent and configuration usage
        print(f"\nIntent detected: {intent}")
        print(f"- User input: {user_input}")
        print(f"- Using agent config from YAML: {list(self.agents_config.keys())[0]}")
        print(f"- Using task config from YAML: {task_config['agent']}")
        if relevant_data:
            print(f"- Data length: {len(relevant_data)} chars")

        try:
            # Call the LLM directly using gpt-4o-mini
            response = completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Sorry, I encountered an error: {str(e)}"