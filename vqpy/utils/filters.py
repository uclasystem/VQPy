class continuing:
    """Checks whether the condition function continues to be true
    for a certain duration.

    Returns True if the `condition` function on `property` is True
    for the given duration, with duration being counted accumulatively.

    Cumulative duration (in number of frames) of condition being met
    will be stored in VObj as a property, with name given by `name`
    parameter as `f"{name}_duration"`. This property can be accessed
    with getv, be used in select_cons, etc.

    Attributes:
    ----------
    condition: func(property) -> bool
        Condition function to be checked.
    duration: int
        Duration in seconds.
    name: str
        Name of the attribute to store the duration.
    """

    def __init__(self, condition, duration, name):
        self.condition = condition
        self.duration = duration
        # use name given as property name of duration
        self.name = f"{name}_duration"

    def __call__(self, obj, property):
        if self.condition(obj.getv(property)):
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
