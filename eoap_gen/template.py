from jinja2 import Environment, PackageLoader, Template, select_autoescape


def get_template(name: str) -> Template:
    env = Environment(
        loader=PackageLoader("eoap_gen"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template(name)
