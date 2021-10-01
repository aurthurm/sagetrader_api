import quandl
from mspt.apps.cot import schemas, models, crud
quandl.ApiConfig.api_key = 'gks41zrRs1S1xSpzycdE'
quandl.ApiConfig.verify_ssl = False


def get_quandl_code(code, categ):
    return f"CFTC/{code}_FO_{categ}"  # L_CHG L_ALL
    

def get_data(cftc_code, start_date: str = None, end_date: str = None):
    quandl_code_all = get_quandl_code(cftc_code, 'L_ALL')
    quandl_code_ch = get_quandl_code(cftc_code, 'L_CHG')
    if start_date and end_date:
        data_all = quandl.get(quandl_code_all, start_date=start_date, end_date=end_date)
        data_ch = quandl.get(quandl_code_ch, start_date=start_date, end_date=end_date)
    else:
        data_all = quandl.get(quandl_code_all)
        data_ch = quandl.get(quandl_code_ch)
    return data_all, data_ch


def persist_data(db_session, contract, data_all, data_ch):
    # print(data)
    oi_all = data_all['Open Interest']
    oi_ch = data_ch['Open Interest - Change']
    ncl_all = data_all['Noncommercial Long']
    ncl_ch = data_ch['Noncommercial Longs - Change']
    ncs_all = data_all['Noncommercial Short']
    ncs_ch = data_ch['Noncommercial Shorts - Change']
    ncsp_all = data_all['Noncommercial Spreads']
    ncsp_ch = data_ch['Noncommercial Spreads - Change']
    cl_all = data_all['Commercial Long']
    cl_ch = data_ch['Commercial Longs - Change']
    cs_all = data_all['Commercial Short']
    cs_ch = data_ch['Commercial Shorts - Change']
    trl_all = data_all['Total Long']
    trl_ch = data_ch['Total Reportable Longs - Change']
    trs_all = data_all['Total Short']
    trs_ch = data_ch['Total Reportable Shorts - Change']
    nrl_all = data_all['Nonreportable Positions Long']
    nrl_ch = data_ch['Non Reportable Longs - Change']
    nrs_all = data_all['Nonreportable Positions Short']
    nrs_ch = data_ch['Non Reportable Shorts- Change']
    
    timestamps = oi_all.index
    
    items = []
    for _time in timestamps:
        index = _time.date().__str__()
        try:
            incoming = {
                'contract_uid': contract.uid,
                'date': _time,
                'open_interest': oi_all[index],
                'open_interest_ch': oi_ch[index],
                'non_commercial_long': ncl_all[index],
                'non_commercial_long_ch': ncl_ch[index],
                'non_commercial_short': ncs_all[index],
                'non_commercial_short_ch': ncs_ch[index],
                'non_commercial_spreads': ncsp_all[index],
                'non_commercial_spreads_ch': ncsp_ch[index],
                'commercial_long': cl_all[index],
                'commercial_long_ch': cl_ch[index],
                'commercial_short': cs_all[index],
                'commercial_short_ch': cs_ch[index],
                'total_long': trl_all[index],
                'total_long_ch': trl_ch[index],
                'total_short': trs_all[index],
                'total_short_ch': trs_ch[index],
                'non_reportable_long': nrl_all[index],
                'non_reportable_long_ch': nrl_ch[index],
                'non_reportable_short': nrs_all[index],
                'non_reportable_short_ch': nrs_ch[index],
            }
            schema = schemas.CFTCReportCreate(**incoming)
            report = crud.cftc_report.get_report(db_session=db_session, date=schema.date, contract_uid=contract.uid)
            if not report:
                crud.cftc_report.create(db_session=db_session, obj_in=incoming)
            items.append(schema)
        except KeyError:
            pass
    return items


def forex_pair_biases(db_session):
    usd = crud.ctfc_contract.get_by_name(db_session=db_session, name="USDX"),
    eur = crud.ctfc_contract.get_by_name(db_session=db_session, name="EUR"),
    gbp = crud.ctfc_contract.get_by_name(db_session=db_session, name="GBP"),
    cad = crud.ctfc_contract.get_by_name(db_session=db_session, name="CAD"),
    aud = crud.ctfc_contract.get_by_name(db_session=db_session, name="AUD"),
    nzd = crud.ctfc_contract.get_by_name(db_session=db_session, name="NZD"),
    chf = crud.ctfc_contract.get_by_name(db_session=db_session, name="CHF"),
    zar = crud.ctfc_contract.get_by_name(db_session=db_session, name="ZAR"),
    jpy = crud.ctfc_contract.get_by_name(db_session=db_session, name="JPY"),
    xau = crud.ctfc_contract.get_by_name(db_session=db_session, name="GOLD"),
    
    reports = crud.cftc_report.get_multi(db_session=db_session, limit=500)
    dates = list()
    for report in reports:
        dates.append(report.date)
    
    data = {}
    for date in dates:
        if date not in data.keys():
            data[date] = dict()
        dated = data[date]
            
        reports = crud.cftc_report.get_by_date(db_session=db_session, date=date)
        
        _pairs = [
            (eur, usd),
            (eur, gbp),
            (eur, cad),
            (eur, nzd),
            (eur, jpy),
            (eur, chf),
            (eur, aud),
            
            (usd, chf),
            (usd, cad),
            (usd, jpy),
            (usd, zar),

            (gbp, usd),
            (gbp, chf),
            (gbp, jpy),
            (gbp, cad),
            (gbp, nzd),
            (gbp, aud),

            (nzd, usd),
            (nzd, cad),
            (nzd, chf),
            (nzd, jpy),
            
            (cad, jpy),
            (cad, chf),

            (aud, usd),
            (aud, nzd),
            (aud, cad),
            (aud, chf),
            (aud, jpy),

            (xau, usd),
        ]
        for _pair in _pairs:
            pair, quote_data = pair_data(reports, _pair[0],  _pair[1])
            
            if pair not in dated.keys():
                dated[pair] = dict()
    
            if quote_data:
                dated[pair] = quote_data
            else:
                dated[pair] = None
                # del dated[pair]

    return data
        

def pair_data(report, base, quote):
    base = base[0]
    quote = quote[0]
    pair = f"{base.name}/{quote.name}"
    
    _base = list(filter(lambda x: x.contract_uid == base.uid, report))
    _quote = list(filter(lambda x: x.contract_uid == quote.uid, report))

    data = dict()
    try:
        data[base.name] = _base[0]
        data[quote.name] = _quote[0]
    except Exception:
        data = None
    return pair, data
