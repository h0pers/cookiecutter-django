from django.db import migrations


def create_homepage(apps, schema_editor):
    content_type_model = apps.get_model("contenttypes", "ContentType")
    page_model = apps.get_model("wagtailcore", "Page")
    site_model = apps.get_model("wagtailcore", "Site")
    home_page_model = apps.get_model("cms", "HomePage")

    # wagtailcore.0002_initial_data creates a placeholder "Welcome" page and a
    # Site for it; deleting the page removes the Site too
    page_content_type = content_type_model.objects.get(
        app_label="wagtailcore",
        model="page",
    )
    page_model.objects.filter(
        content_type=page_content_type,
        slug="home",
        depth=2,
    ).delete()

    home_page_content_type, _ = content_type_model.objects.get_or_create(
        app_label="cms",
        model="homepage",
    )
    home_page = home_page_model.objects.create(
        title="Home",
        draft_title="Home",
        slug="home",
        content_type=home_page_content_type,
        path="00010001",
        depth=2,
        numchild=0,
        url_path="/home/",
    )
    site_model.objects.create(
        hostname="localhost",
        root_page=home_page,
        is_default_site=True,
    )


def remove_homepage(apps, schema_editor):
    content_type_model = apps.get_model("contenttypes", "ContentType")
    home_page_model = apps.get_model("cms", "HomePage")

    # The Site goes with the page (on_delete=CASCADE)
    home_page_model.objects.filter(slug="home", depth=2).delete()
    content_type_model.objects.filter(app_label="cms", model="homepage").delete()


class Migration(migrations.Migration):
    # Runs on the pre-locale Page schema, the way Wagtail's project template does;
    # wagtailcore.0053 then assigns the default locale
    run_before = [
        ("wagtailcore", "0053_locale_model"),
    ]

    dependencies = [
        ("cms", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_homepage, remove_homepage),
    ]
