from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    admin = User.objects.filter(username="admin").first()
    if admin is None:
        admin = User(username="admin", is_staff=True, is_superuser=True)
    else:
        admin.is_staff = True
        admin.is_superuser = True
    admin.password = make_password("1234@")
    admin.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_alter_user_nickname"),
    ]

    operations = [
        migrations.RunPython(create_admin, noop),
    ]
