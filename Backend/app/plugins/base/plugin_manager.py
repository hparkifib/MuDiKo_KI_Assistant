# Plugin Manager - Verwaltet alle Tool-Plugins

import importlib
from typing import Dict, List, Optional
from pathlib import Path
import yaml

from app.plugins.base.plugin_interface import MusicToolPlugin
from app.core.exceptions import PluginNotFoundException, PluginInitializationException

class PluginManager:
    """Verwaltet alle Tool-Plugins."""
    
    def __init__(self, plugins_dir: Path, app_context: Dict):
        """Initialisiert den Plugin Manager.
        
        Args:
            plugins_dir: Pfad zum Plugins-Verzeichnis
            app_context: Dictionary mit shared services
        """
        self.plugins_dir = plugins_dir
        self.app_context = app_context
        self._plugins: Dict[str, MusicToolPlugin] = {}
        self._enabled_plugins: List[str] = []
    
    def discover_and_load_plugins(self):
        """Findet und lädt alle verfügbaren Plugins."""
        if not self.plugins_dir.exists():
            print(f"⚠️ Plugin-Verzeichnis nicht gefunden: {self.plugins_dir}")
            return
        
        print(f"🔍 Suche Plugins in: {self.plugins_dir}")
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                if item.name != 'base':  # Skip base module
                    self._load_plugin(item)
        
        if self._plugins:
            print(f"✅ {len(self._plugins)} Plugin(s) geladen: {', '.join(self._plugins.keys())}")
        else:
            print("⚠️ Keine Plugins gefunden")
    
    def _load_plugin(self, plugin_dir: Path):
        """Lädt ein einzelnes Plugin.
        
        Args:
            plugin_dir: Pfad zum Plugin-Verzeichnis
        """
        config_file = plugin_dir / 'config.yaml'
        
        # Config muss existieren
        if not config_file.exists():
            print(f"⚠️ Plugin {plugin_dir.name}: config.yaml nicht gefunden")
            return
        
        try:
            # Lade Config
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            # Plugin nur laden wenn aktiviert
            if not config.get('enabled', True):
                print(f"⏭️ Plugin {plugin_dir.name}: deaktiviert (enabled: false in config.yaml)")
                return
            
            # Importiere Plugin-Modul
            plugin_module = plugin_dir.name
            module_path = f'app.plugins.{plugin_module}.plugin'
            
            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                print(f"⚠️ Plugin {plugin_module}: Modul 'plugin.py' nicht gefunden oder Import-Fehler: {e}")
                return
            
            # Hol Plugin-Klasse
            plugin_class_name = config.get('class')
            if not plugin_class_name:
                print(f"❌ Plugin {plugin_module}: 'class' fehlt in config.yaml")
                return
            
            if not hasattr(module, plugin_class_name):
                print(f"❌ Plugin {plugin_module}: Klasse '{plugin_class_name}' nicht in plugin.py gefunden")
                return
            
            plugin_class = getattr(module, plugin_class_name)
            plugin_instance = plugin_class()
            
            # Erweitere app_context um Plugin-Config
            plugin_app_context = {
                **self.app_context,
                'plugin_config': config  # Plugin-spezifische Config aus config.yaml
            }
            
            # Initialisiere Plugin mit erweitertem Context
            plugin_instance.initialize(plugin_app_context)
            
            # Registriere Plugin
            self._plugins[plugin_instance.name] = plugin_instance
            self._enabled_plugins.append(plugin_instance.name)
            
            print(f"✅ Plugin geladen: {plugin_instance.display_name} v{plugin_instance.version}")
        
        except Exception as e:
            print(f"❌ Fehler beim Laden von {plugin_dir.name}: {e}")
            import traceback
            traceback.print_exc()
    
    def get_plugin(self, name: str) -> MusicToolPlugin:
        """Gibt ein Plugin nach Name zurück.
        
        Args:
            name: Interner Plugin-Name
            
        Returns:
            MusicToolPlugin: Plugin-Instanz
            
        Raises:
            PluginNotFoundException: Wenn Plugin nicht existiert
        """
        plugin = self._plugins.get(name)
        if not plugin:
            raise PluginNotFoundException(f"Plugin '{name}' nicht gefunden")
        return plugin
    
    def get_all_plugins(self) -> List[MusicToolPlugin]:
        """Gibt alle geladenen Plugins zurück.
        
        Returns:
            List[MusicToolPlugin]: Liste aller Plugin-Instanzen
        """
        return list(self._plugins.values())
    
    def get_enabled_plugins(self) -> List[str]:
        """Gibt Liste der aktivierten Plugin-Namen zurück.
        
        Returns:
            List[str]: Plugin-Namen
        """
        return self._enabled_plugins.copy()
    
    def register_blueprints(self, app):
        """Registriert alle Plugin-Blueprints bei Flask.
        
        Args:
            app: Flask app instance
        """
        for plugin in self._plugins.values():
            try:
                blueprint = plugin.get_blueprint()
                url_prefix = f'/api/tools/{plugin.name}'
                app.register_blueprint(blueprint, url_prefix=url_prefix)
                print(f"✅ Blueprint registriert: {url_prefix}")
            except Exception as e:
                print(f"❌ Fehler bei Blueprint-Registrierung für {plugin.name}: {e}")
                import traceback
                traceback.print_exc()
    
    def get_plugins_info(self) -> List[Dict]:
        """Gibt Info über alle Plugins für API zurück.
        
        Returns:
            List[Dict]: Plugin-Informationen
        """
        return [
            {
                'name': plugin.name,
                'display_name': plugin.display_name,
                'description': plugin.description,
                'version': plugin.version,
                'icon': plugin.get_icon(),
                'frontend_routes': plugin.get_frontend_routes()
            }
            for plugin in self._plugins.values()
        ]
    
    def cleanup_all(self):
        """Cleanup für alle Plugins beim Shutdown."""
        for plugin in self._plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"⚠️ Cleanup-Fehler für {plugin.name}: {e}")
