import pybgpstream

matches=[]
as_path_filter="^1031_6453_3257_60798"
from_t=1708565677
to_t=1708897677
stream2 = pybgpstream.BGPStream(
            from_time=from_t,
            until_time=to_t,
            collectors=[
                "route-views.routeviews.org",
                "route-views2.routeviews.org",
                "route-views.linx",
                "route-views.isc",
                "rrc00.ripe.net",
                "rrc01.ripe.net",
                "rrc07.ripe.net",
                "route-views.oregon-ix.net",
                "route-views.eqix",
                "route-views.saopaulo",
                "route-views.nap.africa-ix.net",
                "route-views.tokyo",
                "route-views.hkix.net",
                "route-views.sg",
                "route-views.apnic.net",
                "route-views.nordu.net",
                "route-server.bcix.de",
                "route-server.cernet.net",
                "route-server.sgix.sg",
                "route-views.pie.net.au"
            ],
            record_type="updates",
            filter = f"prefix 38.62.206.0/24 and elemtype withdrawals"
        )
for rec in stream2.records():
    for elem in rec:
        print(elem)
        timestamp = elem.time
        if 'as-path' in elem.fields:
        # Access the AS path from the element
            as_path = elem.fields['as-path']
            prefix = elem.fields['prefix']
            
