# Generated by Django 4.0.5 on 2022-06-30 20:54

import apps.core.models
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('subtitle', models.CharField(max_length=100, verbose_name='subtitle')),
                ('content', models.CharField(max_length=255, verbose_name='content')),
                ('image', models.ImageField(null=True, upload_to=apps.core.models.banner_image_path, verbose_name='image')),
                ('url', models.CharField(max_length=255, verbose_name='url')),
                ('sequence_order', models.IntegerField(default=1, verbose_name='sequence order')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'banner',
                'verbose_name_plural': 'banners',
                'ordering': ['sequence_order'],
            },
        ),
        migrations.CreateModel(
            name='BranchOffice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_branch_office_number, verbose_name='number')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='code')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('link_google_maps', models.CharField(blank=True, max_length=350, null=True, verbose_name='link google maps')),
                ('geo_location', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326, verbose_name='geo location')),
            ],
            options={
                'verbose_name': 'branch office',
                'verbose_name_plural': 'branch offices',
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_city_number, verbose_name='number')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
            ],
            options={
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='Coverage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='code')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('default', models.BooleanField(default=False, verbose_name='default')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'coverage',
                'verbose_name_plural': 'coverage',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalChangeRate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('valid_from', models.DateField(blank=True, verbose_name='valid_from')),
                ('valid_until', models.DateField(blank=True, verbose_name='valid_until')),
                ('rate', models.FloatField(default=0, verbose_name='rate')),
                ('last_sync_date', models.DateTimeField(blank=True, null=True, verbose_name='last sync date')),
            ],
            options={
                'verbose_name': 'historical change rate',
                'verbose_name_plural': 'historical change rates',
                'ordering': ['valid_from'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('last_sync_date', models.DateTimeField(blank=True, null=True, verbose_name='last sync date')),
            ],
            options={
                'verbose_name': 'location',
                'verbose_name_plural': 'locations',
                'ordering': ['description'],
            },
        ),
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('description', models.CharField(blank=True, db_index=True, max_length=255, unique=True, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'mark',
                'verbose_name_plural': 'marks',
            },
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'model',
                'verbose_name_plural': 'models',
            },
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_municipality_number, verbose_name='number')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
            ],
            options={
                'verbose_name': 'municipality',
                'verbose_name_plural': 'municipalities',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='code')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'plan',
                'verbose_name_plural': 'plans',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=None, null=True, verbose_name='number')),
                ('type', models.SmallIntegerField(choices=[(0, 'RCV')], default=0, verbose_name='type')),
                ('action', models.SmallIntegerField(choices=[(0, 'Nueva')], default=0, verbose_name='action')),
                ('due_date', models.DateTimeField(help_text='Fecha de vencimiento', null=True, verbose_name='due_date')),
                ('status', models.SmallIntegerField(choices=[(0, 'pendiente de pago'), (1, 'pendiente de aprobación'), (2, 'aprobado'), (3, 'vencido'), (4, 'rechazado')], default=0, verbose_name='status')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=50, verbose_name='total')),
                ('total_insured_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=50, verbose_name='total')),
                ('change_factor', models.DecimalField(decimal_places=2, default=0.0, max_digits=50, verbose_name='change factor')),
                ('qrcode', models.ImageField(null=True, upload_to=apps.core.models.qrcode_image_path, verbose_name='qrcode image')),
                ('file', models.FileField(null=True, upload_to=apps.core.models.file_policy_path, verbose_name='file policy pdf')),
            ],
            options={
                'verbose_name': 'policy',
                'verbose_name_plural': 'policies',
                'ordering': ['-number'],
            },
        ),
        migrations.CreateModel(
            name='PolicyCoverage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_policy_coverage_number, verbose_name='number')),
                ('insured_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=50, verbose_name='price')),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=50, verbose_name='cost')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
                'ordering': ['number'],
            },
        ),
        migrations.CreateModel(
            name='Premium',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('insured_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=50, verbose_name='price')),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=50, verbose_name='cost')),
            ],
            options={
                'verbose_name': 'premium',
                'verbose_name_plural': 'premiums',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('type', models.CharField(choices=[('box', 'Caja'), ('about', 'Sobre'), ('service', 'Servicio'), ('partner', 'Asociado')], default='box', max_length=10, verbose_name='type')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('subtitle', models.CharField(max_length=100, verbose_name='subtitle')),
                ('content', models.CharField(max_length=300, verbose_name='content')),
                ('image', models.ImageField(null=True, upload_to=apps.core.models.section_image_path, verbose_name='image')),
                ('shape', models.ImageField(null=True, upload_to=apps.core.models.section_shape_path, verbose_name='shape')),
                ('icon', models.ImageField(null=True, upload_to=apps.core.models.section_icon_path, verbose_name='icon')),
                ('url', models.CharField(max_length=255, verbose_name='url')),
                ('sequence_order', models.IntegerField(default=1, verbose_name='sequence order')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'banner',
                'verbose_name_plural': 'banners',
                'ordering': ['sequence_order'],
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_state_number, verbose_name='number')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
            ],
            options={
                'verbose_name': 'state',
                'verbose_name_plural': 'state',
            },
        ),
        migrations.CreateModel(
            name='Use',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='code')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'use',
                'verbose_name_plural': 'uses',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('serial_bodywork', models.CharField(blank=True, max_length=50, null=True, verbose_name='serial bodywork')),
                ('serial_engine', models.CharField(blank=True, max_length=50, null=True, verbose_name='serial engine')),
                ('license_plate', models.CharField(blank=True, max_length=50, null=True, verbose_name='license plate')),
                ('stalls', models.IntegerField(default=4, verbose_name='stalls')),
                ('color', models.CharField(blank=True, max_length=50, null=True, verbose_name='color')),
                ('year', models.CharField(blank=True, max_length=5, null=True)),
                ('transmission', models.SmallIntegerField(choices=[(1, 'Sincrónica'), (2, 'Automática')], default=1, verbose_name='transmission')),
                ('owner_name', models.CharField(blank=True, help_text='Nombre del dueño', max_length=100, null=True, verbose_name='owner name')),
                ('owner_last_name', models.CharField(blank=True, help_text='Apellido del dueño', max_length=100, null=True, verbose_name='owner lastname')),
                ('owner_identity_card', models.CharField(blank=True, help_text='Cedula del dueño', max_length=100, null=True, verbose_name='owner_identity_card')),
                ('owner_identity_card_image', models.ImageField(help_text='Cédula de identidad del dueño Imagen', null=True, upload_to=apps.core.models.owner_identity_card_image_path, verbose_name='owner identity card')),
                ('owner_license', models.ImageField(help_text='Licencia del dueño', null=True, upload_to=apps.core.models.owner_license_image_path, verbose_name='owner license')),
                ('owner_medical_certificate', models.ImageField(help_text='Certificado médico del dueño', null=True, upload_to=apps.core.models.owner_medical_certificate_image_path, verbose_name='owner medical certificate')),
                ('owner_circulation_card', models.ImageField(help_text='Carnet de circulación del dueño', null=True, upload_to=apps.core.models.owner_circulation_card_image_path, verbose_name='owner circulation card')),
                ('owner_phones', models.CharField(blank=True, help_text='Telefonos del dueño', max_length=100, null=True, verbose_name='owner phones')),
                ('owner_address', models.CharField(blank=True, help_text='Dirección del dueño', max_length=100, null=True, verbose_name='owner address')),
                ('owner_email', models.EmailField(blank=True, help_text='Correo del dueño', max_length=100, null=True, verbose_name='owner email')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.model', verbose_name='model')),
            ],
            options={
                'verbose_name': 'vehicle',
                'verbose_name_plural': 'vehicles',
            },
        ),
    ]
