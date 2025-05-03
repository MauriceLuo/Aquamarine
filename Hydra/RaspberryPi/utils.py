def map_range(x, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another."""
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def deadzone_normalise(input_value, minimum, maximum):
    """
    Applies a deadzone to the input value. Values between `minimum` and `maximum` are set to 0.
    Values below `minimum` are mapped from [-1.0, minimum] to [-1.0, 0].
    Values above `maximum` are mapped from [maximum, 1.0] to [0, 1.0].
    """
    if minimum < -1.0 or maximum > 1.0 or minimum >= maximum:
        raise ValueError("Invalid minimum or maximum range")
    
    if minimum <= input_value <= maximum:
        return 0.0
    elif input_value < minimum:
        return float(map_range(input_value, -1.0, minimum, -1.0, 0.0))
    else:  # input_value > maximum
        return float(map_range(input_value, maximum, 1.0, 0.0, 1.0))

def apply_deadzone(input_value, deadzonemax, deadzonemin):
    if -deadzonemin <= input_value <= deadzonemax:
        # Inside the deadzone
        return 0.000
    elif input_value > deadzonemax:
        # Above the deadzone, scale to 0~1
        return (input_value - deadzonemax) / (1.000 - deadzonemax)
    elif input_value < -deadzonemin:
        # Below the deadzone, scale to 0~-1
        return (input_value + deadzonemin) / (1.000 - deadzonemin)


def constrain(value, min_val,max_val):
    return max(min_val,min(max_val, value))
