import awkward as ak

def unscale_l1_muon_pt(l1_muons, barrel_eta=0.83, endcap_eta=1.24, lutversion=8):
    """Unscale L1 Muon Pt 

    Args:
        l1_muons (ak.Record): Record of particle values configured with_name = Momentum4D.
        barrel_eta (float, optional): Eta region for the barrel. Defaults to 0.83.
        endcap_eta (float, optional): Eta region for the endcap. Defaults to 1.24.
    
    Returns:
        ak.Array: The unscaled l1 muon pt
    """

    ###########################
    # Unscaled BMTF Pt -> scaled Pt / 1.16
    ###########################

    l1_muon_in_barrel = abs(l1_muons.eta) < barrel_eta
    l1_muon_unscaled_bmtf_pt = l1_muons.pt / 1.16

    ###########################
    # TODO: how to unscale overlap region?
    ###########################

    print('[TODO] No unscaling applied for overlap muons. Add proper unscaling function to python/scaling_tools.py:unscale_l1_muon_pt')
    l1_muon_in_overlap = (abs(l1_muons.eta) > barrel_eta) & (abs(l1_muons.eta) < endcap_eta)

    l1_muon_unscaled_omtf_pt = (l1_muons.pt-1.)/2
    l1_muon_unscaled_omtf_pt =ak.where(l1_muon_unscaled_omtf_pt > 1, l1_muon_unscaled_omtf_pt, 1)

    ###########################
    # Unscaled EMTF Pt defined using method here 
    # https://github.com/cms-sw/cmssw/blob/master/L1Trigger/L1TMuonEndCap/src/PtAssignmentEngine2017.cc#L38-L52
    # Using ptLUTVersion_ >= 8 for 2022 LUTs
    ###########################

    l1_muon_in_endcap = abs(l1_muons.eta) > endcap_eta

    # pt sf 
    if lutversion >= 8:
        print('[NOTE] Applying endcap unscaling for ptLUTVersion >= 8')
        ###########
        # (ptLUTVersion_ >= 8) {  // First "physics" LUTs for 2022, will be deployed in June 2022
        l1_muon_unscaled_emtf_pt_sf = 1 / (1.13 + 0.015 * l1_muons.pt)
        l1_muon_unscaled_emtf_pt_sf_floor = (1 - 0.015 * 20) / 1.13 # minimum scaling for pt

    elif lutversion >= 6:
        print('[NOTE] Applying endcap unscaling for ptLUTVersion >= 6')
        ###########
        # (ptLUTVersion_ >= 6) {  // First "physics" LUTs for 2017, deployed June 7
        l1_muon_unscaled_emtf_pt_sf = 1 / (1.2 + 0.015 * l1_muons.pt)
        l1_muon_unscaled_emtf_pt_sf_floor = (1 - 0.015 * 20) / 1.2 # minimum scaling for pt


    # set the unscaled pt sf to the minimum value
    l1_muon_unscaled_emtf_pt_sf = ak.where( l1_muon_unscaled_emtf_pt_sf > l1_muon_unscaled_emtf_pt_sf_floor, l1_muon_unscaled_emtf_pt_sf, l1_muon_unscaled_emtf_pt_sf_floor )

    l1_muon_unscaled_emtf_pt = l1_muons.pt * l1_muon_unscaled_emtf_pt_sf

    ############################
    # Set unscaled pt depending on the region of eta each muon falls in
    ############################

    l1_muon_unscaled_pt = ak.where( l1_muon_in_barrel,  l1_muon_unscaled_bmtf_pt, # if in barrel
                          ak.where( l1_muon_in_overlap, l1_muon_unscaled_omtf_pt, # else if in overlap
                          ak.where( l1_muon_in_endcap,  l1_muon_unscaled_emtf_pt, # else if in endcap
                                    l1_muons.pt)))                                # else

    return l1_muon_unscaled_pt