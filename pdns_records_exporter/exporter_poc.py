from os import name
import pymysql

# params
host = "localhost"
port = 3306
user = "powerdns_user"
passwd = "powerdns_user_password"
db = "powerdns"

# conn to db
conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
cur = conn.cursor()


# read domains
cur.execute("SELECT * FROM domains")

domains = []
for row in cur.fetchall():
    fields = map(lambda x: x[0], cur.description)
    domains.append(dict(zip(fields, row)))

# read records
for d in domains:
    cur.execute("SELECT * FROM records WHERE domain_id=%s", (d["id"],))

    records = []
    for row in cur.fetchall():
        fields = map(lambda x: x[0], cur.description)
        records.append(dict(zip(fields, row)))

    d["records"] = records

# format zone
bind_zones = []
bind_zone_path = "/etc/bind"
bind_zone_tpl = """
zone "%s" {
        type master;
        file "%s/db.%s";
};"""

for d in domains:
    zone = [ "$ORIGIN ." ]
    for r in d["records"]:
        zone.append( "%s\t%s\tIN\t%s\t%s" % (r["name"], r["ttl"], r["type"], r["content"]) )

    db_zone = "/tmp/db.%s" % d["name"]
    with open(db_zone, "w") as fz:
        fz.write("\n".join(zone))

    bind_zones.append( bind_zone_tpl % (d["name"], bind_zone_path, d["name"]) )

# finally write db zones
with open( "/tmp/db.zones", "w") as fz:
    fz.write("\n".join(bind_zones))

# close conn
cur.close()
conn.close()