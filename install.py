# install.py
import os
import sys
import shutil

def is_termux():
    return 'com.termux' in os.environ.get('PREFIX', '')

def is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        # On Windows, geteuid doesn't exist
        return False

choice = input('[+] To install press (Y) to uninstall press (N) >> ').strip().lower()
run = os.system

if choice == 'y':
    if is_termux():
        # Termux Installation
        prefix = os.environ.get('PREFIX', '/data/data/com.termux/files/usr')
        bin_path = os.path.join(prefix, 'bin', 'webzyte')
        share_path = os.path.join(prefix, 'share', 'webzyte')

        os.system('chmod 755 Extract.py')
        os.makedirs(share_path, exist_ok=True)
        shutil.copy('Extract.py', os.path.join(share_path, 'Extract.py'))

        termux_launcher = f'''#!/data/data/com.termux/files/usr/bin/sh
exec python3 {share_path}/Extract.py "$@"
'''
        with open(bin_path, 'w') as f:
            f.write(termux_launcher)

        os.chmod(bin_path, 0o755)
        os.chmod(os.path.join(share_path, 'Extract.py'), 0o755)

        print('''\n[+] WEBZyte installed successfully in Termux!
[+] Now type: \033[1;92mwebzyte\033[0m in terminal to run it.\n''')

    elif sys.platform.startswith('linux'):
        # Linux (non-Termux)
        if not is_root():
            print("\033[91m[!] Error: Please run as root (use sudo)\033[0m")
            sys.exit(1)

        os.system('chmod 755 Extract.py')
        os.makedirs('/usr/share/webzyte', exist_ok=True)
        shutil.copy('Extract.py', '/usr/share/webzyte/Extract.py')

        linux_launcher = '#!/bin/sh\nexec python3 /usr/share/webzyte/Extract.py "$@"'
        with open('/usr/bin/webzyte', 'w') as f:
            f.write(linux_launcher)

        os.chmod('/usr/bin/webzyte', 0o755)
        os.chmod('/usr/share/webzyte/Extract.py', 0o755)

        print('''\n[+] WEBZyte installed successfully on Linux!
[+] Now type: \033[1;92mwebzyte\033[0m in terminal to run it.\n''')

    else:
        # Windows
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tool_name = 'webzyte.py'

        shutil.copy('Extract.py', os.path.join(script_dir, tool_name))

        print(f'''\n[+] WEBZyte ready for use on Windows!
[+] To run: Open terminal in this folder and type:
    \033[1;92mpython {tool_name}\033[0m

Optional: Add this folder to your PATH to run "webzyte.py" from anywhere.
\n''')

elif choice == 'n':
    if is_termux():
        prefix = os.environ.get('PREFIX', '/data/data/com.termux/files/usr')
        os.system(f'rm -rf {prefix}/share/webzyte')
        os.system(f'rm -f {prefix}/bin/webzyte')
        print('[!] WEBZyte removed from Termux successfully')

    elif sys.platform.startswith('linux'):
        if not is_root():
            print("\033[91m[!] Error: Please run as root (use sudo)\033[0m")
            sys.exit(1)
        os.system('rm -rf /usr/share/webzyte')
        os.system('rm -f /usr/bin/webzyte')
        print('[!] WEBZyte removed from Linux successfully')

    else:
        # Windows uninstall (just info)
        print('''[!] On Windows: Simply delete the folder to uninstall.
    Files: Extract.py and webzyte.py (if created)\n''')

else:
    print('[!] Invalid choice. Exiting.')