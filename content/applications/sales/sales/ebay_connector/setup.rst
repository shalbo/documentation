=========================
Odoo-eBay connector setup
=========================

Overview
========

Odoo's eBay connector allows eBay listings to connect with Odoo products. Once connected, updates to
the listings can be made in Odoo or in eBay. When an item sells on eBay, draft Sale Orders are
created in Odoo for the user to review and confirm. Once the Sale Order is confirmed, Odoo
*Inventory* and *Sales* apps function standard to pull products out of inventory, and allow the user
to create invoices.

eBay - Odoo linked fields
-------------------------

- eBay URL
- eBay status
- Quantity sold
- Start date
- Title
- Subtitle
- Item condition
- Category
- Category 2
- Store category
- Store category 2
- Payment policy
- Seller profiles
- Postal code
- Shipping policy
- Listing type (fixed price or auction)

  - Starting price for Auction
  - Buy it now price
  - Fixed Price amount

- Use stock quantity
- Quantity on eBay
- Duration
- Allow best offer
- Private listing
- eBay description
- eBay product image
- Country

eBay terms
----------

**Variations** group multiple products into one, with variation options. Variations can sync to
Odoo's attributes and values. Variations will appear in drop down menus near the top of the page
when viewing an eBay listing.

.. image:: setup/ebay-variation.png
  :align: center
  :alt: An example on eBay of the variations that can be added to a product.

**Item specifics** are found towards the bottom of the listing and list item-specific detail related
to individual products. Item specifics cannot sync to Odoo out of the box; a development will be
needed to link these fields.

.. image:: setup/item-specifics.png
  :align: center
  :alt: Item specifics listed on an eBay product.

**Sandbox** and **Production** are terms that are used to categorize the eBay environments as either
still in development/testing (**Sandbox**) OR for use in the the real-instance of the database with
real customer information/dataset (**Production**). It is recommended to start first in the
**Sandbox** to test, and then following the processes below, create a **Production** instance.

.. seealso::
   eBay's sandbox environment can be accessed by navigating to `eBay's sandbox portal
   <https://sandbox.ebay.com/>`_ at `https://sandbox.ebay.com/`. eBay production can be accessed by
   navigating to `eBay.com portal <https://www.ebay.com/>`_ or `https://www.ebay.com/`.

.. important::
   The environment selection should remain the same for all environment settings on eBay and on
   Odoo throughout this setup.

eBay actions available on Odoo
------------------------------

- **List**: Users can create a new listing with an Odoo product.
- **Revise item button**: Users can make changes to an eBay listing in Odoo, then save the record
  and click :guilabel:`Revise Item` which will update the eBay listing.
- **Relist**: If an item's listing was ended early or :guilabel:`auto-relist` was not selected, a
  user can relist the item from Odoo. The start date will reset.
- **End item's listing button**: Users can end a listing from Odoo.
- **Unlink product listings**: Users can unlink a product from the eBay listing, the listing will
  stay intact on eBay.

Setup required on Odoo prior to eBay setup
==========================================

To start the eBay module(s) need to be install on the database. To install the eBay module(s)
navigate to the Odoo dashboard and click into the :guilabel:`Apps` application. Search the term
`eBay` and install any modules listed that aren't already installed. The primary module is called
`eBay Connector` and there also may be a module called `eBay Connector - Account Deletion`. In later
versions of Odoo this last module was incorporated into the first module listed.

The following items must be configured before eBay is set up:

- Products need to be configured. eBay does not bring in new products into Odoo. All products must
  first be created in Odoo, and then linked to listings.

  - Odoo does not allow multiple eBay listings to be linked per product in Odoo. If you sell the
    same product for multiple listings, follow these instructions:

    - Set up one “base” product (noted in green in the image below) from which all eBay listings
      will pull from. This will be a storable product so stock can be kept. Highlighted in green
      below, this product will be included in the kit on each subsequent “linked” product below.

    - Set up 2+ “linked” products (noted in yellow in the image below), one for each eBay listing.
      The product type will be determined by your accounting settings, as explained in the Odoo
      documentation. Highlighted in yellow below, each product should have a BoM of type = Kit and
      have the “base” product as a component of the kit. When this linked eBay product is sold, the
      delivery order created will have the base product listed in lieu of the linked product.

    .. image:: setup/products-odoo.png
      :align: center
      :alt: Setting up bill of materials with base product and linked products.

- eBay does not automatically create invoices for eBay orders that get pushed into Odoo. Set
  invoicing policy on eBay products: invoicing policy will dictate when the product can be invoiced.
  Since most eBay users collect payment before the product is shipped, “invoice on ordered” will
  allow users to mass create invoices for eBay orders every day.
- Set default outgoing shipment route for the warehouse to be 1 step. See warning below. This has
  been identified as a bug and might be fixed at a later date.

  .. warning::
     Default outgoing shipment routes set to 2-step or 3-step: If there is an additional pick step
     turned on for outgoing shipments, eBay will mark orders as delivered when the pick is
     confirmed, not when the final delivery order is confirmed. This will prevent tracking numbers
     from being input onto the delivery order.
- If the Accounting/Invoicing apps are installed, practice registering payment and reconciling
  invoices created from eBay orders with incoming eBay money.

- Generate a marketplace account deletion/closure notification token. Navigate to
  :menuselection:`Sales app --> Settings --> eBay` to start. Change the mode to
  :guilabel:`Production`, and input random text values for the :guilabel:`Production App Key` and
  for the :guilabel:`Production Cert Key`. Then click on :guilabel:`Generate Token` under the
  :guilabel:`eBay Marketplace Account Deletion/Closure Notifications` section. This token will be
  used during the setup on eBay for the deletion/closure notifications configuration.

.. image:: setup/generate-token.png
   :align: center
   :alt: Generate a verification token in Odoo.

Set up on eBay
==============

Set up eBay developer account
-----------------------------

To start, create an eBay developer account via `eBay's developer portal
<https://go.developer.ebay.com/>`_. This site requires a different login and password than the eBay
account, though the same email address can be used to register. The verification to create a
developer account is around 24 hours.

Set up eBay keyset
------------------

Once the eBay developer account is created, an application will need to be set up. To set up an
application, start on `eBay's developer portal <https://go.developer.ebay.com/>`_ and navigate to
the `Hi [username]` at top right of screen, then click on :guilabel:`Application Keysets`. A screen
will appear with the prompt to :guilabel:`Enter Application Title`. This title can be no more than
fifty characters. Enter the application name, then choose the appropriate environment (Sandbox or
Production) and generate the first keyset. This application name will not be saved until the keyset
is generated. Click on :guilabel:`Create a keyset` to generate the keyset.

.. warning::
   Once a Production Keyset is created, the keyset will be disabled. By default, the keyset will
   been disabled, they can be activated by subscribing to the eBay Marketplace account deletion or
   closure notifications or by applying to eBay for an exemption. On enabling, the database can make
   5000 calls per day with this keyset.

.. image:: setup/disabled-keyset.png
   :align: center
   :alt: Disabled keyset present after creating a keyset.

Configure account deletion / notification settings (Production)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Navigate back to the `eBay developer portal <https://go.developer.ebay.com/>`_. Configure the
account deletion / notification settings in eBay by navigating to the `Hi [username]` at top right
of screen, then :guilabel:`Application Keysets`.

Following the link to comply with the account deletion / closure notification setting by clicking on
:guilabel:`marketplace deletion/account closure` under the :guilabel:`Production` keyset column.
Enter an email under :guilabel:`Email to notify if marketplace account deletion notification
endpoint is down`. Click :guilabel:`Save` to enable the email.

Following this action, enter the URL from Odoo (:guilabel:`Marketplace account deletion
notification endpoint`). Lastly, paste the Verification Token from Odoo. Click :guilabel:`Save` to
enable the :guilabel:`Event Notification Delivery Method`.

.. tip::
   The two Odoo values can be gathered by navigating to :menuselection:`Sales app --> Settings -->
   eBay --> eBay Marketplace Account Deletion/Closure Notifications` section.

.. image:: setup/account-closure.png
   :align: center
   :alt: Configuring account deletion / notification settings in eBay.

Click :guilabel:`Send Test Notification` to test the new notifications. A test result will post,
proceed to the next step when the green check mark reveals itself, or revisit the above settings
again to reconfigure the notifications.

This will enable the ability to create Production Keysets which are needed in the Odoo
configuration. Navigate back to the :menuselection:`Application Keys` page generate a production
keyset.

Creating the keyset
~~~~~~~~~~~~~~~~~~~

A successful setup of the notifications will enable the ability to create Production Keysets which
are needed in the remainder of the Odoo configuration. Navigate back to the
:menuselection:`Application Keys` page generate a production keyset.

The administrator will be prompted to :menuselection:`Confirm the Primary Contact`. Enter or confirm
the account owner (the person legally responsible for the eBay API License Agreement). Fill out
:guilabel:`First Name`, :guilabel:`Last Name`, :guilabel:`Email`, :guilabel:`Phone` and click either
the radio button for :guilabel:`Individual` or :guilabel:`Business`.

.. note::
   The email address or phone number provided does not have to be the same email or phone as the
   account email or phone. eBay will use this information to contact the business or individual if
   there are issues with user tokens. Other contacts can be added from the :menuselection:`Profile &
   Contacts` page on eBay.

Click on :guilabel:`Continue to Create Keys` to confirm the primary contact. The
:menuselection:`Application Keys` will populate in a new screen and an email will also be sent to
the developer account. A :guilabel:`App ID (Client ID)`, :guilabel:`Dev ID`, and :guilabel:`Cert ID
(Client Secret)` will all populate.

.. image:: setup/application-keys.png
   :align: center
   :alt: Application keys are populated after creating the app in eBay.

Copy these values down as they will be input into Odoo later in the process.

Create eBay user token
----------------------

Now, create a *User Token* in eBay by navigating to the `Hi [username]` at top right of screen,
then :guilabel:`User Access Tokens`.

.. image:: setup/user-tokens.png
   :align: center
   :alt: Generate user tokens on the eBay developer console.

Ensure the :guilabel:`Environment` is selected correctly. It can either be :guilabel:`Sandbox` for
testing, or :guilabel:`Production` to use in the live instance of the database. This selection
should remain the same for all environment settings on eBay and on Odoo.

Finally select the radio button labeled :guilabel:`Auth'n'Auth`

Click :guilabel:`Sign in to Production` or :guilabel:`Sign in to Sandbox` to get a user token,
needed in the next step. Again, this button will vary based on the selection made above for either
:guilabel:`Sandbox` or :guilabel:`Production`.

A pop-up window will appear asking to :guilabel:`Confirm your Legal Address`. Enter the necessary
fields and scroll to the bottom of the page. The required fields are :guilabel:`First Name`,
:guilabel:`Last NAme`, :guilabel:`Primary Email`, :guilabel:`Legal Address`, and select either
:guilabel:`Individual` or :guilabel:`Business` for the :guilabel:`Account Type`. To complete the
confirmation, click :guilabel:`Sign into eBay to get a Token`.

.. note::
   eBay will contact this individual or business should there be any issues with the application
   keys. Other contacts can be added on the :menuselection:`Profile & Contacts` eBay page.

The administrator will be redirected to either a *sandbox* or *production* sign-in page for eBay.
This login is different than the eBay developer's console, it is the eBay account where the items
will be sold on. This email and/or login can differ from the eBay developer account.

Enter the :guilabel:`Email` or :guilabel:`Username` for the eBay account and sign into the eBay
account.

.. important::
   Should a test user be needed for the sandbox simulation a test user needs to be created.
   Visit `eBay's Register for Sandbox form <https://developer.ebay.com/sandbox/register>`_. Detailed
   instructions can be found on eBay's help pages: `Create a test Sandbox user
   <https://developer.ebay.com/api-docs/static/gs_create-a-test-sandbox-user.html>`_.

Grant application access
------------------------

After successfully signing into the production or sandbox environment eBay will present the
administrator with an *agreement* to grant access to the user's eBay data.
By clicking :guilabel:`Agree` the administrator is allowing eBay to link the eBay account with the
::abbr:`API (Application Programming Interface)`. This agreement can be changed at any time by
visiting eBay's account preferences.

.. warning::
   eBay has a timed sequence between signing in and agreeing to the terms for the API linkage to the
   account. Once complete a :guilabel:`User Token` will populate on the ::menuselection:`User
   Tokens` page.

A :guilabel:`User Token` will populate on the screen. Make sure to copy this token down as it will
be used in the next steps along with the :guilabel:`Application Keyset`.

.. image:: setup/user-token.png
   :align: center
   :alt: Generated user token and API explorer link on the eBay developer console.

.. important::
   Sign in to the eBay account is necessary to create to the token. The eBay developer can also
   revoke the token by clicking on the :guilabel:`Revoke a Token` link.

API explorer
------------

Now that the :guilabel:`Application Keyset` and :guilabel:`User Token` have been created a test can
be executed via the `API Explorer
<https://developer.ebay.com/DevZone/build-test/test-tool/default.aspx>`_ to ensure that the API is
configured correctly. This test will execute a simple search using the `API (Application Programming
Interface)`.

To begin the `API (Application Programming Interface)` test, click on :guilabel:`Get OAuth
Application Token`. This will populate the key into the :guilabel:`Token` field.

A basic search function is set to execute. Click on :guilabel:`Execute` to complete the test. A
successful test will respond with a :guilabel:`Call Response` of `200 OK` with a corresponding
:guilabel:`Time`.

Entering credentials into Odoo
==============================

The previously copied :guilabel:`User Token` and the :guilabel:`Application Keyset` is now ready to
be entered into the Odoo database.

Navigate back to Odoo in eBay settings (:menuselection:`Sales app --> Configuration --> Settings -->
eBay`) and paste the following credentials from eBay into the corresponding fields in Odoo.

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   * - Platform
     - Dev Key/ID
     - Token
     - App Key/ID
     - Cert Key/ID
   * - eBay
     - Dev ID
     - User Token
     - App ID (Client ID)
     - Cert ID (Client Secret)
   * - Odoo
     - Developer Key
     - Production/Sandbox Token
     - Production/Sandbox App Key
     - Production/Sandbox Cert Key

.. important::
   The :guilabel:`Application Keyset` can be accessed by going to `eBay's developer portal
   <https://go.developer.ebay.com/>`_ and navigate to the `Hi [username]` at top right of screen,
   then click on :guilabel:`Application Keysets`. Get to the *User Token* in eBay by navigating to
   the `Hi [username]` at top right of screen, then :guilabel:`User Access Tokens` and click on
   :guilabel:`Sign in to Sandbox`. The :guilabel:`User Token` can also be accessed by
   clicking on :guilabel:`User Tokens`from the :menuselection:`Application Keys` page.

Test the setup is correct by saving the credentials in Odoo. Once the initial setup is complete a
new menu tab in products will appear called `eBay` with the option to :guilabel:`Sell on eBay`.
See the :doc:`manage` documentation on how to list products.

.. tip::
   Sync Product Categories by clicking on :guilabel:`Product Categories`). Once the categories
   are synced a new menu item should appear called `eBay Category` with eBay categories brought over
   into the database. These are available when listing am eBay item through Odoo.

   .. important::
      If Product Categories beyond 4 paths are required, users will need to manually add those
      paths. This has historically been done by getting a list of all product categories beyond 4
      paths, manually importing them into the Product Category model in Odoo, then linking them
      individually to the product.
