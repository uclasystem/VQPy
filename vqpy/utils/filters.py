class lasting:
    def __init__(self, trigger, time, name):
        self.trigger = trigger
        self.time = time
        self.name = f"{name}_time_periods"

    def __call__(self, obj, item):
        if self.trigger(obj.getv(item)):
            found = False
            for i in range(-1, -obj._track_length, -1):
                time_period = obj.getv(self.name, i)
                if time_period is not None:
                    found = True
                    obj._datas[-1][self.name] = time_period + 1
                    if time_period >= self.time * obj._ctx.fps:
                        return True
                    break
            if not found:
                obj._datas[-1][self.name] = 1
        return False
