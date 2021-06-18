import pymysql
import pathlib

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
        
        print("reading %s domain(s) from db..." % len(self.data_zones))

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

    def export(self, output="/tmp/", zones=[], bindconf=False):
        """export to zone file format"""
        
        print("exporting to zone file format...")
        for d in self.data_zones:
            if len(zones):
                if d["name"] not in zones:
                    continue

            zone = [ "$ORIGIN ." ]

            for r in d["records"]:
                zone.append( "%s\t%s\tIN\t%s\t%s" % (r["name"], r["ttl"], r["type"], r["content"]) )

            # end zone with newline
            zone.append("")

            db_zone = pathlib.Path(  "/%s/db.%s" % (output,d["name"]) ).resolve()
            with open("%s" % db_zone, "w") as fz:
                fz.write("\n".join(zone))
                print("> %s" % db_zone )

        # create bind config ?
        if bindconf:
            pass