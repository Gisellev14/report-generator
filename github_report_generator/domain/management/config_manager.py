import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    DEFAULT_CONFIG = {
        'repo': 'owner/repo',
        'days': '30'
    }
    
    DEFAULT_CONFIG = {
        'repo': 'owner/repo',
        'days': '30'
    }
    
    def __init__(self, config_file: str = '.github_report_gui.json'):
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        
    def load_config(self) -> Dict[str, Any]:
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Use defaults if loading fails
            pass
            
        return self.config
        
    def save_config(self, config: Dict[str, Any]) -> bool:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
            
    def update_config(self, **kwargs) -> None:
        self.config.update(kwargs)
        
    def get_value(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
        
    def set_value(self, key: str, value: Any) -> None:
        self.config[key] = value
