import random

def map_range(x, in_min, in_max, out_min, out_max) -> int:
    """Maps a value from one range to another."""
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def deadzone_normalise(input_value, minimum, maximum) -> float:
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


def apply_deadzone(input_value, deadzonemax, deadzonemin) -> float:
    if -deadzonemin <= input_value <= deadzonemax:
        # Inside the deadzone
        return 0.000
    elif input_value > deadzonemax:
        # Above the deadzone, scale to 0~1
        return (input_value - deadzonemax) / (1.000 - deadzonemax)
    elif input_value < -deadzonemin:
        # Below the deadzone, scale to 0~-1
        return (input_value + deadzonemin) / (1.000 - deadzonemin)


def constrain(value, min_val, max_val) -> float:
    return max(min_val, min(max_val, value))

#get ph value
output_ph : float = 7
def ph_value(target: float, button: bool) -> float:
    global output_ph
    direction:float = 0
    step = 0.1
    if output_ph > target:
        direction = -1.0
    elif output_ph < target:
        direction = 1.0
    else:
        direction = 0
    
    if button and direction != 0:
        output_ph += direction * step
        
    if not button and output_ph != 7:
        output_ph -= direction * step
    
    output_ph = round(output_ph,3)
    return round(output_ph + (random.randrange(-20,20)/100),3)
