import logging
import aiohttp
import aiohttp.web
import aiomysql.sa

# get logger
logger = logging.getLogger("pdnsexporter")

# init web router
router = aiohttp.web.RouteTableDef()

# middleware for basic auth
@aiohttp.web.middleware
async def checkauth(request, handler):
    # read authorization header
    auth = request.headers.get('Authorization')
    if auth is None: 
        return aiohttp.web.Response(status=401)

    # decode the basic authorization
    basicauth = aiohttp.BasicAuth(login="").decode(auth_header=auth)
    if basicauth.login != request.app["cfg"]["api-login"]:
        return aiohttp.web.Response(status=401)

    if basicauth.password != request.app["cfg"]["api-password"]:
        return aiohttp.web.Response(status=401)

    return await handler(request)

@router.get("/zones")
async def list_zones(request):
    """return all zones"""
    # get domains from database
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute("SELECT id,name FROM domains;")
        rows = await cursor.fetchall()
        zones = [dict(q) for q in rows]

    return aiohttp.web.json_response(zones)

@router.get("/zone/{zoneid}")
async def view_zone(request):
    """return content zone in bind format"""
    zone_id = request.match_info["zoneid"]

    # get dns records from database
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute("SELECT name, type, content, ttl FROM records WHERE domain_id=%s;", (zone_id,))
        rows = await cursor.fetchall()
        records = [dict(q) for q in rows]

    # prepare the zone file
    zone = [ "$ORIGIN ." ]
    for r in records:
        zone.append( "%s\t%s\tIN\t%s\t%s" % (r["name"], r["ttl"], r["type"], r["content"]) )
    zone.append("")

    return aiohttp.web.Response(text="\n".join(zone), content_type='text/plain')

@router.get("/metrics")
async def view_metrics(request):
    """return metrics for prometheus"""
    rtypes = ["soa", "a", "aaaa", "txt", "cname", "ptr", "mx", "ns", "svr", "ptr", "mx"]

    # fetch domains and records from database
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute("SELECT id,name FROM domains;")
        rows = await cursor.fetchall()
        zones = [dict(q) for q in rows]

    # iter on each zones to fetch records
    for zone in zones:
        async with request.app['db'].acquire() as conn:
            cursor = await conn.execute("SELECT name, type, content, ttl FROM records WHERE domain_id=%s;", (zone["id"],))
            rows = await cursor.fetchall()
            records = [dict(q) for q in rows]

            # add some stats in zone
            zone["records"] = len(records)
            for rtype in rtypes:
                zone["records_%s" % rtype] = len([r for r in records if r.get('type')==rtype.upper()])

    # prepare metrics
    metrics = []
    metrics.append( "# HELP pdnsexporter_zones_total Total number of zones" )
    metrics.append( "# TYPE pdnsexporter_zones_total counter" )
    metrics.append( "pdnsexporter_zones_total %s" % len(zones) )

    metrics.append( "# HELP pdnsexporter_records_total Total number of records" )
    metrics.append( "# TYPE pdnsexporter_records_total counter" )
    metrics.append( "pdnsexporter_records_total %s" % sum(z.get('records')  for z in zones) )

    for rtype in rtypes:
        metrics.append( "# HELP pdnsexporter_records_%s_total Total number of records %s" % (rtype, rtype.upper()) )
        metrics.append( "# TYPE pdnsexporter_records_%s_total counter" % rtype )
        metrics.append( "pdnsexporter_records_%s_total %s" % (rtype, sum(z.get('records_%s' % rtype)  for z in zones)) )

    for zone in zones:
        metrics.append( "# HELP pdnsexporter_records Number of records" )
        metrics.append( "# TYPE pdnsexporter_records counter" )
        for rtype in rtypes:
            metrics.append( "# HELP pdnsexporter_records_%s Number of records %s" % (rtype, rtype.upper()) )
            metrics.append( "# TYPE pdnsexporter_records_%s counter" % rtype )

        metrics.append( "pdnsexporter_records{identity=\"%s\"} %s" % (zone["name"], zone["records"]) )
        for rtype in rtypes:
            metrics.append( "pdnsexporter_records_%s{identity=\"%s\"} %s" % (rtype, zone["name"], zone["records_%s" % rtype]) )

    metrics.append( "" )

    return aiohttp.web.Response(text="\n".join(metrics), content_type='text/plain')

async def open_db(app):
    """create engine database"""
    engine = await aiomysql.sa.create_engine(db=app["cfg"]['db-pdns-name'],
                                             user=app["cfg"]['db-pdns-user'],
                                             password=app["cfg"]['db-pdns-password'],
                                             host=app["cfg"]['db-pdns-host'],
                                             port=int(app["cfg"]['db-pdns-port']))
    app["db"] = engine

async def close_db(app):
    """close properly all connections with database"""
    app['db'].close()
    await app['db'].wait_closed()

def setup_webapp(cfg):
    """setup the web application"""
    # init the web application
    app = aiohttp.web.Application(middlewares=[checkauth])

    # setup routes
    app.add_routes(router)

    # add config
    app["cfg"] = cfg

    # setup dababase
    app.on_startup.append(open_db)
    app.on_cleanup.append(close_db)
    return app

def run(cfg):
    # prepare tehe web application
    app = setup_webapp(cfg=cfg)
    
    # run webapp
    aiohttp.web.run_app(host=cfg["local-address"], port=cfg["local-port"], app=app, access_log=logger)