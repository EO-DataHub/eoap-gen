import click
import pyeodh


@click.command()
@click.option("--catalog")
@click.option("--collection")
def main(catalog, collection):
    if not catalog or not collection:
        return

    client = pyeodh.Client()
    collection = (
        client.get_catalog_service().get_catalog(catalog).get_collection(collection)
    )

    urls = []
    ids = []

    for item in collection.get_items():
        cog = item.assets.get("cog")
        if cog is not None:
            urls.append(cog.href)
            ids.append(item.id)

    with open("urls.txt", "w") as f:
        print(*urls, file=f, sep="\n", end="")
    with open("ids.txt", "w") as f:
        print(*ids, file=f, sep="\n", end="")


if __name__ == "__main__":
    main()
