#!/usr/bin/env python3
"""
Docstring Checker for Pre-commit Hooks.

This script compares Python files against their HEAD version in git to determine
if changes are logic-only or just docstring/comment modifications. It parses the
AST of both versions, removes docstrings, and compares the resulting trees.

Usage:
    python docstring_checker.py [--verbose] [--debug] file1.py file2.py ...

Options:
    --verbose: Show detailed information about what's being checked
    --debug: Save AST dumps to files for debugging purposes
"""
import ast
import sys
import subprocess
import os
import argparse

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

    # Use a custom NodeTransformer to safely remove docstrings
    class DocstringRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            return self._remove_docstring(node)
        
        def visit_AsyncFunctionDef(self, node):
            self.generic_visit(node)
            return self._remove_docstring(node)
        
        def visit_ClassDef(self, node):
            self.generic_visit(node)
            return self._remove_docstring(node)
        
        def visit_Module(self, node):
            self.generic_visit(node)
            return self._remove_docstring(node)
        
        def _remove_docstring(self, node):
            """Remove docstring from a node if it exists."""
            if not node.body:
                return node
            
            first_stmt = node.body[0]
            # Check if it's an expression statement
            if not isinstance(first_stmt, ast.Expr):
                return node
            
            # Check if the value is a string constant (docstring)
            # For Python 3.8+ use ast.Constant, for older versions ast.Str
            value = first_stmt.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                # Remove the docstring
                node.body = node.body[1:]
            elif isinstance(value, ast.Str):  # For Python < 3.8
                # Remove the docstring
                node.body = node.body[1:]
            
            return node
    
    # Apply the transformer
    tree = DocstringRemover().visit(tree)
    
    # Dump structure. include_attributes=False ignores line numbers/col offsets
    return ast.dump(tree, include_attributes=False)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Check if Python file changes are logic or just docstrings"
    )
    parser.add_argument("files", nargs="+", help="Python files to check")
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed information"
    )
    parser.add_argument(
        "--debug", "-d", action="store_true",
        help="Save AST dumps for debugging"
    )
    
    args = parser.parse_args()
    
    # Force stdout to utf-8
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    files = args.files
    verbose = args.verbose
    debug = args.debug
    
    if not files:
        print("[ERR] No files provided to check.")
        sys.exit(1)
    
    logic_changed = False
    
    print(f"Checking {len(files)} file(s)...")
    if verbose:
        print(f"Verbose mode: ON")
        print(f"Debug mode: {'ON' if debug else 'OFF'}")

    for filename in files:
        # Skip non-Python files
        if not filename.endswith('.py'):
            if verbose:
                print(f"[SKIP] Non-Python file: {filename}")
            continue
            
        # Normalize path for git
        git_path = filename.replace(os.sep, '/')
        
        if verbose:
            print(f"\nProcessing: {filename}")
        
        # 1. Get Old Code (HEAD)
        try:
            old_code = subprocess.check_output(
                ["git", "show", f"HEAD:{git_path}"], 
                stderr=subprocess.DEVNULL,
                encoding="utf-8",
                errors="replace"
            )
            if verbose:
                print(f"  ✓ Retrieved HEAD version ({len(old_code)} chars)")
        except subprocess.CalledProcessError:
            # File might be new or deleted in the working directory
            if os.path.exists(filename):
                print(f"[NEW] New file detected: {filename}")
            else:
                print(f"[DEL] File deleted: {filename}")
            logic_changed = True
            continue
        except UnicodeDecodeError:
            print(f"[ERR] Could not decode HEAD version of {filename}")
            logic_changed = True
            continue

        # 2. Get New Code (Disk)
        try:
            with open(filename, "r", encoding="utf-8", errors="replace") as f:
                new_code = f.read()
            if verbose:
                print(f"  ✓ Retrieved working version ({len(new_code)} chars)")
        except FileNotFoundError:
            print(f"[DEL] File deleted: {filename}")
            logic_changed = True
            continue
        except UnicodeDecodeError:
            print(f"[ERR] Could not decode local version of {filename}")
            logic_changed = True
            continue
        except Exception as e:
            print(f"[ERR] Error reading {filename}: {e}")
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

        # Debug: save AST dumps
        if debug:
            debug_dir = os.path.join(os.path.dirname(__file__), ".ast_debug")
            os.makedirs(debug_dir, exist_ok=True)
            
            safe_name = filename.replace(os.sep, "_").replace(":", "")
            old_ast_file = os.path.join(debug_dir, f"{safe_name}.old.ast")
            new_ast_file = os.path.join(debug_dir, f"{safe_name}.new.ast")
            
            with open(old_ast_file, "w", encoding="utf-8") as f:
                f.write(old_ast)
            with open(new_ast_file, "w", encoding="utf-8") as f:
                f.write(new_ast)
            
            if verbose:
                print(f"  ✓ Saved AST dumps to {debug_dir}")

        if old_ast != new_ast:
            print(f"[MOD] Logic change detected in: {filename}")
            if verbose:
                # Show a hint about the difference
                if len(old_ast) != len(new_ast):
                    print(f"  AST size: {len(old_ast)} → {len(new_ast)} chars")
            logic_changed = True
        else:
            # Debug: confirming it passed as docstring only
            print(f"[OK]  Docstring/Comment/Style only: {filename}")
            if verbose:
                print(f"  AST unchanged (both {len(old_ast)} chars)")

    print("-" * 40)
    if logic_changed:
        print("[!] COMMIT CONTAINS LOGIC CHANGES")
    else:
        print("[✓] ONLY DOCSTRINGS/COMMENTS! (Tests could be skipped)")
    print("-" * 40)
    
    # Return exit code (0 = no logic changes, no need to exit non-zero for pre-commit)
    # This allows the commit to proceed but provides information
    sys.exit(0)

if __name__ == "__main__":
    main()