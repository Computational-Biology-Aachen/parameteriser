from pathlib import Path

import tomllib
import yaml


def format_dependencies(k: str, v: str) -> str:
    if v.startswith(("=", ">")):
        return f"{k} {v}"
    return f"{k} ={v}"


if __name__ == "__main__":
    pyproject_path = Path("pyproject.toml")
    recipe_path = Path("rattler") / "recipe.yaml"

    with pyproject_path.open("rb") as br:
        pyproject = tomllib.load(br)

    with recipe_path.open(encoding="utf-8") as tw:
        recipe = yaml.safe_load(tw)

    recipe["context"]["name"] = pyproject["project"]["name"]
    recipe["context"]["version"] = pyproject["project"]["version"]
    recipe["context"]["description"] = pyproject["project"]["description"]
    recipe["context"]["source_url"] = pyproject["project"]["urls"]["Repository"]

    recipe["requirements"]["run"] = [
        format_dependencies(k, v)
        for k, v in (
            pyproject["tool"]["pixi"].get("dependencies", {})
            | pyproject["tool"]["pixi"].get("pypi-dependencies", {})
        ).items()
    ]

    with recipe_path.open("w", encoding="utf-8") as tw:
        yaml.dump(recipe, tw)
