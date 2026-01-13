#!/usr/bin/env python3
import ast
import sys
import subprocess
import os

def get_ast_dump(source_code, filename="<unknown>"):
    """
    Parse source code into an AST, remove docstrings, and return string dump.
    Returns "SYNTAX_ERROR" if parsing fails, forcing a mismatch.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        print(f"[WARN] Syntax Error parsing {filename}. Assuming logic change.")
        return "SYNTAX_ERROR"

    for node in ast.walk(tree):
        # We only care about Function, Class, AsyncFunction, Module
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef, ast.Module)):
            continue
        
        # Check if the first body element is an Expression (Docstrings are Expressions)
        if not (node.body and isinstance(node.body[0], ast.Expr)):
            continue
        
        # Check if that Expression is a String or Constant (Python 3.8+)
        if isinstance(node.body[0].value, (ast.Str, ast.Constant)):
             # Remove the docstring node from the tree
             node.body.pop(0)

    # Dump structure. include_attributes=False ignores line numbers/col offsets
    return ast.dump(tree, include_attributes=False)

def main():
    # Force stdout to utf-8
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    files = sys.argv[1:]
    logic_changed = False
    
    print(f"Checking {len(files)} files...")

    for filename in files:
        # Normalize path for git
        git_path = filename.replace(os.sep, '/')
        
        # 1. Get Old Code (HEAD)
        try:
            old_code = subprocess.check_output(
                ["git", "show", f"HEAD:{git_path}"], 
                stderr=subprocess.DEVNULL
            ).decode("utf-8")
        except subprocess.CalledProcessError:
            print(f"[NEW] File detected: {filename}")
            logic_changed = True
            continue
        except UnicodeDecodeError:
            print(f"[ERR] Could not decode HEAD version of {filename}")
            logic_changed = True
            continue

        # 2. Get New Code (Disk)
        try:
            with open(filename, "r", encoding="utf-8") as f:
                new_code = f.read()
        except FileNotFoundError:
            print(f"[DEL] File deleted: {filename}")
            logic_changed = True
            continue
        except UnicodeDecodeError:
            print(f"[ERR] Could not decode local version of {filename}")
            logic_changed = True
            continue

        # 3. Compare AST
        # Pass filename for better error reporting
        old_ast = get_ast_dump(old_code, f"HEAD:{filename}")
        new_ast = get_ast_dump(new_code, filename)

        if old_ast == "SYNTAX_ERROR" or new_ast == "SYNTAX_ERROR":
            print(f"[ERR] Syntax Error detected in: {filename}")
            logic_changed = True
            continue

        if old_ast != new_ast:
            print(f"[MOD] Logic change detected in: {filename}")
            logic_changed = True
        else:
            # Debug: confirming it passed as docstring only
            print(f"[OK]  Docstring/Style only: {filename}")

    print("-" * 40)
    if logic_changed:
        print("[!] COMMIT CONTAINS LOGIC CHANGES")
    else:
        print("[OK] JUST DOCSTRINGS/COMMENTS! (Tests could be skipped)")
    print("-" * 40)

if __name__ == "__main__":
    main()