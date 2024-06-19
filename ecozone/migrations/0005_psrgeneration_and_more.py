# Generated by Django 5.0.6 on 2024-06-19 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "ecozone",
            "0004_rename_ecozone_gr_name_f1196a_idx_ecozone_gri_name_ee4cf0_idx_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="PSRGeneration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start", models.DateTimeField()),
                (
                    "control_area",
                    models.CharField(
                        choices=[
                            ("10YDE-VE-------2", "50Hertz"),
                            ("10YDE-RWENET---I", "Amprion"),
                            ("10YDE-EON------1", "TenneT"),
                            ("10YDE-ENBW-----N", "TransnetBW"),
                        ],
                        max_length=16,
                        verbose_name="Control area",
                    ),
                ),
                (
                    "psr",
                    models.CharField(
                        choices=[
                            ("b01", "Biomasse"),
                            ("b02", "Braunkohle"),
                            ("b03", "Fossil Coal-derived gas"),
                            ("b04", "Erdgas"),
                            ("b05", "Steinkohle"),
                            ("b06", "Mineralöl"),
                            ("b07", "Fossil Oil shale"),
                            ("b08", "Fossil Peat"),
                            ("b09", "Geothermie"),
                            ("b10", "Pumpspeicher"),
                            ("b11", "Wasserkraft (Laufwasser)"),
                            ("b12", "Wasserspeicher"),
                            ("b13", "Marine"),
                            ("b14", "Kernenergie"),
                            ("b15", "Sonstige Erneuerbare Energien"),
                            ("b16", "Photovoltaik"),
                            ("b17", "Abfall"),
                            ("b18", "Windenergie (Offshore-Anlage)"),
                            ("b19", "Windenergie (Onshore-Anlage)"),
                            ("b20", "Sonstige konventionelle Energien"),
                        ],
                        max_length=3,
                        verbose_name="PSR type",
                    ),
                ),
                ("power_mw", models.FloatField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["start", "control_area", "psr"],
                        name="ecozone_psr_start_268810_idx",
                    ),
                    models.Index(
                        fields=["start", "psr"], name="ecozone_psr_start_646b83_idx"
                    ),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="psrgeneration",
            constraint=models.UniqueConstraint(
                fields=("start", "control_area", "psr"),
                name="unique_psr_generation_record",
            ),
        ),
    ]
