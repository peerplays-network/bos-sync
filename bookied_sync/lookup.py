import os
import logging

from peerplays.instance import BlockchainInstance
from peerplays.account import Account
from peerplays.proposal import Proposal, Proposals
from peerplays.storage import configStorage as config
from peerplays.witness import Witnesses
from .exceptions import ObjectNotFoundError
from .update import UpdateTransaction
from bookiesports import BookieSports
from . import log


class Lookup(dict, BlockchainInstance):
    """ This Lookup class is used as the main class which is inherited by all
        the other classes used in this module.

        It serves as:
            * connector to the blockchain and the wallet
            * configuration interface for accounts, etc.
            * management of proposal and direct buffers
            * broadcasting of buffers
            * management of blockchain object updates (see ``update()``)

        **Proposal buffers**

        New proposals can contain multiple operations which are buffered
        locally becore broadcasting.

        **Direct buffers**

        Direct buffers are used to allow quick approvals of existing proposals
        without interfering with the construction of a new proposal.

    """
    #: Singelton to store data and prevent rereading if Lookup is
    #: instantiated multiple times
    data = dict()
    approval_map = {}

    direct_buffer = None
    proposal_buffer = None
    sports_folder = None

    _approving_account = None
    _proposing_account = None
    _network_name = None

    def __init__(
        self,
        sports_folder=None,
        network=None,
        proposing_account=None,
        approving_account=None,
        *args,
        **kwargs
    ):
        """ Let's load all the data from the folder and its subfolders
        """
        kwargs.pop("proposer", None)  # Do not forward proposer
        kwargs.pop("approver", None)  # Do not forward approver
        BlockchainInstance.__init__(self, *args, **kwargs)

        # self._cwd = os.path.dirname(os.path.realpath(__file__))
        self._cwd = os.getcwd()

        if not self.proposing_account and proposing_account:
            self.proposing_account = proposing_account
        elif self.proposing_account:
            pass
        elif "default_account" in config:
            proposing_account = config["default_account"]
        else:
            log.error("No proposing account known")
            raise Exception("No proposing account known!")

        if not self.approving_account and approving_account:
            self.approving_account = approving_account
        elif self.approving_account:
            pass
        elif "default_account" in config:
            approving_account = config["default_account"]
        else:
            log.error("No approving account known")
            raise Exception("No approving account known!")

        # We define two transaction buffers
        if not Lookup.direct_buffer:
            self.clear_direct_buffer()
        if not Lookup.proposal_buffer:
            self.clear_proposal_buffer()

        # Do not reload sports if already stored in data
        if (
            not Lookup.data or
            (sports_folder and Lookup.sports_folder != sports_folder) or
            (network and Lookup._network_name != network)
        ):
            # Load sports
            self._bookiesports = BookieSports(
                network=network,
                sports_folder=sports_folder
            )
            Lookup.sports_folder = sports_folder
            Lookup._network_name = network
            self.data["sports"] = self._bookiesports

            # Ensure that the node is on the right network
            sports_chain_id = self._bookiesports.chain_id
            node_chain_id = self.blockchain.rpc.chain_params["chain_id"]
            assert sports_chain_id == "*" or sports_chain_id == node_chain_id, "You are connecting to {} while network {} requires {}".format(
                node_chain_id, network, sports_chain_id
            )

    # Redirect those to object variables to be "static" (singeltons)
    @property
    def approving_account(self):
        return Lookup._approving_account

    @approving_account.setter
    def approving_account(self, approver):
        Lookup._approving_account = approver

    @property
    def proposing_account(self):
        return Lookup._proposing_account

    @proposing_account.setter
    def proposing_account(self, proposer):
        Lookup._proposing_account = proposer
        self.clear_proposal_buffer()

    """ Legacy implementations
    """
    def set_approving_account(self, account):
        self.approving_account = account

    def set_proposing_account(self, account):
        self.proposing_account = account

    @property
    def wallet(self):
        return self.peerplays.wallet

    @staticmethod
    def _clear():
        Lookup.data = dict()
        Lookup.approval_map = {}
        Lookup.direct_buffer = None
        Lookup.proposal_buffer = None

    def clear_proposal_buffer(self, expiration=60 * 60):
        Lookup.proposal_buffer_tx = self.peerplays.new_tx()
        Lookup.proposal_buffer = self.peerplays.new_proposal(
            Lookup.proposal_buffer_tx,
            proposer=self.proposing_account,
            proposal_expiration=expiration
        )

    def clear_direct_buffer(self):
        Lookup.direct_buffer = self.peerplays.new_tx()

    def broadcast(self):
        """ Since we are using multiple txbuffers, we need to do multiple
            broadcasts
        """
        txs = list()

        for tx in [
            Lookup.direct_buffer.broadcast(),
            Lookup.proposal_buffer.broadcast()
        ]:
            if tx and dict(tx) and tx.get("operations", []):
                txs.append(UpdateTransaction(tx))

        self.clear_proposal_buffer()
        self.clear_direct_buffer()
        return txs

    def proposal_transactions(self):
        return Lookup.proposal_buffer.parent.json()

    def proposal_operations(self):
        return self.proposal_transactions()["operations"]

    def approval_transactions(self):
        return Lookup.direct_buffer.parent.json()

    def approval_operations(self):
        return self.approval_transactions()["operations"]

    def set_blocking(self, block=True):
        """ This sets a flag that forces the broadcast to block until the
            transactions made it into a block
        """
        self.peerplays.set_blocking(block)

    # List calls
    def list_sports(self):
        """ List all sports in the  lookup
        """
        from .sport import LookupSport
        return [LookupSport(x) for x in self.data["sports"]]

    def get_sport(self, sportname):
        from .sport import LookupSport
        return LookupSport(sportname)

    # Update call
    def update(self):
        """ This call makes sure that the data in the  lookup matches the data
            on the blockchain for the object we are currenty looking at.

            It works like this:

            1. Test if the  lookup knows the "id" of the object on chain
            2. If it does not, try to identify the object from the blockchain
                * if available, warn about existing id
                * if pending creation proposal, approve it
                * if none of the above, create proposal
            3. Test if  lookup and blockchain data match, if not
                * if exists proposal for update, approve
                * if not, create proposal to update
        """
        # See if  lookup already has an id
        if "id" not in self or not self["id"]:

            # Test if an object with the characteristics (i.e. name) exist
            id = self.find_id()
            if id:
                log.info((
                    "Object \"{}\" carries id {} on the blockchain. "
                    "Please update your lookup"
                ).format(self.identifier, id))
                self["id"] = id

            else:
                have_approved = False
                for has_pending_new in self.has_pending_new():
                    log.info((
                        "Object \"{}\" has pending update proposal. Approving {}"
                    ).format(self.identifier, has_pending_new))
                    have_approved = True
                    self.approve(**has_pending_new)

                    # We now test if we have approved a proposal that only had
                    # one operation, if that is the case, we can stop because
                    # no other proposed create operation should be approved
                    # other then the first in the line
                    proposal = has_pending_new.get("proposal")
                    if len(list(proposal.proposed_operations)) < 2:
                        log.info("Skipping here, as we only approve one create operation")
                        break

                if not have_approved:
                    # If not found, nor approved, then propose
                    log.info((
                        "Object \"{}\" does not exist on chain. Proposing ..."
                    ).format(self.identifier))
                    try:
                        self.propose_new()
                    except Exception as e:
                        log.critical(
                            "Trying to propose new object but failed: {}".format(str(e))
                        )

                # We do not need to go over for proposing an update
                return

        # Now test if the object is fully synced
        if not self.is_synced():
            log.info("Object not fully synced: {}: {}".format(
                self.__class__.__name__,
                str(self.get("name", ""))
            ))
            have_approved = False
            for has_pending_update in self.has_pending_update():
                log.info(
                    "Object has pending update: {}: {} in {}".format(
                        self.__class__.__name__,
                        str(self.get("name", "")),
                        str(has_pending_update)
                    ))
                have_approved = True
                self.approve(**has_pending_update)

                # In contrast to has_pending_new, we here do not break the loop
                # as we allow to approve updates multiple times if we agree. No
                # damange can be done (in contrast to has_pending_new.

            if not have_approved:
                log.info("Object has no pending update, yet: {}: {}".format(
                    self.__class__.__name__,
                    str(self.get("name", ""))
                ))
                try:
                    self.propose_update()
                except Exception as e:
                    log.critical(
                        "Trying to propose an update but failed: {}".format(str(e))
                    )

    def get_pending_operations(self, account="witness-account"):
        pending_proposals = Proposals(account)
        witnesses = Witnesses(only_active=True)
        props = list()
        for proposal in pending_proposals:
            # Do not inspect proposals that have not been proposed by a witness
            if proposal.proposer not in witnesses:
                log.info(
                    "Skipping proposal {} as it has been proposed by a non witness '{}'".format(
                        proposal["id"],
                        Account(proposal.proposer)["name"]))
                continue
            ret = []
            if not proposal["id"] in Lookup.approval_map:
                Lookup.approval_map[proposal["id"]] = {}
            for oid, operations in enumerate(proposal.proposed_operations):
                if oid not in Lookup.approval_map[proposal["id"]]:
                    Lookup.approval_map[proposal["id"]][oid] = False
                ret.append((operations, proposal["id"], oid))
            props.append(dict(proposal=proposal, data=ret))
        return props

    def get_buffered_operations(self):
        # Obtain the proposals that we have in our buffer
        # from peerplaysbase.operationids import getOperationNameForId
        for oid, op in enumerate(
            Lookup.proposal_buffer.list_operations()
        ):
            yield op.json(), "0.0.0", "0.0.%d" % oid

    def approve(self, pid, oid, **kwargs):
        """ Approve a proposal

            This call basically flags a single update operation of a proposal
            as "approved". Only if all operations in the proposal are approved,
            will this tool approve the whole proposal and otherwise ignore the
            proposal.

            The call has to identify the correct operation of a proposal on its
            own.

            Internally, a proposal is approved partially using a map that
            contains the approval of each operation in a proposal. Once all
            operations of a proposal are approved, the whole proopsal is
            approved.

            :param str pid: Proposal id
            :param int oid: Operation number within the proposal
        """
        if pid[:3] == "0.0":
            log.info("Cannot approve pending-for-broadcast proposals")
            return
        assert self.approving_account, "No approving_account defined!"

        Lookup.approval_map[pid][oid] = True

        def pretty_proposal_map():
            ret = dict()
            for k, v in Lookup.approval_map.items():
                ret[k] = "{:.1f}".format(sum(v.values()) / len(v) * 100)
            return ret

        log.info("Approval Map: {}".format(pretty_proposal_map()))

        approved_read_for_delete = []
        for p in Lookup.approval_map:
            if all(Lookup.approval_map[p].values()):
                proposal = Proposal(p)
                account = Account(self.approving_account)
                if account["id"] not in proposal["available_active_approvals"]:
                    log.info("Approving proposal {} by {}".format(
                        p, account["name"]))
                    approved_read_for_delete.append(p)
                    log.info(self.peerplays.approveproposal(
                        p,
                        account=self.approving_account,
                        append_to=Lookup.direct_buffer
                    ))
                else:
                    log.info(
                        "Proposal {} has already been approved by {}".format(
                            p, account["name"])
                    )

        # In order not to approve the same proposal again and again, we remove
        # it from the map
        for p in approved_read_for_delete:
            del Lookup.approval_map[p]

    def has_pending_new(self):
        """ This call tests if a proposal that would create this object is
            pending on-chain

            It only returns true if the exact content is proposed
        """
        from peerplaysbase.operationids import getOperationNameForId
        for proposalObject in self.get_pending_operations():
            proposal = proposalObject["proposal"]
            for op, pid, oid in proposalObject["data"]:
                if getOperationNameForId(op[0]) == self.operation_create:
                    log.debug("Testing pending proposal {}".format(proposal["id"]))
                    if self.test_operation_equal(op[1], proposal=proposal):
                        yield dict(pid=pid, oid=oid, proposal=proposal)

    def has_buffered_new(self):
        """ This call tests if an operation is buffered for proposal

            It only returns true if the exact content is proposed
        """
        from peerplaysbase.operationids import getOperationNameForId
        for op, pid, oid in self.get_buffered_operations():
            if getOperationNameForId(op[0]) == self.operation_create:
                if self.test_operation_equal(op[1]):
                    return pid, oid

    def has_pending_update(self):
        """ Test if there is an update on-chain to properly match blockchain
            content with lookup content

            It only returns true if the exact content is proposed
        """
        from peerplaysbase.operationids import getOperationNameForId
        for proposalObject in self.get_pending_operations():
            proposal = proposalObject["proposal"]
            for op, pid, oid in proposalObject["data"]:
                if getOperationNameForId(op[0]) == self.operation_update:
                    if self.test_operation_equal(op[1], proposal=proposal):
                        yield dict(pid=pid, oid=oid, proposal=proposal)

    def has_buffered_update(self):
        """ Test if there is an update buffered locally to properly match
            blockchain content with  lookup content

            It only returns true if the exact content is proposed
        """
        from peerplaysbase.operationids import getOperationNameForId
        for op, pid, oid in self.get_buffered_operations():
            if getOperationNameForId(op[0]) == self.operation_update:
                if self.test_operation_equal(op[1]):
                    return pid, oid

    @property
    def id(self):
        """ Returns the id of the object on chain

            :raises IdNotFoundError: if the object couldn't be matched to an
                object on chain
        """
        # Do we already know the id?
        if (
            "id" in self and
            self["id"] and
            isinstance(self["id"], str) and
            len(self["id"].split(".")) == 3
        ):
            return self["id"]

        # Try find the id on the blockchain
        found = self.find_id()
        if found:
            return found

        # Try find the id in the pending on-chain proposals
        # we expect the first proposalthat proposes the
        # parent object to go through
        found = list(self.has_pending_new())
        if found:
            return found[0]["pid"]  # pid of first return element

        # Try find the id in the locally buffered proposals
        found = self.has_buffered_new()  # not a generator
        if found:
            return found[1]

        raise ObjectNotFoundError(
            "Object not found on chain: {}: {}".format(
                self.__class__.__name__,
                str(self.items())))
        return found

    @property
    def parent_id(self):
        """ Obtain the id of the parent object
        """
        if hasattr(self, "parent"):
            return self.parent.id

    def is_bookiesports_in_sync(self):
        """ Test if bookiesports is in sync
        """
        for sport in self.list_sports():
            if not sport.is_synced():
                return False

            # Go through all event groups of the sport
            for e in sport.eventgroups:
                if not e.is_synced():
                    return False

            # Go through all the rules linked in the sport
            for r in sport.rules:
                if not r.is_synced():
                    return False

        return True

    def sync_bookiesports(self):
        """ Sync eventgroups and sports according to bookiesports/lookup
        """
        # Go through all sports
        for sport in self.list_sports():

            if not sport.is_synced():
                log.warning("Updating sport {}".format(sport["identifier"]))
                sport.update()

            # Go through all event groups of the sport
            for e in sport.eventgroups:

                if not e.is_synced():
                    log.warning("Updating eventgroup {}".format(e["identifier"]))
                    e.update()

            # Go through all the rules linked in the sport
            for r in sport.rules:

                if not r.is_synced():
                    log.warning("Updating rule {}".format(r["identifier"]))
                    r.update()
        return self

    # Prototypes #############################################################
    def test_operation_equal(self, sport, **kwargs):
        """ This method checks if an object or operation on the blockchain
            has the same content as an object in the  lookup
        """
        pass

    def find_id(self):
        """ Try to find an id for the object of the  lookup on the
            blockchain

            ... note:: This only checks if a sport exists with the same name in
                       **ENGLISH**!
        """
        pass

    def is_synced(self):
        """ Test if data on chain matches lookup
        """
        pass

    def propose_new(self):
        """ Propose operation to create this object
        """
        pass

    def propose_update(self):
        """ Propose to update this object to match  lookup
        """
        pass
