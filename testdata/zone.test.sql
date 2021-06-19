insert into domains (name,type) values ('zone.test','NATIVE');
insert into records (domain_id, name, type,content,ttl,prio,disabled) select id ,'zone.test', 'SOA', 'ns.zone.test. ns.zone.test. 1201604290 28800 7200 604800 900', 3600, 0, 0 from domains where name='zone.test';
insert into records (domain_id, name, type,content,ttl,prio,disabled) select id ,'zone.test', 'NS', 'ns.zone.test', 3600, 0, 0 from domains where name='zone.test';
insert into records (domain_id, name, type,content,ttl,prio,disabled) select id ,'ns.zone.test', 'A', '2.2.2.2', 3600, 0, 0 from domains where name='zone.test';
insert into records (domain_id, name, type,content,ttl,prio,disabled) select id ,'www.zone.test', 'CNAME', 'cname.zone.test', 3600, 0, 0 from domains where name='zone.test';
insert into records (domain_id, name, type,content,ttl,prio,disabled) select id ,'cname.zone.test', 'A', '1.2.3.4', 3600, 0, 0 from domains where name='zone.test';
insert into records (domain_id, name, type,content,ttl,prio,disabled) select id ,'txt.zone.test', 'TXT', '"hello world"', 3600, 0, 0 from domains where name='zone.test';
insert into records (domain_id, name, type,content,ttl,prio,disabled) select id ,'ns.zone.test', 'AAAA', 'fe80::42:1eff:feed:f6d6', 3600, 0, 0 from domains where name='zone.test';