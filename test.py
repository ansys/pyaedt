import re
import sys

from docstring_parser import DocstringStyle
from docstring_parser import parse
import libcst as cst


class DocstringTypeInjector(cst.CSTTransformer):
    def __init__(self):
        self.type_map = {
            "str": "str",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "list": "list",
            "dict": "dict",
            "tuple": "tuple",
            "object": "Any",
            # Add specific class mappings found in your library
            "FacePrimitive": "FacePrimitive",
            "Object3d": "Object3d",
            "BoundaryDictionary": "BoundaryDictionary",
        }

    def _clean_type_string(self, type_str: str) -> str:
        """
        Heuristic parser to convert docstring type text to Python type strings.
        Example: "str, optional" -> "Optional[str]"
        Example: "int or float" -> "Union[int, float]"
        """
        if not type_str:
            return "Any"

        # Clean up common artifacts
        type_str = type_str.replace("`", "").strip()

        # Check for optional
        is_optional = False
        if ", optional" in type_str:
            is_optional = True
            type_str = type_str.replace(", optional", "")

        # Split by "or" or "," for Union types
        # Regex looks for " or " or ", " but tries to avoid splitting inside brackets
        parts = re.split(r", | or ", type_str)

        clean_parts = []
        for part in parts:
            part = part.strip()
            # Handle class paths: ansys.aedt...FacePrimitive -> FacePrimitive
            if "." in part and not part.startswith("list"):
                part = part.split(".")[-1]

            # Map known types
            mapped = self.type_map.get(part, part)

            # Simple list heuristic: "list of str" -> "List[str]"
            if "list of" in mapped.lower():
                inner = mapped.lower().replace("list of", "").strip()
                inner_mapped = self.type_map.get(inner, "Any")
                mapped = f"List[{inner_mapped}]"

            if mapped not in clean_parts:
                clean_parts.append(mapped)

        # Construct Union
        if len(clean_parts) > 1:
            final_type = f"Union[{', '.join(clean_parts)}]"
        elif clean_parts:
            final_type = clean_parts[0]
        else:
            final_type = "Any"

        if is_optional and "Optional" not in final_type:
            final_type = f"Optional[{final_type}]"

        return final_type

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        # 1. Extract docstring
        docstring_node = original_node.get_docstring()
        if not docstring_node:
            return updated_node

        doc_content = eval(docstring_node.value)  # Safer: ast.literal_eval

        # 2. Parse NumPy Docstring
        try:
            doc = parse(doc_content, style=DocstringStyle.NUMPY)
        except Exception:
            return updated_node

        # 3. Create a map of param name -> docstring type
        param_types = {p.arg_name: p.type_name for p in doc.params if p.type_name}

        # 4. Update Arguments
        new_params = []
        for param in updated_node.params.params:
            # Only annotate if missing annotation and exists in docstring
            if param.annotation is None and param.name.value in param_types:
                type_str = self._clean_type_string(param_types[param.name.value])

                # Create the annotation node
                try:
                    # We parse the string back into a CST node to handle complex types like Union[...]
                    annotation_node = cst.parse_expression(type_str)
                    new_param = param.with_changes(annotation=cst.Annotation(annotation=annotation_node))
                    new_params.append(new_param)
                except Exception:
                    # If parsing fails, skip touching this param
                    new_params.append(param)
            else:
                new_params.append(param)

        # 5. Handle Return Type
        return_annotation = updated_node.returns
        if updated_node.returns is None and doc.returns:
            try:
                # Taking the first return type mentioned
                ret_type_str = self._clean_type_string(doc.returns[0].type_name)
                # Map 'bool' strings correctly if they come from text
                if ret_type_str.lower() == "true" or ret_type_str.lower() == "false":
                    ret_type_str = "bool"

                ret_node = cst.parse_expression(ret_type_str)
                return_annotation = cst.Annotation(annotation=ret_node)
            except:
                pass

        return updated_node.with_changes(
            params=updated_node.params.with_changes(params=new_params), returns=return_annotation
        )


def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    source_tree = cst.parse_module(source_code)
    transformer = DocstringTypeInjector()
    modified_tree = source_tree.visit(transformer)

    print(modified_tree.code)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print("Usage: python annotate_from_docs.py <path_to_file.py>")
