from peerplaysbase.operationids import operations


class UpdateTransaction(dict):

    def __init__(self, transaction):

        if isinstance(transaction, dict):
            dict.__init__(self, transaction)

    @property
    def operations(self):
        return self.get("operations", [])

    def is_proposal(self, op_id=0):
        return self.operations[int(op_id)][0] == operations["proposal_create"]

    def is_approval(self, op_id=0):
        return self.operations[int(op_id)][0] == operations["proposal_update"]

    def get_proposal_id_from_approval(self, op_id=0):
        assert self.is_approval(op_id)
        return self.operations[op_id][1]["proposal"]

    def get_proposal_id_from_proposal(self, op_id=0):
        assert self.is_proposal(op_id)
        return self.get_result()

    def action(self, op_id=0):
        if self.is_approval(op_id):
            return "approval"
        elif self.is_proposal(op_id):
            return "proposal"

    def get_proposal_id(self, op_id=0):
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
        if not "operation_results" in self:
            return
        return self["operation_results"][int(op_id)][1]
