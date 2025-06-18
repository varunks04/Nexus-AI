#!/usr/bin/env python3
"""
Test archive functionality specifically
"""

from app import create_app

def test_archive_with_no_entries():
    """Test archive page when no entries exist"""
    print("📚 Testing archive with no entries...")
    
    try:
        app, managers = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            response = client.get('/archive')
            print(f"✅ Archive page status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Archive page loads successfully with no entries")
                return True
            else:
                print(f"❌ Archive page failed with status: {response.status_code}")
                if hasattr(response, 'data'):
                    print(f"Response data: {response.data.decode()[:200]}...")
                return False
                
    except Exception as e:
        print(f"❌ Archive test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_archive_with_no_entries()
