import filecmp
from pathlib import Path

from click.testing import CliRunner

from eoap_gen.cli import generate


def test_generate_output() -> None:
    """
    Test the generate function and compare its output with a reference directory.
    """

    runner = CliRunner()
    reference_output_path = Path("tests/data/ref-out")

    config_path = Path("tests/data/config.yml")
    output_path = Path("tests/output")
    docker_url_base = "ghcr.io/figi44/eoap"
    docker_tag = "main"

    # Generate output
    result = runner.invoke(
        generate,
        [
            "--config",
            config_path,
            "--output",
            output_path,
            "--docker-url-base",
            docker_url_base,
            "--docker-tag",
            docker_tag,
        ],
    )

    diff_files = []
    test_files = [
        "cli/workflow-packed.cwl",
        "cli/get_urls/get_urls.Dockerfile",
        "cli/make_stac/make_stac.Dockerfile",
    ]

    for test_file in test_files:
        if not filecmp.cmp(output_path / test_file, reference_output_path / test_file):
            diff_files.append(test_file)

    assert result.exit_code == 0
    assert not diff_files, f"The following files differ: {', '.join(diff_files)}"
