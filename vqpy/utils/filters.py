class continuing:
    """A filter constraint that checks if the condition on property
    is True for a certain duration

    Returns True if the condition on `property` is True for the given
    duration, with duration being counted accumulatively.
    Attribute with name `property`_duration is used to store the
    cumulative duration of condition being met.
    """

    def __init__(self, condition, duration, name):
        self.condition = condition
        self.duration = duration
        # use name given as property name of duration
        self.name = f"{name}_duration"

    def __call__(self, obj, item):
        if self.condition(obj.getv(item)):
            # increment duration if `condition` returns True
            found = False
            # check frames from the last to the first
            for i in range(-1, -obj._track_length, -1):
                duration = obj.getv(self.name, i)
                if duration is not None:
                    # increment duration
                    found = True
                    obj._datas[-1][self.name] = duration + 1
                    if duration >= self.duration * obj._ctx.fps:
                        return True
                    break
            if not found:
                # initialize duration if duration attribute not found
                obj._datas[-1][self.name] = 1
        return False
