drop table if exists unnest_users  ;
drop table if exists unnest_events ;

create table unnest_users 
ENGINE = IcebergS3('http://minio:9000/warehouse/unnest/users/', 'minioadmin', 'minioadmin') 
SETTINGS 
storage_catalog_type = 'rest' ,
storage_catalog_url = 'http://iceberg-rest:8181',
storage_warehouse = 'warehouse',
object_storage_endpoint = 'http://minio:9000',
storage_region = 'us-east-1';

create table if not exists unnest_events
ENGINE = IcebergS3('http://minio:9000/warehouse/unnest/events/', 'minioadmin', 'minioadmin') 
SETTINGS 
storage_catalog_type = 'rest' ,
storage_catalog_url = 'http://iceberg-rest:8181',
storage_warehouse = 'warehouse',
object_storage_endpoint = 'http://minio:9000',
storage_region = 'us-east-1';

select * from unnest_users as uu ;
select * from unnest_events as uu ;



 SET allow_experimental_database_iceberg = 1;

        CREATE DATABASE iceberg_lake
        ENGINE = DataLakeCatalog('http://lakekeeper:8181/catalog')
        SETTINGS
            catalog_type = 'rest',
            warehouse = 'warehouse',
            storage_endpoint = 'http://minio:9000',
            aws_access_key_id = 'minioadmin',
            aws_secret_access_key = 'minioadmin';

