from scripts.vcp import VCP


def test_vcp():
    vcp = VCP(key='fb47a82b0ca8567bfb72fc376716c882237c759d226f0cf9779a815')

    # 回测
    # code_list = ['002434.SZ', '002647.SZ', '300222.SZ', '300503.SZ', '300517.SZ', '300518.SZ', '300712.SZ',
    #              '603050.SH', '603110.SH', '603218.SH', '603358.SH', '603629.SH', '603657.SH', '603908.SH']
    # loopbackTesting(code_list, '20201113')
    # loopbackTestingDir()

    # stage2('000040.SZ')
    # vcp_analyse('000003.SZ')
    vcp.vcp_search()
    # getcandlecharts(code_list)
