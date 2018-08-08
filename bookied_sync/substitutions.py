

def decode_variables(**kwargs):
    """ This method simplyfies dealing with substitutions. It replaces the
        keywords (teams, result, ..) with instances of the below defined classes
    """
    substitutions = {
        "teams": Teams,
        "result": Result,
        "handicaps": Handicaps,
        "overunder": OverUnder,
    }

    ret = {k: v(**kwargs) for k, v in substitutions.items()}
    # Add a scalar value for metric if present
    if "metric" in kwargs:
        ret["metric"] = kwargs.get("metric")
    return ret


class Result:
    """ Defines a few variables to be used in conjuctions with {result.X}
    """
    def __init__(self, **kwargs):
        result = kwargs.get("result", [0, 0]) or [0, 0]
        self.hometeam = result[0]
        self.awayteam = result[1]

        self.total = sum([float(x) for x in result])

        # aliases
        self.home = self.hometeam
        self.away = self.awayteam


class Teams:
    """ Defines a few variables to be used in conjuctions with {teams.X}
    """
    def __init__(self, **kwargs):
        teams = kwargs.get("teams", ["", ""]) or ["", ""]
        self.home = " ".join([
            x.capitalize() for x in teams[0].split(" ")])
        self.away = " ".join([
            x.capitalize() for x in teams[1].split(" ")])


class Handicaps:
    """ Defines a few variables to be used in conjuctions with {handicaps.X}
    """
    def __init__(self, **kwargs):
        handicaps = kwargs.get("handicaps", [0, 0]) or [0, 0]

        self.home = handicaps[0]
        self.away = handicaps[1]

        # The other team has the advantage in the 'score'
        self.home_score_float = float(self.away) if float(self.away) >= 0 else 0
        self.away_score_float = float(self.home) if float(self.home) >= 0 else 0

        self.home_score_int = int(self.away) if int(self.away) >= 0 else 0
        self.away_score_int = int(self.home) if int(self.home) >= 0 else 0

        # Defaults to integer
        if kwargs.get("handicap_allow_float", True):
            self.home_score = self.home_score_float
            self.away_score = self.away_score_float
        else:
            self.home_score = self.home_score_int
            self.away_score = self.away_score_int


class OverUnder:
    """ Defines a few variables to be used in conjuctions with {handicaps.X}
    """
    def __init__(self, **kwargs):
        # store value
        self.value = float(kwargs.get("overunder", 0) or 0)


def substitute_bettingmarket_name(scheme, **kwargs):
    """ This allows to place certain variables in betting market names
    """
    ret = dict()
    for lang, name in scheme.items():
        if lang[0] == "_":
            continue
        ret[lang] = name.format(**decode_variables(**kwargs))
    return ret


def substitute_metric(text, **kwargs):
    """ This allows to place certain variables in the Rules for grading
    """
    return text.format(**decode_variables(**kwargs))
