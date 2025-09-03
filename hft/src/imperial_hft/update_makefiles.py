import os
import re

def update_makefile(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if it already has build and clean targets
    has_build = re.search(r'^build:', content, re.MULTILINE)
    has_clean = re.search(r'^clean:', content, re.MULTILINE)
    
    if has_build and has_clean:
        return False  # Already has both targets
    
    # Parse the existing makefile to find the main target
    lines = content.strip().split('\n')
    if not lines:
        return False
    
    # Find the first target (usually the executable name)
    first_target_match = re.match(r'^([^:\s]+):', lines[0])
    if not first_target_match:
        return False
    
    target_name = first_target_match.group(1)
    
    # Build new makefile content
    new_content = f"# Default target\nall: build\n\n"
    new_content += f"# Build target\nbuild: {target_name}\n\n"
    new_content += content
    
    if not has_clean:
        new_content += f"\n# Clean target\nclean:\n\trm -f {target_name} *.o\n"
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

# Find all Makefiles and update them
for root, dirs, files in os.walk('.'):
    if 'Makefile' in files:
        filepath = os.path.join(root, 'Makefile')
        if update_makefile(filepath):
            print(f"Updated: {filepath}")
        else:
            print(f"Skipped (already has targets): {filepath}")
