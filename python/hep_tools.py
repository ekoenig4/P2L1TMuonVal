import awkward as ak
import numpy as np

from .awkward_tools import array_p4

def get_dphi(phi_1, phi_2):
    dphi = phi_2 - phi_1
    dphi = ak.where( dphi >= np.pi, dphi - 2.0*np.pi, dphi)
    dphi = ak.where( dphi < -np.pi, dphi + 2.0*np.pi, dphi)
    return dphi

def get_deta(eta_1, eta_2):
    deta = eta_2 - eta_1 
    return deta

def get_dr(eta_1, phi_1, eta_2, phi_2):
    deta = get_deta(eta_1, eta_2)
    dphi = get_dphi(phi_1, phi_2)
    return np.sqrt(deta**2 + dphi**2)

def pair_leading_parts(parts, return_mask=False):
    """Pair leading two particles in the list

    Args:
        parts (ak.Record): Record of particle values configured with_name = Momentum4D.
        return_mask (bool, optional): return mask used to get events with at least 2 particles. Defaults to False.

    Returns:
        ak.Record: The P4 sum of the paired particles
    """
    has_two_parts = ak.count(parts.pt, axis=1) >= 2
    selected_parts = parts[has_two_parts]
    leading_part, subleading_part = selected_parts[:,0], selected_parts[:,1]
    dipart = array_p4(leading_part) + array_p4(subleading_part)
    if return_mask:
        return dipart, has_two_parts
    return dipart

def pair_opposite_charged_parts(parts):
    """Pair particles together that have opposite signed charges 

    Args:
        parts (ak.Record): Record of particle values configured with_name = Momentum4D. Requires a charge field which has values of +1 and -1.
        *NOTE* If using L1 Objects with hwCharge please see pair_opposite_hw_chared_parts, as hwCharge uses 0 and 1 instead
    Returns:
        Di-Particle ak.Record: The P4 sum of the paired particles
    """
    has_opposite_charged = ak.any(parts.charge == 1, axis=1) & ak.any(parts.charge == -1, axis=1)
    selected_parts = parts[has_opposite_charged]
    # Select the leading particle in the list 
    leading_part, subleading_parts = selected_parts[:,0], selected_parts[:,1:]

    # Find the next leading particle in the list with an opposite charge
    subleading_part = subleading_parts[ ak.argmin(leading_part.charge * subleading_parts.charge, axis=1) ][:,0]
    
    dipart = leading_part + subleading_part
    return dipart

def pair_opposite_hw_charged_parts(parts):
    """Pair particles together that have opposite signed hw charges 

    Args:
        parts (ak.Record): Record of particle values configured with_name = Momentum4D. Requires a charge field which has values of 0 and 1.
        *NOTE* If using Gen or HLT Objects with non hwCharge please see pair_opposite_chared_parts, as hwCharge uses 0 and 1 instead
    Returns:
        Di-Particle ak.Record: The P4 sum of the paired particles
    """
    has_opposite_charged = ak.any(parts.charge == 0, axis=1) & ak.any(parts.charge == 1, axis=1)
    selected_parts = parts[has_opposite_charged]
    # Select the leading particle in the list 
    leading_part, subleading_parts = selected_parts[:,0], selected_parts[:,1:]

    # Find the next leading particle in the list with an opposite charge
    subleading_part = subleading_parts[ ak.argmin(leading_part.charge == subleading_parts.charge, axis=1) ][:,0]
    
    dipart = leading_part + subleading_part
    return dipart
