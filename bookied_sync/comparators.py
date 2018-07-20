from peerplays.event import Event
from .utils import dList2Dict


def cmp_fuzzy(spread=1):
    """ This method returns a method!

        It is used to obtain a compare method that contains a given
        'spread' (allowed threshold) around a center as provide by the
        Lookup
    """
    def cmp(soll, ist):
        def in_range(x, center):
            x = float(x)
            center = float(center)
            return x >= center - spread and x <= center + spread

        ist_description = ist.get("description", ist.get("new_description"))
        if not ist_description:
            return False

        self_description = dList2Dict(soll.description)
        description = dList2Dict(ist_description)
        if "_dynamic" not in self_description or "_dynamic" not in description:
            return False

        if self_description["_dynamic"].lower() != description["_dynamic"]:
            return False

        # Handicap ##########################
        if self_description["_dynamic"].lower() == "hc":
            assert "_hca" in self_description and \
                "_hch" in self_description and \
                "_hca" in description and \
                "_hch" in description, \
                "dynamic betting market is missing _hca or _hch"

            # Need the handicap of home and away to match fuzzy
            if (
                in_range(description["_hch"], self_description["_hch"]) and
                in_range(description["_hca"], self_description["_hca"])
            ):
                return True

        # Overunder #########################
        elif self_description["_dynamic"].lower() == "ou":
            assert "_ou" in self_description and \
                "_ou" in description, \
                "dynamic betting market is missing _overunder"
            return in_range(
                description["_ou"],
                self_description["_ou"]
            )

        else:
            raise
    # Return the new cmp function that contains the 'spread'
    return cmp


def cmp_lang(key, lang):
    def cmp(soll, ist):
        _ist = ist.get(key, ist.get("new_{}".format(key)))
        _soll = getattr(soll, key)
        if not _ist:
            return False
        lang_ist = dList2Dict(_ist).get(lang)
        lang_soll = dList2Dict(_soll).get(lang)
        return lang_ist == lang_soll
    return cmp


def cmp_langs(key, langs=["en"], apply_filter=None):
    def cmp(soll, ist):
        ist = ist.get(key, ist.get("new_{}".format(key)))
        if not ist:
            return False

        if apply_filter:
            langs = filter(apply_filter, dList2Dict(ist).keys())

        return all([
            bool([k, dList2Dict(soll.description).get(k)] in ist)
            for k in langs
        ])
    return cmp


def cmp_all_langs(key):
    def cmp(soll, ist):
        _soll = getattr(soll, key)
        _ist = ist.get(key, ist.get("new_{}".format(key)))
        return (
            (bool(_ist) and bool(_soll)) and
            all([a in _ist for a in _soll]) and
            all([b in _soll for b in _ist])
        )
    return cmp


def cmp_required_keys(*required_keys):
    def cmp(soll, ist):
        def test(data, keys):
            return any([x in data for x in keys])
        if not any([test(ist, x) for x in required_keys]):
            raise ValueError
        return True
    return cmp


def cmp_status():
    def cmp(soll, ist):
        return (
            not bool(soll.get("status")) or
            not bool(ist.get("status")) or
            ist.get("status") == soll.get("status")
        )
    return cmp


def cmp_parent(name):
    def cmp(soll, ist):
        alt_key_name = "new_{}".format(name)
        parent_id = ist.get(name, ist.get(alt_key_name))
        test_parent = soll.valid_object_id(parent_id)
        return (not test_parent or ist.get(name, ist.get(alt_key_name)) == soll.parent.id)
    return cmp


def cmp_start_time():
    def cmp(soll, ist):
        from peerplays.utils import formatTime
        return (
            not bool(soll.get("start_time")) or
            not bool(ist.get("start_time")) or
            ist.get("start_time") == formatTime(soll.get("start_time"))
        )
    return cmp


def cmp_description(lang="en"):
    return cmp_lang("description", lang)


def cmp_descriptions(langs=["en"]):
    return cmp_langs("description", langs)


def cmp_external_descriptions():
    return cmp_langs("description", apply_filter=lambda x: x[0] != "_")


def cmp_all_description():
    return cmp_all_langs("description")


def cmp_all_name():
    return cmp_all_langs("name")


def cmp_name(lang="en"):
    return cmp_lang("name", lang)


def cmp_names(langs=["en"]):
    return cmp_langs("name", langs)


def cmp_event():
    return cmp_parent("event_id")


def cmp_group():
    return cmp_parent("group_id")


def cmp_event_group():
    return cmp_parent("event_group_id")


def cmp_sport():
    return cmp_parent("sport_id")


def cmp_season():
    def cmp(soll, ist):
        """ Currently disabled
        """
        return True
    return cmp
