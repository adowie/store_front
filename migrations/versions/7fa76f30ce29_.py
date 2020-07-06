"""empty message

Revision ID: 7fa76f30ce29
Revises: 
Create Date: 2020-07-06 03:25:14.547123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fa76f30ce29'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('image', sa.String(length=1024), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_category_name'), 'category', ['name'], unique=False)
    op.create_table('company_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('image', sa.String(length=100), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_type_name'), 'company_type', ['name'], unique=True)
    op.create_table('discount',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(length=264), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discount_name'), 'discount', ['name'], unique=False)
    op.create_index(op.f('ix_discount_reason'), 'discount', ['reason'], unique=False)
    op.create_table('payment_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=254), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_type_description'), 'payment_type', ['description'], unique=True)
    op.create_index(op.f('ix_payment_type_name'), 'payment_type', ['name'], unique=True)
    op.create_table('plan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('cost', sa.Float(), nullable=True),
    sa.Column('details', sa.String(length=1024), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plan_name'), 'plan', ['name'], unique=True)
    op.create_table('product_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_type_name'), 'product_type', ['name'], unique=True)
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=True)
    op.create_table('subscriber',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriber_email'), 'subscriber', ['email'], unique=True)
    op.create_table('uom',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('uom', sa.Float(), nullable=True),
    sa.Column('base', sa.Integer(), nullable=True),
    sa.Column('conversion', sa.Float(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_uom_name'), 'uom', ['name'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=True),
    sa.Column('fullname', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_', sa.String(length=220), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('image', sa.String(length=224), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('is_logged_in', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_fullname'), 'user', ['fullname'], unique=False)
    op.create_index(op.f('ix_user_password_'), 'user', ['password_'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    op.create_table('view',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('access',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('view_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['view_id'], ['view.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('logo', sa.String(length=254), nullable=True),
    sa.Column('store_front_image', sa.String(length=254), nullable=True),
    sa.Column('tax', sa.Float(), nullable=True),
    sa.Column('location', sa.String(length=1024), nullable=True),
    sa.Column('contact', sa.String(length=11), nullable=True),
    sa.Column('thank_note', sa.String(length=250), nullable=True),
    sa.Column('active', sa.Integer(), nullable=True),
    sa.Column('closed', sa.Integer(), nullable=True),
    sa.Column('published', sa.Integer(), nullable=True),
    sa.Column('paused', sa.Integer(), nullable=True),
    sa.Column('twitter', sa.String(length=250), nullable=True),
    sa.Column('google', sa.String(length=250), nullable=True),
    sa.Column('instagram', sa.String(length=250), nullable=True),
    sa.Column('facebook', sa.String(length=250), nullable=True),
    sa.Column('order_hold_limit', sa.Integer(), nullable=True),
    sa.Column('coords', sa.String(length=30), nullable=True),
    sa.Column('plan_id', sa.Integer(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('company_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_type_id'], ['company_type.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_email'), 'company', ['email'], unique=False)
    op.create_index(op.f('ix_company_name'), 'company', ['name'], unique=True)
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('type_', sa.String(length=15), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Float(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('params', sa.Text(), nullable=True),
    sa.Column('sent', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_name'), 'notification', ['name'], unique=False)
    op.create_index(op.f('ix_notification_type_'), 'notification', ['type_'], unique=False)
    op.create_table('companies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('customer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('customer_type', sa.String(length=254), nullable=True),
    sa.Column('company_name', sa.String(length=254), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('last_business', sa.DateTime(), nullable=True),
    sa.Column('street', sa.String(length=254), nullable=True),
    sa.Column('street2', sa.String(length=254), nullable=True),
    sa.Column('city', sa.String(length=254), nullable=True),
    sa.Column('zip_code', sa.String(length=254), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('contact', sa.String(length=100), nullable=True),
    sa.Column('barcode', sa.String(length=254), nullable=True),
    sa.Column('credit_limit', sa.Float(), nullable=True),
    sa.Column('tax_id', sa.String(length=50), nullable=True),
    sa.Column('avatar', sa.String(length=324), nullable=True),
    sa.Column('default_', sa.Boolean(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['email'], ['user.email'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_company_name'), 'customer', ['company_name'], unique=False)
    op.create_index(op.f('ix_customer_customer_type'), 'customer', ['customer_type'], unique=False)
    op.create_index(op.f('ix_customer_name'), 'customer', ['name'], unique=False)
    op.create_table('pos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pos_', sa.String(length=32), nullable=True),
    sa.Column('created_date', sa.Date(), nullable=True),
    sa.Column('progress', sa.String(length=20), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('pos_')
    )
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_code', sa.String(length=20), nullable=True),
    sa.Column('barcode', sa.String(length=254), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=84), nullable=True),
    sa.Column('description', sa.String(length=254), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('cost', sa.Float(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('qty', sa.Float(), nullable=True),
    sa.Column('taxable', sa.Boolean(), nullable=True),
    sa.Column('image', sa.String(length=1024), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_barcode'), 'product', ['barcode'], unique=False)
    op.create_index(op.f('ix_product_item_code'), 'product', ['item_code'], unique=False)
    op.create_table('session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_', sa.String(length=32), nullable=True),
    sa.Column('created_date', sa.Date(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_session_'), 'session', ['session_'], unique=False)
    op.create_table('vline',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('created_date', sa.Date(), nullable=True),
    sa.Column('serving', sa.Integer(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vline_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vline', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('created_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('category_product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('favourite_company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('favourite_product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('order_date', sa.DateTime(), nullable=True),
    sa.Column('tax_amount', sa.Float(), nullable=True),
    sa.Column('disc_amount', sa.Float(), nullable=True),
    sa.Column('sub_total', sa.Float(), nullable=True),
    sa.Column('total', sa.Float(), nullable=True),
    sa.Column('amount_due', sa.Float(), nullable=True),
    sa.Column('filter_state', sa.String(length=164), nullable=True),
    sa.Column('prints', sa.Integer(), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('barcode', sa.String(length=254), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('pos_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.ForeignKeyConstraint(['pos_id'], ['pos.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_barcode'), 'order', ['barcode'], unique=True)
    op.create_index(op.f('ix_order_name'), 'order', ['name'], unique=False)
    op.create_table('product_photo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('image', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_prices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_code', sa.String(length=254), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['item_code'], ['product.item_code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('uom_shedule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uom_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.ForeignKeyConstraint(['uom_id'], ['uom.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('variation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('qty', sa.Float(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_variation_name'), 'variation', ['name'], unique=False)
    op.create_table('vlineup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('line_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('joined', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('place_in_line', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['line_id'], ['vline.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_line',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('qty', sa.Float(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('tax', sa.Float(), nullable=True),
    sa.Column('extended', sa.Float(), nullable=True),
    sa.Column('orderline_date', sa.DateTime(), nullable=True),
    sa.Column('voided', sa.Boolean(), nullable=True),
    sa.Column('discount', sa.Float(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.item_code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pos_id', sa.String(length=64), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('amount_due', sa.Float(), nullable=True),
    sa.Column('amount_tended', sa.Float(), nullable=True),
    sa.Column('change', sa.Float(), nullable=True),
    sa.Column('voided', sa.Boolean(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('payment_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['payment_type_id'], ['payment_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_name'), 'payment', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payment_name'), table_name='payment')
    op.drop_table('payment')
    op.drop_table('order_line')
    op.drop_table('vlineup')
    op.drop_index(op.f('ix_variation_name'), table_name='variation')
    op.drop_table('variation')
    op.drop_table('uom_shedule')
    op.drop_table('product_prices')
    op.drop_table('product_photo')
    op.drop_index(op.f('ix_order_name'), table_name='order')
    op.drop_index(op.f('ix_order_barcode'), table_name='order')
    op.drop_table('order')
    op.drop_table('favourite_product')
    op.drop_table('favourite_company')
    op.drop_table('category_product')
    op.drop_table('vline_history')
    op.drop_table('vline')
    op.drop_index(op.f('ix_session_session_'), table_name='session')
    op.drop_table('session')
    op.drop_index(op.f('ix_product_item_code'), table_name='product')
    op.drop_index(op.f('ix_product_barcode'), table_name='product')
    op.drop_table('product')
    op.drop_table('pos')
    op.drop_index(op.f('ix_customer_name'), table_name='customer')
    op.drop_index(op.f('ix_customer_customer_type'), table_name='customer')
    op.drop_index(op.f('ix_customer_company_name'), table_name='customer')
    op.drop_table('customer')
    op.drop_table('company_category')
    op.drop_table('companies')
    op.drop_index(op.f('ix_notification_type_'), table_name='notification')
    op.drop_index(op.f('ix_notification_name'), table_name='notification')
    op.drop_table('notification')
    op.drop_index(op.f('ix_company_name'), table_name='company')
    op.drop_index(op.f('ix_company_email'), table_name='company')
    op.drop_table('company')
    op.drop_table('access')
    op.drop_table('view')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_password_'), table_name='user')
    op.drop_index(op.f('ix_user_fullname'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_uom_name'), table_name='uom')
    op.drop_table('uom')
    op.drop_index(op.f('ix_subscriber_email'), table_name='subscriber')
    op.drop_table('subscriber')
    op.drop_index(op.f('ix_role_name'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_product_type_name'), table_name='product_type')
    op.drop_table('product_type')
    op.drop_index(op.f('ix_plan_name'), table_name='plan')
    op.drop_table('plan')
    op.drop_index(op.f('ix_payment_type_name'), table_name='payment_type')
    op.drop_index(op.f('ix_payment_type_description'), table_name='payment_type')
    op.drop_table('payment_type')
    op.drop_index(op.f('ix_discount_reason'), table_name='discount')
    op.drop_index(op.f('ix_discount_name'), table_name='discount')
    op.drop_table('discount')
    op.drop_index(op.f('ix_company_type_name'), table_name='company_type')
    op.drop_table('company_type')
    op.drop_index(op.f('ix_category_name'), table_name='category')
    op.drop_table('category')
    # ### end Alembic commands ###
