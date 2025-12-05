#!/usr/bin/env python3
import subprocess
import os
import time
import signal

# Kill all git processes
try:
    subprocess.run(['taskkill', '/F', '/IM', 'git.exe'], stderr=subprocess.DEVNULL)
    time.sleep(1)
except:
    pass

os.chdir(r'c:\Users\Lenovo\Documents\Phyton-Programs\7 Rings Run - Game')

# Remove merge state
try:
    if os.path.exists('.git/MERGE_HEAD'):
        os.remove('.git/MERGE_HEAD')
        print('✓ Removed MERGE_HEAD')
except Exception as e:
    print(f'Error removing MERGE_HEAD: {e}')

# Clean reset
try:
    result = subprocess.run(['git', 'reset', '--hard', 'HEAD'], capture_output=True, timeout=10)
    print('✓ Git reset done')
except subprocess.TimeoutExpired:
    print('✗ Git reset timed out')

# Set editor to dummy
try:
    subprocess.run(['git', 'config', 'core.editor', 'true'], capture_output=True, timeout=5)
    print('✓ Set core.editor to true')
except:
    pass

# Try push
try:
    result = subprocess.run(
        ['git', 'push', '-u', 'origin', 'main', '--force'],
        capture_output=True,
        text=True,
        timeout=30
    )
    print('✓ Push completed!')
    if result.stdout:
        print('Output:', result.stdout[:200])
    if result.stderr:
        print('Stderr:', result.stderr[:200])
except subprocess.TimeoutExpired:
    print('✗ Push timed out')
except Exception as e:
    print(f'✗ Push failed: {e}')
