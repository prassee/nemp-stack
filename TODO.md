# Kanban Board

## Backlog
- [ ] Bronze - replica of MySQL tables 
- [ ] change from Mysql to PGSQL
- [ ] name the schemas to unnest,base,analytics
- [ ] OLAKE configs for backfill and CDC
- [ ] run OLAKE CDC sync as cron job
- [ ] Silver - Fact Tables
- [ ] Gold - Analytics based on CH MVs
- [ ] make the NMT stack to run correctly
- [ ] run iceberg specific queries from CH
- [ ] upgrade the stack to K8s Kind
- [ ] install docker and run the OLake UI setup
- [ ] sign up for AWS a/c to run NMT stack
- [ ] install temporal to trigger the OLAKE Sync job as needed
- [ ] Temporal job to run the data-publish-app to update the user details (run once at 5 mins)
- [ ] bronze layer from CDC should be named as un-nest i.e replica of Mysql Tables (synced once in 10 mins) + Data coming from 3rd Party (added with refreshed date)
- [ ] replica of bronze tables but partitioned based on created date with columns like obs_year, obs_month, obs_day <decide> what to store in Silver Layer / Data coming from 3rd party + merged with Mysql / PgSQL tables 
- [ ] create a domain layer table 
- [ ] replace PgSQL with MySQL in the current setup.
- [ ] how to pick the correct set of data from bronze and merge them in to silver (else better usethe append sync mode on OLAKE UI)
- [ ] add a temporal job on etl and data-publish app

## In Progress
- [ ] arrange storage folders in Minio for medallion architecture

## Done
- [x] load data to the Mysql Tables
- [x] configure SQLMesh 
- [x] connect to Mysql 
- [x] make CH to read Iceberg taebls and create MVs
