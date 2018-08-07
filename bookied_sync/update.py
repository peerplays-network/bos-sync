from peerplaysbase.operationids import operations


class UpdateTransaction(dict):

    def __init__(self, transaction):
        """ This class makes it easier for us to deal with the proposals from
            the outside.

            Whenever you call ``lookup.update()``, you will be returned an
            list of instances of this class
        """
        if isinstance(transaction, dict):
            dict.__init__(self, transaction)

    @property
    def operations(self):
        """ List the operations returned
        """
        return self.get("operations", [])

    def is_proposal(self, op_id=0):
        """ Is this a proposal_create operation?
        """
        return self.operations[int(op_id)][0] == operations["proposal_create"]

    def is_approval(self, op_id=0):
        """ Is this the approval of an operation?
        """
        return self.operations[int(op_id)][0] == operations["proposal_update"]

    def get_proposal_id_from_approval(self, op_id=0):
        """ Obtain the proposal id from the approval
        """
        assert self.is_approval(op_id)
        return self.operations[op_id][1]["proposal"]

    def get_proposal_id_from_proposal(self, op_id=0):
        """ Try to obtain the proposal id from a proposal when it hits the
            blockchain
        """
        assert self.is_proposal(op_id)
        return self.get_result()

    def action(self, op_id=0):
        """ what kind of action is this, approval, or proposal?
        """
        if self.is_approval(op_id):
            return "approval"
        elif self.is_proposal(op_id):
            return "proposal"

    def get_proposal_id(self, op_id=0):
        """ Obtain the proposal id
        """
        if self.is_approval(op_id):
            return self.get_proposal_id_from_approval(op_id)
        elif self.is_proposal(op_id):
            return self.get_proposal_id_from_proposal(op_id)

    def __repr__(self):
        return "<UpdateTransaction expiration={} ops={} is_proposal={} is_approval={}>".format(
            self.get("expiration"),
            len(self.operations),
            {i: self.is_proposal(i) for i, _ in enumerate(self.operations)},
            {i: self.is_approval(i) for i, _ in enumerate(self.operations)}
        )

    def get_result(self, op_id=0):
        """ Obtain the proposal id from the create_propoal operation

            .. note:: this obviously only works *after* the operation has been
                added to the blockchain!
        """
        if "operation_results" not in self:
            return
        return self["operation_results"][int(op_id)][1]
