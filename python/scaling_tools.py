import awkward as ak

def unscale_l1_muon_pt(l1_muon_pt, l1_muon_eta, barrel_eta=0.83, endcap_eta=1.24, lutversion=8):
    """Unscale L1 Muon Pt 

    Args:
        l1_muon_pt (ak.Array): Array of L1 muon pt
        l1_muon_eta (ak.Array): Array of L1 muon eta
        barrel_eta (float, optional): Eta region for the barrel. Defaults to 0.83.
        endcap_eta (float, optional): Eta region for the endcap. Defaults to 1.24.
    
    Returns:
        ak.Array: The unscaled l1 muon pt
    """

    ###########################
    # Unscaled BMTF Pt -> scaled Pt / 1.16
    ###########################

    l1_muon_in_barrel = abs(l1_muon_eta) < barrel_eta
    l1_muon_unscaled_bmtf_pt = l1_muon_pt / 1.16

    ###########################
    # TODO: how to unscale overlap region?
    ###########################

    print('[TODO] No unscaling applied for overlap muons. Add proper unscaling function to python/scaling_tools.py:unscale_l1_muon_pt')
    l1_muon_in_overlap = (abs(l1_muon_eta) > barrel_eta) & (abs(l1_muon_eta) < endcap_eta)

    l1_muon_unscaled_omtf_pt = (l1_muon_pt-1.)/2
    l1_muon_unscaled_omtf_pt =ak.where(l1_muon_unscaled_omtf_pt > 1, l1_muon_unscaled_omtf_pt, 1)

    ###########################
    # Unscaled EMTF Pt defined using method here 
    # https://github.com/cms-sw/cmssw/blob/master/L1Trigger/L1TMuonEndCap/src/PtAssignmentEngine2017.cc#L38-L52
    # Using ptLUTVersion_ >= 8 for 2022 LUTs
    ###########################

    l1_muon_in_endcap = abs(l1_muon_eta) > endcap_eta

    # pt sf 
    if lutversion >= 8:
        print('[NOTE] Applying endcap unscaling for ptLUTVersion >= 8')
        ###########
        # (ptLUTVersion_ >= 8) {  // First "physics" LUTs for 2022, will be deployed in June 2022
        l1_muon_unscaled_emtf_pt_sf = 1 / (1.13 + 0.015 * l1_muon_pt)
        l1_muon_unscaled_emtf_pt_sf_floor = (1 - 0.015 * 20) / 1.13 # minimum scaling for pt

    elif lutversion >= 6:
        print('[NOTE] Applying endcap unscaling for ptLUTVersion >= 6')
        ###########
        # (ptLUTVersion_ >= 6) {  // First "physics" LUTs for 2017, deployed June 7
        l1_muon_unscaled_emtf_pt_sf = 1 / (1.2 + 0.015 * l1_muon_pt)
        l1_muon_unscaled_emtf_pt_sf_floor = (1 - 0.015 * 20) / 1.2 # minimum scaling for pt


    # set the unscaled pt sf to the minimum value
    l1_muon_unscaled_emtf_pt_sf = ak.where( l1_muon_unscaled_emtf_pt_sf > l1_muon_unscaled_emtf_pt_sf_floor, l1_muon_unscaled_emtf_pt_sf, l1_muon_unscaled_emtf_pt_sf_floor )

    l1_muon_unscaled_emtf_pt = l1_muon_pt * l1_muon_unscaled_emtf_pt_sf

    ############################
    # Set unscaled pt depending on the region of eta each muon falls in
    ############################

    l1_muon_unscaled_pt = ak.where( l1_muon_in_barrel,  l1_muon_unscaled_bmtf_pt, # if in barrel
                          ak.where( l1_muon_in_overlap, l1_muon_unscaled_omtf_pt, # else if in overlap
                          ak.where( l1_muon_in_endcap,  l1_muon_unscaled_emtf_pt, # else if in endcap
                                    l1_muon_pt)))                                # else

    return l1_muon_unscaled_pt

def gmtMuonOfflineEtCutBarrel(offline) : return (offline+0.238)/1.137
def gmtMuonOfflineEtCutOverlap(offline) : return (offline+2.569)/1.346
def gmtMuonOfflineEtCutEndcap(offline) : return (offline-11.219)/1.503

def menu_scaling_l1_muon_pt(l1_muon_pt, l1_muon_eta, barrel_eta=0.83, endcap_eta=1.24):
    """
    Scale the L1 muon pt as defined by the menu
    https://github.com/cms-l1-dpg/Phase2-L1MenuTools/blob/30d2aa9ee83f11f228653d33e41a4ad455bd8cb1/rates/plots/rates_emulator_125x_v29.py#L66-L68

    Args:
        l1_muon_pt (ak.Array): Array of L1 muon pt
        l1_muon_eta (ak.Array): Array of L1 muon eta
        barrel_eta (float, optional): Eta region for the barrel. Defaults to 0.83.
        endcap_eta (float, optional): Eta region for the endcap. Defaults to 1.24.
    
    Returns:
        ak.Array: The menu scaled l1 muon pt
    """
    
    ###########################
    # Menu BMTF Pt 
    ###########################

    l1_muon_in_barrel = abs(l1_muon_eta) < barrel_eta
    l1_muon_menu_bmtf_pt = gmtMuonOfflineEtCutBarrel(l1_muon_pt)

    ###########################
    # Menu OMTF Pt 
    ###########################

    l1_muon_in_overlap = (abs(l1_muon_eta) > barrel_eta) & (abs(l1_muon_eta) < endcap_eta)
    l1_muon_menu_omtf_pt = gmtMuonOfflineEtCutOverlap(l1_muon_pt)

    ###########################
    # Menu EMTF Pt 
    ###########################

    l1_muon_in_endcap = abs(l1_muon_eta) > endcap_eta
    l1_muon_menu_emtf_pt = gmtMuonOfflineEtCutEndcap(l1_muon_pt)

    ############################
    # Set scaled pt depending on the region of eta each muon falls in
    ############################

    l1_muon_menu_pt = ak.where( l1_muon_in_barrel,  l1_muon_menu_bmtf_pt, # if in barrel
                      ak.where( l1_muon_in_overlap, l1_muon_menu_omtf_pt, # else if in overlap
                      ak.where( l1_muon_in_endcap,  l1_muon_menu_emtf_pt, # else if in endcap
                                l1_muon_pt)))                            # else

    return l1_muon_menu_pt



def gmtTkMuonOfflineEtCutBarrel(offline) : return (offline-0.988)/1.049
def gmtTkMuonOfflineEtCutOverlap(offline) : return (offline-1.075)/1.052
def gmtTkMuonOfflineEtCutEndcap(offline) : return (offline-1.333)/1.07

def menu_scaling_l1_tkmuon_pt(l1_muon_pt, l1_muon_eta, barrel_eta=0.83, endcap_eta=1.24):
    """
    Scale the L1 tk muon pt as defined by the menu
    https://github.com/cms-l1-dpg/Phase2-L1MenuTools/blob/30d2aa9ee83f11f228653d33e41a4ad455bd8cb1/rates/plots/rates_emulator_125x_v29.py#L70-L72

    Args:
        l1_muon_pt (ak.Array): Array of L1 muon pt
        l1_muon_eta (ak.Array): Array of L1 muon eta
        barrel_eta (float, optional): Eta region for the barrel. Defaults to 0.83.
        endcap_eta (float, optional): Eta region for the endcap. Defaults to 1.24.
    
    Returns:
        ak.Array: The menu scaled l1 muon pt
    """

    ###########################
    # Menu BMTF Pt 
    ###########################

    l1_muon_in_barrel = abs(l1_muon_eta) < barrel_eta
    l1_muon_menu_bmtf_pt = gmtTkMuonOfflineEtCutBarrel(l1_muon_pt)

    ###########################
    # Menu OMTF Pt 
    ###########################

    l1_muon_in_overlap = (abs(l1_muon_eta) > barrel_eta) & (abs(l1_muon_eta) < endcap_eta)
    l1_muon_menu_omtf_pt = gmtTkMuonOfflineEtCutOverlap(l1_muon_pt)

    ###########################
    # Menu EMTF Pt 
    ###########################

    l1_muon_in_endcap = abs(l1_muon_eta) > endcap_eta
    l1_muon_menu_emtf_pt = gmtTkMuonOfflineEtCutEndcap(l1_muon_pt)

    ############################
    # Set scaled pt depending on the region of eta each muon falls in
    ############################

    l1_muon_menu_pt = ak.where( l1_muon_in_barrel,  l1_muon_menu_bmtf_pt, # if in barrel
                      ak.where( l1_muon_in_overlap, l1_muon_menu_omtf_pt, # else if in overlap
                      ak.where( l1_muon_in_endcap,  l1_muon_menu_emtf_pt, # else if in endcap
                                l1_muon_pt)))                            # else

    return l1_muon_menu_pt