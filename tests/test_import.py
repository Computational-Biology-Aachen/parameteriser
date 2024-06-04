def test_import() -> None:
    import parameteriser  # noqa: F401
    from parameteriser import (
        blast_sequence_against_others,  # noqa: F401
        brenda,  # noqa: F401
        estimate_mean_std,  # noqa: F401
        plot_parameter_distribution,  # noqa: F401
        plot_parameter_distributions,  # noqa: F401
        print_organisms,  # noqa: F401
        print_table,  # noqa: F401
        select_organism,  # noqa: F401
        select_substrate,  # noqa: F401
    )

    assert True
