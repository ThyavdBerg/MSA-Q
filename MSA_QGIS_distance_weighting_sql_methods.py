from math import pi, sqrt, exp
from decimal import Decimal, Context

def SqlDwPrenticeSugita(turb_const, diffusion_const, wind_speed, distance, fall_speed):
    """A distance weighting function.
    The pollen dispersal and deposition function from the Prentice/Sugita's (mixed) basin models and the
    HUMPOL model.

    :param turb_const: Atmospheric constant (n)
    :type turb_const: float

    :param diffusion_const: Vertical Diffusion constant (Cz)
    :type diffusion_const: float

    :param wind_speed: Annual average of wind speed (u)
    :type wind_speed: float

    :param distance: distance from the vector point producing the pollen to the sampling site. (z)
    :type distance: float

    :param fall_speed: Fall speed for the pollen taxon (vg)
    :type fall_speed: float

    :returns: pollen dispersal and deposition factor, or -1 if distance is 0."""


    if distance == 0:
        return -1
    else:
        # change everything to decimal instead of float to deal with floating point rounding error
        # not sure yet if this is necessary, but leaving it in for now.
        context = Context(prec=6)
        turb_const = Decimal(turb_const)
        diffusion_const = Decimal(diffusion_const)
        wind_speed = Decimal(wind_speed)
        distance = Decimal(distance)
        fall_speed = Decimal(fall_speed)
        decimal_pi = context.create_decimal_from_float(pi)

        atmos_const = Decimal(0.5) * turb_const
        pollen_dispersal_deposition = ((Decimal(0.5)/(decimal_pi*distance)) * ((4 * fall_speed) / (turb_const * wind_speed * context.sqrt(decimal_pi)*diffusion_const) * atmos_const * (distance ** (atmos_const-1)) * context.exp(
            (-1*(4 * fall_speed) / (turb_const * wind_speed * context.sqrt(decimal_pi)*diffusion_const)) * (distance ** atmos_const))))*10000000


    # simple, non decimal converted version
    # if distance == 0:
    #     return -1
    # else:
    #     atmos_const = 0.5 * turb_const
    #     pollen_dispersal_deposition = (0.5/(pi*distance)) * ((4 * fall_speed) / (turb_const * wind_speed * sqrt(pi)*diffusion_const) * atmos_const * (distance ** (atmos_const-1)) * exp(
    #         (-1*(4 * fall_speed) / (turb_const * wind_speed * sqrt(pi)*diffusion_const)) * (distance ** atmos_const)))

        return f"{Decimal(pollen_dispersal_deposition):.6E}" #cast to scientific notation to preserve accuracy in saving the number in SQLite


####* ADD NEW DISTANCE WEIGHTING FUNCTIONS HERE.

####* template distance weighting function, please copy, don't overwrite
# def SqlDw{name of your distance weighting function}(self, distance, input_variable1, input_variable2):
#     """ A distance weighting function.
#     {put description of your distance weighting function here}
#     :param input_variable1:
#     :type input_variable1:
#     :param input_variable2:
#     :type input_variable2:"""
#     distance_weight = {your pollen distance weighting function here}
#     return distance_weight