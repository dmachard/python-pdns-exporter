import pymysql

class Exporter:
    def __init__(self, host="127.0.0.1", port=3306, user="powerdns", passwd="", db="powerdns"):
        """exporter class"""
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db

        self.data_zones = []

        self.connect()

    def connect(self):
        """connect to the database and extract records"""
        conn = pymysql.connect(host=self.host, port=self.port,
                                    user=self.user, passwd=self.passwd,
                                    db=self.db)

        # get domains from database
        self.data_zones.clear()

        cur = conn.cursor()
        cur.execute("SELECT * FROM domains")

        for row in cur.fetchall():
            fields = map(lambda x: x[0], cur.description)
            self.data_zones.append(dict(zip(fields, row)))
        
        # get records from databases
        for d in self.data_zones:
            cur.execute("SELECT * FROM records WHERE domain_id=%s", (d["id"],))

            records = []
            for row in cur.fetchall():
                fields = map(lambda x: x[0], cur.description)
                records.append(dict(zip(fields, row)))

            d["records"] = records
            
        # close conn
        cur.close()
        conn.close()

    def export(self, output_path="/tmp/", bind_zone_path = "/etc/bind"):
        """export to zone file format"""
        bind_zones = []
        bind_zone_tpl = """
        zone "%s" {
                type master;
                file "%s/db.%s";
        };"""

        for d in self.data_zones:
            zone = [ "$ORIGIN ." ]
            for r in d["records"]:
                zone.append( "%s\t%s\tIN\t%s\t%s" % (r["name"], r["ttl"], r["type"], r["content"]) )

            db_zone = "/%s/db.%s" % (output_path,d["name"])
            with open(db_zone, "w") as fz:
                fz.write("\n".join(zone))

            bind_zones.append( bind_zone_tpl % (d["name"], bind_zone_path, d["name"]) )

        # finally write db zones
        with open( "%s/db.zones" % output_path, "w") as fz:
            fz.write("\n".join(bind_zones))