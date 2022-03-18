import math

def SqlDwPrenticeSugita(atmos_const, diffusion_const, wind_speed, distance, fall_speed):
    """A distance weighting function.
    The pollen dispersal and deposition function from the Prentice/Sugita's (mixed) basin models and the
    HUMPOL model.

    :param atmos_const: Atmospheric constant
    :type atmos_const: float

    :param diffusion_const: Diffusion constant
    :type diffusion_const: float

    :param wind_speed: Annual average of wind speed
    :type wind_speed: float

    :param distance: distance from the vector point producing the pollen to the sampling site.
    :type distance: float

    :param fall_speed: Fall speed for the pollen taxon
    :type fall_speed: float

    :returns: pollen dispersal and deposition factor, or -1 if distance is 0."""

    if distance == 0:
        return -1
    else:
        turb_const = 2 * atmos_const
        settling_coefficient = (4 * fall_speed) / (turb_const * wind_speed * math.sqrt(math.pi * diffusion_const))
        pollen_dispersal_deposition = settling_coefficient * atmos_const * (distance ** (atmos_const * -1)) * math.exp(
            (settling_coefficient * -1) * (distance ** atmos_const))
        return pollen_dispersal_deposition

    # #* ADD NEW DISTANCE WEIGHTING FUNCTIONS HERE.
    #
    # #* template distance weighting function
    # def SqlDw_{name of your distance weighting function}(self, distance, input_variable1, input_variable2):
    #     """ A distance weighting function.
    #     {put description of your distance weighting function here}
    #
    #     :param input_variable1:
    #     :type input_variable1:
    #
    #     :param input_variable2:
    #     :type input_variable2:"""
    #     distance_weight = {your pollen distance weighting function here}
    #     return distance_weight