from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("master", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="gst",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
