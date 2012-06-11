# -*- coding: utf-8 -*-
"""
    products_from_icecat

    Creates the products from ICECAT product database

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) LTD
    :license: BSD, see LICENSE for more details.
"""
import logging
import random
from optparse import OptionParser
from celery.task import task

import requests
from lxml import etree
from cStringIO import StringIO


ICECAT_USERNAME = "sharoonthomas"
ICECAT_PASSWORD = "n5fxg6KNqWeOIkM"
PRODUCT_LIST_URL = "http://data.icecat.biz/export/level4/EN/daily.index.xml"

logging.basicConfig(level=logging.INFO)


def get_product_list_xml(filename=None):
    """
    Fetch the product list XML from the given url.

    :param filename: if provided, will read from file, else imports daily file 
    :return: Extracted product list element from file
    """
    if not filename:
        res = requests.get(
            PRODUCT_LIST_URL, auth=(ICECAT_USERNAME, ICECAT_PASSWORD)
        )
        tree = etree.parse(StringIO(res.content))
    else:
        tree = etree.parse(open(filename))

    root = tree.getroot()

    logging.info("Fetched the product XML file from Icecat DB.")

    return root.xpath('files.index/file')


def create_products_from_xml(filename):
    """
    Itearate over each product in the list of products.
    Fetch the detailed decsription of that product and call the method
    to create the product in backend

    """
    from trytond.pool import Pool

    static_folder_obj = Pool().get('nereid.static.folder')
    company_obj = Pool().get('company.company')

    products = get_product_list_xml(filename)
    company, = company_obj.search([], limit=1)

    logging.info("%d products to import" % len(products))

    folder_id = static_folder_obj.search([
            ('folder_name', '=', 'product')
    ])
    if not folder_id:
        with Transaction().new_cursor() as txn:
            folder_id = [static_folder_obj.create({
                'folder_name': 'product',
                'description': 'Product Images',
            })]
            txn.cursor.commit()

    folder_id, = folder_id

    for product in products:
        create_product.delay(product.get('Product_ID'), company)


def create_image(name, prod_id, url, size):
    """
    Creates a static file and returns the ID
    """
    from trytond.pool import Pool

    print name, url

    static_file_obj = Pool().get('nereid.static.file')
    static_folder_obj = Pool().get('nereid.static.folder')

    folder_id, = static_folder_obj.search([
        ('folder_name', '=', 'product')
    ])

    return static_file_obj.create({
        'name': name.replace('/', '-') + '-' + prod_id + '-%s' % size,
        'folder': folder_id,
        'type': 'remote',
        'remote_path': url
    })


@task(name="product_import.create_product")
def create_product(product_id, company):
    from trytond.transaction import Transaction

    prod_url = "http://data.icecat.biz/export/level4/INT/%s.xml" % product_id
    res = requests.get(prod_url, auth=(ICECAT_USERNAME, ICECAT_PASSWORD))
    try:
        tree = etree.parse(StringIO(res.content))
    except etree.XMLSyntaxError, e:
        return
    else:
        with Transaction().start('nereid', 1, None) as txn:
            # Commit for each product so that there are no long transactions
            with Transaction().set_context(company=company):
                _create_product(tree.getroot().xpath('Product')[0], company)
            txn.cursor.commit()


def _create_product(data, company):
    """Create the product in backend
    """
    from trytond.pool import Pool

    product_obj = Pool().get('product.product')
    category_obj = Pool().get('product.category')
    browse_node_obj = Pool().get('product.browse_node')
    uom_obj = Pool().get('product.uom')
    static_file_obj = Pool().get('nereid.static.file')
    image_set_obj = Pool().get('product.product.imageset')

    unit, = uom_obj.search([('name', '=', 'Unit')])

    if not all([
        data.get('Code') != '-1',
        data.get('HighPic'),
        data.get('LowPic'),
        data.get('ThumbPic'),
        ]):
        # The data quality is insufficient
        return

    browse_nodes = browse_node_obj.search([
        ('code', '=', data.xpath('Category')[0].get('ID'))
    ])
    if not browse_nodes:
        browse_nodes = [browse_node_obj.create({
            'name': data.xpath('Category/Name[@langid="1"]')[0].get('Value'),
            'code': data.xpath('Category')[0].get('ID')
        })]


    name = data.get('Name')
    prod_id = data.get('ID')

    #: Create a random price 
    price = random.choice(xrange(1, 1000))

    description = ""
    if data.xpath('ProductDescription[@LongDesc!=""]'):
        description += data.xpath(
            'ProductDescription[@LongDesc!=""]'
        )[0].get('LongDesc')
        description += "\n"
    for desc in data.xpath('ProductDescription[@ShortDesc!=""]'):
        description += "  * %s\n" % desc.get('ShortDesc')

    # Create the product only if it does not exist
    values = {
        'name': name,
        'code': prod_id,
        'default_uom': unit,
        'uri': product_obj.on_change_with_uri({
            'name': name
        }) + '-%s' % prod_id,
        'type': 'goods',

        'list_price': price,
        'cost_price': price * 0.90,

        'browse_nodes': [('set', browse_nodes)],
        'description': description
    }

    product_ids = product_obj.search([('code', '=', prod_id)])

    if not product_ids:
        product_id = product_obj.create(values)
        logging.info("Product with ID %s created in Tryton" % product_id)
    else:
        product_id = product_ids[0]
        product_obj.write(product_id, values)

    # Re browse the product
    product = product_obj.browse(product_id)

    if not product.image_sets:
        # Create images if they dont exist
        image_set_obj.create({
            'name': 'ICECat Images',
            'product': product_id,
            'thumbnail_image': create_image(
                name, prod_id, data.get('ThumbPic'), 'thumbnail'
            ),
            'medium_image': create_image(
                name, prod_id, data.get('LowPic'), 'medium'
            ),
            'large_image': create_image(
                name, prod_id, data.get('HighPic'), 'large'
            ),
        })
        logging.info("Created Images as there are no image sets")

    # Set the related products of the product into redis
    product_ice_ids = [
        p.get('ID') for p in data.xpath('ProductRelated/Product')
    ]
    existing_prod_ids = product_obj.search([
        ('code', 'in', product_ice_ids)
    ])
    existing_product_ice_ids = [
        p.code for p in product_obj.browse(existing_prod_ids)
    ]
    product_obj.write(
        product_id, {'cross_sells': [('set', existing_prod_ids)]}
    )

    for product_ice_id in set(product_ice_ids) - set(existing_product_ice_ids):
        create_product.delay(product_ice_id, company)

    del data


if __name__ == '__main__':
    usage="Usage: %prog [options] database"
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--config", dest="config", default=None)
    parser.add_option("-f", "--file", dest="filename", default=None)
    (options, args) = parser.parse_args()
    DATABASE = args[0]

    if options.config:
        from trytond.config import CONFIG
        CONFIG.update_etc(options.config)

    from trytond.modules import register_classes
    register_classes()

    from trytond.pool import Pool
    pool = Pool(DATABASE)
    pool.init()

    from trytond.transaction import Transaction
    with Transaction().start(DATABASE, 1, None) as txn:
        create_products_from_xml(options.filename)
        txn.cursor.commit()
