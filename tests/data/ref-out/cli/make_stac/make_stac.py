import datetime
import os
import shutil
from pathlib import Path

import click
import pystac
import pystac.utils


@click.command()
@click.argument("files", nargs=-1)
def main(files):
    catalog = pystac.Catalog(id="catalog", description="Root catalog")
    for path in files:
        name = Path(path).stem
        os.mkdir(name)
        f_copy = shutil.copy(path, f"{name}/")
        item = pystac.Item(
            id=name,
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [[-180, -90], [-180, 90], [180, 90], [180, -90], [-180, -90]]
                ],
            },
            bbox=None,
            datetime=datetime.datetime.now(),
            properties={
                "created": pystac.utils.datetime_to_str(datetime.datetime.now()),
                "updated": pystac.utils.datetime_to_str(datetime.datetime.now()),
            },
            extra_fields={"bbox": [-180, -90, 180, 90]},
        )
        item.add_asset(
            name,
            pystac.Asset(
                href=os.path.basename(f_copy),
                media_type=pystac.MediaType.GEOTIFF,
                roles=["data"],
                extra_fields={"file:size": os.path.getsize(f_copy)},
            ),
        )
        catalog.add_item(item)
    catalog.normalize_and_save(
        root_href="./", catalog_type=pystac.CatalogType.SELF_CONTAINED
    )


if __name__ == "__main__":
    main()
