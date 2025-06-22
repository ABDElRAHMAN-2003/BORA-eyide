import os
from typing import Dict

class UserPreferences:
    def __init__(self, preferences_file: str = "src/data/userPref.txt"):
        self.preferences_file = preferences_file
        self.preferences = self.load_preferences()
    
    def load_preferences(self) -> Dict:
        """Load user preferences from text file"""
        prefs = {}
        try:
            with open(self.preferences_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        prefs[key.strip().lower().replace(' ', '_')] = value.strip()
            return prefs
        except FileNotFoundError:
            print(f"Preferences file not found: {self.preferences_file}")
            return {
                "executive_name": "Executive",
                "preferred_greeting": "Good day",
                "communication_style": "professional",
                "team": "Magdy, Saif, Julia, Ali, Omar, Amr",
                "supervisor": "Dr. Noha"
            }
    
    def get_executive_name(self) -> str:
        return self.preferences.get("executive_name", "Executive")
    
    def get_greeting(self) -> str:
        return self.preferences.get("preferred_greeting", "Good day")
    
    def get_communication_style(self) -> str:
        return self.preferences.get("communication_style", "professional")
    
    def get_team(self) -> str:
        return self.preferences.get("team", "Magdy, Saif, Julia, Ali, Omar, Amr")
    
    def get_supervisor(self) -> str:
        return self.preferences.get("supervisor", "Dr. Noha")
