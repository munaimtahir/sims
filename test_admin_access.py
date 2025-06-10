import subprocess
import sys
import time

print("🚀 Starting SIMS Server and Testing Admin Page")
print("=" * 60)

try:
    # Start the Django server
    print("1. Starting Django development server...")
    server_process = subprocess.Popen([
        sys.executable, "manage.py", "runserver", "127.0.0.1:8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait a bit for server to start
    time.sleep(3)
    
    # Check if server is running
    if server_process.poll() is None:
        print("   ✅ Server is running")
        
        # Test the admin page
        import os
        import django
        from django.test import Client
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sims_project.settings')
        django.setup()
        
        print("\n2. Testing admin page accessibility...")
        client = Client()
        
        try:
            response = client.get('/admin/')
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 302:
                location = response.get('Location', '')
                print(f"   Redirects to: {location}")
                if '/admin/login/' in location:
                    print("   ✅ Correctly redirects to login page")
                    
                    # Test login page
                    login_response = client.get('/admin/login/')
                    print(f"   Login page status: {login_response.status_code}")
                    
                    if login_response.status_code == 200:
                        content = login_response.content.decode()
                        print(f"   Login page content length: {len(content)} chars")
                        
                        if len(content) > 100:
                            print("   ✅ Login page has content")
                            if 'login-form' in content:
                                print("   ✅ Login form found")
                            else:
                                print("   ❌ Login form not found")
                        else:
                            print("   ❌ Login page appears empty")
                    else:
                        print("   ❌ Login page not accessible")
                else:
                    print("   ⚠️  Unexpected redirect location")
            elif response.status_code == 200:
                print("   ✅ Admin page accessible directly")
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing admin page: {e}")
        
        print("\n3. Server URLs to test:")
        print("   - http://127.0.0.1:8000/admin/")
        print("   - http://localhost:8000/admin/")
        print("   - http://127.0.0.1:8000/admin/login/")
        
    else:
        # Server failed to start
        stdout, stderr = server_process.communicate()
        print("   ❌ Server failed to start")
        print(f"   STDOUT: {stdout}")
        print(f"   STDERR: {stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Clean up
    try:
        if 'server_process' in locals() and server_process.poll() is None:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
    except:
        pass

print("\n" + "=" * 60)
print("Test complete!")
print("\n💡 If admin page is still not working:")
print("1. Check if any antivirus/firewall is blocking localhost")
print("2. Try clearing browser cache")
print("3. Try a different browser")
print("4. Check if another service is using port 8000")
