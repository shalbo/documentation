=========================
Linking existing listings
=========================

Turn off eBay scheduled actions
===============================

To start linking existing listings in eBay, first turn off the eBay notifications in the scheduled
actions in Odoo. The :guilabel:`Scheduled Actions` can be accessed by first activating
:doc:`../../../general/developer_mode` and go to :menuselection:`Settings --> Technical
--> Automation --> Scheduled Actions`.

By turning off the following scheduled actions this will allow users to sync and validate eBay data
before orders come in.

- :guilabel:`eBay: get new orders`: eBay will push all new orders not already in Odoo (based on
  client_order_reference, or sales order reference field), and will update orders if there has been
  a change from eBay. Orders will be put in draft mode. Customers will be created if they are not
  already in Odoo.
- :guilabel:`eBay: synchronize stock`: eBay will display the stock on hand in Odoo.
- :guilabel:`eBay: update categories`: eBay will push updated monthly categories (only up to fourth
  layer, will need to manually update the rest).

Sync eBay categories
--------------------

Navigate to :menuselection:`Settings --> Technical --> Automation --> Scheduled Actions`. Click into
the scheduled action labeled: `Ebay: update categories` and then click :guilabel:`Run Manually`.
This action will populate the :menuselection:`Sales --> Configuration --> eBay Categories` menu item
with all standard eBay product categories. Odoo only recognizes eBay category paths up to four
layers deep. If a product has a listing of more than four, the category field will only populate up
to the fourth layer.

Users can import the remaining product categories into the eBay product categories manually using
using the :guilabel:`Action` menu and :guilabel:`Import` feature. A template of additional product
categories is forthcoming.

Link eBay listings
==================

Manual listing link
-------------------

Go to the product in Odoo, click :guilabel:`link to listing`, enter in listing ID from eBay in the
pop up (the listing ID is in the eBay product URL). An example URL would be as such:
`www.ebay.com/itm/272222656444?hash=item3f61bc17bb:g:vJ0AAOSwslJizv8u`. Once the listing ID has been
entered the eBay listing information will sync into Odoo.

Automated listing link (technical)
----------------------------------

To automate the listing link, first, manually import the URL to product.template. Then add the
existing field `Use eBay` to a product.template menu. Select all products that need to be listed,
and mass edit /  update the checkbox to TRUE. Following this step, create a text field to populate
the listing ID on the product.template : `x_studio_listingid`.

Now, mass update `x_studio_listingid` with the product.template ID. Next, write the server action:
`sync listing` run method on the selected products where the listing_id (transient)=
`x_studio_listingid`. Finally verify the listing data is pushed into Odoo product.template.

.. note::
   If an order comes in and the listing from the order is not linked to a product, eBay will create
   a consumable product.product in its place. These consumables should be altered on the Sales Order
   while in draft state to represent a storable product, and then the user can link to the listing
   as they come in.

Turn on eBay scheduled Actions
==============================

The next step will be to turn on the eBay notifications in the scheduled actions in Odoo. The
:guilabel:`Scheduled Actions` can be accessed by first activating
:doc:`../../../general/developer_mode` and go to :menuselection:`Settings --> Technical
--> Automation --> Scheduled Actions`.

By turning on the following scheduled actions this will allow users to sync and validate eBay data
automatically.

- :guilabel:`eBay: get new orders`: eBay will push all new orders not already in Odoo (based on
  client_order_reference, or sales order reference field), and will update orders if there has been
  a change from eBay. Orders will be put in draft mode. Customers will be created if they are not
  already in Odoo.
- :guilabel:`eBay: synchronize stock`: eBay will display the stock on hand in Odoo.
- :guilabel:`eBay: update categories`: eBay will push updated monthly categories (only up to fourth
  layer, will need to manually update the rest).
