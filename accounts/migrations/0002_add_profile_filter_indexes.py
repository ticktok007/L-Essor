# accounts/migrations/0002_add_profile_filter_indexes.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["role"], name="auth_user_role_btree_idx"),
        ),
        migrations.AddIndex(
            model_name="profile",
            index=models.Index(
                fields=["department"],
                name="accounts_profile_department_btree_idx",
            ),
        ),
    ]
