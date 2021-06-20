import pymysql
import pathlib
import logging
import sys
import configparser

from pdns_exporter import setup_logger

logger = setup_logger("exporter")

bind_zone_tpl = """
zone "%s" {
    type master;
    file "%s";
};
"""

pdns_config = [
    "/etc/powerdns/pdns.conf.test", # for test unit
    "/etc/powerdns/pdns.conf",
    "/etc/pdns/pdns.conf"
]

class PdnsExporter:
    def __init__(self, host="127.0.0.1", port=3306, user="powerdns", passwd="", db="powerdns", connect_timeout=10):
        """exporter class"""
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.connect_timeout = connect_timeout

        self.data_zones = []

    def search_config(self, search_local=True):
        """search config file, support powerdns file"""
        # init the parser
        parser = configparser.ConfigParser()

        # search powerdns config file style on the system
        if search_local:
            for cfg in pdns_config:
                f = pathlib.Path(cfg)
                if f.exists():
                    logger.debug("reading configuration from %s" % f)
                    with open(f) as cfg_fd:
                        parser.read_string("[cfg]\n" + cfg_fd.read())
                    break
            
            # config to read ?
            if len(parser.sections()):
                if parser.get("cfg", "launch") == "gmysql":
                    self.host = parser.get("cfg", "gmysql-host")
                    self.port = parser.getint("cfg", "gmysql-port")
                    self.user = parser.get("cfg", "gmysql-user")
                    self.passwd = parser.get("cfg", "gmysql-password")
                    self.db = parser.get("cfg", "gmysql-dbname")

        else:
            logger.debug("loading default configuration")

    def connect_mysql(self):
        """connect to the database and extract records"""

        conn = pymysql.connect( host=self.host, port=self.port,
                                user=self.user, passwd=self.passwd,
                                db=self.db,
                                connect_timeout=self.connect_timeout)

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

    def metrics(self):
        """export database metrics"""
        self.search_config()
        self.connect_mysql()

        metrics = {}
        rtypes = ["A", "AAAA", "TXT", "CNAME", "PTR", "MX", "NS"]

        metrics["total_zones"] = len(self.data_zones)
        for rtype in rtypes: metrics["total_%s" % rtype] = 0 
        
        for d in self.data_zones:
            for rtype in rtypes:
                metrics["total_%s" % rtype] = len([_d for _d in d["records"] if _d.get('type')==rtype])

        return metrics

    def export(self, output="/tmp/", zones=[], bindconf=True, binddb_path="/etc/bind/"):
        """export to zone file format"""

        self.search_config()
        self.connect_mysql()

        print("exporting to zone file format...")
        bind_zones = []
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

            bind_db_path = pathlib.Path( "%s/db.%s" % (binddb_path, d["name"]))
            bind_zones.append( bind_zone_tpl % (d["name"], "%s" % bind_db_path) )
            
        # create bind config ?
        if bindconf:
            bind_zones.append("")

            db_zones = pathlib.Path( "%s/db.zones" % output )
            with open( "%s" % db_zones, "w") as fz:
                fz.write("\n".join(bind_zones))
            print("> %s" % db_zones )
