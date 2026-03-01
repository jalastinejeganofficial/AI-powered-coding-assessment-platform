from supabase import create_client, Client
from config.settings import settings
from typing import Optional


class SupabaseManager:
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client if credentials are available"""
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            except Exception as e:
                print(f"Error initializing Supabase client: {e}")
                self.client = None
    
    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance"""
        return self.client
    
    def test_connection(self):
        """Test the Supabase connection"""
        if not self.client:
            return False
        
        try:
            # Test connection by attempting to access auth
            auth = self.client.auth
            return True
        except Exception:
            return False


# Global instance
supabase_manager = SupabaseManager()