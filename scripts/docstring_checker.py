#!/usr/bin/env python3
import ast
import sys
import subprocess
import os

def get_clean_ast(source_code):
    """Parse source code into an AST and remove docstrings."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef, ast.Module)):
            continue
        if not (node.body and isinstance(node.body[0], ast.Expr)):
            continue
        # Remove docstring
        if isinstance(node.body[0].value, (ast.Str, ast.Constant)):
             node.body.pop(0)

    return ast.dump(tree, include_attributes=False)

def main():
    # Force stdout to use utf-8 if possible, otherwise rely on ASCII below
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    files = sys.argv[1:]
    logic_changed = False
    
    for filename in files:
        # Standardize paths for Git (Windows uses backslashes)
        git_path = filename.replace(os.sep, '/')
        
        # 1. Check for New Files
        try:
            # We use stderr=subprocess.DEVNULL to hide the git error message when file is new
            old_code = subprocess.check_output(
                ["git", "show", f"HEAD:{git_path}"], 
                stderr=subprocess.DEVNULL
            ).decode("utf-8")
        except subprocess.CalledProcessError:
            # If git fails, the file is new (not in HEAD)
            print(f"[NEW] File detected: {filename}")
            logic_changed = True
            continue

        # 2. Get Current Code (from disk/staging)
        try:
            with open(filename, "r", encoding="utf-8") as f:
                new_code = f.read()
        except FileNotFoundError:
            print(f"[DEL] File deleted: {filename}")
            logic_changed = True
            continue

        # 3. Compare AST
        if get_clean_ast(old_code) != get_clean_ast(new_code):
            print(f"[MOD] Logic change detected in: {filename}")
            logic_changed = True

    print("-" * 40)
    if logic_changed:
        print("[!] COMMIT CONTAINS LOGIC CHANGES")
    else:
        print("[OK] JUST DOCSTRINGS/COMMENTS! (Tests could be skipped)")
    print("-" * 40)

if __name__ == "__main__":
    main()