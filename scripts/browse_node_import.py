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

def create_browse_nodes_from_file(filename):
    """
    This method must be called within the context of an open transaction

    :param filename: The full path to the file containing uncompressed XML
    :param pool: Initialised pool for the database
    """
    from trytond.pool import Pool
    browse_node_obj = Pool().get('product.browse_node')
    static_file_obj = Pool().get('nereid.static.file')
    static_folder_obj = Pool().get('nereid.static.folder')

    # Disable the left and right so that MPTT doesnt kick in
    browse_node_obj.parent.left = None
    browse_node_obj.parent.right = None

    id_map = {}
    tree = etree.parse(filename)
    browse_nodes = tree.getroot().xpath('Response/CategoriesList/Category')
    logging.info("%d Categories to import" % len(browse_nodes))

    folder_id = static_folder_obj.create({
        'folder_name': 'browsenodes',
        'description': 'Browse Nodes Images',
    })

    for browse_node in browse_nodes:
        name_en = browse_node.xpath('Name[@langid=1]')
        desc_en = browse_node.xpath('Description[@langid=1]')
        data = {
            # Get the english name
            'name': name_en and name_en[0].get('Value') or 'Products',
            'code': browse_node.get('ID'),
            'description': desc_en and desc_en[0].get('Value') or '',

            # Fill the hierarchy only at a second pass
            'parent': False
        }
        id_map[browse_node.get('ID')] = browse_node_obj.create(data)

    logging.info("%d Categories created without hierarchy" % len(id_map))

    logging.info("Setting up hierarchies")
    for category in browse_nodes:
        if category.get('ID') == '1':
            # its the root category
            continue
        parent_category = category.xpath('ParentCategory')
        if parent_category:
            browse_node_obj.write(
                id_map[category.get('ID')],
                {'parent': id_map[parent_category[0].get('ID')]}
            )
    logging.info("Saved hierarchy")

    # Now create the hierarchies
    logging.info("Creating URIs for all categories")
    for cat_id, category_id in id_map.iteritems():
        try:
            browse_node_obj.update_uri([category_id])
            browse_node_obj.write(category_id, {'displayed_on_eshop': True})
        except Exception, exc:
            if 'UserError' in exc:
                logging.warning(
                    "Error on URI creation for Category ID:%s\n%s" % (cat_id, exc)
                )
            else:
                raise exc

    logging.info("Lick in the MPTT")
    # Kick the mptt back in
    browse_node_obj.parent.left = "left"
    browse_node_obj.parent.right = "right"
    # Something to trigger rewrite of mptt
    browse_node_obj.write(category_id, {'displayed_on_eshop': True})

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
        create_browse_nodes_from_file(FILE)
        txn.cursor.commit()

