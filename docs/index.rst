.. Bookied documentation master file, created by
   sphinx-quickstart on Thu Nov  9 12:48:47 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Bookied-Sync's documentation!
========================================

``bookied-sync`` is used to keep objects synchronized with the
blockchain and simplify the use of proposals and approvals to do so.

Inheritance and Relations
-------------------------

All on-chain objects have a **Lookup** counterparty. We deal with the
following **object types**:

* :class:`bookied_sync.sport.LookupSport`,
* :class:`bookied_sync.eventgroup.LookupEventGroup`,
* :class:`bookied_sync.event.LookupEvent`,
* :class:`bookied_sync.bettingmarketgroup.LookupBettingMarketGroup`,
* :class:`bookied_sync.bettingmarket.LookupBettingMarket`, and
* :class:`bookied_sync.rule.LookupRule`

Additionally to that, a few auxiliary Lookup classes simplify extra
tasks, such as ensuring event participants are correctly validated and
normalized and event statuses can be updated properly.

For each of these objects, a separate python class exists (e.g.
:class:`bookied_sync.sport.LookupSport`). These classes inherit a general
:class:`bookied_sync.lookup.Lookup` class that and merely define object
specifics such as:

* is the lookup in sync with the blockchain,
* how to identify the on-chain object if it exists,
* which operations are used to update or create a new on-chain objects,
* how to update/create on-chain objects,

The general :class:`bookied_sync.lookup.Lookup` contains methods to

* initialized and load data from ``bookiesports``,
* *update objects* (see below)
* deal with proposals (create, approve) (see below)

Relation to BookieSports
------------------------

From the objects listed above, we distinguish between those that are
described by ``BookieSports`` and those that are dynamically managed.

Bookiesports (``pip3 install bookiesports``) constitutes a list of
YAML-formatted files with all required information to describe the
following on-chain objects in full:

* :class:`bookied_sync.sport.LookupSport`,
* :class:`bookied_sync.eventgroup.LookupEventGroup`, and
* :class:`bookied_sync.rule.LookupRule`.

These are considered rather *static* and don't change ever so often.

In contrast, the following on-chain objects are changing constantly:

* :class:`bookied_sync.event.LookupEvent`,
* :class:`bookied_sync.bettingmarketgroup.LookupBettingMarketGroup`, and
* :class:`bookied_sync.bettingmarket.LookupBettingMarket`.

As a consequence, they are not described by bookiesports but rather
triggered and managed from auto-side (e.g. via ``bos-auto``).

Updating on-chain objects
-------------------------

Conceptually, *lookups* try to either create an object on chain or update
the existing one. To do so, we first try to *find* an object on the
blockchain. Each type comes with its own implementation of ``find_id()``
which mostly compares parent ids, description, and sometimes other
parameters of an object.

Additionally, a method ``is_synced()`` is used to ensure that the entire
object is identical to what the lookup object expects (e.g. from
``bookiesports``). This comparison is done by ``test_operation_equal()``
which uses different comparators (``cmp_*``). If those evaluate
positively, the object is in sync, else it needs to be updated.

If an object could not be found by ``find_id()``, it needs to be
created.

The entire procedure is managed by
:func:`bookied_sync.lookup.Lookup.update`, so that a lookup object can
be updated/created simply by using ``lookupInstance.update()``.

Dealing with Proposals
----------------------

For sake of trust and decentralization, an object cannot just be updated
or created by a single entity. Hence, we need to go through
**proposals** for creating and/or updating each and every object type.

This means that when trying to create or update a lookup on-chain, we
need to ensure that no proposal is already awaiting approvals before
creating a new proposal. In case a proposal exists for anything we want
to do on chain, we need to approve the proposal instead.

Given that a proposal can carry multiple operations, approving an
entire proposal requires agreeing with all operations of that proposal.
To do so, we make use of the ``test_operation_equal()`` implementation
again to ensure that the proposal content is identical to the lookup's
expectations. Additionally, we maintain an ``approvalMap`` that tracks
which operation in which proposal has been agreed with. Only if all
operations in a proposal have been agreed on will the entire proposal be
approved.

Relative IDs
------------

When a new event is announced, it usually comes with betting market
groups and betting markets right away. This means a proposal is
constructed that contains the creation of not only the event, but also
the betting market group(s) and multiple betting markets. Since those
groups and markets need to refer to their parent object (the event) but
those don't have an id assigned already, the PeerPlays blockchain makes
use of so called relative object ids of the form `0.0.x` which refer to
object created in the `x-th` operation of the same proposal!

Fuzzy comparators
-----------------

Comparators are used to identify objects on-chain and ensure they are
fully synced. However, sometimes, in particular for handicap markets,
the lookup may not yet know which handicap value has been used to create
betting market groups already.
For this case, fuzzy comparators have been developed to compare handicap
(and other parameters) more lately but withing pre-defined boundaries.
This way, we can identify and find objects even though we might not
exactly know the handicap value used to create them and properly resolve
them.

Substitutions
-------------

Event descriptions, betting market group names and betting market names
are dynamically evaluated and defined. This allows us to use
*variables*, which are dynamic and filled in by ``bookie-sync``,
automatically. :doc:`nameingscheme`

API
===

.. toctree::
   :maxdepth: 3

   bookied_sync

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
