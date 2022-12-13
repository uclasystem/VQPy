class lasting:
    """A filter constraint that checks if the property is lasting for a
    certain time period

    Returns True if the `property` is True for the given time period,
    with time period being counted accumulatively.
    Attribute with name `property`_time_periods is used to store the
    cumulative time period of condition being met.
    """

    def __init__(self, trigger, time, name):
        self.trigger = trigger
        self.time = time
        # use name given as property name of time periods
        self.name = f"{name}_time_periods"

    def __call__(self, obj, item):
        if self.trigger(obj.getv(item)):
            # increment time period if `trigger` returns True
            found = False
            # check frames from the last to the first
            for i in range(-1, -obj._track_length, -1):
                time_period = obj.getv(self.name, i)
                if time_period is not None:
                    # increment time period
                    found = True
                    obj._datas[-1][self.name] = time_period + 1
                    if time_period >= self.time * obj._ctx.fps:
                        return True
                    break
            if not found:
                # initialize time period if time_period attribute not found
                obj._datas[-1][self.name] = 1
        return False
