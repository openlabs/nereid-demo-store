# -*- coding: utf-8 -*-
"""
    categories_from_icecat

    Creates the categories from ICECAT category database

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) LTD
    :license: BSD, see LICENSE for more details.
"""
import logging
from optparse import OptionParser

from lxml import etree

logging.basicConfig(level=logging.INFO)

def create_categories_from_file(filename):
    """
    This method must be called within the context of an open transaction

    :param filename: The full path to the file containing uncompressed XML
    :param pool: Initialised pool for the database
    """
    from trytond.pool import Pool
    category_obj = Pool().get('product.category')
    static_file_obj = Pool().get('nereid.static.file')
    static_folder_obj = Pool().get('nereid.static.folder')

    id_map = {}
    tree = etree.parse(filename)
    categories = tree.getroot().xpath('Response/CategoriesList/Category')
    logging.info("%d Categories to import" % len(categories))

    folder_id = static_folder_obj.create({
        'folder_name': 'category',
        'description': 'Product Category Images',
    })

    for category in categories:
        name_en = category.xpath('Name[@langid=1]')
        desc_en = category.xpath('Description[@langid=1]')
        data = {
            # Get the english name
            'name': name_en and name_en[0].get('Value') or 'Products',
            'description': desc_en and desc_en[0].get('Value') or '',

            # Enable later
            'displayed_on_eshop': False,

            # Fill the hierarchy only at a second pass
            'parent': False
        }
        id_map[category.get('ID')] = category_obj.create(data)

        if category.get('LowPic'):
            image_id = static_file_obj.create({
                'name': (name_en and name_en[0].get('Value').replace('/', '-') \
                    or 'Products') + '-' + category.get('ID'),
                'folder': folder_id,
                'type': 'remote',
                'remote_path': category.get('LowPic')
            })

            category_obj.write(
                id_map[category.get('ID')],
                {'image': image_id}
            )
    logging.info("%d Categories created without hierarchy" % len(id_map))

    logging.info("Setting up hierarchies")
    for category in categories:
        if category.get('ID') == '1':
            # its the root category
            continue
        parent_category = category.xpath('ParentCategory')
        if parent_category:
            category_obj.write(
                id_map[category.get('ID')],
                {'parent': id_map[parent_category[0].get('ID')]}
            )
    logging.info("Saved hierarchy")

    # Now create the hierarchies
    logging.info("Creating URIs for all categories")
    for cat_id, category_id in id_map.iteritems():
        try:
            category_obj.update_uri([category_id])
            category_obj.write(category_id, {'displayed_on_eshop': True})
        except Exception, exc:
            if 'UserError' in exc:
                logging.warning(
                    "Error on URI creation for Category ID:%s\n%s" % (cat_id, exc)
                )
            else:
                raise exc

    logging.info("URI creation completed")


if __name__ == '__main__':
    usage="Usage: %prog [options] database category_file"
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--config", dest="config", default=None)
    (options, args) = parser.parse_args()
    DATABASE, FILE = args

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
        create_categories_from_file(FILE)
        txn.cursor.commit()
