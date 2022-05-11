"""
This module take care of the transformation of cooklang code to hugo-compatible markdown
"""
import os
from pathlib import Path

from .parser import run_lexer

MARKDOWN_TEMPLATE = """{md_code}

## Ingrédients

{md_ingredients_list}

## Materiel

{md_cookwares_list}

## Préparation

{md_steps}

"""


def transform_all_recipes(cooklang_dir: Path, md_dir: Path) -> None:
    """walk through the `cooklang_dir` filesystem.
    - For every folder, create the corresponding one in `md_dir
    - For every cooklang file, create the corresponding markdown file
    """
    md_dir.mkdir(parents=True, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(cooklang_dir):
        # create output_dirpath
        print(f"{dirpath=}")
        output_dirpath = md_dir / (dirpath.removeprefix(str(cooklang_dir)).removeprefix("/"))
        dirpath = Path(dirpath)
        print(f"{output_dirpath=}")

        # For every folder, create the corresponding one in `md_dir
        for dirname in dirnames:
            (output_dirpath / dirname).mkdir(parents=True, exist_ok=True)

        # For every cooklang file, create the corresponding markdown files
        for filename in filenames:
            if filename.endswith(".cook"):
                output_filename = filename.removesuffix("cook") + "md"
                with (dirpath / filename).open() as f:
                    cooklang_content = f.read()
                md_content = transform(cooklang_content)
                print(output_dirpath)
                print(output_filename)
                with (output_dirpath / output_filename).open("w") as f:
                    f.write(md_content)


def transform(cooklang_code: str) -> str:
    """transform some cooklang code to hugo markdown code

    the cooklang code is structured like:
    - set of metadata
    - set of steps
    loop:
        - a metadata indicating the begining of optional steps
        - set of optional steps

    """
    cooklang_ast = run_lexer(cooklang_code)

    md_code = "---\n"

    # possible metadata at the begining of the document are:
    # - source
    # - servings
    # - time
    # - title
    # - tags
    block_id = 0
    while (block := cooklang_ast[block_id])["type"] == "metadata":
        md_code += f"{block['key']}: {block['value']}\n"
        block_id += 1
    md_code += "---"

    # process the first set of steps:
    md_steps, md_ingredients_list, md_cookwares_list, block_id_i = process_steps(cooklang_ast[block_id:])
    block_id += block_id_i

    # check for optional steps
    while (
        block_id < len(cooklang_ast)
        and (block := cooklang_ast[block_id])["type"] == "metadata"
        and block["key"] == "steps"
    ):
        block_id += 1
        md_steps_opt, md_ingredients_list_opt, md_cookwares_list_opt, block_id_i = process_steps(
            cooklang_ast[block_id:]
        )
        block_id += block_id_i
        if md_steps_opt:
            md_steps += f"\n{block['value']}\n{md_steps_opt}"
        if md_ingredients_list_opt:
            md_ingredients_list += f"\n{block['value']}\n{md_ingredients_list_opt}"
        if md_cookwares_list_opt:
            md_cookwares_list += f"\n{block['value']}\n{md_cookwares_list_opt}"

    return MARKDOWN_TEMPLATE.format(
        md_code=md_code,
        md_ingredients_list=md_ingredients_list,
        md_cookwares_list=md_cookwares_list,
        md_steps=md_steps,
    )


def process_steps(cooklang_ast: dict) -> tuple[list, list, list]:
    newline = True
    block_id = 0
    markdown_steps = ""
    markdown_ingredients_list = ""
    markdown_cookwares_list = ""
    while block_id < len(cooklang_ast) and (block := cooklang_ast[block_id])["type"] != "metadata":
        if block["type"] == "newline":
            if not newline:
                markdown_steps += "\n"
                newline = True
            block_id += 1
            continue
        if newline:
            newline = False
            markdown_steps += "* "
        if block["type"] == "ingredient":
            markdown_steps += f"{{{{< ingredient \"{block['name']}\" \"{block['quantity']} {block['units']}\" >}}}}"
            markdown_ingredients_list += f"* {block['name']} : {block['quantity']} {block['units']}\n"
        if block["type"] == "cookware":
            markdown_steps += f"{block['name']}"
            markdown_cookwares_list += f"* {block['name']}\n"
        if block["type"] == "timer":
            markdown_steps += f"{block['quantity']} {block['units']}"
        if block["type"] == "text":
            markdown_steps += block["value"]
        block_id += 1
    return markdown_steps, markdown_ingredients_list, markdown_cookwares_list, block_id
